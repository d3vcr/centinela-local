# CENTINELA LOCAL — Sincronización de Runtime 2026-08-17

## Propósito

Incorporar al repositorio el **runtime de CENTINELA actualmente en ejecución**
en producción, como referencia verificable y exclusiva de CENTINELA.
Esta carpeta NO contiene código de NEXO ECU, firmware, cockpit, MQTT,
odómetro, combustible ni herramientas ajenas a CENTINELA.

## Estado operativo (CONFIRMADO 2026-08-17)

| Ítem | Valor |
|---|---|
| Host | `motoguarana` (Raspberry Pi) |
| Sistema | Raspberry Pi OS, systemd, SQLite local |
| Servicio | `nexo-centinela.service` → `active` |
| Panel | `nexo-admin-v2.service` (puerto 8190) → `active` |
| Symlink | `/opt/nexo/current-centinela` → `/opt/nexo/releases/centinela-v23-v2tools-20260816-40ab2b6` |
| Override systemd | `nexo-centinela.service.d/20-versioned-release.conf` (WorkingDirectory/PYTHONPATH versionados) |
| Principio | read-only por defecto (`physical_outputs_enabled=false`, `remote_start_locked=true`) |

## Contenido

```
current/
  apps_centinela/         Código Python en ejecución (9 módulos, fecha Jul 27)
  admin/                  Panel admin + centinela v2 (nexo_admin_centinela_v2.py)
  systemd/                Unidades systemd de producción (service, override, admin)
  scripts/                deploy y rollback de CENTINELA
  MANIFEST-SHA256-20260817.md
  README.md
EVIDENCIA-SINCRONIZACION-20260817.md
```

## Fuente de verdad

- **Repositorio:** `https://github.com/d3vcr/centinela-local.git`
- **Rama:** `main`
- **Fecha de sincronización:** 2026-08-17
- **Origen de los archivos:** `/opt/nexo/apps/centinela`, `/opt/nexo/admin`,
  `/etc/systemd/system/nexo-centinela.service*`, `/opt/nexo/scripts/`
  en `motoguarana`.
- **Repositorio NEXO asociado (contexto, no contenido):** `d3vcr/nexo-ecu`,
  rama `recovery/nexo-v2-production-snapshot-20260803`, commit `b4357a4`.

## Reglas de sincronización

1. Actualizar el runtime SOLO cuando el código en ejecución cambie y se
   verifique su hash en `motoguarana`.
2. Registrar cada sincronización en `EVIDENCIA-*.md` con hashes y fechas.
3. No mezclar archivos de NEXO (firmware, ECU, odómetro, cockpit, MQTT)
   en esta carpeta.
4. El MANIFEST SHA-256 se regenera con: `sha256sum current/**/*`