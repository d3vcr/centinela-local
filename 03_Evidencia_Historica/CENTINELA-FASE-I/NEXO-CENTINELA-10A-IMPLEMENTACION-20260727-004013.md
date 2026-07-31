# NEXO-10A — Evidencia de implementación de Centinela v0.1

Fecha de validación: 2026-07-27 00:39:40 CST

Repositorio autoritativo: `C:\Users\edzab\Documents\NEXO\nexo-orbital-guardian-production`

Raspberry Pi: `motoguarana`

## Objetivo y límites

Se implementó Centinela v0.1 como observador determinista y exclusivamente
readonly del dominio NEXO. Clasifica salud, conserva estado y eventos locales,
expone una API loopback y presenta un resumen en Orbital Guardian.

Centinela no controla, no repara, no publica MQTT, no escribe SQLite, no
reinicia servicios, no modifica firmware, no cambia Tailscale y no ejecuta
acciones físicas.

## Arquitectura

Fuentes readonly:

- NEXO API: `/health`, `/live`, `/odometer` en `127.0.0.1:8080`.
- systemd: propiedades y estados de unidades mediante consultas sin `sudo`.
- `tailscale serve status`.
- listeners obtenidos con `ss -ltn`.

Flujo:

`fuentes readonly -> collector -> reglas/máquina de estados -> state.json/events.jsonl -> API 127.0.0.1:8090 -> proxy allowlist 8181 -> Orbital Guardian`

## Reglas y estabilidad

Se incluyeron las 14 reglas solicitadas: API inalcanzable/degradada, invariantes
de seguridad, servicio NEXO caído/reiniciando, ECU stale/offline, GPS
stale/offline, regresión de muestra, destino Tailscale distinto, legacy
reactivado, boot-check fallido y cambio de referencia del odómetro.

Cada regla mantiene fallos y recuperaciones consecutivas, `first_seen`,
`last_seen`, `occurrences` y transiciones `ACTIVATED`, `UPDATED`, `RECOVERED`.
Los reinicios se evalúan en una ventana de diez minutos. Una observación activa
se actualiza sin duplicar el evento en cada ciclo. Seguridad crítica se activa
inmediatamente; las demás reglas aplican su histéresis explícita.

## Persistencia y API

- `/var/lib/nexo/centinela/state.json`: `nexo:nexo`, modo `0600`.
- `/var/lib/nexo/centinela/events.jsonl`: `nexo:nexo`, modo `0600`.
- Directorio: `nexo:nexo`, modo `0750`.
- Escritura atómica de estado; eventos limitados a los 500 más recientes.
- Corrupción recuperable sin impedir el arranque.
- API enlazada exclusivamente a `127.0.0.1:8090`.
- `GET /health`, `GET /state`, `GET /events?limit=10`: HTTP 200.
- Métodos de escritura y endpoints de control no existen.

## Integración Orbital Guardian

Se añadió un cliente independiente de Centinela y un proxy de allowlist exacta:

- `/api/centinela/health`
- `/api/centinela/state`
- `/api/centinela/events`

Portal, Cockpit, Dashboard y Street muestran el resumen readonly usando los
componentes visuales existentes. La indisponibilidad de 8090 se representa como
Centinela offline sin tocar `lastGoodEcuSample`, borrar ECU ni desmontar el
dashboard.

## Pruebas ejecutadas

- Ruff: aprobado.
- Mypy: aprobado, 9 archivos fuente sin errores.
- Pytest dirigido: 22 pruebas aprobadas.
- TypeScript typecheck: aprobado.
- ESLint: aprobado.
- Vitest: 29 archivos, 246 pruebas aprobadas.
- Build Vite: aprobado, 92 módulos; 6 archivos y 5 rutas verificados.
- `bash -n`: aprobado.
- ShellCheck: aprobado.
- `py_compile` del servidor SPA: aprobado.
- `git diff --check`: aprobado.

Los primeros intentos de Ruff, Mypy, pytest y typecheck detectaron errores
reales de formato/tipado y una aserción de permisos específica de POSIX; se
corrigieron y sus ejecuciones finales quedaron aprobadas. No se ocultaron
fallos ni se realizaron pruebas físicas.

## Despliegue

- Código: `/opt/nexo/apps/centinela`.
- Unidad: `/etc/systemd/system/nexo-centinela.service`.
- Release frontend inmutable:
  `/opt/nexo/releases/orbital-guardian-centinela-v0.1-20260727-003558`.
- SHA-256 del archivo frontend:
  `6d8250c6604eb7f56e55427c7be78e0a42992d6787129bc78679768486e02734`.
- Backup:
  `/var/lib/nexo/backups/centinela-v0.1-20260727-003558`.
- Deploy persistente:
  `/opt/nexo/scripts/deploy/deploy-nexo-centinela.sh`.
- Rollback persistente:
  `/opt/nexo/scripts/recovery/rollback-nexo-centinela.sh`.

El despliegue reinició únicamente `nexo-orbital-guardian-temp.service`, porque
era necesario cambiar la release frontend de 8181. No se reinició la Pi.

## Estado operacional validado

- `nexo-centinela.service`: enabled, active, `Result=success`,
  `ExecMainStatus=0`, `NRestarts=0`.
- Estado Centinela: `HEALTHY`.
- Listener: `127.0.0.1:8090`.
- 8181 proxy Centinela: health/state/events HTTP 200.
- Portal, Cockpit, Dashboard y Street en 8181: HTTP 200.
- 8080 escucha en loopback y sus endpoints oficiales son consumidos
  correctamente; 8081 y 8181 permanecen HTTP 200.
- Los ocho servicios protegidos permanecen enabled/active.
- `nexo-startup-verify.service`: enabled, `Result=success`,
  `ExecMainStatus=0`.
- Los cuatro servicios legacy reales con prefijo `motoguarana-` permanecen
  disabled/inactive.
- Tailscale raíz continúa apuntando a `http://127.0.0.1:8181`.
- Las cuatro rutas Tailscale verificadas devolvieron HTTP 200.
- Los funnels 8443 -> 3040 y 10000 -> 3070 permanecen intactos.
- `physical_outputs_enabled=false`.
- `relay_outputs_enabled=0` (equivalente falso).
- `remote_start_locked=true`.
- `database.readonly=true`.
- `database.query_only=1`.
- Odómetro: `10148.2 km`.
- No existe superficie de publicación MQTT o tópico `cmd` en el código
  desplegado de Centinela; no hubo publicación MQTT cmd.
- Journal de Centinela sin entradas warning/alert durante la validación.

## Rollback exacto

Preflight readonly:

```bash
sudo /opt/nexo/scripts/recovery/rollback-nexo-centinela.sh \
  --backup-dir /var/lib/nexo/backups/centinela-v0.1-20260727-003558
```

Aplicación explícita:

```bash
sudo /opt/nexo/scripts/recovery/rollback-nexo-centinela.sh \
  --backup-dir /var/lib/nexo/backups/centinela-v0.1-20260727-003558 \
  --apply \
  --confirm ROLLBACK_NEXO_CENTINELA
```

El rollback deshabilita y detiene exclusivamente Centinela, restaura su
código/unidad si existían, restaura la release frontend anterior
`/opt/nexo/releases/orbital-guardian-279ba1bdc628-20260726-233240` y reinicia
únicamente el frontend 8181. No afecta 8080, 8081, Tailscale ni NEXO core.

## Limitaciones v0.1

No incluye IA generativa, recomendaciones o reparación automática, reinicios
automáticos, comandos MQTT, control remoto, predicción, aprendizaje histórico,
odómetro dinámico, alertas externas, firmware ni acciones sobre la motocicleta.
