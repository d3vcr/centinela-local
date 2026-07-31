# CEN-00R — Estado y gates

Fecha: 2026-07-31

| Gate | Estado | Evidencia y limitación |
|---|---|---|
| R1 — Identidad Git | `APROBADO` | `main`, base `bbc7568`, remoto esperado, sincronizado y limpio al iniciar |
| R2 — Auditoría Mac | `APROBADO_CON_LIMITACIONES` | `AUSENTE_NO_LOCALIZADA`; ZIP candidato no abierto; recuperación manual definida |
| R3 — Dashboard | `APROBADO` | Imagen original incorporada sin transformación y con hash origen/destino idéntico |
| R4 — Phase I | `APROBADO_CON_LIMITACIONES` | Dos fuentes documentales primarias y copias byte-idénticas; no tienen commit propio |
| R5 — V3-06 | `APROBADO_CON_LIMITACIONES` | Fuente primaria local exacta, duplicado y sidecar; script no incorporado ni reusable |
| R6 — Vigencia | `APROBADO` | V2 histórico/operativo documental, V3 línea oficial local, runtime no verificado |
| R7 — Procedencia | `APROBADO_CON_LIMITACIONES` | Rutas, fechas y hashes completos; Mac ausente, Phase I/V3-06 sin commit fuente |
| R8 — Secretos | `APROBADO` | Ninguna fuente sensible incorporada; ZIP, patch y scripts excluidos |
| R9 — Alcance | `APROBADO` | Cero código, ejecución, Pi, SQLite, instalaciones y cambios NEXO |
| R10 — Cierre | `APROBADO` | Declaración formal coherente con ausencias y límites |

## Resultado

`CEN-00_CERRADO_CON_AUSENCIAS_CONTROLADAS`

## Gates que continúan después del cierre

- El informe Mac sólo puede incorporarse tras entrega explícita, revisión sensible y hash.
- Phase I y V3-06 no son componentes reutilizables ni certificados.
- Runtime y Engineer permanecen separados.
- Observación y administración permanecen separadas.
- MQTT de control, relés, arranque, firmware, SQLite productiva, systemd, calibración y odómetro siguen prohibidos.
- El estado operativo requiere una fase readonly autorizada y no se infiere de documentos.

## Autorización limitada

`CEN-02_AUTORIZADO_SOLO_PARA_DISENO_DOCUMENTAL`

No se autoriza código productivo, ejecución histórica, integración ni despliegue.
