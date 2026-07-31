# CEN-01 — Estado, decisiones y gates

**Estado formal:** `CEN-01_CERRADO_CON_PENDIENTES_DOCUMENTADOS`
**Fecha:** 2026-07-31
**Siguiente fase:** no iniciada.

## 1. Criterio de cierre

CEN-01 se cierra porque las familias conocidas fueron identificadas, clasificadas y vinculadas a evidencia o a una ausencia explícita. Este cierre es documental. No certifica componentes, no selecciona una implementación y no autoriza CEN-02.

## 2. Decisiones registradas

| Familia | Decisión CEN-01 | Razón |
|---|---|---|
| Phase I | `REQUIERE_CARACTERIZACION` | Diseño compatible con observación local, pero fuente/commit no verificados |
| NEXO-11 v0.1/v0.2 | `REQUIERE_CARACTERIZACION` | Mayor cobertura; fuente y vigencia ausentes; separar runtime de despliegue |
| V3-06 administrador | `REQUIERE_CARACTERIZACION` | Sólo síntesis; superficie de acciones potencialmente sensible |
| Visual / Orbital | `SOLO_REFERENCIA` | Consumidor documentado; paquete independiente no localizado |
| Baseline Centinela Local | `MARCO_RECTOR` | Documentación propuesta sin implementación |

No se declara ningún componente `REUTILIZABLE`, `CERTIFICADO`, `ACTIVO` ni `DESCARTADO`.

## 3. Gates previos a caracterización futura

### G1 — Identidad de fuente

- ruta exacta y origen;
- branch y commit verificables;
- SHA-256 calculado sobre los archivos recuperados;
- estado Git y lista completa de archivos;
- ausencia de mezcla con worktrees históricos o producción.

### G2 — Aislamiento

- copia o worktree dedicado;
- sin acceso a `/opt/nexo`, Raspberry Pi, Tailscale o servicios productivos;
- sin uso de SQLite productiva;
- sin publicación MQTT ni salidas físicas;
- dependencias inventariadas antes de cualquier instalación autorizada.

### G3 — Efectos laterales

- mapa de lecturas y escrituras;
- red, subprocess, shell, systemd y persistencia identificados;
- distinción entre estado auxiliar y estado productivo;
- comportamiento ante offline, stale, timeout y datos incompletos;
- rollback exacto del entorno de prueba.

### G4 — Calidad y reproducibilidad

- lint, tipos y pruebas identificados;
- ejecución sólo tras autorización de la fase correspondiente;
- fixtures sin datos productivos;
- resultados con comando, timestamp y exit status;
- discrepancias entre documento y código registradas.

### G5 — Límite Runtime/Engineer

- Runtime observa y explica sin ejecutar acciones;
- Engineer tiene catálogo cerrado y confirmación explícita;
- nada de shell arbitrario por defecto;
- MQTT permanece bloqueado;
- acciones, si alguna vez se habilitan, conservan evidencia antes/después, autorización expirable y rollback.

## 4. Gates específicos por familia

### Phase I

1. Recuperar el commit real del paquete y las pruebas.
2. Confirmar que sólo usa GET loopback y biblioteca estándar.
3. Verificar cero escrituras, MQTT y subprocess no declarados.
4. Comparar exactamente las doce reglas con el documento.
5. Evaluar si el snapshot puede adoptar el contrato local sin afirmar causalidad.

### NEXO-11 v0.1/v0.2

1. Separar `collectors/rules/engine` de persistencia, servidor y deploy.
2. Confirmar que JSON/JSONL nunca sustituyen ni modifican estado productivo.
3. Auditar `mode=ro`, `query_only` y manejo de locks/timeouts antes de cualquier lectura SQLite futura.
4. Excluir instaladores, backups y reinicios del componente Runtime.
5. Tratar estado systemd/Tailscale documentado como histórico hasta una observación autorizada.

### V3-06

1. Obtener el archivo por una vía autorizada y comprobar su hash.
2. Revisar estáticamente imports, shell, MQTT, acciones, confirmaciones y secretos antes de ejecutarlo.
3. Diseñar simulación cerrada y pruebas negativas.
4. No incorporarlo entero: decidir por capacidades después de caracterización.
5. Reservar toda ejecución de acciones para CEN-10 o fase expresamente autorizada.

### Visual

1. Localizar el código físico y la imagen original.
2. Confirmar que consume resultados y no duplica el motor.
3. Preservar `offline`, `stale`, `null` y procedencia de datos.
4. Mantener allowlist de rutas y loopback.

## 5. Pendientes de CEN-00 heredados

| Pendiente | Impacto | Gate de resolución |
|---|---|---|
| Reporte final Mac ausente | Arquitectura/estado incompletos | Incorporar original con hash y procedencia |
| Imagen visual ausente | Contrato visual parcial | Incorporar original sin sustituirlo por descripción |
| Fuente dedicada V3-06 ausente | Riesgo y límites no verificables | Caracterización estática aislada |
| Phase I sin commit verificable | Reproducibilidad incompleta | Recuperar commit y árbol fuente |
| Vigencia NEXO/runtime no observada | No se puede afirmar estado actual | Auditoría readonly separada y autorizada |

## 6. Stop rules

Detener la fase futura si:

- HEAD, branch, remote o fuente no coinciden con el gate autorizado;
- aparecen credenciales o datos productivos;
- una herramienta intenta escribir SQLite, publicar MQTT, controlar salidas o cambiar calibración/odómetro;
- se requiere SSH, reinicio, systemd, Tailscale o despliegue sin autorización literal;
- el componente mezcla observación y acción sin una frontera demostrable;
- la procedencia no permite distinguir original, copia y síntesis.

## 7. Próximo paso propuesto, no ejecutado

Preparar una autorización separada para CEN-02 que indique una sola familia, fuente exacta, entorno aislado, pruebas permitidas y stop rules. Hasta recibirla, el repositorio permanece en cierre documental CEN-01.

Mensaje de commit propuesto para una revisión futura autorizada:

`docs(centinela): complete CEN-01 component inventory`
