# EVIDENCIA — Sincronización de Runtime CENTINELA 2026-08-17

## Clasificación: CONFIRMADO

| Campo | Valor |
|---|---|
| Repositorio destino | `https://github.com/d3vcr/centinela-local.git` |
| Rama | `main` |
| Host de origen | `motoguarana` (Raspberry Pi) |
| Fecha | 2026-08-17 |
| Alcance | Runtime de CENTINELA únicamente (exclusividad verificada) |

## Origen de los archivos

| Origen (motoguarana) | Destino (este repo) |
|---|---|
| `/opt/nexo/apps/centinela/*.py` | `current/apps_centinela/` |
| `/opt/nexo/admin/nexo_admin_centinela_v2.py` | `current/admin/` |
| `/etc/systemd/system/nexo-centinela.service` | `current/systemd/` |
| `/etc/systemd/system/nexo-centinela.service.d/20-versioned-release.conf` | `current/systemd/` |
| `/etc/systemd/system/nexo-admin-v2.service` | `current/systemd/` |
| `/opt/nexo/scripts/deploy/deploy-nexo-centinela.sh` | `current/scripts/` |
| `/opt/nexo/scripts/recovery/rollback-nexo-centinela.sh` | `current/scripts/` |

## Estado operativo verificado

- `nexo-centinela.service`: **active** (read-only observer, v0.1)
- `nexo-admin-v2.service`: **active** (panel admin + centinela v2, puerto 8190)
- Symlink `current-centinela` → `releases/centinela-v23-v2tools-20260816-40ab2b6`
- Principio read-only: `ReadOnlyPaths=/opt/nexo /etc/nexo` en la unidad
- Política NEXO: `physical_outputs_enabled=false`, `remote_start_locked=true`
  (OBSERVADO vía `/live` de la API)

## Lo que está DESACTIVADO (documentado, no sincronizado como código)

| Ítem | Estado |
|---|---|
| Release `centinela-v22-tailscale-parser-20260810-d71f799d5655` | No en ejecución (histórica en `/opt/nexo/releases`) |
| Release `orbital-guardian-centinela-v0.1-20260727-003558` | No en ejecución (histórica) |
| Overrides previos de `nexo-centinela.service.d/` | Reemplazados por `20-versioned-release.conf` |
| Adapter TTS `/voice/speak` (repo NEXO `d3vcr/nexo-ecu`, commit `7147fc4`) | Disponible en el monorepo NEXO; **no desplegado** en `motoguarana` (fuera del alcance exclusivo de CENTINELA LOCAL) |

## Verificación de integridad

- SHA-256 de los 15 archivos: verificados en `motoguarana` y registrados en
  `current/MANIFEST-SHA256-20260817.md`.
- No se copió código de NEXO ECU, firmware, cockpit, odómetro, combustible,
  MQTT ni herramientas administrativas ajenas a CENTINELA.

## Referencia NEXO (contexto de despliegue)

- Repositorio: `d3vcr/nexo-ecu`
- Rama: `recovery/nexo-v2-production-snapshot-20260803`
- Commit: `b4357a4` (snapshot de producción donde vive el runtime CENTINELA)