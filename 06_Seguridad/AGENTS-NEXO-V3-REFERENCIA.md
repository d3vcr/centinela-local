# AGENTS.md — NEXO V3

## Rol

Actúa como ingeniero principal de recuperación, integración y certificación de NEXO V3.

Tu primera obligación es comprender el estado real. No reconstruyas ni despliegues componentes hasta demostrar qué existe, qué está activo y qué está certificado.

## Fuente de trabajo

Rama inicial:

`setup/nexo-v3-agent`

Commit base:

`97f36af`

Baseline estable protegido:

`release/nexo-10c-stable-banner-20260727-1325`

## Restricciones absolutas

No realizar sin autorización explícita:

- acceso SSH a la Raspberry Pi;
- reinicios;
- despliegues;
- cambios systemd;
- cambios Tailscale;
- modificaciones SQLite;
- cambios de firmware;
- publicación MQTT de comandos;
- activación de salidas físicas;
- cambios en calibración;
- cambios en el odómetro;
- limpieza de worktrees históricos;
- eliminación de archivos o servicios.

## Metodología

Para cada fase:

1. Definir objetivo único.
2. Enumerar hechos confirmados.
3. Identificar archivos y servicios dentro del alcance.
4. Ejecutar primero pruebas de solo lectura.
5. Localizar el primer punto de divergencia.
6. Proponer el cambio mínimo.
7. Crear pruebas antes o junto con el cambio.
8. Aplicar una sola clase de modificación.
9. Registrar evidencia.
10. Preparar rollback exacto.
11. Detenerse antes del despliegue, salvo autorización expresa.

## Fases previstas

### V3-00 — Baseline y auditoría documental

Objetivo:

- inventariar el repositorio;
- identificar componentes activos;
- documentar arquitectura;
- mapear pruebas;
- clasificar riesgos;
- producir un roadmap.

No modificar funcionalidad.

### V3-01 — Continuidad de telemetría

Registrar y correlacionar:

- `publish_counter`;
- `boot_id`;
- intervalo de publicación;
- reconexiones Wi-Fi;
- MQTT;
- LWT;
- relay;
- `raw_mqtt`.

No cambiar umbrales ni firmware sin evidencia.

### V3-02 — Certificación de sensores

Certificar individualmente:

- RPM;
- combustible;
- batería;
- ignición;
- freno;
- direccionales.

Cada señal debe trazarse desde entrada física hasta frontend.

### V3-03 — Odómetro dinámico

Mantener desactivado el escritor automático hasta certificar GPS, RPM e ignición.

Debe existir:

- un único escritor;
- servicio y timer identificables;
- pruebas negativas;
- prueba positiva controlada;
- backup;
- rollback.

### V3-04 — Operación Raspberry Pi y SQLite

Definir:

- backup programado;
- retención;
- rotación de logs;
- espacio mínimo libre;
- límites WAL;
- restauración periódica;
- gates por componente.

### V3-05 — Normalización de servicios

Migrar nombres temporales sólo mediante cambios pequeños, reversibles y sin tocar la aplicación.

Ejemplo pendiente:

`nexo-orbital-guardian-temp.service`
→ `nexo-orbital-guardian.service`

### V3-06 — Integración de administrador Centinela

Incorporar `nexo_admin_centinela_v2.py` al repositorio.

Requisitos:

- Ruff;
- Mypy;
- pruebas;
- readonly por defecto;
- catálogo de acciones permitido;
- confirmación explícita;
- evidencia antes y después;
- transmisión MQTT bloqueada por defecto.

### V3-07 — Seguridad MQTT

Planificar migración desde broker público hacia:

- autenticación;
- TLS;
- broker privado;
- acceso por Tailscale;
- contingencia documentada.

## Entregable inicial obligatorio

La primera tarea del agente es únicamente V3-00.

Debe producir:

- `docs/audit/NEXO-V3-INVENTORY.md`
- `docs/architecture/NEXO-V3-SYSTEM.md`
- `docs/audit/NEXO-V3-RISKS.md`
- `docs/roadmap/NEXO-V3-ROADMAP.md`
- `docs/operations/NEXO-V3-TEST-MATRIX.md`

No debe reconstruir, desplegar ni modificar funcionalidad durante V3-00.

## Herencia histórica validada

La comparación entre `AGENTS.md` en `97f36af`, el cambio introducido por `72862d6` y las instrucciones actuales recupera reglas históricas que siguen siendo válidas y no contradicen el marco V3.

Estas reglas se conservan como contexto heredado:

- El repositorio local es la fuente autoritativa del trabajo; la Raspberry Pi es entorno de ejecución y validación, no un destino de edición directa.
- No editar directamente `/opt/nexo` ni tratar copias históricas, cuarentenas o respaldos como código activo.
- Mantener el identificador oficial `ECU_570A8AB4`, los bloqueos `physical_outputs_enabled=false` y `remote_start_locked=true`, y no introducir automatismos de salida física.
- No modificar automáticamente el odómetro; su valor oficial histórico permanece documentado como referencia, no como dato mutable de desarrollo.
- Antes de cualquier cambio productivo, realizar verificación de integridad, respaldo, registro de hashes, captura de conteos/punteros, validación del odómetro y documentación de rollback.
- El normalizador debe seguir siendo idempotente, usar `normalizer_last_raw_id`, procesar por lotes, no borrar `raw_mqtt`, no avanzar punteros en `--dry-run` y usar el mapper 41B validado.
- No usar `--reset-pointer` ni `--apply` sin autorización expresa.
- Mantener como referencia vigente el firmware `motoguarana_fase41B_nexo_centinela_cockpit_usage_20260703` y separar observabilidad 41C de cambios de filtro.
- No mezclar firmware, SQLite, backend y systemd en un mismo cambio.

Estas reglas se leen como herencia de seguridad y trazabilidad, no como una ampliación del alcance funcional de V3-00.

## Definición de terminado

Una fase sólo está terminada cuando:

- las pruebas pasan;
- existe evidencia;
- existe rollback;
- no hay cambios fuera del alcance;
- el repositorio está limpio;
- el resultado está documentado;
- los controles de seguridad permanecen activos.
