# CEN-00 — Informe inicial

Fecha: 2026-07-30

Dictamen: `CEN-00_ABIERTO_CONTROLADO`.

## Resultado

Se creó un baseline exclusivamente documental en una rama y worktree aislados.
El trabajo define misión, dominios, arquitectura preliminar, seguridad,
capacidades, riesgos, pruebas, roadmap y procedencia.

No se modificó funcionalidad ni se accedió a la Raspberry Pi. No hubo
instalaciones, red, SQLite, MQTT, systemd, firmware, modelos o despliegue.

## Baseline Git

- Repositorio de origen:
  `C:\Users\edzab\Documents\NEXO\nexo-v3-agent`
- Rama inicial observada: `setup/nexo-v3-agent`
- HEAD inicial:
  `3b56d11db0f5d74eaf1422fa6f56d42669ea2fbb`
- Rama documental: `docs/centinela-local-cen-00`
- Worktree:
  `C:\Users\edzab\Documents\NEXO\nexo-centinela-local-cen-00`

El worktree original estaba detrás de su referencia local y contenía cambios
previos no atribuidos. Se mantuvo intacto.

## Evidencia incorporada

- carta fundacional;
- roadmap y arquitectura V3 del baseline local;
- política `AGENTS.md` del baseline;
- documentación histórica Fase I y Centinela v0.1/v0.2;
- evidencia histórica de implementación 10A;
- síntesis documental de V2/V3;
- síntesis propuesta de V3-06.

## Limitaciones

- informe Mac Kubuntu faltante;
- imagen original faltante;
- documentos Fase I sin commit;
- runtime V2/V3 no observado en esta fase;
- V3-06 sin fuente documental dedicada preexistente;
- no se verificó si la referencia local de Git refleja el remoto actual, porque
  CEN-00 no autorizó Internet.

## Contradicciones principales

1. Los estados históricos del 2026-06-27 y 2026-07-05 describen NEXO inicial,
   mientras el roadmap V3 posterior declara V3-00 completo localmente.
2. Fase I define un evaluador de una pasada, loopback y sin persistencia;
   v0.1/v0.2 posteriores describen servicio y persistencia de evidencia.
3. El requisito futuro V3-06 propone un administrador con catálogo de acciones,
   mientras CEN-00 y el antecedente Centinela son read-only.
4. La carta exige `relay_outputs_enabled=false`, además de los dos invariantes
   presentes en la arquitectura V3; debe conservarse como requisito explícito.

## Rollback

El cambio es aditivo. El rollback exacto es retirar únicamente
`CENTINELA LOCAL/` de la rama documental. Eliminar rama o worktree requiere
autorización expresa y no forma parte de CEN-00.

## Recomendación

Mantener el estado abierto. Incorporar primero el informe Mac, la imagen
original y una fuente V3-06 inequívoca; después resolver la procedencia de Fase
I y revisar el resumen V2/V3 con una fase read-only autorizada.
