# Estado documental NEXO V2/V3

Fecha de corte documental: 2026-07-30

Clasificación: `DOCUMENTADO` a partir del repositorio local. No equivale a
estado operativo actual.

## NEXO V2

`HISTÓRICO`: los documentos del 2026-06-27 y 2026-07-05 describen Motoguaraña
y NEXO temprano, servicios legacy, firmware 41B y controles físicos
bloqueados. Esas fuentes fueron superadas en partes por la evolución posterior
y no pueden usarse solas como baseline actual.

`NO_DETERMINABLE` en CEN-00: servicios activos, puertos, rutas efectivas,
SQLite oficial, escritor de odómetro y carga real de la Pi.

## NEXO V3

`OBSERVADO` en el repositorio local del commit `3b56d11`:

- existe el paquete documental obligatorio V3-00;
- el roadmap declara V3-00 completado localmente;
- V3-01 y V3-02 tienen material de preparación;
- V3-06 y V3-07 permanecen futuras;
- existen implementaciones locales de ingesta, normalización, API, sessionizer,
  Centinela y Cockpit;
- la arquitectura marca como pendiente todo lo que depende de la Pi.

`DOCUMENTADO`: `apps/centinela` es un observador read-only; V3-06 prevé integrar
un administrador con Ruff, Mypy, pruebas, catálogo permitido, confirmación y
MQTT bloqueado.

## Estado Git del baseline

- rama: `docs/centinela-local-cen-00`;
- base: `3b56d11db0f5d74eaf1422fa6f56d42669ea2fbb`;
- la rama inicial observada estaba tres commits detrás de su referencia local;
- no se hizo fetch, pull, merge ni rebase;
- no se usa una copia sincronizada como evidencia de despliegue.

## Controles que se conservan

- `physical_outputs_enabled=false`;
- `relay_outputs_enabled=false`;
- `remote_start_locked=true`;
- firmware, SQLite, systemd, Tailscale, MQTT de control, calibración y odómetro
  fuera de CEN-00.

## Conclusión

El baseline documental permite diseñar CENTINELA LOCAL, pero el estado
operativo V2/V3 sigue `NO_VERIFICADO_EN_CEN-00`. Una validación posterior
requerirá autorización read-only específica y no puede inferirse de la Pi
encendida ni de documentos históricos.
