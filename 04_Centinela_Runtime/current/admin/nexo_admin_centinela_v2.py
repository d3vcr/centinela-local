#!/usr/bin/env python3
"""NEXO ADMIN + CENTINELA v2.

Panel administrativo local para Raspberry Pi NEXO.

Seguridad por diseño:
- Solo lectura por defecto.
- No publica MQTT.
- No activa salidas físicas.
- No modifica firmware, Tailscale, SQLite u odómetro.
- La web escucha solo en 127.0.0.1.
- Reinicios de servicios requieren root, --apply y confirmación exacta.

Instalación en la Pi:
    sudo python3 nexo_admin_centinela_v2.py install

Uso:
    nexo-admin status
    nexo-admin doctor
    nexo-admin watch
    nexo-admin report --bundle
    nexo-admin commands --verbose
    nexo-admin logs nexo-centinela.service
    nexo-admin tunnel
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import html
import http.server
import json
import logging
import os
import platform
import re
import shutil
import signal
import socket
import sqlite3
import subprocess
import sys
import tarfile
import textwrap
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping, Sequence

VERSION = "2.0.0"
APP_NAME = "NEXO ADMIN + CENTINELA v2"
DEVICE_ID = "ECU_570A8AB4"
API_BASE = os.environ.get("NEXO_API_BASE", "http://127.0.0.1:8080").rstrip("/")
CENTINELA_BASE = os.environ.get("NEXO_CENTINELA_BASE", "http://127.0.0.1:8090").rstrip("/")
BACKUP_BASE = os.environ.get("NEXO_BACKUP_BASE", "http://127.0.0.1:8081").rstrip("/")
FRONTEND_BASE = os.environ.get("NEXO_FRONTEND_BASE", "http://127.0.0.1:8181").rstrip("/")
DB_PATH = Path(os.environ.get("NEXO_DB_PATH", "/var/lib/nexo/db/nexo.sqlite3"))
NEXO_ROOT = Path(os.environ.get("NEXO_ROOT", "/opt/nexo"))
CURRENT_FRONTEND = Path("/opt/nexo/current-frontend")
INSTALL_DIR = Path("/opt/nexo/admin")
INSTALL_PATH = INSTALL_DIR / "nexo_admin_centinela_v2.py"
WRAPPER_PATH = Path("/usr/local/bin/nexo-admin")
SERVICE_PATH = Path("/etc/systemd/system/nexo-admin-v2.service")
DEFAULT_STATE_DIR = Path("/var/lib/nexo/admin")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8190

SAFETY_EXPECTED = {
    "physical_outputs_enabled": False,
    "relay_outputs_enabled": False,
    "remote_start_locked": True,
}

CORE_SERVICES = [
    "mosquitto.service",
    "ecu-remote-relay.service",
    "nexo-ingest.service",
    "nexo-normalizer.timer",
    "nexo-normalizer.service",
    "nexo-api.service",
    "nexo-cockpit.service",
    "nexo-centinela.service",
    "nexo-orbital-guardian-temp.service",
    "nexo-startup-verify.service",
    "tailscaled.service",
]

MUTABLE_SERVICE_ALLOWLIST = {
    "nexo-normalizer.timer",
    "nexo-normalizer.service",
    "nexo-api.service",
    "nexo-cockpit.service",
    "nexo-centinela.service",
    "nexo-orbital-guardian-temp.service",
    "nexo-startup-verify.service",
}

EXPECTED_PORTS = {
    8080: "API NEXO readonly",
    8081: "Cockpit/respaldo",
    8090: "Centinela",
    8181: "Orbital Guardian",
    8190: "NEXO Admin",
}

HTTP_TARGETS = {
    "api_health": f"{API_BASE}/health",
    "api_live": f"{API_BASE}/live",
    "api_gps": f"{API_BASE}/gps",
    "api_odometer": f"{API_BASE}/odometer",
    "centinela_health": f"{CENTINELA_BASE}/health",
    "centinela_state": f"{CENTINELA_BASE}/state",
    "centinela_events": f"{CENTINELA_BASE}/events",
    "backup_root": f"{BACKUP_BASE}/",
    "frontend_root": f"{FRONTEND_BASE}/",
    "frontend_cockpit": f"{FRONTEND_BASE}/cockpit/",
    "frontend_dashboard": f"{FRONTEND_BASE}/dashboard/",
    "frontend_street": f"{FRONTEND_BASE}/street/",
}

CATALOG_PATHS = [
    Path("/opt/nexo/config/nexo_ecu_commands.json"),
    Path("/opt/nexo/nexo_ecu_commands.json"),
    Path("/opt/nexo/docs/nexo_ecu_commands.json"),
    Path("/var/lib/nexo/admin/nexo_ecu_commands.json"),
]

# Referencia de los 42 comandos observados. Esta herramienta nunca los transmite.
BUILTIN_COMMANDS: list[dict[str, Any]] = [
    {"id":"diag","category":"diagnostico","risk":"diagnostic","description":"Publica diagnóstico completo.","payload":{"cmd":"diag"}},
    {"id":"config_dump","category":"diagnostico","risk":"diagnostic","description":"Devuelve configuración completa.","payload":{"cmd":"config_dump"}},
    {"id":"input_selftest","category":"diagnostico","risk":"diagnostic","description":"Devuelve canales digitales.","payload":{"cmd":"input_selftest"}},
    {"id":"config_save","category":"sistema","risk":"persistent","description":"Guarda configuración actual.","payload":{"cmd":"config_save"}},
    {"id":"config_defaults","category":"sistema","risk":"destructive","description":"Restaura valores predeterminados.","payload":{"cmd":"config_defaults"}},
    {"id":"safe_reboot","category":"sistema","risk":"sensitive","description":"Reinicia la ESP32.","payload":{"cmd":"safe_reboot"}},
    {"id":"safe_mode","category":"sistema","risk":"persistent","description":"Safe Mode cosmético.","payload":{"cmd":"safe_mode","enabled":True}},
    {"id":"set_active_level","category":"canales","risk":"persistent","description":"Define LOW/HIGH activo.","payload":{"cmd":"set_active_level","channel":"brake_global","active_level":"LOW"}},
    {"id":"set_debounce","category":"canales","risk":"persistent","description":"Configura debounce.","payload":{"cmd":"set_debounce","channel":"brake_global","debounce_ms":40}},
    {"id":"set_blink_window","category":"canales","risk":"persistent","description":"Ventana de parpadeo.","payload":{"cmd":"set_blink_window","channel":"turn_left","window_ms":800}},
    {"id":"set_channel_connected","category":"canales","risk":"persistent","description":"Declara canal conectado.","payload":{"cmd":"set_channel_connected","channel":"lights_main","connected":True}},
    {"id":"set_channel_approved","category":"canales","risk":"persistent","description":"Marca canal aprobado.","payload":{"cmd":"set_channel_approved","channel":"lights_main","approved":True}},
    {"id":"force_channel","category":"banco","risk":"bench","description":"Fuerza estado lógico de banco.","payload":{"cmd":"force_channel","channel":"brake_global","state":True}},
    {"id":"force_channel_clear","category":"banco","risk":"bench","description":"Libera un canal forzado.","payload":{"cmd":"force_channel_clear","channel":"brake_global"}},
    {"id":"force_clear_all","category":"banco","risk":"bench","description":"Libera todos los canales.","payload":{"cmd":"force_clear_all"}},
    {"id":"rpm_set_ppr","category":"rpm","risk":"blocked","description":"Ajuste PPR bloqueado operativamente.","payload":{"cmd":"rpm_set_ppr","ppr":1.0}},
    {"id":"rpm_cal_target","category":"rpm","risk":"blocked","description":"Autocalibración RPM bloqueada.","payload":{"cmd":"rpm_cal_target","rpm":1400}},
    {"id":"rpm_set_smoothing","category":"rpm","risk":"persistent","description":"Ajusta suavizado visual.","payload":{"cmd":"rpm_set_smoothing","alpha":0.25}},
    {"id":"rpm_reset_counters","category":"rpm","risk":"sensitive","description":"Reinicia contadores RPM.","payload":{"cmd":"rpm_reset_counters"}},
    {"id":"set_fuel_connected","category":"analogicos","risk":"persistent","description":"Declara boya conectada.","payload":{"cmd":"set_fuel_connected","connected":True}},
    {"id":"set_battery_connected","category":"analogicos","risk":"persistent","description":"Declara batería conectada.","payload":{"cmd":"set_battery_connected","connected":True}},
    {"id":"set_battery_divider","category":"analogicos","risk":"persistent","description":"Configura divisor de batería.","payload":{"cmd":"set_battery_divider","ratio":4.7037}},
    {"id":"fuel_sample","category":"combustible","risk":"diagnostic","description":"Solicita muestra ADC de gasolina.","payload":{"cmd":"fuel_sample"}},
    {"id":"battery_sample","category":"bateria","risk":"diagnostic","description":"Solicita muestra de batería.","payload":{"cmd":"battery_sample"}},
    {"id":"fuel_cal_start","category":"combustible","risk":"persistent","description":"Inicia calibración.","payload":{"cmd":"fuel_cal_start"}},
    {"id":"fuel_mark","category":"combustible","risk":"persistent","description":"Marca empty/low/mid/full.","payload":{"cmd":"fuel_mark","point":"empty"}},
    {"id":"fuel_cal_apply","category":"combustible","risk":"persistent","description":"Aplica calibración.","payload":{"cmd":"fuel_cal_apply"}},
    {"id":"fuel_cal_reset","category":"combustible","risk":"destructive","description":"Borra puntos de calibración.","payload":{"cmd":"fuel_cal_reset"}},
    {"id":"fuel_curve","category":"combustible","risk":"persistent","description":"Curva normal/inverted.","payload":{"cmd":"fuel_curve","mode":"normal"}},
    {"id":"fuel_set_manual","category":"combustible","risk":"override","description":"Fuerza porcentaje manual.","payload":{"cmd":"fuel_set_manual","percent":50}},
    {"id":"fuel_manual_clear","category":"combustible","risk":"sensitive","description":"Quita override manual.","payload":{"cmd":"fuel_manual_clear"}},
    {"id":"set_fuel_capacity_l","category":"combustible","risk":"persistent","description":"Configura capacidad del tanque.","payload":{"cmd":"set_fuel_capacity_l","liters":6.0}},
    {"id":"set_fuel_consumption_lph","category":"combustible","risk":"persistent","description":"Configura consumo estimado L/h.","payload":{"cmd":"set_fuel_consumption_lph","lph":1.5}},
    {"id":"usage_reset_totals","category":"uso","risk":"destructive","description":"Borra horómetro y sesiones.","payload":{"cmd":"usage_reset_totals"}},
    {"id":"set_stat","category":"estadisticas","risk":"persistent","description":"Guarda estadística genérica.","payload":{"cmd":"set_stat","key":"example","value":"0"}},
    {"id":"stat_clear","category":"estadisticas","risk":"sensitive","description":"Borra una estadística.","payload":{"cmd":"stat_clear","key":"example"}},
    {"id":"stat_clear_all","category":"estadisticas","risk":"destructive","description":"Borra todas las estadísticas.","payload":{"cmd":"stat_clear_all"}},
    {"id":"oled_page","category":"oled","risk":"cosmetic","description":"Fija página OLED.","payload":{"cmd":"oled_page","page":0}},
    {"id":"oled_auto","category":"oled","risk":"cosmetic","description":"Activa rotación automática.","payload":{"cmd":"oled_auto"}},
    {"id":"oled_dwell","category":"oled","risk":"cosmetic","description":"Tiempo por página.","payload":{"cmd":"oled_dwell","ms":2600}},
    {"id":"sim","category":"simulacion","risk":"bench","description":"Simulación manual de banco.","payload":{"cmd":"sim","enabled":True}},
    {"id":"sim_auto","category":"simulacion","risk":"bench","description":"Simulación automática.","payload":{"cmd":"sim_auto","enabled":True}},
]

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
SECRET_PATTERNS = [
    (re.compile(r"(?i)(password|passwd|token|secret|api[_-]?key)\s*[:=]\s*\S+"), r"\1=<REDACTED>"),
    (re.compile(r"(?i)(Authorization:\s*Bearer)\s+\S+"), r"\1 <REDACTED>"),
]

@dataclasses.dataclass
class CmdResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    elapsed_ms: int
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self) | {"ok": self.ok}

@dataclasses.dataclass
class Check:
    name: str
    status: str
    detail: str


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def redact(text: str) -> str:
    value = ANSI_RE.sub("", text or "")
    for pattern, replacement in SECRET_PATTERNS:
        value = pattern.sub(replacement, value)
    return value


def get_state_dir() -> Path:
    candidate = Path(os.environ.get("NEXO_ADMIN_STATE_DIR", str(DEFAULT_STATE_DIR)))
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        probe = candidate / ".probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return candidate
    except OSError:
        fallback = Path.home() / ".local/state/nexo-admin-v2"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback

STATE_DIR = get_state_dir()
REPORT_DIR = STATE_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = STATE_DIR / "nexo-admin-v2.log"
logging.basicConfig(
    level=os.environ.get("NEXO_ADMIN_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stderr), logging.FileHandler(LOG_PATH, encoding="utf-8")],
)
LOG = logging.getLogger("nexo-admin-v2")


def run(command: Sequence[str], timeout: float = 8.0) -> CmdResult:
    started = time.monotonic()
    cmd = [str(x) for x in command]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return CmdResult(cmd, proc.returncode, redact(proc.stdout), redact(proc.stderr), int((time.monotonic()-started)*1000))
    except subprocess.TimeoutExpired as exc:
        return CmdResult(cmd, 124, redact(exc.stdout or ""), redact(exc.stderr or "timeout"), int((time.monotonic()-started)*1000), True)
    except OSError as exc:
        return CmdResult(cmd, 127, "", redact(str(exc)), int((time.monotonic()-started)*1000))


def http_fetch(url: str, timeout: float = 4.0) -> dict[str, Any]:
    started = time.monotonic()
    req = urllib.request.Request(url, headers={"Accept":"application/json,text/plain,*/*","User-Agent":f"nexo-admin/{VERSION}","Cache-Control":"no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(2_000_001)
            text = raw[:2_000_000].decode("utf-8", errors="replace")
            ctype = response.headers.get("Content-Type", "")
            data: Any = None
            parse_error = None
            if "json" in ctype.lower() or text.lstrip().startswith(("{", "[")):
                try:
                    data = json.loads(text)
                except json.JSONDecodeError as exc:
                    parse_error = str(exc)
            return {"ok":200 <= response.status < 400,"url":url,"status":response.status,"content_type":ctype,"elapsed_ms":int((time.monotonic()-started)*1000),"data":data,"text":redact(text[:20000]) if data is None else None,"parse_error":parse_error,"truncated":len(raw)>2_000_000}
    except urllib.error.HTTPError as exc:
        body = exc.read(20000).decode("utf-8", errors="replace")
        return {"ok":False,"url":url,"status":exc.code,"elapsed_ms":int((time.monotonic()-started)*1000),"error":redact(str(exc)),"text":redact(body)}
    except Exception as exc:
        return {"ok":False,"url":url,"status":None,"elapsed_ms":int((time.monotonic()-started)*1000),"error":redact(f"{type(exc).__name__}: {exc}")}


def deep_find(obj: Any, key: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(obj, Mapping):
        for current, value in obj.items():
            if current == key:
                found.append(value)
            found.extend(deep_find(value, key))
    elif isinstance(obj, list):
        for value in obj:
            found.extend(deep_find(value, key))
    return found


def systemd_state(unit: str) -> dict[str, Any]:
    result = run(["systemctl","show",unit,"-p","LoadState","-p","UnitFileState","-p","ActiveState","-p","SubState","-p","Result","-p","ExecMainStatus","-p","NRestarts","-p","MainPID","-p","TimersMonotonic","--no-pager"], timeout=5)
    data: dict[str, Any] = {"unit":unit,"command_ok":result.ok}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            data[key] = value
    if not result.ok:
        data["error"] = result.stderr.strip()
    return data


def services_snapshot() -> list[dict[str, Any]]:
    return [systemd_state(unit) for unit in CORE_SERVICES]


def listeners_snapshot() -> dict[str, Any]:
    result = run(["ss","-ltnp"], timeout=5)
    listeners = []
    pattern = re.compile(r"LISTEN\s+\d+\s+\d+\s+(\S+):(\d+)\s+")
    for line in result.stdout.splitlines():
        match = pattern.search(line)
        if match and int(match.group(2)) in EXPECTED_PORTS:
            port = int(match.group(2))
            listeners.append({"host":match.group(1),"port":port,"role":EXPECTED_PORTS[port],"raw":line.strip()})
    return {"ok":result.ok,"listeners":listeners,"error":result.stderr.strip() or None}


def filesystem_snapshot() -> dict[str, Any]:
    data: dict[str, Any] = {}
    for path in [DB_PATH, Path(str(DB_PATH)+"-wal"), Path(str(DB_PATH)+"-shm")]:
        try:
            stat = path.stat()
            data[str(path)] = {"exists":True,"size_bytes":stat.st_size,"size_mib":round(stat.st_size/1024/1024,2),"mtime":dt.datetime.fromtimestamp(stat.st_mtime,dt.timezone.utc).isoformat()}
        except FileNotFoundError:
            data[str(path)] = {"exists":False}
        except OSError as exc:
            data[str(path)] = {"exists":None,"error":str(exc)}
    base = DB_PATH.parent if DB_PATH.parent.exists() else Path("/")
    usage = shutil.disk_usage(base)
    data["disk"] = {"total_gib":round(usage.total/1024**3,2),"used_gib":round(usage.used/1024**3,2),"free_gib":round(usage.free/1024**3,2),"used_pct":round(usage.used/usage.total*100,1) if usage.total else None}
    return data


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return conn.execute("SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name=? LIMIT 1", (table,)).fetchone() is not None


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    safe = table.replace('"','""')
    return [str(row[1]) for row in conn.execute(f'PRAGMA table_info("{safe}")')]


def latest_row(conn: sqlite3.Connection, table: str, preferred: Sequence[str]) -> dict[str, Any] | None:
    if not table_exists(conn, table):
        return None
    columns = table_columns(conn, table)
    selected = [c for c in preferred if c in columns] or columns[:20]
    order = next((c for c in ("id","received_ts","updated_ts") if c in columns), None)
    safe_table = table.replace('"','""')
    quoted = ", ".join('"'+c.replace('"','""')+'"' for c in selected)
    sql = f'SELECT {quoted} FROM "{safe_table}"' + (f' ORDER BY "{order}" DESC' if order else "") + " LIMIT 1"
    row = conn.execute(sql).fetchone()
    return dict(zip(selected, row)) if row else None


def db_snapshot() -> dict[str, Any]:
    result: dict[str, Any] = {"path":str(DB_PATH),"exists":DB_PATH.exists(),"readonly_requested":True,"query_only":None,"accessible":False,"tables":{}}
    if not DB_PATH.exists():
        return result
    uri = f"file:{urllib.parse.quote(str(DB_PATH), safe='/')}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True, timeout=1.0)
        conn.execute("PRAGMA query_only=ON")
        conn.execute("PRAGMA busy_timeout=1000")
        result["query_only"] = int(conn.execute("PRAGMA query_only").fetchone()[0])
        result["journal_mode"] = str(conn.execute("PRAGMA journal_mode").fetchone()[0])
        result["accessible"] = True
        result["tables"]["raw_mqtt"] = latest_row(conn,"raw_mqtt",["id","received_ts","topic","device_id"])
        result["tables"]["ecu_samples"] = latest_row(conn,"ecu_samples",["id","received_ts","device_id","firmware","schema_version","rpm","rpm_real","rpm_real_value","rpm_estado_senal","fuel_percent","fuel_raw","battery_v","battery_estado","ignition_state","brake_global","lights_state","turn_left","turn_right","online","mqtt_estado","ssid","rssi","boot_id","publish_counter","physical_outputs_enabled","relay_outputs_enabled","remote_start_locked"])
        result["tables"]["gps_samples"] = latest_row(conn,"gps_samples",["id","received_ts","lat","lon","accuracy_m","speed_kmh","satellites","provider","fresh","gps_received_age_s"])
        result["tables"]["odometer_state"] = latest_row(conn,"odometer_state",["id","updated_ts","total_km","trip_a_km","trip_b_km","writer"])
        if table_exists(conn,"system_state"):
            cols = table_columns(conn,"system_state")
            if {"key","value"}.issubset(cols):
                rows = conn.execute("SELECT key,value,updated_ts FROM system_state ORDER BY key" if "updated_ts" in cols else "SELECT key,value,NULL FROM system_state ORDER BY key").fetchall()
                result["tables"]["system_state"] = [{"key":r[0],"value":r[1],"updated_ts":r[2]} for r in rows[:200]]
        conn.close()
    except sqlite3.Error as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def release_snapshot() -> dict[str, Any]:
    data: dict[str, Any] = {"current_frontend_link":str(CURRENT_FRONTEND),"current_frontend":None,"releases":[],"backups":[]}
    try:
        if CURRENT_FRONTEND.exists() or CURRENT_FRONTEND.is_symlink():
            data["current_frontend"] = str(CURRENT_FRONTEND.resolve(strict=False))
    except OSError as exc:
        data["current_frontend_error"] = str(exc)
    for key, directory in (("releases",NEXO_ROOT/"releases"),("backups",Path("/var/lib/nexo/backups"))):
        if directory.exists():
            try:
                items = sorted((p for p in directory.iterdir() if p.is_dir()), key=lambda p:p.stat().st_mtime, reverse=True)
                data[key] = [{"name":p.name,"path":str(p),"mtime":dt.datetime.fromtimestamp(p.stat().st_mtime,dt.timezone.utc).isoformat()} for p in items[:20]]
            except OSError as exc:
                data[key+"_error"] = str(exc)
    return data


def timer_snapshot() -> dict[str, Any]:
    data = systemd_state("nexo-normalizer.timer")
    cat = run(["systemctl","cat","nexo-normalizer.timer","--no-pager"], timeout=5)
    data["schedule_lines"] = [line.strip() for line in cat.stdout.splitlines() if any(k in line for k in ("OnBootSec","OnActiveSec","OnUnitInactiveSec","AccuracySec","Persistent","RandomizedDelaySec"))]
    data["unit_text"] = cat.stdout if cat.ok else None
    data["unit_error"] = cat.stderr.strip() or None
    return data


def tailscale_snapshot() -> dict[str, Any]:
    result = run(["tailscale","serve","status","--json"], timeout=6)
    if result.ok and result.stdout.strip():
        try:
            return {"ok":True,"format":"json","data":json.loads(result.stdout)}
        except json.JSONDecodeError:
            pass
    result = run(["tailscale","serve","status"], timeout=6)
    routes, current = [], ""
    for raw in result.stdout.splitlines():
        line = raw.strip()
        if line.startswith(("https://","http://")):
            current = line
        elif "proxy " in line:
            routes.append({"url":current,"target":line.split("proxy ",1)[1].strip()})
    routes.sort(key=lambda item:(item["url"],item["target"]))
    return {"ok":result.ok,"format":"text","routes":routes,"raw":result.stdout,"error":result.stderr.strip() or None}


def host_snapshot() -> dict[str, Any]:
    load = os.getloadavg() if hasattr(os,"getloadavg") else (None,None,None)
    try:
        uptime = float(Path("/proc/uptime").read_text().split()[0])
    except Exception:
        uptime = None
    try:
        temp = int(Path("/sys/class/thermal/thermal_zone0/temp").read_text().strip())/1000
    except Exception:
        temp = None
    throttled = run(["vcgencmd","get_throttled"], timeout=3)
    return {"hostname":socket.gethostname(),"platform":platform.platform(),"python":sys.version.split()[0],"uid":os.geteuid() if hasattr(os,"geteuid") else None,"time_utc":utc_now(),"uptime_seconds":uptime,"load_1m":load[0],"load_5m":load[1],"load_15m":load[2],"temperature_c":temp,"throttled":throttled.stdout.strip() if throttled.ok else None,"state_dir":str(STATE_DIR),"log_path":str(LOG_PATH)}


def command_catalog() -> dict[str, Any]:
    for path in CATALOG_PATHS:
        if not path.exists():
            continue
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            commands = parsed.get("commands")
            if isinstance(commands,list):
                base = {item["id"]:item for item in BUILTIN_COMMANDS}
                normalized = []
                for item in commands:
                    cid = item.get("id")
                    fallback = base.get(cid,{})
                    normalized.append({"id":cid,"category":item.get("category",fallback.get("category")),"risk":fallback.get("risk","unknown"),"description":item.get("label") or fallback.get("description"),"payload":item.get("payload") or fallback.get("payload"),"params":item.get("params",[]),"persists":item.get("persists"),"response":item.get("response"),"tx_policy":"BLOCKED"})
                known = {item.get("id") for item in normalized}
                normalized.extend(dict(item,tx_policy="BLOCKED",source="builtin-v2-reference") for item in BUILTIN_COMMANDS if item["id"] not in known)
                return {"source":str(path),"meta":parsed.get("_meta",{}),"topics":parsed.get("topics",{}),"commands":normalized,"tx_enabled":False,"policy":"Catálogo visible; publicación MQTT deshabilitada."}
        except (OSError,json.JSONDecodeError) as exc:
            LOG.warning("No se pudo cargar catálogo %s: %s", path, exc)
    return {"source":"builtin-v2-reference","meta":{"device_id":DEVICE_ID,"warning":"Plantillas de referencia; validar contra firmware exacto."},"commands":[dict(item,tx_policy="BLOCKED") for item in BUILTIN_COMMANDS],"tx_enabled":False,"policy":"Catálogo visible; publicación MQTT deshabilitada."}


def endpoint_snapshot(include_bodies: bool=True) -> dict[str, Any]:
    result = {}
    for name,url in HTTP_TARGETS.items():
        item = http_fetch(url)
        if not include_bodies:
            data = item.get("data")
            item["summary"] = {key:(deep_find(data,key)[0] if deep_find(data,key) else None) for key in ("ok","status","state","generated_at")}
            item.pop("data",None); item.pop("text",None)
        result[name] = item
    return result


def normalize_bool(value: Any) -> bool | None:
    if isinstance(value,bool): return value
    if isinstance(value,(int,float)): return bool(value)
    if isinstance(value,str):
        low = value.strip().lower()
        if low in {"true","1","yes","on"}: return True
        if low in {"false","0","no","off"}: return False
    return None


def extract_safety(endpoints: Mapping[str,Any], database: Mapping[str,Any]) -> dict[str,Any]:
    candidates = []
    for name in ("api_health","api_live"):
        data = endpoints.get(name,{}).get("data")
        if data is not None: candidates.append(data)
    ecu = database.get("tables",{}).get("ecu_samples")
    if ecu: candidates.append(ecu)
    observed = {}
    for key,expected in SAFETY_EXPECTED.items():
        values = []
        for candidate in candidates:
            values.extend(v for v in (normalize_bool(x) for x in deep_find(candidate,key)) if v is not None)
        observed[key] = {"expected":expected,"values":values,"pass":bool(values) and all(v==expected for v in values)}
    return observed


def feedback(snapshot: Mapping[str,Any]) -> list[dict[str,str]]:
    notes = []
    endpoints = snapshot.get("endpoints",{})
    failed_http = [name for name,item in endpoints.items() if not item.get("ok") and name not in {"api_gps","centinela_events"}]
    if failed_http: notes.append({"severity":"FAIL","title":"Endpoints sin respuesta","detail":", ".join(failed_http)})
    failed_units = [item["unit"] for item in snapshot.get("services",[]) if item.get("LoadState")=="loaded" and item.get("ActiveState")=="failed"]
    if failed_units: notes.append({"severity":"FAIL","title":"Servicios failed","detail":", ".join(failed_units)})
    bad_safety = [key for key,item in snapshot.get("safety",{}).items() if not item.get("pass")]
    if bad_safety: notes.append({"severity":"FAIL","title":"Seguridad no demostrada","detail":", ".join(bad_safety)})
    db = snapshot.get("database",{})
    if not db.get("accessible") or db.get("query_only")!=1: notes.append({"severity":"FAIL","title":"SQLite readonly no demostrado","detail":db.get("error") or f"accessible={db.get('accessible')} query_only={db.get('query_only')}"})
    host = snapshot.get("host",{})
    load1 = host.get("load_1m"); cpus = os.cpu_count() or 1
    if isinstance(load1,(int,float)) and load1 > cpus*1.5: notes.append({"severity":"WARN","title":"Carga elevada","detail":f"load1={load1:.2f}, CPUs={cpus}. Evitar auditorías pesadas."})
    files = snapshot.get("filesystem",{}); disk = files.get("disk",{})
    if isinstance(disk.get("free_gib"),(int,float)) and disk["free_gib"]<1: notes.append({"severity":"FAIL","title":"Espacio crítico","detail":f"{disk['free_gib']} GiB libres"})
    elif isinstance(disk.get("free_gib"),(int,float)) and disk["free_gib"]<2: notes.append({"severity":"WARN","title":"Espacio limitado","detail":f"{disk['free_gib']} GiB libres"})
    wal = files.get(str(Path(str(DB_PATH)+"-wal")),{})
    if isinstance(wal.get("size_mib"),(int,float)) and wal["size_mib"]>256: notes.append({"severity":"WARN","title":"WAL grande","detail":f"{wal['size_mib']} MiB; revisar lectores prolongados."})
    if not notes: notes.append({"severity":"PASS","title":"Estado nominal","detail":"No se detectaron fallos críticos."})
    return notes


def build_snapshot(include_catalog: bool=False, include_bodies: bool=True) -> dict[str,Any]:
    endpoints = endpoint_snapshot(include_bodies)
    database = db_snapshot()
    snapshot: dict[str,Any] = {"meta":{"app":APP_NAME,"version":VERSION,"device_id":DEVICE_ID,"generated_at":utc_now(),"readonly":True,"mqtt_tx_enabled":False},"host":host_snapshot(),"services":services_snapshot(),"timer":timer_snapshot(),"listeners":listeners_snapshot(),"endpoints":endpoints,"database":database,"filesystem":filesystem_snapshot(),"release":release_snapshot(),"tailscale":tailscale_snapshot()}
    snapshot["safety"] = extract_safety(endpoints,database)
    if include_catalog: snapshot["command_catalog"] = command_catalog()
    snapshot["feedback"] = feedback(snapshot)
    return snapshot


def doctor_checks(snapshot: Mapping[str,Any]) -> list[Check]:
    checks = []
    for name,item in snapshot["endpoints"].items():
        optional = name in {"api_gps","centinela_events"}
        checks.append(Check(f"HTTP {name}","PASS" if item.get("ok") else ("WARN" if optional else "FAIL"),f"status={item.get('status')} elapsed={item.get('elapsed_ms')}ms"))
    for service in snapshot["services"]:
        unit = service["unit"]; active = service.get("ActiveState"); result = service.get("Result")
        if unit=="nexo-normalizer.service": good = active in {"inactive","activating"} and result in {"success",""}
        elif unit.endswith(".timer"): good = active=="active"
        else: good = active=="active"
        checks.append(Check(f"Servicio {unit}","PASS" if good else "FAIL",f"active={active} sub={service.get('SubState')} result={result} restarts={service.get('NRestarts')}"))
    for key,item in snapshot["safety"].items(): checks.append(Check(f"Seguridad {key}","PASS" if item.get("pass") else "FAIL",f"expected={item.get('expected')} values={item.get('values')}"))
    db = snapshot["database"]
    checks.append(Check("SQLite accessible","PASS" if db.get("accessible") else "FAIL",db.get("error") or f"path={db.get('path')}"))
    checks.append(Check("SQLite query_only","PASS" if db.get("query_only")==1 else "FAIL",f"query_only={db.get('query_only')} journal_mode={db.get('journal_mode')}"))
    current = snapshot["release"].get("current_frontend")
    checks.append(Check("Frontend activo","PASS" if current else "FAIL",current or "symlink ausente"))
    ports = {item["port"] for item in snapshot["listeners"].get("listeners",[])}
    for port in (8080,8081,8090,8181): checks.append(Check(f"Listener {port}","PASS" if port in ports else "FAIL",EXPECTED_PORTS[port]))
    return checks


def health_score(checks: Sequence[Check]) -> dict[str,Any]:
    weights = {"PASS":1.0,"WARN":0.5,"FAIL":0.0}
    score = 100*sum(weights.get(item.status,0) for item in checks)/max(len(checks),1)
    return {"score":round(score,1),"pass":sum(c.status=="PASS" for c in checks),"warn":sum(c.status=="WARN" for c in checks),"fail":sum(c.status=="FAIL" for c in checks),"total":len(checks)}


def print_header() -> None:
    print("="*80); print(f" {APP_NAME} · {VERSION}"); print("="*80)
    print(f"Host: {socket.gethostname()}  Device: {DEVICE_ID}")
    print(f"API: {API_BASE}  Centinela: {CENTINELA_BASE}  Orbital: {FRONTEND_BASE}")
    print(f"SQLite: {DB_PATH}")
    print("Política: readonly · MQTT TX bloqueado · salidas físicas bloqueadas")
    print("="*80)


def json_print(value: Any) -> None:
    print(json.dumps(value,ensure_ascii=False,indent=2,default=str))


def cmd_status(_: argparse.Namespace) -> int:
    snapshot = build_snapshot()
    print_header(); print(f"Release activa: {snapshot['release'].get('current_frontend') or 'NO DETECTADA'}\n")
    print("SERVICIOS")
    for item in snapshot["services"]: print(f"{item['unit']:<42} active={item.get('ActiveState','?'):<10} sub={item.get('SubState','?'):<12} result={item.get('Result','?'):<10} restarts={item.get('NRestarts','?')}")
    print("\nENDPOINTS")
    for name,item in snapshot["endpoints"].items(): print(f"{name:<24} HTTP={str(item.get('status')):<4} ok={str(item.get('ok')):<5} {item.get('elapsed_ms')}ms")
    print("\nSEGURIDAD")
    for key,item in snapshot["safety"].items(): print(f"{'PASS' if item['pass'] else 'FAIL':<5} {key:<30} expected={item['expected']} values={item['values']}")
    db=snapshot["database"]; odo=db.get("tables",{}).get("odometer_state")
    print(f"\nSQLite: accessible={db.get('accessible')} query_only={db.get('query_only')} journal={db.get('journal_mode')}")
    if odo: print(f"Odómetro: {odo.get('total_km')} km · writer={odo.get('writer')}")
    print("\nRETROALIMENTACIÓN")
    for note in snapshot["feedback"]: print(f"[{note['severity']}] {note['title']}: {note['detail']}")
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    snapshot=build_snapshot(); checks=doctor_checks(snapshot); score=health_score(checks)
    print_header(); print(f"CALIDAD OPERATIVA: {score['score']} % · PASS={score['pass']} WARN={score['warn']} FAIL={score['fail']}\n")
    for check in checks: print(f"[{check.status:<4}] {check.name:<48} {check.detail}")
    print("\nRETROALIMENTACIÓN")
    for note in snapshot["feedback"]: print(f"[{note['severity']}] {note['title']}: {note['detail']}")
    return 1 if score["fail"] else 0


def cmd_watch(args: argparse.Namespace) -> int:
    interval=max(2.0,args.interval)
    try:
        while True:
            os.system("clear" if os.name!="nt" else "cls")
            snapshot=build_snapshot(include_bodies=False); score=health_score(doctor_checks(snapshot))
            print_header(); print(f"{utc_now()} · Calidad {score['score']} % · fallos={score['fail']}")
            print(f"Release: {snapshot['release'].get('current_frontend')}\n")
            for name in ("api_health","api_live","api_gps","api_odometer","centinela_health","frontend_root"):
                item=snapshot["endpoints"].get(name,{})
                print(f"{name:<22} HTTP={item.get('status')} ok={item.get('ok')} {item.get('elapsed_ms')}ms")
            print()
            for item in snapshot["services"]:
                if item["unit"] in {"nexo-normalizer.timer","nexo-normalizer.service","nexo-api.service","nexo-centinela.service","nexo-orbital-guardian-temp.service"}: print(f"{item['unit']:<42} {item.get('ActiveState')}/{item.get('SubState')} result={item.get('Result')} restarts={item.get('NRestarts')}")
            print()
            for note in snapshot["feedback"]: print(f"[{note['severity']}] {note['title']}: {note['detail']}")
            print(f"\nActualización cada {interval:.0f}s · Ctrl+C para salir")
            time.sleep(interval)
    except KeyboardInterrupt:
        return 0


def write_report(snapshot: Mapping[str,Any]) -> tuple[Path,Path]:
    stamp=dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    jpath=REPORT_DIR/f"nexo-admin-report-{stamp}.json"; tpath=REPORT_DIR/f"nexo-admin-report-{stamp}.txt"
    jpath.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    checks=doctor_checks(snapshot); score=health_score(checks)
    lines=[f"{APP_NAME} {VERSION}",f"Generated: {snapshot['meta']['generated_at']}",f"Score: {score['score']}% PASS={score['pass']} WARN={score['warn']} FAIL={score['fail']}","","CHECKS"]+[f"[{c.status}] {c.name}: {c.detail}" for c in checks]+["","FEEDBACK"]+[f"[{n['severity']}] {n['title']}: {n['detail']}" for n in snapshot["feedback"]]
    tpath.write_text("\n".join(lines)+"\n",encoding="utf-8")
    return jpath,tpath


def cmd_report(args: argparse.Namespace) -> int:
    snapshot=build_snapshot(args.include_catalog,True); jpath,tpath=write_report(snapshot)
    print(f"JSON: {jpath}\nTXT:  {tpath}")
    if args.bundle:
        bundle=REPORT_DIR/f"nexo-admin-support-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.tar.gz"
        with tarfile.open(bundle,"w:gz") as archive:
            archive.add(jpath,arcname=jpath.name); archive.add(tpath,arcname=tpath.name)
            if LOG_PATH.exists(): archive.add(LOG_PATH,arcname=LOG_PATH.name)
        print(f"BUNDLE: {bundle}")
    return 0


def cmd_commands(args: argparse.Namespace) -> int:
    catalog=command_catalog(); print_header(); print(f"Fuente: {catalog['source']}\nTX MQTT: BLOQUEADO\nPolítica: {catalog['policy']}\n")
    for index,item in enumerate(catalog["commands"],1):
        print(f"{index:>2}. {str(item.get('id')):<26} {str(item.get('risk','unknown')).upper():<12} {str(item.get('category','')):<16} {item.get('description','')}")
        if args.verbose:
            print("    template:",json.dumps(item.get("payload"),ensure_ascii=False))
            if item.get("response"): print("    response:",item["response"])
    print("\nNingún comando se publica desde esta herramienta.")
    return 0


def cmd_api(args: argparse.Namespace) -> int:
    names=list(HTTP_TARGETS) if not args.name else [args.name]
    result={name:http_fetch(HTTP_TARGETS[name],args.timeout) for name in names}; json_print(result)
    return 0 if all(item.get("ok") for item in result.values()) else 1


def cmd_db(_: argparse.Namespace) -> int: json_print({"database":db_snapshot(),"filesystem":filesystem_snapshot()}); return 0

def cmd_services(_: argparse.Namespace) -> int: json_print(services_snapshot()); return 0

def cmd_release(_: argparse.Namespace) -> int: json_print(release_snapshot()); return 0

def cmd_tailscale(_: argparse.Namespace) -> int: json_print(tailscale_snapshot()); return 0


def cmd_logs(args: argparse.Namespace) -> int:
    allowed=CORE_SERVICES+["nexo-admin-v2.service"]
    if args.unit not in allowed: print("Unidad fuera de la lista permitida.",file=sys.stderr); return 2
    command=["journalctl","-u",args.unit,"--no-pager","-n",str(args.lines)]
    if args.since: command.extend(["--since",args.since])
    result=run(command,15); print(result.stdout)
    if result.stderr: print(result.stderr,file=sys.stderr)
    return 0 if result.ok else result.returncode


def require_root() -> None:
    if not hasattr(os,"geteuid") or os.geteuid()!=0: raise PermissionError("Esta operación requiere root. Use sudo.")


def cmd_service_action(args: argparse.Namespace) -> int:
    try: require_root()
    except PermissionError as exc: print(str(exc),file=sys.stderr); return 2
    if args.unit not in MUTABLE_SERVICE_ALLOWLIST: print("Servicio fuera de la lista cerrada.",file=sys.stderr); return 2
    token=f"{args.action.upper()}_{args.unit.replace('.','_').replace('-','_').upper()}"
    if not args.apply or args.confirm!=token: print(f"Operación bloqueada. Requiere: --apply --confirm {token}"); return 2
    before=build_snapshot(); bad=[k for k,v in before["safety"].items() if not v.get("pass")]
    if bad: print("Operación bloqueada: seguridad no demostrada: "+", ".join(bad),file=sys.stderr); return 3
    command=["systemctl","restart",args.unit] if args.action=="restart" else ["systemctl","reset-failed",args.unit]
    result=run(command,30); time.sleep(2)
    audit={"at":utc_now(),"action":args.action,"unit":args.unit,"result":result.as_dict(),"after":systemd_state(args.unit),"safety_before":before["safety"]}
    path=REPORT_DIR/f"service-action-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"; path.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
    json_print(audit); return 0 if result.ok else 1


def unit_text(user: str, group: str, port: int) -> str:
    return textwrap.dedent(f"""\
    [Unit]
    Description=NEXO Admin + Centinela v2 local readonly panel
    After=network-online.target nexo-api.service nexo-centinela.service
    Wants=network-online.target

    [Service]
    Type=simple
    User={user}
    Group={group}
    WorkingDirectory={INSTALL_DIR}
    Environment=PYTHONUNBUFFERED=1
    Environment=NEXO_ADMIN_STATE_DIR={DEFAULT_STATE_DIR}
    ExecStart=/usr/bin/python3 -B {INSTALL_PATH} serve --host 127.0.0.1 --port {port}
    Restart=on-failure
    RestartSec=5
    NoNewPrivileges=true
    PrivateTmp=true
    ProtectSystem=strict
    ProtectHome=true
    ReadWritePaths={DEFAULT_STATE_DIR}
    LockPersonality=true
    RestrictSUIDSGID=true
    RestrictRealtime=true
    CapabilityBoundingSet=
    AmbientCapabilities=
    RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
    UMask=0077

    [Install]
    WantedBy=multi-user.target
    """)


def cmd_install(args: argparse.Namespace) -> int:
    try: require_root()
    except PermissionError as exc: print(str(exc),file=sys.stderr); return 2
    source=Path(__file__).resolve(); user=args.user or os.environ.get("SUDO_USER") or "d3v3lop3rs"
    group="nexo" if run(["getent","group","nexo"],3).ok else user
    INSTALL_DIR.mkdir(parents=True,exist_ok=True); DEFAULT_STATE_DIR.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,INSTALL_PATH); os.chmod(INSTALL_PATH,0o755)
    WRAPPER_PATH.write_text(f"#!/bin/sh\nexec /usr/bin/python3 -B {INSTALL_PATH} \"$@\"\n",encoding="utf-8"); os.chmod(WRAPPER_PATH,0o755)
    SERVICE_PATH.write_text(unit_text(user,group,args.port),encoding="utf-8"); os.chmod(SERVICE_PATH,0o644)
    shutil.chown(DEFAULT_STATE_DIR,user=user,group=group)
    steps=[run(["systemctl","daemon-reload"],10),run(["systemctl","enable","--now","nexo-admin-v2.service"],30)]
    status=systemd_state("nexo-admin-v2.service")
    payload={"installed":all(step.ok for step in steps),"script":str(INSTALL_PATH),"wrapper":str(WRAPPER_PATH),"service":str(SERVICE_PATH),"state_dir":str(DEFAULT_STATE_DIR),"listen":f"http://127.0.0.1:{args.port}/","user":user,"group":group,"steps":[step.as_dict() for step in steps],"status":status,"tunnel":f"ssh -N -L 28190:127.0.0.1:{args.port} motoguarana"}
    json_print(payload); return 0 if payload["installed"] and status.get("ActiveState")=="active" else 1


def cmd_uninstall(args: argparse.Namespace) -> int:
    try: require_root()
    except PermissionError as exc: print(str(exc),file=sys.stderr); return 2
    run(["systemctl","disable","--now","nexo-admin-v2.service"],30); SERVICE_PATH.unlink(missing_ok=True); WRAPPER_PATH.unlink(missing_ok=True)
    if args.remove_script: INSTALL_PATH.unlink(missing_ok=True)
    run(["systemctl","daemon-reload"],10); print("NEXO Admin v2 deshabilitado. No se tocaron servicios NEXO ni datos."); return 0


def cmd_tunnel(args: argparse.Namespace) -> int:
    print(f"Panel NEXO Admin:\n  ssh -N -L 28190:127.0.0.1:{args.port} motoguarana\n  http://127.0.0.1:28190/\n")
    print("Dashboard Orbital:\n  ssh -N -L 28181:127.0.0.1:8181 motoguarana\n  http://127.0.0.1:28181/")
    return 0

PAGE = """<!doctype html><html lang=es><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><meta http-equiv=refresh content=10><title>NEXO Admin</title><style>:root{color-scheme:dark;font-family:Inter,system-ui,sans-serif}body{margin:0;background:#091014;color:#dcecf2}header{padding:22px 26px;background:#0d171d;border-bottom:1px solid #24404a;position:sticky;top:0}h1{margin:0 0 6px;font-size:22px;letter-spacing:.06em}small{color:#8fb0ba}main{padding:20px;display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}.card{background:#0f1a20;border:1px solid #24404a;border-radius:12px;padding:16px;box-shadow:0 6px 24px #0006}.card h2{margin:0 0 12px;font-size:16px}.pass{color:#73e0a1}.warn{color:#ffd166}.fail{color:#ff7b7b}table{width:100%;border-collapse:collapse;font-size:13px}td,th{text-align:left;padding:6px;border-bottom:1px solid #1d3038;vertical-align:top}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;color:#b8d7df}a{color:#70d6ff}.full{grid-column:1/-1}</style></head><body><header><h1>NEXO ADMIN + CENTINELA v2</h1><small>Readonly · MQTT TX bloqueado · actualización cada 10 s · {generated}</small></header><main>{content}</main></body></html>"""


def esc_json(value: Any) -> str: return html.escape(json.dumps(value,ensure_ascii=False,indent=2,default=str))


def render_web(snapshot: Mapping[str,Any]) -> str:
    score=health_score(doctor_checks(snapshot)); current=html.escape(str(snapshot["release"].get("current_frontend")))
    services="".join(f"<tr><td>{html.escape(i['unit'])}</td><td>{html.escape(str(i.get('ActiveState')))}</td><td>{html.escape(str(i.get('SubState')))}</td><td>{html.escape(str(i.get('Result')))}</td><td>{html.escape(str(i.get('NRestarts')))}</td></tr>" for i in snapshot["services"])
    endpoints="".join(f"<tr><td>{html.escape(n)}</td><td>{html.escape(str(i.get('status')))}</td><td>{html.escape(str(i.get('ok')))}</td><td>{html.escape(str(i.get('elapsed_ms')))} ms</td></tr>" for n,i in snapshot["endpoints"].items())
    safety="".join(f"<tr><td>{html.escape(k)}</td><td>{html.escape(str(i.get('expected')))}</td><td>{html.escape(str(i.get('values')))}</td><td class={'pass' if i.get('pass') else 'fail'}>{'PASS' if i.get('pass') else 'FAIL'}</td></tr>" for k,i in snapshot["safety"].items())
    notes="".join(f"<p class={i['severity'].lower()}><b>{html.escape(i['severity'])} · {html.escape(i['title'])}</b><br>{html.escape(i['detail'])}</p>" for i in snapshot["feedback"])
    content=f"<section class=card><h2>Calidad operativa</h2><p class={'pass' if score['fail']==0 else 'fail'} style='font-size:34px;margin:8px 0'>{score['score']} %</p><p>PASS={score['pass']} · WARN={score['warn']} · FAIL={score['fail']}</p><p>Release:<br>{current}</p></section><section class=card><h2>Retroalimentación</h2>{notes}</section><section class='card full'><h2>Servicios</h2><table><tr><th>Unidad</th><th>Active</th><th>Sub</th><th>Result</th><th>Restarts</th></tr>{services}</table></section><section class='card full'><h2>Endpoints</h2><table><tr><th>Nombre</th><th>HTTP</th><th>OK</th><th>Tiempo</th></tr>{endpoints}</table></section><section class=card><h2>Seguridad</h2><table><tr><th>Invariante</th><th>Esperado</th><th>Observado</th><th>Estado</th></tr>{safety}</table></section><section class=card><h2>Timer</h2><pre>{esc_json({'TimersMonotonic':snapshot['timer'].get('TimersMonotonic'),'schedule_lines':snapshot['timer'].get('schedule_lines'),'Result':snapshot['timer'].get('Result')})}</pre></section><section class='card full'><h2>Centinela</h2><pre>{esc_json({k:v for k,v in snapshot['endpoints'].items() if k.startswith('centinela_')})}</pre></section><section class='card full'><h2>SQLite readonly</h2><pre>{esc_json(snapshot['database'])}</pre></section><section class=card><h2>Acceso</h2><p>Panel: <code>ssh -N -L 28190:127.0.0.1:8190 motoguarana</code></p><p>Orbital: <code>ssh -N -L 28181:127.0.0.1:8181 motoguarana</code></p><p><a href=/api/snapshot>Snapshot JSON</a> · <a href=/api/catalog>Catálogo</a></p></section>"
    return PAGE.format(generated=html.escape(snapshot["meta"]["generated_at"]),content=content)


class Handler(http.server.BaseHTTPRequestHandler):
    server_version=f"NexoAdmin/{VERSION}"
    def log_message(self,fmt: str,*args: Any)->None: LOG.info("web %s %s",self.address_string(),fmt%args)
    def headers(self,status: int,ctype: str,length: int)->None:
        self.send_response(status); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(length)); self.send_header("Cache-Control","no-store"); self.send_header("X-Content-Type-Options","nosniff"); self.send_header("X-Frame-Options","DENY"); self.send_header("Content-Security-Policy","default-src 'self'; style-src 'unsafe-inline'"); self.end_headers()
    def send_json(self,value: Any,status: int=200)->None:
        body=json.dumps(value,ensure_ascii=False,indent=2,default=str).encode(); self.headers(status,"application/json; charset=utf-8",len(body)); self.wfile.write(body)
    def do_GET(self)->None:
        path=urllib.parse.urlparse(self.path).path
        if path=="/healthz": self.send_json({"ok":True,"app":APP_NAME,"version":VERSION,"readonly":True}); return
        if path=="/api/catalog": self.send_json(command_catalog()); return
        if path=="/api/snapshot": self.send_json(build_snapshot()); return
        if path=="/":
            body=render_web(build_snapshot()).encode(); self.headers(200,"text/html; charset=utf-8",len(body)); self.wfile.write(body); return
        self.send_json({"ok":False,"error":"not_found"},404)
    def do_POST(self)->None: self.send_json({"ok":False,"error":"method_not_allowed","detail":"La web es readonly."},405)
    do_PUT=do_POST; do_PATCH=do_POST; do_DELETE=do_POST


def cmd_serve(args: argparse.Namespace) -> int:
    try: address=socket.gethostbyname(args.host)
    except socket.gaierror: address=args.host
    if address not in {"127.0.0.1","::1"}: print("Bind rechazado: solo loopback.",file=sys.stderr); return 2
    server=http.server.ThreadingHTTPServer((args.host,args.port),Handler); server.daemon_threads=True
    def stop(signum: int,frame: Any)->None: LOG.info("Señal %s; cerrando",signum); threading.Thread(target=server.shutdown,daemon=True).start()
    signal.signal(signal.SIGTERM,stop); signal.signal(signal.SIGINT,stop)
    LOG.info("Panel en http://%s:%s/",args.host,args.port); print(f"NEXO Admin v2 activo en http://{args.host}:{args.port}/")
    try: server.serve_forever(poll_interval=.5)
    finally: server.server_close()
    return 0


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(prog="nexo-admin",description="NEXO Admin + Centinela v2: diagnóstico readonly, feedback y panel local.")
    p.add_argument("--version",action="version",version=f"%(prog)s {VERSION}")
    sub=p.add_subparsers(dest="command",required=True)
    q=sub.add_parser("status"); q.set_defaults(func=cmd_status)
    q=sub.add_parser("doctor"); q.set_defaults(func=cmd_doctor)
    q=sub.add_parser("watch"); q.add_argument("--interval",type=float,default=5); q.set_defaults(func=cmd_watch)
    q=sub.add_parser("report"); q.add_argument("--include-catalog",action="store_true"); q.add_argument("--bundle",action="store_true"); q.set_defaults(func=cmd_report)
    q=sub.add_parser("commands"); q.add_argument("--verbose",action="store_true"); q.set_defaults(func=cmd_commands)
    q=sub.add_parser("api"); q.add_argument("name",nargs="?",choices=list(HTTP_TARGETS)); q.add_argument("--timeout",type=float,default=4); q.set_defaults(func=cmd_api)
    q=sub.add_parser("db"); q.set_defaults(func=cmd_db)
    q=sub.add_parser("services"); q.set_defaults(func=cmd_services)
    q=sub.add_parser("release"); q.set_defaults(func=cmd_release)
    q=sub.add_parser("tailscale"); q.set_defaults(func=cmd_tailscale)
    q=sub.add_parser("logs"); q.add_argument("unit",choices=CORE_SERVICES+["nexo-admin-v2.service"]); q.add_argument("--lines",type=int,default=120); q.add_argument("--since"); q.set_defaults(func=cmd_logs)
    q=sub.add_parser("service"); q.add_argument("action",choices=["restart","reset-failed"]); q.add_argument("unit",choices=sorted(MUTABLE_SERVICE_ALLOWLIST)); q.add_argument("--apply",action="store_true"); q.add_argument("--confirm"); q.set_defaults(func=cmd_service_action)
    q=sub.add_parser("serve"); q.add_argument("--host",default=DEFAULT_HOST); q.add_argument("--port",type=int,default=DEFAULT_PORT); q.set_defaults(func=cmd_serve)
    q=sub.add_parser("install"); q.add_argument("--user"); q.add_argument("--port",type=int,default=DEFAULT_PORT); q.set_defaults(func=cmd_install)
    q=sub.add_parser("uninstall"); q.add_argument("--remove-script",action="store_true"); q.set_defaults(func=cmd_uninstall)
    q=sub.add_parser("tunnel"); q.add_argument("--port",type=int,default=DEFAULT_PORT); q.set_defaults(func=cmd_tunnel)
    return p


def main(argv: Sequence[str]|None=None)->int:
    args=parser().parse_args(argv)
    try: return int(args.func(args))
    except KeyboardInterrupt: return 130
    except Exception as exc:
        LOG.exception("Fallo no controlado"); print(f"ERROR: {type(exc).__name__}: {exc}\nLog: {LOG_PATH}",file=sys.stderr); return 1

if __name__=="__main__": raise SystemExit(main())
