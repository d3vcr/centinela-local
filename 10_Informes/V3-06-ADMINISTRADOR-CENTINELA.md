# V3-06 — Administrador Centinela

Fecha de síntesis: 2026-07-30

Clasificación: `PROPUESTO`. Este documento no es una certificación ni una
autorización de implementación.

## Fuentes

- `AGENTS.md`, sección V3-06;
- `docs/roadmap/NEXO-V3-ROADMAP.md`, fila V3-06;
- presencia local de
  `C:\Users\edzab\Downloads\nexo_admin_centinela_v2.py`.

El script no fue copiado, abierto, ejecutado ni importado.

Metadatos observados:

- tamaño: 52,811 bytes;
- SHA-256:
  `8f2242116d36e113292713f7d2004db4503224be793d1a86928513efc1509820`;
- fecha de modificación local: 2026-07-27 13:07:24 -06:00.

## Requisitos documentados

- Ruff y Mypy;
- pruebas unitarias y de integración;
- readonly por defecto;
- catálogo cerrado de acciones permitidas;
- confirmación explícita;
- evidencia antes y después;
- transmisión MQTT bloqueada por defecto;
- rollback hacia modo exclusivamente read-only.

## Gates previos

1. V3-05 estable.
2. Fuente dedicada V3-06 aceptada.
3. Revisión estática del script en fase autorizada.
4. Contratos separados para consulta y acción.
5. Catálogo sin shell general.
6. Pruebas negativas de autorización.
7. Sin acceso productivo durante caracterización.

## Relación con CENTINELA LOCAL

CEN-00 no incorpora el administrador. CEN-03 y CEN-04 deben permanecer
read-only. Cualquier administración futura corresponde a CEN-10 y requiere
política, catálogo, simulación, autorización estructurada, expiración,
evidencia y rollback.

## Estado

La fuente documental dedicada solicitada sigue faltante. Esta síntesis evita
que el script local sea tratado como especificación.
