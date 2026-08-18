"""Pure Centinela v0.2 rule evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import CollectorSnapshot, Finding, Severity


@dataclass(frozen=True)
class RuleSpec:
    code: str
    component: str
    severity: Severity
    activation_count: int
    recovery_count: int
    recoverable: bool
    source: str


RULES = (
    RuleSpec(
        "CENTINELA_API_UNREACHABLE",
        "api",
        Severity.CRITICAL,
        3,
        2,
        True,
        "GET /health",
    ),
    RuleSpec(
        "CENTINELA_API_DEGRADED",
        "api",
        Severity.WARNING,
        2,
        2,
        True,
        "GET /health",
    ),
    RuleSpec(
        "CENTINELA_SECURITY_INVARIANT_BROKEN",
        "security",
        Severity.CRITICAL,
        1,
        2,
        False,
        "GET /health + GET /live",
    ),
    RuleSpec(
        "CENTINELA_NEXO_SERVICE_DOWN",
        "services",
        Severity.CRITICAL,
        2,
        2,
        True,
        "systemd",
    ),
    RuleSpec(
        "CENTINELA_SERVICE_RESTARTING",
        "services",
        Severity.WARNING,
        1,
        2,
        True,
        "systemd NRestarts",
    ),
    RuleSpec(
        "CENTINELA_ECU_STALE",
        "ecu",
        Severity.WARNING,
        2,
        2,
        True,
        "GET /live ecu.status",
    ),
    RuleSpec(
        "CENTINELA_ECU_OFFLINE",
        "ecu",
        Severity.CRITICAL,
        2,
        2,
        True,
        "GET /live ecu.status",
    ),
    RuleSpec(
        "CENTINELA_GPS_STALE",
        "gps",
        Severity.INFO,
        2,
        2,
        True,
        "GET /live gps.status",
    ),
    RuleSpec(
        "CENTINELA_GPS_OFFLINE",
        "gps",
        Severity.WARNING,
        2,
        2,
        True,
        "GET /live gps.status",
    ),
    RuleSpec(
        "CENTINELA_SAMPLE_REGRESSION",
        "ecu",
        Severity.WARNING,
        1,
        2,
        True,
        "GET /live ecu.sample",
    ),
    RuleSpec(
        "CENTINELA_TAILSCALE_TARGET_MISMATCH",
        "tailscale",
        Severity.CRITICAL,
        2,
        2,
        True,
        "tailscale serve status",
    ),
    RuleSpec(
        "CENTINELA_LEGACY_REACTIVATED",
        "services",
        Severity.WARNING,
        2,
        2,
        True,
        "systemd legacy state",
    ),
    RuleSpec(
        "CENTINELA_BOOT_CHECK_FAILED",
        "services",
        Severity.WARNING,
        2,
        2,
        True,
        "systemd boot-check",
    ),
    RuleSpec(
        "CENTINELA_ODOMETER_REFERENCE_CHANGED",
        "storage",
        Severity.INFO,
        1,
        1,
        True,
        "GET /odometer",
    ),
    RuleSpec(
        "CENTINELA_TELEMETRY_PIPELINE_LAG",
        "telemetry",
        Severity.WARNING,
        2,
        2,
        True,
        "SQLite readonly raw_mqtt -> ecu_samples",
    ),
    RuleSpec(
        "CENTINELA_NORMALIZER_STALLED",
        "telemetry",
        Severity.CRITICAL,
        2,
        2,
        True,
        "SQLite readonly normalizer cursor",
    ),
    RuleSpec(
        "CENTINELA_API_PARTIAL_ECU",
        "api",
        Severity.WARNING,
        2,
        2,
        True,
        "GET /live ecu.sample",
    ),
    RuleSpec(
        "CENTINELA_SAMPLE_CADENCE_EVENT",
        "ecu",
        Severity.INFO,
        1,
        1,
        True,
        "SQLite readonly raw_mqtt cadence event",
    ),
    RuleSpec(
        "CENTINELA_SAMPLE_CADENCE_DEGRADED",
        "ecu",
        Severity.WARNING,
        1,
        3,
        True,
        "SQLite readonly raw_mqtt cadence",
    ),
    RuleSpec(
        "CENTINELA_FRONTEND_BUILD_MISMATCH",
        "frontend",
        Severity.WARNING,
        2,
        2,
        True,
        "Orbital Guardian asset build ID",
    ),
)

RULES_BY_CODE = {rule.code: rule for rule in RULES}


def _status(payload: dict[str, Any] | None, family: str) -> dict[str, Any]:
    if payload is None:
        return {}
    value = payload.get(family)
    if not isinstance(value, dict):
        return {}
    status = value.get("status")
    return status if isinstance(status, dict) else {}


def _sample(payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {}
    ecu = payload.get("ecu")
    if not isinstance(ecu, dict):
        return {}
    sample = ecu.get("sample")
    return sample if isinstance(sample, dict) else {}


def _object(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def evaluate_conditions(
    snapshot: CollectorSnapshot,
    *,
    previous_sample: dict[str, Any] | None,
    restart_count_in_window: int,
    odometer_reference_km: float,
    tailscale_target: str,
) -> dict[str, Finding | None]:
    health = snapshot.health
    live = snapshot.live
    conditions: dict[str, Finding | None] = {rule.code: None for rule in RULES}

    if health is None:
        conditions["CENTINELA_API_UNREACHABLE"] = Finding(
            "API NEXO /health no disponible",
            {"error": snapshot.api_errors.get("health", "unreachable")},
        )
    elif health.get("ok") is False or str(health.get("status", "ok")).lower() in {
        "degraded",
        "unhealthy",
        "error",
    }:
        conditions["CENTINELA_API_DEGRADED"] = Finding(
            "API NEXO reporta degradación de infraestructura",
            {"ok": health.get("ok"), "status": health.get("status")},
        )

    if health is not None:
        safety = _object(health.get("safety"))
        database = _object(health.get("database"))
        sample = _sample(live)
        violations: dict[str, Any] = {}
        if safety.get("physical_outputs_enabled") is not False:
            violations["physical_outputs_enabled"] = safety.get("physical_outputs_enabled")
        if safety.get("remote_start_locked") is not True:
            violations["remote_start_locked"] = safety.get("remote_start_locked")
        if "relay_outputs_enabled" in sample and sample.get("relay_outputs_enabled") not in (
            0,
            False,
        ):
            violations["relay_outputs_enabled"] = sample.get("relay_outputs_enabled")
        if database.get("readonly") is not True:
            violations["database.readonly"] = database.get("readonly")
        if "query_only" in database and database.get("query_only") != 1:
            violations["database.query_only"] = database.get("query_only")
        if violations:
            conditions["CENTINELA_SECURITY_INVARIANT_BROKEN"] = Finding(
                "Invariante de seguridad readonly incumplida", violations
            )

    down = [
        name
        for name, state in snapshot.services.items()
        if state.get("active_state") != "active"
    ]
    if down:
        conditions["CENTINELA_NEXO_SERVICE_DOWN"] = Finding(
            "Servicios NEXO protegidos no activos", {"units": down}
        )

    if restart_count_in_window >= 3:
        severity = Severity.CRITICAL if restart_count_in_window >= 6 else Severity.WARNING
        conditions["CENTINELA_SERVICE_RESTARTING"] = Finding(
            "Reinicios nuevos anormales dentro de diez minutos",
            {"new_restarts_10m": restart_count_in_window},
            severity,
        )

    ecu_status = _status(live, "ecu")
    ecu_state = str(ecu_status.get("state", "")).lower()
    if ecu_state == "offline" or ecu_status.get("offline") is True:
        conditions["CENTINELA_ECU_OFFLINE"] = Finding(
            "ECU offline; se conserva la última muestra",
            {"status": ecu_status},
        )
    elif ecu_state == "stale" or ecu_status.get("stale") is True:
        conditions["CENTINELA_ECU_STALE"] = Finding(
            "ECU stale; se conserva la última muestra",
            {"status": ecu_status},
        )

    gps_status = _status(live, "gps")
    gps_state = str(gps_status.get("state", "")).lower()
    if gps_state == "offline" or gps_status.get("offline") is True:
        conditions["CENTINELA_GPS_OFFLINE"] = Finding(
            "GPS offline sin afectar el estado ECU", {"status": gps_status}
        )
    elif gps_state == "stale" or gps_status.get("stale") is True:
        conditions["CENTINELA_GPS_STALE"] = Finding(
            "GPS stale sin afectar el estado ECU", {"status": gps_status}
        )

    current_sample = _sample(live)
    if previous_sample and current_sample:
        same_boot = current_sample.get("boot_id") == previous_sample.get("boot_id")
        regressions: dict[str, Any] = {}
        if same_boot:
            for field in ("id", "publish_counter"):
                previous = previous_sample.get(field)
                current = current_sample.get(field)
                if (
                    isinstance(previous, int | float)
                    and isinstance(current, int | float)
                    and current < previous
                ):
                    regressions[field] = {"previous": previous, "current": current}
            previous_ts = previous_sample.get("received_ts")
            current_ts = current_sample.get("received_ts")
            if (
                isinstance(previous_ts, str)
                and isinstance(current_ts, str)
                and current_ts < previous_ts
            ):
                regressions["received_ts"] = {
                    "previous": previous_ts,
                    "current": current_ts,
                }
        if regressions:
            conditions["CENTINELA_SAMPLE_REGRESSION"] = Finding(
                "Muestra ECU retrocedió dentro del mismo boot", regressions
            )

    expected_line = f"|-- / proxy {tailscale_target}"
    if snapshot.tailscale_error is not None or expected_line not in snapshot.tailscale_status:
        conditions["CENTINELA_TAILSCALE_TARGET_MISMATCH"] = Finding(
            "Tailscale Serve raíz no apunta al target oficial",
            {
                "expected": tailscale_target,
                "error": snapshot.tailscale_error,
                "status": snapshot.tailscale_status,
            },
        )

    reactivated = [
        name
        for name, state in snapshot.legacy.items()
        if state.get("active_state") != "inactive"
        or state.get("unit_file_state") != "disabled"
    ]
    if reactivated:
        conditions["CENTINELA_LEGACY_REACTIVATED"] = Finding(
            "Unidades legacy retiradas fueron reactivadas", {"units": reactivated}
        )

    if (
        snapshot.boot_check.get("result") != "success"
        or snapshot.boot_check.get("exec_main_status") not in {0, "0"}
    ):
        conditions["CENTINELA_BOOT_CHECK_FAILED"] = Finding(
            "El último boot-check NEXO no terminó correctamente",
            {"boot_check": snapshot.boot_check},
        )

    odometer = snapshot.odometer or {}
    odometer_value = odometer.get("odometer")
    total_km = (
        odometer_value.get("total_km") if isinstance(odometer_value, dict) else None
    )
    if isinstance(total_km, int | float) and total_km != odometer_reference_km:
        conditions["CENTINELA_ODOMETER_REFERENCE_CHANGED"] = Finding(
            "La referencia observada del odómetro cambió",
            {"previous": odometer_reference_km, "current": total_km},
        )

    metrics = snapshot.telemetry_metrics
    raw_to_normalized = metrics.get("raw_to_normalized_lag_ms")
    if isinstance(raw_to_normalized, int | float) and raw_to_normalized > 2500:
        conditions["CENTINELA_TELEMETRY_PIPELINE_LAG"] = Finding(
            "La normalización no sigue la cadencia raw",
            {
                "raw_to_normalized_lag_ms": raw_to_normalized,
                "raw_id": metrics.get("raw_id"),
                "normalized_id": metrics.get("normalized_id"),
            },
        )
    if isinstance(raw_to_normalized, int | float) and raw_to_normalized > 10_000:
        conditions["CENTINELA_NORMALIZER_STALLED"] = Finding(
            "El normalizador no avanza mientras existen tramas ECU raw",
            {
                "raw_to_normalized_lag_ms": raw_to_normalized,
                "normalizer_cursor": metrics.get("normalizer_cursor"),
            },
        )
    partial_fields = metrics.get("partial_fields")
    if isinstance(partial_fields, list) and partial_fields:
        conditions["CENTINELA_API_PARTIAL_ECU"] = Finding(
            "La API entregó una muestra ECU parcial",
            {"missing_fields": partial_fields, "sample_id": metrics.get("sample_id")},
        )
    new_source_gaps = metrics.get("new_source_gap_count")
    if isinstance(new_source_gaps, int) and new_source_gaps > 0:
        conditions["CENTINELA_SAMPLE_CADENCE_EVENT"] = Finding(
            "Pausa transitoria de publicación ECU registrada",
            {
                "new_gap_count": new_source_gaps,
                "source_publish_interval_ms": metrics.get(
                    "source_publish_interval_ms"
                ),
            },
        )
    gap_events_60s = metrics.get("source_gap_events_60s")
    if isinstance(gap_events_60s, int) and gap_events_60s >= 3:
        conditions["CENTINELA_SAMPLE_CADENCE_DEGRADED"] = Finding(
            "La fuente ECU presenta pausas persistentes de publicación",
            {
                "gap_events_60s": gap_events_60s,
                "source_publish_interval_ms": metrics.get(
                    "source_publish_interval_ms"
                ),
            },
        )
    frontend = metrics.get("frontend")
    frontend_map = frontend if isinstance(frontend, dict) else {}
    if frontend_map and frontend_map.get("matched") is not True:
        conditions["CENTINELA_FRONTEND_BUILD_MISMATCH"] = Finding(
            "El build servido no coincide con la release esperada",
            {
                "expected": frontend_map.get("expected"),
                "actual": frontend_map.get("actual"),
                "asset": frontend_map.get("asset"),
                "error": frontend_map.get("error"),
            },
        )

    return conditions
