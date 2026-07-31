# Estado documental NEXO V2/V3

Fecha de corte inicial: 2026-07-30

Revalidación documental CEN-00R: 2026-07-31

Clasificación: `DOCUMENTADO` a partir del repositorio local. No equivale a
estado operativo actual.

## NEXO V2

`HISTÓRICO`: los documentos del 2026-06-27 y 2026-07-05 describen Motoguaraña
y NEXO temprano, servicios legacy, firmware 41B y controles físicos
bloqueados. Esas fuentes fueron superadas en partes por la evolución posterior
y no pueden usarse solas como baseline actual.

`NO_DETERMINABLE` en CEN-00: servicios activos, puertos, rutas efectivas,
SQLite oficial, escritor de odómetro y carga real de la Pi.

`DOCUMENTADO` en CEN-00R: el repositorio local `nexo` estaba en rama `codex/nexo-rebuild-phase-e`, HEAD `bc6299a5a83f1dfe3c6723f1069ea8b15be8bd00`, remoto configurado `https://github.com/d3vcr/nexo-ecu.git`. Los documentos `docs/ESTADO_NEXO.md` y `docs/NEXO-ESTADO.md` tienen último commit relacionado `8a134861729a0594dec197e98574bd7ca3d0dded` del 2026-07-10. Se mantienen como referencia operativa e histórica; no prueban estado actual.

## NEXO V3

`OBSERVADO` en el repositorio local del commit `3b56d11`:

- existe el paquete documental obligatorio V3-00;
- el roadmap declara V3-00 completado localmente;
- V3-01 y V3-02 tienen material de preparación;
- V3-06 y V3-07 permanecen futuras;
- existen implementaciones locales de ingesta, normalización, API, sessionizer,
  Centinela y Cockpit;
- la arquitectura marca como pendiente todo lo que depende de la Pi.

`DOCUMENTADO_VIGENTE_COMO_LINEA_OFICIAL_LOCAL` en CEN-00R: el repositorio `nexo-v3-agent` estaba en rama `setup/nexo-v3-agent`, HEAD `3b56d11db0f5d74eaf1422fa6f56d42669ea2fbb`, remoto configurado `https://github.com/d3vcr/nexo-ecu.git`. El roadmap y `AGENTS.md` coinciden byte por byte con las referencias incorporadas. La arquitectura coincide en contenido al normalizar CRLF/LF; el hash normalizado común es `801d56e3a40b4f6a3fd3526e656db48b76824df197374a19e5cae426d906ed6a`.

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

La vigencia documental queda resuelta de forma conservadora: NEXO V2 es referencia operativa e histórica documentada; NEXO V3 es la línea oficial local de integración y evolución. El estado operativo de ambos sigue `NO_VERIFICADO_EN_CEN-00R`. No se declara que la Raspberry Pi ejecute V3.
