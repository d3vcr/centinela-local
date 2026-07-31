# Fase I — Centinela read-only local

## Qué es Centinela

Centinela es un evaluador **local, determinista y completamente read-only**
de salud operacional para NEXO v2. Consume exclusivamente la API local de
Fase E mediante peticiones GET y produce un reporte JSON con:

- estado global (`overall_status`);
- hallazgos (`findings`) con código, severidad, componente, resumen,
  evidencia concreta y recomendación no operativa;
- cobertura de reglas (`coverage`).

El paquete vive en `apps/centinela/nexo_centinela/` y no depende de los
paquetes de recorder, storage ni API (solo de la biblioteca estándar).

## Qué NO es Centinela

- No es inteligencia artificial generativa: no usa LLM, aprendizaje
  automático ni servicios remotos.
- No es un actuador: nunca controla la motocicleta ni ejecuta acciones
  físicas.
- No es un servidor: no abre puertos, no expone HTTP nuevo.
- No es un recolector: no escribe SQLite, no crea archivos de estado
  permanentes, no persiste nada entre ejecuciones.
- No es un diagnosticador causal: registra observaciones (por ejemplo,
  cambios de `boot_id`) sin atribuir causas físicas.

## Por qué no controla la moto

Centinela se construye sin ninguna vía de mando por diseño:

1. el cliente HTTP solo puede construir peticiones GET (no existe parámetro
   de método en `ReadOnlyApiClient`);
2. la única superficie aceptada es `http://127.0.0.1:8765` o
   `http://localhost:8765`; cualquier otro host, puerto o esquema se
   rechaza antes de abrir una conexión;
3. la API de Fase E que consume es a su vez read-only (rechaza
   POST/PUT/PATCH/DELETE con 405) y no publica MQTT;
4. no hay MQTT, WebSocket, EventSource, comandos ni credenciales en el
   paquete;
5. las recomendaciones de los hallazgos son informativas y terminan
   siempre en la instrucción de no ejecutar acciones sobre la motocicleta.

## Fuentes permitidas (endpoints reales consumidos)

Los nombres se confirmaron contra `apps/api/nexo_api/app.py`:

| Endpoint | Uso en Centinela |
|---|---|
| `/api/v1/health` | disponibilidad, modo read-only, safety |
| `/api/v1/live` | familias live, frescura, boot_id, rpm, LWT, safety |
| `/api/v1/metrics` | adquirido para evidencia; sin regla propia todavía |
| `/api/v1/gaps` | cobertura raw→estructurado (lag) |
| `/api/v1/rejections?limit=200` | conteo de rechazos recientes |
| `/api/v1/boot-observations?limit=200` | churn de boot_id |
| `/api/v1/schema` | compatibilidad de contrato y read-only |

Notas de nomenclatura: la API real expone `diagnostics` (no `diag`),
`connectivity` (no `lwt`) y `boot-observations` (no `boot/observations`).
El estado de diagnóstico y de LWT se lee desde `/api/v1/live`, que ya
incluye los últimos items de las cuatro familias; `/health` raíz es un
alias de `/api/v1/health` y no se consulta por separado.

## Arquitectura

```
apps/centinela/nexo_centinela/
├── __init__.py    versión del prototipo
├── __main__.py    python -m apps.centinela.nexo_centinela
├── cli.py         CLI local, códigos de salida, sin trazas
├── client.py      cliente GET-only, validación de base, timeouts
├── snapshot.py    adquisición de instantánea (endpoints reales)
├── rules.py       12 reglas deterministas + contexto configurable
├── engine.py      agregación de severidad y construcción del reporte
└── models.py      Finding, Coverage, Report, Severity
```

Flujo: `cli` → `client`+`snapshot` (GET únicos, orden fijo) → `rules`
(cada regla produce exactamente un hallazgo) → `engine` (agregación) →
JSON por stdout. Para reglas con historia (churn, rechazos) se usan los
endpoints históricos existentes; las pruebas también pueden inyectar
instantáneas fabricadas sin HTTP.

## Reglas implementadas

| Código | Componente | Dispara | Sin evidencia |
|---|---|---|---|
| `API_UNAVAILABLE` | api | health sin respuesta utilizable (red, timeout, HTTP≠200, JSON/Content-Type inválido) → **critical** | — |
| `API_NOT_READ_ONLY` | api | health niega `sqlite_read_only` o `query_only` → **critical** | campos ausentes → unknown |
| `LIVE_NO_DATA` | live | una o más familias sin `item` → **warning** | live inaccesible → unknown |
| `ECU_STALE` | ecu | frescura ECU `stale` según umbral documentado por la API → **warning** | `no_data` o ilegible → unknown |
| `CONNECTIVITY_OFFLINE` | connectivity | último LWT con `online=false` → **warning** | sin item LWT → unknown |
| `BOOT_ID_MISSING` | telemetry | hay item ecu/status sin `boot_id` entero → **warning** | sin telemetría → unknown |
| `BOOT_CHURN` | device | ≥3 cambios de boot_id dentro de la ventana → **warning** | endpoint o timestamps inválidos → unknown |
| `REJECTION_SPIKE` | ingest | rechazos en la ventana > umbral → **warning** | endpoint ausente, timestamps inválidos o página truncada → unknown (nunca cero) |
| `RAW_STRUCTURED_LAG` | storage | `missing_typed_rows > 0` en la cobertura de `/api/v1/gaps` → **warning** | gaps ausente o entradas ilegibles → unknown |
| `RPM_SIGNAL_DEGRADED` | ecu | muestra ECU fresca sin campo `rpm` numérico → **warning**; `rpm=0` fresca es **ok** (motor apagado no es fallo) | muestra ausente o no fresca → unknown |
| `SAFETY_INVARIANT_VIOLATION` | safety | `physical_outputs_enabled≠false` o `remote_start_locked≠true` en cualquier fuente → **critical** | campos ausentes → unknown (nunca critical automático) |
| `SCHEMA_OR_CONTRACT_UNAVAILABLE` | contract | esquema inaccesible o con migraciones pendientes → **warning**; esquema que declara escritura → **critical** | campos ilegibles → unknown |

## Severidades y política de agregación

Niveles: `ok`, `warning`, `critical`, `unknown`.

1. Cualquier hallazgo `critical` ⇒ `overall_status = critical`.
2. Sin critical, cualquier `warning` ⇒ `overall_status = warning`.
3. Sin critical ni warning ⇒ `ok` solo si hay al menos una regla evaluada
   con evidencia y los `unknown` no superan a los `ok`.
4. Si la evidencia insuficiente domina (más `unknown` que `ok`, o ninguna
   regla evaluada) ⇒ `overall_status = unknown`.

## Política de `unknown`

- La ausencia de evidencia **nunca** se traduce a `ok` ni a valores cero.
- Un endpoint caído produce `unknown` en las reglas que dependen de él
  (además del hallazgo `API_UNAVAILABLE` cuando aplica).
- Los hallazgos `unknown` aparecen en `findings` con la explicación de qué
  evidencia falta.
- `coverage` reporta `available_rules`, `evaluated_rules` (con evidencia
  real: ok/warning/critical) y `unknown_rules`.

## Códigos de salida de la CLI

| Código | Significado |
|---|---|
| 0 | `overall_status = ok` |
| 1 | `overall_status = warning` |
| 2 | `overall_status = critical` (incluye API caída) |
| 3 | `overall_status = unknown`, argumentos inválidos o error interno de adquisición |

## Limitaciones actuales

- La ventana de análisis (`--boot-window-minutes`) se comparte entre boot
  churn y conteo de rechazos.
- El conteo de rechazos y churn se basa en la página más reciente
  (límite 200); si la página se trunca dentro de la ventana el resultado
  es `unknown`, no un número inventado.
- `/api/v1/metrics` se adquiere pero aún no respalda una regla propia:
  sus contadores son acumulados desde el origen de la base y no permiten
  detectar picos sin historia adicional.
- Centinela no diferencia "moto apagada" de "sensor caído": eso requiere
  contexto que la API no expone; por eso `rpm=0` fresca es `ok` y el LWT
  offline es `warning`, no `critical`.

## Relación futura con el dashboard (Fase F/G)

El reporte JSON está pensado para que el dashboard local lo consuma como
un bloque de "salud" (mismo shape estable: `overall_status`, `findings`,
`coverage`). Una fase futura puede servirlo tras el mismo origen permitido
del dashboard sin cambiar el motor de reglas.

## Relación futura con Guardian

Guardian (odómetro y protecciones de datos) permanece fuera del alcance:
Centinela podría, en el futuro, **leer** indicadores publicados por
Guardian a través de la API local y convertirlos en hallazgos, pero nunca
escribirá el odómetro ni modificará sus datos. Cualquier integración será
igualmente GET-only.
