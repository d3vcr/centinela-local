# Fase I — Ejecución local de Centinela

Guía operativa del prototipo read-only. Todo ocurre en la Dell, contra
`127.0.0.1`. No se toca la Raspberry Pi, no se usa Tailscale, no hay MQTT
ni despliegues.

## Requisitos

- Entorno virtual de Fase F:
  `C:\Users\edzab\Documents\NEXO\.venv-phase-f-api-integration`
- API local de Fase E escuchando en `127.0.0.1:8765`. La forma más simple
  es el runner portable de Fase G (levanta API con base sembrada):

```powershell
C:\Users\edzab\Documents\NEXO\.venv-phase-f-api-integration\Scripts\python.exe `
  tools\run_phase_g_local.py
```

## Ejecución

Desde la raíz del repositorio:

```powershell
C:\Users\edzab\Documents\NEXO\.venv-phase-f-api-integration\Scripts\python.exe `
  -m apps.centinela.nexo_centinela --base-url http://127.0.0.1:8765
```

El reporte JSON sale por stdout. Nada se escribe a disco. Los caracteres
no ASCII se emiten escapados (`\uXXXX`) para que la salida sea imprimible
en cualquier consola Windows; `json.loads` recupera el texto original.

### Opciones

| Opción | Default | Descripción |
|---|---|---|
| `--base-url` | `http://127.0.0.1:8765` | única base aceptada (también `http://localhost:8765`); cualquier otro host, puerto o esquema se rechaza |
| `--timeout` | `5.0` | segundos por petición GET (0 < t ≤ 300) |
| `--output` | `json` | único formato admitido |
| `--boot-window-minutes` | `30` | ventana para churn de boot_id y conteo de rechazos |
| `--rejection-threshold` | `5` | rechazos tolerados en la ventana antes de warning |

### Códigos de salida

| Código | Significado |
|---|---|
| 0 | estado global `ok` |
| 1 | estado global `warning` |
| 2 | estado global `critical` (incluye API local caída) |
| 3 | estado global `unknown`, argumentos inválidos o error interno |

En PowerShell el código queda en `$LASTEXITCODE`.

### Ejemplo de salida

```json
{
  "generated_at": "2026-07-13T12:00:00Z",
  "overall_status": "warning",
  "findings": [
    {
      "code": "ECU_STALE",
      "severity": "warning",
      "component": "ecu",
      "summary": "La muestra ECU supera el umbral de frescura documentado por la API.",
      "evidence": {
        "endpoint": "/api/v1/live",
        "status": "stale",
        "age_seconds": 180.0,
        "threshold_seconds": 5.0,
        "last_received_at": "2026-07-13T11:57:00Z"
      },
      "recommendation": "Confirmar localmente si la telemetría ECU sigue llegando al recorder. No ejecutar acciones sobre la motocicleta ni sobre servicios remotos."
    }
  ],
  "coverage": {
    "available_rules": 12,
    "evaluated_rules": 12,
    "unknown_rules": 0
  }
}
```

## Garantías de seguridad operativa

- **GET-only:** el cliente no puede construir POST/PUT/PATCH/DELETE; las
  pruebas verifican con un servidor falso que solo llegan GET.
- **Local-only:** hosts distintos de `127.0.0.1`/`localhost`, puertos
  distintos de `8765` y esquemas distintos de `http` se rechazan antes de
  abrir conexión alguna.
- **Sin estado:** no se crean archivos, no se escribe SQLite, no queda
  nada persistente entre ejecuciones.
- **Sin fallback silencioso:** si la API no responde, el reporte lo dice
  (`API_UNAVAILABLE`, evidencia con el desenlace real); nunca se rellenan
  datos desde fixtures.
- **Sin trazas ni cuerpos sensibles:** los errores se resumen (clase de
  excepción o código HTTP), sin volcar cuerpos de respuesta ni stack
  traces.

## Interpretación rápida

- `unknown` significa "no hay evidencia suficiente", no "sano" ni "cero".
- LWT `offline` es `warning`: puede ser un apagado normal.
- `rpm=0` con muestra fresca es `ok`: el motor puede estar apagado.
- Un `critical` de `SAFETY_INVARIANT_VIOLATION` significa que alguna
  fuente reportó `physical_outputs_enabled=true` o
  `remote_start_locked=false`; revisar recorder y contrato localmente,
  sin actuar sobre la moto.

## Pruebas y validación local

```powershell
$py = 'C:\Users\edzab\Documents\NEXO\.venv-phase-f-api-integration\Scripts\python.exe'

# pruebas focalizadas
& $py -m pytest -p no:cacheprovider -q tests\centinela

# lint y tipos (el paquete no está en pyproject; se pasan flags equivalentes)
& $py -m ruff check --isolated --select E,F,I,UP,B,SIM --line-length 100 `
  --target-version py312 apps\centinela tests\centinela
& $py -m mypy --strict apps\centinela\nexo_centinela tests\centinela\centinela_testkit.py `
  tests\centinela\conftest.py tests\centinela\test_centinela_rules.py `
  tests\centinela\test_centinela_engine.py tests\centinela\test_centinela_client.py `
  tests\centinela\test_centinela_cli.py

# suite completa
& $py -m pytest -ra -p no:cacheprovider
```

## Limitaciones

- Requiere que la API de Fase E esté levantada en el puerto 8765; si no,
  el resultado es `critical` por `API_UNAVAILABLE` (comportamiento
  deliberado, no un error de Centinela).
- La ventana histórica observable está limitada a la última página (200)
  de rechazos y observaciones de arranque.
- No hay modo daemon ni programación periódica: cada ejecución es una
  pasada única y determinista.
