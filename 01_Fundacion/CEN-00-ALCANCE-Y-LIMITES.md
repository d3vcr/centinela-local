# CEN-00 — Alcance y límites

Fecha: 2026-07-30

Estado: `CEN-00_ABIERTO_CONTROLADO`

## Objetivo único

Crear un baseline documental trazable para CENTINELA LOCAL sin implementar,
instalar, ejecutar, desplegar ni seleccionar tecnología.

## Dentro del alcance

- conservar la carta fundacional;
- registrar fuentes por nombre, origen, hash y vigencia;
- separar Centinela Runtime de Centinela Engineer;
- documentar arquitectura preliminar, capacidades, riesgos y roadmap;
- registrar contradicciones y fuentes faltantes;
- preparar criterios de pruebas futuras.

## Fuera del alcance

- código y pruebas ejecutables;
- modelos locales o remotos;
- instalaciones y dependencias;
- SSH, Tailscale, systemd, journal y runtime de la Raspberry Pi;
- consultas a SQLite;
- MQTT;
- firmware, calibración, odómetro y salidas físicas;
- despliegue, commit, push o merge.

La creación de la rama documental
`docs/centinela-local-cen-00` fue autorizada expresamente el 2026-07-30. Esa
autorización no amplía el alcance a commits, publicación ni operación.

## Frontera con NEXO

NEXO conserva telemetría, almacenamiento, API, interfaz y despliegue.
CENTINELA LOCAL observa contratos autorizados y puede preparar propuestas,
pero no se inserta en la cadena crítica ni adquiere autoridad de control.

## Clasificación obligatoria

- `OBSERVADO`: comprobado directamente en el entorno local indicado.
- `DOCUMENTADO`: afirmado por una fuente identificada.
- `HISTÓRICO`: evidencia válida para su fecha, no confirmada como actual.
- `INFERIDO`: conclusión razonada que requiere validación.
- `PROPUESTO`: diseño futuro sin implementación.

## Rollback

Antes de un commit, el rollback consiste en retirar únicamente
`CENTINELA LOCAL/` del worktree documental y eliminar la rama/worktree solo
con autorización expresa. No se toca el worktree original.
