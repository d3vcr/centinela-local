# CENTINELA LOCAL — Cotejo de implementación

**Fecha:** 2026-08-21
**Repositorio:** `d3vcr/centinela-local`
**Rama:** `main`
**HEAD auditado:** `64a73775d82505c9d484c4b4a5020c61e7619e1f`
**Alcance:** separar lo que está implementado en el runtime/local de CENTINELA de lo que se ha implementado recientemente en el ecosistema NEXO pero todavía no está sincronizado en este repositorio.

## 1. Estado de la repo al auditar

La última sincronización del repositorio es del 2026-08-17. El commit `64a7377` incorporó el runtime de producción verificado en `motoguarana`: 9 módulos de `apps_centinela`, panel administrativo v2, unidades systemd, override versionado, scripts de despliegue/rollback y manifiesto SHA-256 de 15 archivos.

El README de la rama `main` todavía presenta el estado formal de `CEN-00` y remite al snapshot de runtime del 2026-08-17.

## 2. Implementado y respaldado directamente por esta repo

| Capacidad | Estado | Evidencia |
|---|---|---|
| Runtime CENTINELA local/read-only | IMPLEMENTADO | `04_Centinela_Runtime/current/apps_centinela/` |
| Motor de reglas/engine | IMPLEMENTADO | módulo `engine.py` y módulos asociados en snapshot |
| Persistencia auxiliar de CENTINELA | IMPLEMENTADO | `persistence.py` en snapshot |
| Servidor local de observación | IMPLEMENTADO | `server.py` en snapshot |
| Panel administrativo CENTINELA v2 | IMPLEMENTADO | `current/admin/nexo_admin_centinela_v2.py` |
| Servicios systemd | IMPLEMENTADO | `current/systemd/` |
| Deploy y rollback | IMPLEMENTADO | `current/scripts/` |
| Protección read-only | IMPLEMENTADO/VERIFICADO | `ReadOnlyPaths=/opt/nexo /etc/nexo`; escritura limitada a persistencia auxiliar |
| `physical_outputs_enabled=false` | VERIFICADO | evidencia de sincronización 2026-08-17 |
| `remote_start_locked=true` | VERIFICADO | evidencia de sincronización 2026-08-17 |
| Manifiesto SHA-256 | IMPLEMENTADO | `MANIFEST-SHA256-20260817.md` |
| Procedencia del runtime | IMPLEMENTADO | `EVIDENCIA-SINCRONIZACION-20260817.md` |

## 3. Implementado recientemente en el sistema, pero NO sincronizado todavía aquí

Estas capacidades pertenecen al trabajo reciente del ecosistema NEXO/Centinela y no deben declararse como código propio de `centinela-local` hasta cotejar los archivos realmente desplegados y sus hashes.

| Capacidad | Estado de implementación conocido | Estado en `centinela-local` |
|---|---|---|
| Núcleo de voz de Centinela v0.3 | IMPLEMENTADO/PROBADO en el trabajo reciente | NO SINCRONIZADO |
| Evidencia de voz v0.4 | GENERADA/PROBADA en el trabajo reciente | NO SINCRONIZADA |
| Salida de audio por Raspberry Pi | PROBADA operativamente | NO DOCUMENTADA EN ESTE SNAPSHOT |
| Pruebas de voz en dos consolas/flujo de datos | PROBADAS durante banco | NO DOCUMENTADAS EN ESTE SNAPSHOT |
| Observación de ECU/GPS en tiempo real | UTILIZADA EN PRUEBAS RECIENTES | NO SINCRONIZADA COMO EVIDENCIA EN ESTA REPO |
| Integración con firmware/ECU | PARTE DEL ECOSISTEMA NEXO, NO DEL ALCANCE EXCLUSIVO DEL REPO | NO DEBE COPIARSE COMO CÓDIGO AQUÍ |
| Integración GPS/odómetro | PARTE DEL ecosistema NEXO | NO DEBE COPIARSE COMO CÓDIGO AQUÍ |

**Regla:** una capacidad probada en NEXO no convierte automáticamente al repositorio `centinela-local` en fuente de verdad. Primero se debe identificar el archivo desplegado, origen, commit/artefacto y SHA-256.

## 4. Pendientes reales

### P0 — Sincronización de fuente de verdad

- [ ] Capturar el estado actual del runtime de CENTINELA en `motoguarana`.
- [ ] Comparar cada archivo desplegado contra `04_Centinela_Runtime/current/`.
- [ ] Generar un nuevo manifiesto SHA-256 fechado.
- [ ] Registrar qué archivos cambiaron y por qué.
- [ ] Crear un nuevo commit de sincronización sólo después del cotejo.

### P1 — Contrato de integración

- [ ] Documentar formalmente qué datos recibe CENTINELA desde NEXO.
- [ ] Separar claramente ECU, GPS, audio y administración de la frontera de CENTINELA LOCAL.
- [ ] Registrar estados `online/offline/stale/timeout` y comportamiento ante datos incompletos.
- [ ] Mantener la política read-only y las barreras de seguridad como gates obligatorios.

### P2 — Voz/audio

- [ ] Incorporar evidencia de la versión de voz actualmente utilizada.
- [ ] Registrar backend/dispositivo de salida y ruta de audio sin convertir el hardware de NEXO en código del repositorio.
- [ ] Añadir pruebas reproducibles de emisión de voz y de fallo de audio.
- [ ] Distinguir claramente "voz implementada" de "voz desplegada en el runtime del snapshot".

### P3 — Pruebas y certificación

- [ ] Consolidar pruebas de banco recientes en `08_Pruebas/`.
- [ ] Registrar comandos, timestamp, resultado y artefactos.
- [ ] Añadir pruebas negativas para pérdida de datos, timeout y datos stale.
- [ ] Ejecutar una revisión final de seguridad/read-only antes de declarar una nueva fase cerrada.

## 5. Lo que NO falta por implementar en este repositorio

No se debe trasladar aquí código de firmware ESP32, ECU, MQTT productivo, cockpit, odómetro o lógica general de NEXO. El commit de sincronización del 2026-08-17 estableció explícitamente ese límite.

Tampoco se debe declarar como pendiente de `centinela-local` una funcionalidad que ya exista en otro repositorio. Debe clasificarse como **implementada fuera del repo / pendiente de integración documental**.

## 6. Veredicto

`centinela-local` NO está vacío ni en estado puramente documental: contiene un runtime real de CENTINELA verificado y reproducible desde el snapshot 2026-08-17.

Sin embargo, la repo está **desactualizada respecto al estado de trabajo más reciente del sistema**. El siguiente paso correcto es una sincronización forense del runtime actual, no una reescritura ni una copia indiscriminada desde NEXO.

**Clasificación actual:** `RUNTIME_IMPLEMENTADO + SINCRONIZACION_PENDIENTE + INTEGRACION_DOCUMENTAL_PENDIENTE`.
