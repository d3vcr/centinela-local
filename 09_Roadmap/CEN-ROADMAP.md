# CENTINELA LOCAL — Roadmap

Estado: `PROPUESTO`. Solo CEN-00 está abierto.

| Fase | Objetivo | Gate principal | Salida | Estado |
|---|---|---|---|---|
| CEN-00 | Fundación y límites | Ocho fuentes registradas | Baseline documental | Abierto controlado |
| CEN-01 | Inventario existente | CEN-00 cerrado | Código, docs, pruebas y servicios clasificados | No autorizado |
| CEN-02 | Contratos y arquitectura | Inventario aprobado | Esquemas y políticas | No autorizado |
| CEN-03 | Observador read-only | Fuentes allowlisted | Adaptadores sin escritura | No autorizado |
| CEN-04 | Motor determinista | Observador certificado | Reglas explicables | No autorizado |
| CEN-05 | API e interfaz local | Motor certificado | Consulta local | No autorizado |
| CEN-06 | Conocimiento y memoria | Retención aprobada | Procedencia y supersesión | No autorizado |
| CEN-07 | Conversación | Hardware medido | Explicación con evidencia | No autorizado |
| CEN-08 | Engineer | Flujo Git aprobado | Parches revisables | No autorizado |
| CEN-09 | Voz | Texto seguro | Consulta por voz | No autorizado |
| CEN-10 | Administración controlada | Fases read-only certificadas | Catálogo mínimo reversible | No autorizado |

## Regla de entrada

No iniciar una fase sin fase anterior cerrada, alcance, fuentes, riesgos,
pruebas, rollback y stop rules.

## Regla de salida

No cerrar una fase sin pruebas, evidencia, ausencia de cambios fuera de
alcance, controles intactos, limitaciones y rollback verificable.

## Gate actual

CEN-01 permanece bloqueado por las fuentes faltantes y la procedencia
incompleta descritas en `01_Fundacion/CEN-00-ESTADO.md`.
