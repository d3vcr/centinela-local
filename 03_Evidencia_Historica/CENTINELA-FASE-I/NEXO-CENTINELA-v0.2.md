# NEXO Centinela v0.2 — diagnóstico readonly de cadencia

## Alcance

Centinela v0.2 mantiene el contrato de v0.1: observa, clasifica y alerta. No
controla, no repara, no publica MQTT, no escribe SQLite, no reinicia servicios
ni ejecuta acciones físicas.

La versión añade observabilidad del tramo `raw_mqtt -> normalizador -> API ->
build frontend` para separar huecos de fuente, atraso de normalización,
respuestas parciales y builds incorrectos.

## Métricas

La respuesta `GET /state` incorpora `telemetry_metrics`:

- `source_publish_interval_ms`;
- `raw_arrival_interval_ms`;
- `normalized_interval_ms`;
- `normalizer_commit_interval_ms`;
- `raw_to_normalized_lag_ms`;
- `normalized_to_api_lag_ms`;
- `api_sample_age_ms`;
- `api_latency_ms`;
- `sample_id`, `publish_counter`, `boot_id`;
- `sample_advances`, `sample_regressions`;
- `source_gaps`, `normalizer_lag_events`, `partial_payloads`;
- `retained_sample_cycles`, `status_transitions`;
- build frontend esperado, servido y coincidencia.

Las consultas SQLite se abren con `mode=ro` y `PRAGMA query_only=ON`. El build
se comprueba contra la entrada JavaScript servida por 8181 y se conserva en
caché durante 60 segundos para limitar CPU e I/O.

## Reglas nuevas

| Regla | Activación | Severidad |
|---|---|---|
| `CENTINELA_TELEMETRY_PIPELINE_LAG` | `raw_to_normalized_lag_ms > 2500` durante dos polls | WARNING |
| `CENTINELA_NORMALIZER_STALLED` | lag mayor de 10 s durante dos polls | CRITICAL |
| `CENTINELA_API_PARTIAL_ECU` | campos físicos requeridos nulos durante dos polls | WARNING |
| `CENTINELA_SAMPLE_CADENCE_DEGRADED` | huecos raw recientes mayores de 2.5 s durante dos polls | WARNING |
| `CENTINELA_FRONTEND_BUILD_MISMATCH` | build servido distinto del esperado durante dos polls | WARNING |

La histéresis, transiciones y persistencia siguen usando el motor determinista
de v0.1.

## Frontend

Los stores permanecen independientes. Para ECU:

- `undefined` y `null` en payload parcial conservan el campo anterior;
- `false` y `0` de una muestra nueva se aplican;
- cambio de boot acepta un contador menor;
- timestamp, id o contador antiguos se descartan;
- stale, offline y timeout conservan el último snapshot.

La instrumentación se activa únicamente con `?nexoDiagnostics=1`. Sin ese
parámetro no crea estado global ni eventos. Cuando está activa registra
secuencia de requests, respuestas, descarte/aceptación, muestra anterior y
aceptada, estado presentado, RPM, testigos, mounts, renders y build ID. Mantiene
como máximo 500 eventos en memoria y no persiste secretos.

## Normalización

El timer repo-managed usa `OnUnitInactiveSec=1s`. La unidad de normalización
continúa siendo `Type=oneshot`, conserva el bloqueo `flock` exclusivo y procesa
como máximo 500 filas por ejecución. No se modifican mapper, esquema, datos,
umbrales de freshness ni API.

## API

Se conservan los endpoints loopback:

- `GET /health`;
- `GET /state`;
- `GET /events?limit=N`.

No existen endpoints de control ni métodos de escritura.

## Despliegue y rollback

El despliegue v0.2:

1. valida servicios, seguridad, odómetro, baseline frontend e integridad;
2. crea backup SQLite consistente y SHA-256;
3. respalda Centinela, unidades, drop-in y symlink frontend;
4. instala únicamente Centinela, timer/drop-in y release frontend;
5. reinicia exclusivamente timer del normalizador, Centinela y frontend 8181;
6. confirma 8080, 8090, 8081, 8181 y Tailscale sin cambios.

El rollback restaura esos mismos archivos y release. La copia SQLite es
evidencia preventiva y no se restaura automáticamente porque esta fase no
modifica el contenido ni el esquema de la base.

## Limitaciones

Los huecos reales de publicación de la ESP/fuente sólo se detectan y
clasifican. Centinela no puede corregir firmware, Wi-Fi, relay externo ni MQTT,
y no enmascara esas pausas aumentando umbrales.
