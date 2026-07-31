# CEN-01 — Inventario verificable de componentes Centinela

**Estado:** `CEN-01_CERRADO_CON_PENDIENTES_DOCUMENTADOS`
**Fecha de corte:** 2026-07-31
**Repositorio inventariado:** `centinela-local`
**Commit documental revisado:** `3cf6df909401da9395cc897625768dce849b1f35`
**Alcance:** documentación local; sin ejecución de código histórico, sin acceso a Raspberry Pi y sin modificar NEXO.

## 1. Objetivo y criterio de evidencia

CEN-01 identifica las familias de componentes llamadas “Centinela”, separa lo que existe físicamente de lo descrito en documentos y registra qué puede evaluarse para reutilización. Este inventario no certifica operación actual ni autoriza integración.

Se usan cuatro niveles:

- **OBSERVADO_LOCAL:** archivo presente y leído en el commit de corte.
- **EVIDENCIA_HISTORICA:** hecho informado por un documento con fecha, rama o resultado histórico; no equivale a estado vigente.
- **DOCUMENTACION_SOLAMENTE:** diseño, requisito, síntesis o referencia sin fuente implementada incluida.
- **NO_VERIFICADO:** requiere código, runtime o fuente primaria ausente del repositorio.

Las decisiones de inventario son:

- `REUTILIZABLE`: evidencia suficiente para incorporación directa. Ningún componente obtiene esta clasificación en CEN-01.
- `REQUIERE_CARACTERIZACION`: candidato que debe revisarse y probarse aisladamente antes de decidir.
- `SOLO_REFERENCIA`: útil como antecedente, no como componente integrable.
- `DESCARTAR`: incompatibilidad demostrada. CEN-01 no descarta implementaciones sin examinar su fuente.

## 2. Resumen ejecutivo

El repositorio contiene una base documental CEN-00 y no contiene código ejecutable, paquetes Centinela ni binarios. Se distinguen cinco familias:

| Familia | Evidencia disponible | Estado en CEN-01 | Decisión |
|---|---|---|---|
| A. Phase I, evaluador local | Documentos históricos con módulos, API, reglas, pruebas y semántica de salida | `EVIDENCIA_HISTORICA`; fuente no incorporada | `REQUIERE_CARACTERIZACION` |
| B. NEXO-11, v0.1/v0.2 | Documentos históricos de daemon, persistencia separada, API, reglas y despliegue | `EVIDENCIA_HISTORICA`; operación vigente no observada | `REQUIERE_CARACTERIZACION` |
| C. Administrador V3-06 | Síntesis y requisitos; script externo no incluido | `DOCUMENTACION_SOLAMENTE` / fuente `NO_VERIFICADO` | `REQUIERE_CARACTERIZACION` |
| D. Visual / Orbital | Contrato de visualización e integración descrito; paquete independiente ausente | `DOCUMENTACION_SOLAMENTE` | `SOLO_REFERENCIA` hasta localizar fuente |
| E. Centinela Local nuevo | Carta, arquitectura, seguridad, interfaces, pruebas y roadmap propuestos | Baseline documental `OBSERVADO_LOCAL`; implementación ausente | Diseño rector, no componente ejecutable |

Conclusión: existe material suficiente para cerrar el inventario documental con pendientes explícitos, pero no para declarar un motor Centinela reutilizable, activo o certificado.

## 3. Familia A — NEXO Phase I, evaluador local

### 3.1 Componentes descritos

Los documentos históricos describen el paquete `apps/centinela/nexo_centinela/` con:

| Módulo | Responsabilidad documentada |
|---|---|
| `__init__.py` | Paquete |
| `__main__.py` | Entrada de módulo |
| `cli.py` | Interfaz de línea de comandos y códigos de salida |
| `client.py` | Cliente HTTP loopback, sólo GET |
| `engine.py` | Coordinación de evaluación |
| `models.py` | Modelos de datos |
| `rules.py` | Doce reglas deterministas |
| `snapshot.py` | Ensamble del snapshot observado |

El contrato histórico registra API en `127.0.0.1:8765`, acceso sólo GET y estos endpoints:

- `/api/v1/health`
- `/api/v1/live`
- `/api/v1/metrics`
- `/api/v1/gaps`
- `/api/v1/rejections?limit=200`
- `/api/v1/boot-observations?limit=200`
- `/api/v1/schema`

También documenta salida JSON por `stdout`, códigos 0/1/2/3, biblioteca estándar solamente y ausencia de escrituras a disco, SQLite, MQTT o estado persistente.

### 3.2 Pruebas y procedencia

Se referencian `test_cli.py`, `test_client.py`, `test_engine.py`, `test_rules.py`, `conftest.py` y un testkit. Los documentos de procedencia señalan un worktree `nexo-phase-i-centinela`, rama `claude/nexo-phase-i-centinela`, con archivos en estado intent-to-add y sin commit verificado. En CEN-01 no se ejecutaron esas pruebas ni se inspeccionó el código fuente original.

### 3.3 Evaluación

- Fortaleza documental: separación clara entre observación y acción; evaluación determinista; modo de una sola ejecución.
- Incertidumbre: no hay árbol fuente incorporado ni commit verificable del conjunto descrito.
- Compatibilidad potencial: alta con un Runtime local de sólo lectura, pero debe demostrarse mediante caracterización reproducible.
- Decisión: `REQUIERE_CARACTERIZACION`.

## 4. Familia B — NEXO-11 y evolución v0.1/v0.2

### 4.1 Componentes v0.1 descritos

La documentación registra los módulos `config.py`, `models.py`, `collectors.py`, `rules.py`, `engine.py`, `persistence.py`, `server.py` y `main.py`. Describe recolección desde API, systemd en modo informativo, estado Tailscale y archivos; catorce reglas; un servidor loopback `127.0.0.1:8090`; y exposición sólo GET hacia una integración Orbital en el puerto 8181.

La persistencia documentada está separada de SQLite productiva:

- `/var/lib/nexo/centinela/state.json`
- `/var/lib/nexo/centinela/events.jsonl`

El servicio histórico aparece como `deploy/systemd/nexo-centinela.service`, con ruta desplegada informada `/opt/nexo/apps/centinela`.

Un informe fechado 2026-07-27 registra el servicio como activo y habilitado, con resultado exitoso. Se conserva como evidencia histórica: CEN-01 no observó el runtime actual y no convierte ese registro en afirmación de vigencia.

### 4.2 Evolución v0.2 descrita

v0.2 añade cinco reglas documentadas:

- retraso del pipeline;
- normalizador detenido;
- ECU parcial;
- cadencia degradada;
- discrepancia de build del frontend.

También describe lectura SQLite mediante `mode=ro` y `PRAGMA query_only=ON`. Los documentos de despliegue incluyen backups, instalación y reinicios. Esas operaciones son herramientas de despliegue y no deben formar parte del observador Runtime de sólo lectura.

### 4.3 Pruebas históricas

Se informan Ruff aprobado, Mypy sobre nueve archivos fuente, Pytest con 22 pruebas y Vitest con 29 archivos/246 pruebas. Son resultados fechados y documentados, no reejecutados ni certificados por CEN-01.

### 4.4 Evaluación

- Fortaleza documental: mayor cobertura operacional y persistencia aislada.
- Incertidumbre: fuente física y estado vigente no incluidos; semántica de escrituras auxiliares por caracterizar.
- Riesgo: mezclar el observador con instaladores, backups o reinicios rompería el límite Runtime/Engineer.
- Decisión: `REQUIERE_CARACTERIZACION`, separando motor, persistencia auxiliar, servidor y herramientas operacionales.

## 5. Familia C — Administrador Centinela V3-06

La fuente dedicada de V3-06 no está incorporada. Una síntesis local referencia un archivo externo:

- ruta histórica informada: `C:\Users\edzab\Downloads\nexo_admin_centinela_v2.py`;
- tamaño informado: 52,811 bytes;
- SHA-256 informado: `8f2242116d36e113292713f7d2004db4503224be793d1a86928513efc1509820`.

El archivo no fue copiado, abierto, importado ni ejecutado durante CEN-01. Por ello, su comportamiento efectivo es `NO_VERIFICADO`.

Los requisitos V3-06 documentados exigen Ruff, Mypy, pruebas, modo sólo lectura predeterminado, catálogo cerrado de acciones, confirmación explícita, evidencia antes/después y transmisión MQTT bloqueada. CEN-10 añade simulación, expiración de autorización y rollback.

Decisión: `REQUIERE_CARACTERIZACION` en un entorno aislado futuro. No puede incorporarse como Runtime ni como Engineer basándose sólo en la síntesis.

## 6. Familia D — integración visual / Orbital

Los documentos describen un cliente/proxy con allowlist desde Orbital 8181 hacia Centinela 8090, visualización segura de estado offline y consumo de resultados. No se encontró en el commit un paquete físico independiente `centinela-visual` ni evidencia de un motor diagnóstico propio.

La interfaz visual debe conservarse como consumidor, no como fuente de diagnóstico. Decisión: `SOLO_REFERENCIA` hasta ubicar y caracterizar su código.

## 7. Familia E — baseline nuevo de Centinela Local

El commit de corte contiene 39 archivos documentales distribuidos en fundación, arquitectura, evidencia histórica, propuestas Runtime y Engineer, seguridad, interfaces, pruebas, roadmap e informes. No contiene código, dependencias, ejecutables ni binarios.

Los componentes Runtime, Engineer, sesión/memoria e interfaz están marcados como propuestos. Los archivos del reporte Mac y la referencia visual son placeholders: las fuentes originales siguen ausentes. Esta familia es el marco rector para futuras fases, no una implementación.

## 8. Matriz consolidada por capacidad

| Capacidad | Phase I | NEXO-11 v0.1/v0.2 | V3-06 | Visual | Baseline local |
|---|---|---|---|---|---|
| Observación HTTP loopback | Histórica, 8765 | Histórica, 8090 | No verificado | Consumidor documentado | Propuesta |
| Evaluación determinista | 12 reglas descritas | 14 + 5 reglas descritas | No verificado | No demostrada | Requisito |
| Persistencia auxiliar | No | JSON/JSONL histórica | No verificado | No demostrada | Propuesta separada |
| Lectura SQLite | No | v0.2, readonly documentado | No verificado | No demostrada | Sujeta a gate |
| Acciones administrativas | No | Sólo herramientas de despliegue separables | Catálogo requerido | No | Reservado a Engineer |
| MQTT de comandos | No | No atribuido al motor | Debe estar bloqueado | No | Prohibido por defecto |
| UI | JSON CLI | API consumida por Orbital | No verificado | Sí, como consumidor | Propuesta |
| Fuente incluida aquí | No | No | No | No | Sólo documentación |

### 8.1 Matriz consolidada de componentes y evidencias

Para evitar atribuir a un archivo propiedades no demostradas, cada registro conserva `NO_VERIFICADO` donde la fuente física o el runtime están ausentes.

#### CEN-COMP-001 — Evaluador Phase I

| Campo | Valor |
|---|---|
| ID | `CEN-COMP-001` |
| Nombre | `nexo_centinela` Phase I |
| Familia | A |
| Tipo | código descrito en documentación |
| Host | Dell documentado; operación actual no verificada |
| Repositorio | NEXO, referencia histórica; remoto no verificado |
| Rama | `claude/nexo-phase-i-centinela` documentada |
| Commit | `NO_VERIFICADO`; archivos informados intent-to-add |
| Ruta | `apps/centinela/nexo_centinela/` |
| Estado operativo | histórico |
| Certificación | no demostrada |
| Entradas | siete endpoints GET loopback en `127.0.0.1:8765` |
| Salidas | snapshot/diagnóstico JSON por stdout; exit 0/1/2/3 |
| Escrituras | ninguna documentada |
| Efectos laterales | ninguno documentado; fuente no inspeccionada |
| Pruebas | cuatro módulos de test, `conftest.py` y testkit referenciados; no ejecutados |
| Seguridad | GET-only, sin MQTT, SQLite, persistencia ni acciones según documento |
| Reutilización | pendiente de caracterización |
| Riesgo | medio |
| Evidencia | `03_Evidencia_Historica/CEN-00-FASE-I-CENTINELA-READONLY.md`; `CEN-00-FASE-I-CENTINELA-LOCAL.md` |

#### CEN-COMP-002 — Runtime Centinela v0.1

| Campo | Valor |
|---|---|
| ID | `CEN-COMP-002` |
| Nombre | Runtime Centinela NEXO-11 v0.1 |
| Familia | B |
| Tipo | código/servicio descrito en documentación |
| Host | Raspberry Pi histórica |
| Repositorio | NEXO documentado; fuente no incluida aquí |
| Rama | `setup/nexo-v3-agent` documentada para la evidencia |
| Commit | `3b56d11` documentado para la evidencia, no para runtime vigente |
| Ruta | `/opt/nexo/apps/centinela` documentada |
| Estado operativo | histórico; activo el 2026-07-27 según informe, hoy no verificado |
| Certificación | probada históricamente; no certificada en CEN-01 |
| Entradas | API, `systemctl show`, unidades fallidas, Tailscale y archivos |
| Salidas | API GET loopback 8090, estado y eventos |
| Escrituras | `state.json` y `events.jsonl` documentadas fuera de SQLite productiva |
| Efectos laterales | persistencia auxiliar confirmada por documento |
| Pruebas | Ruff, Mypy, 22 Pytest y 246 Vitest informados; no reejecutados |
| Seguridad | observador; debe excluir operación y despliegue |
| Reutilización | parcial/pending de caracterización |
| Riesgo | medio |
| Evidencia | `03_Evidencia_Historica/CEN-00-CENTINELA-V0.1.md`; evidencia 10A incorporada |

#### CEN-COMP-003 — Extensión Centinela v0.2

| Campo | Valor |
|---|---|
| ID | `CEN-COMP-003` |
| Nombre | Extensión de reglas y collectors v0.2 |
| Familia | B |
| Tipo | código documentado |
| Host | Raspberry Pi histórica |
| Repositorio | NEXO documentado; fuente no incluida aquí |
| Rama | `setup/nexo-v3-agent` documentada para la evidencia |
| Commit | `3b56d11` documentado para la evidencia |
| Ruta | `/opt/nexo/apps/centinela` documentada |
| Estado operativo | histórico/no verificado actualmente |
| Certificación | probada históricamente; certificación no demostrada |
| Entradas | runtime v0.1 y SQLite con `mode=ro`/`query_only` documentados |
| Salidas | cinco diagnósticos adicionales |
| Escrituras | persistencia auxiliar heredada; SQLite productiva readonly según documento |
| Efectos laterales | posibles si se mezcla con herramientas de deploy |
| Pruebas | resultados históricos incorporados; no ejecutados en CEN-01 |
| Seguridad | separar collectors readonly de backup, instalación y reinicios |
| Reutilización | parcial/pending de caracterización |
| Riesgo | alto |
| Evidencia | `03_Evidencia_Historica/CEN-00-CENTINELA-V0.2.md` |

#### CEN-COMP-004 — Servicio systemd histórico

| Campo | Valor |
|---|---|
| ID | `CEN-COMP-004` |
| Nombre | `nexo-centinela.service` |
| Familia | B |
| Tipo | servicio |
| Host | Raspberry Pi histórica |
| Repositorio | NEXO documentado |
| Rama | no verificada para el unit activo |
| Commit | no verificado para el unit activo |
| Ruta | `deploy/systemd/nexo-centinela.service` documentada |
| Estado operativo | histórico; activo/habilitado informado el 2026-07-27 |
| Certificación | no demostrada |
| Entradas | configuración y runtime Centinela |
| Salidas | proceso daemon/API 8090 |
| Escrituras | posibles por runtime y journald; no verificadas actualmente |
| Efectos laterales | ciclo de vida de servicio; reinicio fuera de alcance |
| Pruebas | estado histórico documentado |
| Seguridad | no inspeccionar ni modificar sin autorización SSH/systemd separada |
| Reutilización | pendiente |
| Riesgo | alto |
| Evidencia | documentos v0.1/v0.2 y evidencia 10A |

#### CEN-COMP-005 — Adaptador visual Orbital

| Campo | Valor |
|---|---|
| ID | `CEN-COMP-005` |
| Nombre | Integración visual Orbital–Centinela |
| Familia | D |
| Tipo | interfaz documentada |
| Host | Raspberry Pi histórica / navegador; no verificado |
| Repositorio | NEXO documentado; paquete independiente no localizado |
| Rama | no verificada para código visual |
| Commit | no verificado para código visual |
| Ruta | proxy Orbital 8181 → Centinela 8090; ruta fuente exacta no verificada |
| Estado operativo | histórico/documental |
| Certificación | no demostrada |
| Entradas | endpoints GET allowlisted de Centinela |
| Salidas | estado visible, incluido offline seguro |
| Escrituras | ninguna documentada |
| Efectos laterales | ninguno documentado |
| Pruebas | Vitest histórico agregado; atribución exacta no verificable aquí |
| Seguridad | consumidor GET; no convertir UI en motor o actuador |
| Reutilización | pendiente; sólo referencia actual |
| Riesgo | medio |
| Evidencia | documentos de arquitectura, interfaces y v0.1/v0.2 incorporados |

#### CEN-COMP-006 — Administrador V3-06

| Campo | Valor |
|---|---|
| ID | `CEN-COMP-006` |
| Nombre | `nexo_admin_centinela_v2.py` |
| Familia | C |
| Tipo | código externo referido |
| Host | Dell histórico según ruta; ejecución no verificada |
| Repositorio | no verificado |
| Rama | no verificada |
| Commit | no verificado |
| Ruta | `C:\Users\edzab\Downloads\nexo_admin_centinela_v2.py` informada |
| Estado operativo | no verificado |
| Certificación | no demostrada |
| Entradas | no verificadas |
| Salidas | consulta/actuación esperadas por requisitos, no verificadas |
| Escrituras | no verificadas |
| Efectos laterales | posibles acciones, shell y MQTT; requieren auditoría |
| Pruebas | Ruff, Mypy y pruebas son requisitos, no resultados confirmados |
| Seguridad | readonly por defecto, catálogo cerrado, confirmación y MQTT bloqueado requeridos |
| Reutilización | pendiente |
| Riesgo | crítico hasta caracterización |
| Evidencia | `03_Evidencia_Historica/CEN-00-V3-06-SINTESIS.md` |

#### CEN-COMP-007 — Runtime Centinela Local propuesto

| Campo | Valor |
|---|---|
| ID | `CEN-COMP-007` |
| Nombre | Centinela Runtime local |
| Familia | E |
| Tipo | documentación/diseño |
| Host | local propuesto; no asignado |
| Repositorio | `centinela-local` confirmado |
| Rama | `main` confirmada |
| Commit | baseline `3cf6df909401da9395cc897625768dce849b1f35` |
| Ruta | `04_Centinela_Runtime/` |
| Estado operativo | documental |
| Certificación | no demostrada |
| Entradas | fuentes readonly por definir y gatear |
| Salidas | observaciones/diagnósticos propuestos |
| Escrituras | ninguna implementación; presupuesto de recursos documentado |
| Efectos laterales | ninguno implementado |
| Pruebas | estrategia documental en `08_Pruebas/` |
| Seguridad | salidas físicas, MQTT, SQLite productiva y cambios operativos prohibidos |
| Reutilización | no aplica todavía |
| Riesgo | bajo como documento; no evaluable como software |
| Evidencia | `04_Centinela_Runtime/README.md`; alcance y presupuesto de recursos |

#### CEN-COMP-008 — Engineer Centinela Local propuesto

| Campo | Valor |
|---|---|
| ID | `CEN-COMP-008` |
| Nombre | Centinela Engineer local |
| Familia | E |
| Tipo | documentación/diseño |
| Host | local propuesto; no asignado |
| Repositorio | `centinela-local` confirmado |
| Rama | `main` confirmada |
| Commit | baseline `3cf6df909401da9395cc897625768dce849b1f35` |
| Ruta | `05_Centinela_Engineer/` |
| Estado operativo | documental |
| Certificación | no demostrada |
| Entradas | evidencia del Runtime y autorización futura |
| Salidas | propuestas/acciones controladas futuras |
| Escrituras | ninguna implementación presente |
| Efectos laterales | potenciales; sujetos a catálogo, confirmación y rollback |
| Pruebas | flujo de aprobación documentado; pruebas no implementadas |
| Seguridad | separación estricta del Runtime, sin MQTT ni shell por defecto |
| Reutilización | no aplica todavía |
| Riesgo | alto si se implementa sin gates |
| Evidencia | `05_Centinela_Engineer/README.md`; límites y flujo de aprobación |

#### CEN-COMP-009 — Contratos e interfaz local propuestos

| Campo | Valor |
|---|---|
| ID | `CEN-COMP-009` |
| Nombre | Contratos de interfaz Centinela Local |
| Familia | E |
| Tipo | documentación/interfaz |
| Host | no aplica |
| Repositorio | `centinela-local` confirmado |
| Rama | `main` confirmada |
| Commit | baseline `3cf6df909401da9395cc897625768dce849b1f35` |
| Ruta | `07_Interfaces/` |
| Estado operativo | documental |
| Certificación | no demostrada |
| Entradas | datos con procedencia, frescura y nulabilidad propuestas |
| Salidas | contratos/UI propuestos |
| Escrituras | ninguna |
| Efectos laterales | ninguno documentado |
| Pruebas | criterios documentales en `08_Pruebas/` |
| Seguridad | no ocultar offline/stale/null ni confundir UI con diagnóstico |
| Reutilización | parcial como contrato de diseño |
| Riesgo | bajo |
| Evidencia | `07_Interfaces/` y `08_Pruebas/` |

#### CEN-COMP-010 — Fuentes originales pendientes

| Campo | Valor |
|---|---|
| ID | `CEN-COMP-010` |
| Nombre | Reporte Mac e imagen de dashboard |
| Familia | E, con procedencia externa pendiente |
| Tipo | evidencia/placeholders |
| Host | Mac para reporte; no verificado para imagen |
| Repositorio | no verificado para originales |
| Rama | no aplica/no verificada |
| Commit | no verificado |
| Ruta | placeholders bajo `03_Evidencia_Historica/` |
| Estado operativo | documental; originales ausentes |
| Certificación | no demostrada |
| Entradas | referencias Markdown |
| Salidas | constancia de ausencia |
| Escrituras | ninguna |
| Efectos laterales | ninguno |
| Pruebas | no aplica |
| Seguridad | incorporar sólo originales con hash y procedencia |
| Reutilización | no hasta recuperar originales |
| Riesgo | medio por interpretación errónea |
| Evidencia | placeholders S06 y S07 documentados en CEN-00 |

## 9. Contradicciones y puntos de divergencia

1. Phase I es single-run, stateless y API-only; v0.1 se describe como daemon con servicio y persistencia auxiliar.
2. Phase I observa vía API; v0.2 incorpora lectura directa de SQLite en modo readonly.
3. v0.1 se llama read-only pero escribe estado y eventos propios. Para este proyecto, read-only debe significar “no mutar estado productivo”, no “cero escrituras”.
4. Los scripts v0.2 de backup, instalación y reinicio son operacionales; deben quedar fuera del observador.
5. Un evaluador determinista y un administrador con acciones son dominios distintos. Las acciones pertenecen a Engineer/CEN-10.
6. La persistencia operacional de eventos no debe confundirse con memoria de sesión ni con evidencia histórica.
7. La visualización consume conclusiones; no existe evidencia de que sea un motor diagnóstico.
8. Sin el script V3-06 no se puede verificar que respete el límite Runtime/Engineer ni que carezca de shell arbitrario.
9. La causalidad no está demostrada: Phase I la evita expresamente y las fuentes posteriores no están presentes.
10. Manejo de stale/offline está documentado, pero no implementado en este repositorio.

## 10. Resultado CEN-01

CEN-01 queda `CEN-01_CERRADO_CON_PENDIENTES_DOCUMENTADOS` porque el universo conocido fue clasificado y sus faltantes están registrados. El cierre no equivale a certificación, selección de implementación ni inicio de CEN-02.

Pendientes que pasan como gates, no como trabajo ejecutado:

- recuperar fuentes originales con ruta, commit y hash verificables;
- obtener el reporte Mac y la imagen visual originales;
- caracterizar Phase I, v0.1/v0.2, V3-06 y visual en entornos aislados;
- resolver explícitamente persistencia, SQLite, servicio y límites Runtime/Engineer;
- verificar vigencia remota y operacional antes de cualquier afirmación de estado actual.
