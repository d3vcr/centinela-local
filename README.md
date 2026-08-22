# CENTINELA LOCAL

Baseline documental y runtime verificable de CENTINELA.

**Estado auditado:** `RUNTIME_IMPLEMENTADO + SINCRONIZACION_PENDIENTE + INTEGRACION_DOCUMENTAL_PENDIENTE`

La rama `main` contiene un snapshot real del runtime de CENTINELA sincronizado desde `motoguarana` el 2026-08-17, incluyendo módulos Python, panel administrativo v2, systemd, scripts de deploy/rollback y manifiesto SHA-256.

## Fuente de verdad actual

- Repositorio: `d3vcr/centinela-local`
- Rama: `main`
- Snapshot de runtime: 2026-08-17
- Última actualización documental: 2026-08-21
- Último commit: `2923de1`

## Lectura inicial

1. `01_Fundacion/` — carta, estado y procedencia.
2. `04_Centinela_Runtime/` — runtime real sincronizado desde producción.
3. `08_Pruebas/` — pruebas y evidencia.
4. `09_Roadmap/` — gates y fases.
5. `10_Informes/CEN-ESTADO-COTEJO-20260821.md` — **cotejo actualizado de implementado vs pendiente**.

## Importante: frontera con NEXO

Este repositorio conserva exclusivamente CENTINELA LOCAL. No se debe copiar aquí código de ECU, firmware ESP32, MQTT productivo, cockpit, odómetro o lógica general de NEXO.

Las capacidades implementadas recientemente fuera de esta repo —por ejemplo voz/audio y pruebas de integración— deben registrarse como **implementadas fuera del repo** hasta que el runtime desplegado sea cotejado por archivo, origen y SHA-256.

## Próximo paso

Actualizar el snapshot desde el runtime real de `motoguarana`, comparar hashes contra `04_Centinela_Runtime/current/`, registrar cambios y sólo entonces declarar sincronizada la nueva versión.
