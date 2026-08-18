# README — Runtime CENTINELA actual (snapshot 2026-08-17)

## Estado: CONFIRMADO en producción

- Host: `motoguarana`
- Servicio: `nexo-centinela.service` — **active**
- Panel: `nexo-admin-v2.service` (127.0.0.1:8190) — **active**
- Symlink actual: `/opt/nexo/current-centinela` → `/opt/nexo/releases/centinela-v23-v2tools-20260816-40ab2b6`
- Override: `20-versioned-release.conf` (WorkingDirectory y PYTHONPATH apuntan
  al release versionado)

## Archivos

| Carpeta | Descripción |
|---|---|
| `apps_centinela/` | Módulos `apps.centinela` ejecutados vía `python3 -m apps.centinela.main` |
| `admin/` | Panel `nexo_admin_centinela_v2.py` (servicio `nexo-admin-v2`, puerto 8190) |
| `systemd/` | Unidades systemd y override de producción |
| `scripts/` | `deploy-nexo-centinela.sh` y `rollback-nexo-centinela.sh` |

## Verificación

- Hashes: `MANIFEST-SHA256-20260817.md` (coinciden con `motoguarana`)
- Principio read-only confirmado por la unidad:
  `ReadOnlyPaths=/opt/nexo /etc/nexo`, `ReadWritePaths=/var/lib/nexo/centinela`

## Releases de CENTINELA en producción (históricas, no en ejecución)

- `/opt/nexo/releases/centinela-v22-tailscale-parser-20260810-d71f799d5655`
- `/opt/nexo/releases/centinela-v23-v2tools-20260816-40ab2b6` ← **en ejecución**
- `/opt/nexo/releases/orbital-guardian-centinela-v0.1-20260727-003558`