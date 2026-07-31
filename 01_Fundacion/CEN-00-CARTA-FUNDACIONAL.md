# CENTINELA LOCAL — CEN-00

## Carta fundacional, alcance y baseline documental

Fecha de inicio: 30 de julio de 2026
Estado: `CEN-00_ABIERTO_CONTROLADO`
Naturaleza del trabajo: exclusivamente documental
Código productivo autorizado: ninguno
Acceso operativo autorizado: ninguno
Selección de modelo local: aplazada
Despliegue: prohibido durante CEN-00

## 1. Dictamen inicial

CENTINELA LOCAL se constituye como un subproyecto independiente del ecosistema NEXO/Motoguaraña.

Su finalidad es observar, interpretar y explicar el estado técnico del sistema sin convertirse en una vía de control de la motocicleta ni en un reemplazo prematuro de NEXO V2 o NEXO V3.

El proyecto preservará la concepción histórica de Centinela como evaluador determinista y read-only. Esa base se considerará antecedente técnico recuperable, no producto automáticamente certificado.

CENTINELA LOCAL evolucionará mediante dos dominios separados:

* `Centinela Runtime`, destinado a la observación y diagnóstico operativo ligero en la Raspberry Pi.
* `Centinela Engineer`, destinado a la asistencia de ingeniería, revisión y preparación de cambios desde la Dell y, posteriormente, desde la Mac histórica si esta queda certificada como estación secundaria.

CEN-00 no autoriza implementación, instalación, ejecución remota, selección de modelos, modificación de repositorios ni pruebas contra la motocicleta.

## 2. Carta fundacional

CENTINELA LOCAL existe para aumentar la comprensión, trazabilidad, mantenibilidad y seguridad del ecosistema NEXO.

Su misión es convertir evidencia técnica dispersa —telemetría, contratos, estados de servicios, registros, SQLite, API, documentación y pruebas— en diagnósticos comprensibles y verificables.

El sistema deberá favorecer:

* evidencia antes que inferencia;
* explicación antes que actuación;
* seguridad antes que autonomía;
* observación determinista antes que razonamiento generativo;
* cambios revisables antes que modificaciones automáticas;
* trazabilidad antes que conveniencia;
* funcionamiento local antes que dependencia permanente de Internet;
* separación estricta entre diagnóstico, desarrollo y administración.

Centinela no adquirirá autoridad por el hecho de usar un modelo de lenguaje. Toda capacidad dependerá de herramientas explícitas, contratos tipados y políticas externas al modelo.

La autonomía futura no significará libertad operativa. Significará capacidad de coordinar tareas previamente autorizadas dentro de límites comprobables.

## 3. Invariantes de seguridad

Deben permanecer permanentemente vigentes:

* `physical_outputs_enabled=false`
* `relay_outputs_enabled=false`
* `remote_start_locked=true`

CENTINELA LOCAL no podrá:

* arrancar la motocicleta;
* energizar o desenergizar relés;
* enviar comandos MQTT de control;
* modificar el odómetro;
* recalibrar combustible;
* recalibrar GPS;
* recalibrar RPM;
* recalibrar sensores;
* escribir en la SQLite productiva;
* cambiar punteros de normalización;
* reiniciar servicios;
* instalar paquetes;
* desplegar software;
* cargar firmware;
* cambiar configuraciones de red;
* modificar Tailscale;
* revelar secretos;
* actuar basándose únicamente en la respuesta de un modelo de lenguaje.

Estas restricciones deberán implementarse posteriormente como controles estructurales y no solamente como instrucciones escritas.

## 4. Definición de Centinela Runtime

Centinela Runtime será el componente ligero que podrá ejecutarse en la Raspberry Pi `motoguarana`.

Su función será observar y diagnosticar el runtime real de NEXO sin administrarlo.

Responsabilidades previstas:

* consultar endpoints locales autorizados;
* leer estados y propiedades de servicios;
* consultar registros dentro de límites definidos;
* examinar archivos explícitamente permitidos;
* realizar consultas read-only a SQLite;
* normalizar observaciones;
* ejecutar reglas deterministas;
* calcular estado general, cobertura y hallazgos;
* generar evidencia con fecha, origen y hash;
* exponer resultados a una interfaz local cuando CEN-05 lo autorice;
* continuar ofreciendo diagnóstico básico aunque no exista Internet.

Centinela Runtime no será:

* una estación de desarrollo;
* un reemplazo de la API NEXO;
* un nuevo normalizador;
* un escritor de telemetría;
* un cliente de control MQTT;
* un administrador general de Linux;
* un sistema de actualización;
* un reemplazo del firmware;
* el propietario de SQLite;
* el escritor del odómetro;
* el lugar principal para ejecutar modelos grandes.

Su presupuesto de CPU, memoria, almacenamiento y latencia se definirá después de medir el hardware y la carga real de la Pi. No se instalarán modelos ni frameworks antes de esa medición.

## 5. Definición de Centinela Engineer

Centinela Engineer será el componente de asistencia de ingeniería ejecutado inicialmente en la Dell.

Su misión será ayudar a comprender y desarrollar NEXO y Centinela sin obtener autoridad directa sobre el runtime productivo.

Responsabilidades futuras:

* examinar repositorios autorizados;
* comprender contratos y arquitectura;
* localizar regresiones;
* revisar código;
* relacionar fallos con cambios;
* ejecutar pruebas locales permitidas;
* preparar parches;
* generar documentación;
* comparar ramas y commits;
* verificar cambios contra políticas;
* preparar commits o solicitudes de revisión;
* integrarse con VS Code y herramientas como Codex CLI dentro de CEN-08.

Centinela Engineer no deberá:

* editar directamente `/opt/nexo`;
* usar la Pi como repositorio de desarrollo;
* desplegar por iniciativa propia;
* ejecutar comandos remotos con efectos;
* publicar MQTT;
* modificar SQLite productiva;
* instalar dependencias sin alcance aprobado;
* mezclar cambios de firmware, backend, frontend, infraestructura y seguridad;
* presentar un parche generado como cambio certificado;
* hacer commit, push o merge sin autorización correspondiente.

La Mac con Kubuntu permanecerá clasificada como estación histórica y laboratorio secundario hasta que su informe final de auditoría sea incorporado y revisado.

## 6. Límites respecto de NEXO V2

NEXO V2 es actualmente la referencia operativa e histórica.

Centinela podrá observarlo mediante superficies autorizadas, pero no apropiarse de sus responsabilidades.

NEXO V2 conservará, mientras siga operativo:

* recepción de telemetría;
* relay MQTT;
* ingesta;
* normalización;
* SQLite oficial;
* API local;
* servicios systemd;
* interfaces activas;
* referencia protegida del odómetro;
* controles físicos bloqueados.

Centinela no deberá:

* renombrar componentes V2;
* reemplazar servicios V2;
* copiar automáticamente su código;
* asumir que todos sus archivos son canónicos;
* confundir componentes legacy con arquitectura vigente;
* interpretar una función activa como función certificada;
* retirar V2 antes de que V3 alcance paridad demostrada.

## 7. Límites respecto de NEXO V3

NEXO V3 es la línea oficial de integración, recuperación y evolución.

Centinela no será una reescritura alternativa de NEXO V3 ni una rama informal dentro de él.

La relación será:

* NEXO V3 define contratos, servicios y superficies operativas.
* CENTINELA LOCAL consume esos contratos mediante interfaces autorizadas.
* Centinela puede detectar contradicciones o regresiones.
* Centinela puede preparar propuestas para NEXO V3.
* NEXO V3 conserva la responsabilidad sobre telemetría, almacenamiento, API, interfaces y despliegue.
* La incorporación de componentes Centinela a NEXO V3 requerirá una fase explícita y certificada.

La documentación actual confirma que V3 se rige por evidencia, cambios mínimos, rollback verificable, seguridad por defecto y certificación por fases.

## 8. Arquitectura preliminar

### 8.1 Plano de datos NEXO

La cadena operativa continúa siendo responsabilidad de NEXO:

ESP32 y sensores
→ transporte MQTT
→ relay o broker autorizado
→ ingesta
→ SQLite oficial
→ normalización
→ API local
→ Cockpit e interfaces

Centinela no se insertará como dependencia obligatoria dentro de esa cadena.

Una caída de Centinela no deberá interrumpir la telemetría, la API, SQLite, el Cockpit ni los servicios esenciales.

### 8.2 Plano de observación Centinela

Fuentes autorizadas
→ `centinela-observer`
→ `centinela-tools`
→ `centinela-policy`
→ `centinela-core`
→ `centinela-agent`
→ `centinela-evidence`
→ API, interfaz y conversación

### 8.3 Plano de conocimiento

Documentación aprobada
→ `centinela-knowledge`
→ indexación controlada
→ referencias con procedencia
→ recuperación de contexto
→ respuesta o diagnóstico con evidencia

### 8.4 Plano de memoria

Sesiones
→ incidentes
→ decisiones
→ evidencias
→ resultados certificados
→ `centinela-memory`

La memoria deberá distinguir obligatoriamente:

* hecho confirmado;
* evidencia histórica;
* hipótesis;
* decisión;
* propuesta;
* resultado de prueba;
* componente certificado;
* componente experimental;
* dato obsoleto o supersedido.

### 8.5 Plano de ingeniería

Repositorio autorizado
→ lectura y análisis
→ pruebas locales
→ propuesta de modificación
→ revisión humana
→ commit o pull request autorizado
→ despliegue externo a Centinela

### 8.6 Frontera de control

Las capacidades de actuación no existirán en las fases iniciales.

CEN-10 deberá introducir, como un subsistema separado:

* catálogo cerrado;
* parámetros validados;
* simulación previa;
* autorización explícita;
* evidencia antes y después;
* tiempo de expiración de la autorización;
* rollback;
* registro inmutable;
* denegación segura ante incertidumbre.

El agente conversacional nunca será por sí solo el mecanismo de autorización.

## 9. Módulos previstos

`centinela-core`: modelos de dominio, severidad, hallazgos, cobertura y estado general.

`centinela-observer`: adaptadores read-only para API, systemd, journal, archivos y SQLite.

`centinela-tools`: herramientas pequeñas, explícitas, tipadas y con resultados estructurados.

`centinela-policy`: autorización, invariantes, denegaciones y límites operativos.

`centinela-agent`: interpretación, planificación y coordinación, sin acceso directo al sistema.

`centinela-memory`: sesiones, decisiones, incidentes y contexto técnico.

`centinela-knowledge`: contratos, manuales, arquitectura y documentación aprobada.

`centinela-api`: interfaz local de consulta.

`centinela-ui`: conversación, diagnóstico y visualización integrada.

`centinela-evidence`: hashes, timestamps, procedencia y paquetes de evidencia.

`centinela-tests`: pruebas unitarias, de integración, políticas, seguridad, contratos y regresión.

`centinela-runtime`: distribución ligera para Raspberry Pi.

`centinela-engineer`: integración de desarrollo para Dell o estación certificada.

Estos nombres son límites funcionales preliminares, no autorización para crear paquetes o seleccionar frameworks durante CEN-00.

## 10. Matriz de capacidades

### Permitidas durante CEN-00

* leer la documentación adjunta;
* clasificar evidencia;
* crear documentos dentro del nuevo proyecto;
* producir inventarios;
* registrar contradicciones;
* generar hashes de archivos adjuntos;
* definir políticas;
* diseñar arquitectura preliminar;
* documentar riesgos;
* mantener un índice incremental;
* preparar criterios de pruebas futuras.

### Permitidas en futuras fases read-only, después de certificación

* HTTP GET contra endpoints allowlisted;
* consulta read-only de SQLite;
* lectura controlada de `systemd`;
* lectura limitada de journal;
* lectura de archivos allowlisted;
* verificación de puertos locales;
* generación de reportes;
* comparación de contratos;
* análisis local de repositorios;
* ejecución de pruebas locales sin efectos.

### Restringidas

Requieren fase independiente, política aprobada y autorización:

* persistencia de memoria;
* escritura en repositorios;
* creación de ramas;
* aplicación de parches;
* commits y push;
* uso de modelos locales;
* acceso a Internet;
* instalación de dependencias;
* lectura remota de la Pi;
* reinicio de procesos de laboratorio;
* creación de servicios Centinela;
* integración con voz;
* lectura de datos potencialmente sensibles;
* ejecución de herramientas administrativas en modo simulación.

### Prohibidas

* MQTT de control;
* activación de relés;
* arranque remoto;
* modificación de salidas físicas;
* escritura en SQLite productiva;
* cambio del odómetro;
* recalibración autónoma;
* modificación autónoma de firmware;
* despliegue autónomo;
* cambio autónomo de systemd;
* cambio autónomo de red o Tailscale;
* publicación de secretos;
* ejecución de archivos históricos sin revisión;
* uso de evidencia simulada como evidencia real;
* ocultamiento de fallos;
* autorización basada exclusivamente en texto generado por un modelo.

## 11. Información que debe recuperarse

### Identidad y procedencia

* nombre exacto de cada archivo;
* fecha;
* origen;
* rama o commit relacionado;
* clasificación;
* SHA-256;
* estado de vigencia;
* relación con V2, V3 o Centinela.

### Centinela histórico

* arquitectura de la antigua Fase I;
* operación local;
* endpoints consumidos;
* reglas deterministas;
* modelos de hallazgos;
* pruebas existentes;
* limitaciones;
* cambios posteriores hasta v0.2;
* servicio desplegado en la Pi;
* diferencias entre el prototipo original y el servicio actual.

La documentación histórica confirma que el diseño inicial rechazaba hosts y métodos no autorizados y consumía únicamente endpoints locales definidos.

### NEXO V2

* componentes activos;
* rutas reales;
* servicios y timers;
* API y puertos;
* SQLite oficial;
* escritor del odómetro;
* seguridad;
* fuentes de telemetría;
* componentes legacy;
* prototipos;
* riesgos operativos;
* elementos no reproducibles desde el repositorio.

### NEXO V3

* roadmap vigente;
* arquitectura vigente;
* AGENTS.md;
* contratos;
* estado de fases;
* componentes implementados;
* componentes únicamente documentados;
* pruebas;
* ramas, commits y releases relevantes;
* deuda técnica;
* requisitos V3-06.

### Equipos

Dell:

* sistema operativo;
* CPU;
* RAM;
* GPU;
* almacenamiento;
* herramientas de desarrollo;
* repositorios;
* entornos virtuales;
* limitaciones.

Raspberry Pi:

* modelo;
* arquitectura;
* RAM;
* almacenamiento;
* temperatura y carga típica;
* servicios;
* puertos;
* versiones de Python y Node;
* restricciones de recursos;
* dependencias ya presentes.

Mac con Kubuntu:

* hardware;
* almacenamiento;
* estado del sistema;
* versiones instaladas;
* repositorios encontrados;
* secretos o credenciales detectados sin revelar contenido;
* posibles roles futuros;
* limitaciones y riesgos.

## 12. Riesgos técnicos y de seguridad

### R01 — Confusión entre V2, NEXO-11 y V3

Impacto: decisiones basadas en una arquitectura inexistente.

Control: toda afirmación deberá indicar `OBSERVADO`, `DOCUMENTADO`, `HISTÓRICO`, `INFERIDO` o `PROPUESTO`.

### R02 — Convertir el prototipo histórico en producto sin auditoría

Impacto: arrastrar supuestos y contratos obsoletos.

Control: inventario CEN-01 y pruebas de caracterización antes de reutilizar código.

### R03 — Acceso excesivo del agente

Impacto: una instrucción o error de razonamiento podría afectar el sistema.

Control: herramientas allowlisted, sin shell general y política externa al modelo.

### R04 — Escalada indirecta mediante herramientas

Impacto: una herramienta aparentemente diagnóstica podría ejecutar efectos.

Control: separar ejecutables de consulta y acción; revisar dependencias y llamadas internas.

### R05 — Interpretación causal incorrecta

Impacto: presentar correlación como causa confirmada.

Control: separar observación, hipótesis y causa certificada.

### R06 — Telemetría stale interpretada como actual

Impacto: diagnósticos falsos.

Control: toda lectura debe incluir timestamp, edad, fuente y estado de frescura.

### R07 — Contaminación de memoria

Impacto: una hipótesis antigua puede reaparecer como hecho.

Control: procedencia, vigencia, supersesión y niveles de confianza.

### R08 — Exposición de secretos

Impacto: compromiso de GitHub, MQTT, SSH o red.

Control: detección y redacción; nunca incorporar secretos al conocimiento del agente.

### R09 — Saturación de la Raspberry Pi

Impacto: degradación de NEXO por modelos, indexación o consultas costosas.

Control: medición previa, límites de recursos y degradación segura.

### R10 — Deriva entre repositorio y runtime

Impacto: diagnosticar una versión distinta de la realmente desplegada.

Control: registrar commit, ruta, hash y unidad systemd de cada componente.

### R11 — Manipulación o pérdida de evidencia

Impacto: imposibilidad de reproducir un diagnóstico.

Control: manifiestos SHA-256, timestamps, origen y reportes inmutables.

### R12 — Dependencia prematura de un modelo específico

Impacto: arquitectura condicionada por hardware o proveedor no validado.

Control: contrato abstracto de modelo y selección aplazada hasta CEN-07.

### R13 — Voz interpretada como autorización

Impacto: acciones accidentales o ambiguas.

Control: la voz nunca sustituirá confirmación estructurada para acciones restringidas.

### R14 — Automatización administrativa prematura

Impacto: reinicios, despliegues o modificaciones no deseadas.

Control: no diseñar actuación operativa hasta certificar CEN-03 y CEN-04.

## 13. Roadmap CEN-00 a CEN-10

### CEN-00 — Fundación, contexto y límites

Entrada: esta carta y las ocho fuentes mínimas.

Salida: carta fundacional, definiciones, límites, arquitectura preliminar, matriz de capacidades, riesgos, roadmap, estructura documental y manifiesto de fuentes.

Pruebas y evidencia: revisión de enlaces, clasificación de afirmaciones, comprobación de duplicados, detección de secretos por nombres y hashes.

Rollback: eliminar únicamente los documentos nuevos de CEN-00.

Detención: falta de una fuente crítica, contradicción de seguridad o presencia de secretos sin sanear.

### CEN-01 — Inventario de Centinela existente

Entrada: CEN-00 cerrado y fuentes registradas.

Salida: inventario de código, documentación, pruebas, servicios, releases y prototipos.

Pruebas y evidencia: hashes, árbol acotado, historial Git y clasificación de cada componente.

Rollback: ninguno sobre runtime; solo revertir documentación de inventario.

Detención: repositorio incorrecto, worktree desconocido o archivo histórico riesgoso.

### CEN-02 — Contratos, modelos y arquitectura

Entrada: inventario aprobado.

Salida: contratos de observaciones, hallazgos, severidades, herramientas, políticas y evidencia.

Pruebas: esquemas, serialización, compatibilidad y pruebas negativas de autorización.

Rollback: volver al contrato documental anterior.

Detención: contrato que permita efectos implícitos o mezcle consulta con acción.

### CEN-03 — Observador read-only

Entrada: contratos aprobados y fuentes allowlisted.

Salida: adaptadores read-only sin razonamiento generativo.

Pruebas: GET-only, SQLite read-only, systemd read-only, límites de journal, timeouts y ausencia de escritura.

Evidencia: capturas reproducibles contra fixtures o entornos aislados.

Rollback: retirar el observador sin afectar NEXO.

Detención: cualquier escritura, dependencia circular o impacto sobre el runtime.

### CEN-04 — Motor determinista de diagnóstico

Entrada: observador certificado.

Salida: reglas, cobertura, severidad y estado general reproducibles.

Pruebas: unitarias, casos límite, regresión, freshness y ausencia de causalidad inventada.

Rollback: volver a la versión anterior del catálogo de reglas.

Detención: regla no explicable o sin evidencia concreta.

### CEN-05 — API e interfaz local

Entrada: motor determinista certificado.

Salida: API local de consulta e interfaz básica integrada sin controles físicos.

Pruebas: loopback, métodos no permitidos, autenticación local si corresponde, contratos y degradación segura.

Rollback: detener únicamente la interfaz Centinela.

Detención: exposición no autorizada o interferencia con puertos NEXO.

### CEN-06 — Conocimiento y memoria

Entrada: fuentes aprobadas y política de retención.

Salida: conocimiento indexado y memoria con procedencia, vigencia y supersesión.

Pruebas: recuperación correcta, aislamiento de sesiones, eliminación, redacción de secretos y no contaminación.

Rollback: reconstruir índices desde las fuentes originales.

Detención: imposibilidad de rastrear una afirmación hasta su fuente.

### CEN-07 — Conversación con modelo de lenguaje

Entrada: mediciones de hardware y diagnóstico determinista estable.

Salida: explicación conversacional que cite evidencia y use herramientas mediante política.

Pruebas: alucinaciones, prompt injection, denegaciones, falta de evidencia, desconexión de Internet y caída del modelo.

Rollback: desactivar el modelo y conservar el motor determinista.

Detención: el modelo evade políticas o presenta inferencias como hechos.

### CEN-08 — Centinela Engineer

Entrada: repositorio, permisos y flujo de revisión definidos.

Salida: asistencia de código, pruebas, parches y documentación sin despliegue autónomo.

Pruebas: repositorio limpio, límites de escritura, cambios mínimos, diff, pruebas selectivas y protección de secretos.

Rollback: descartar únicamente cambios generados y conservar evidencia.

Detención: cambio fuera de alcance, worktree sucio no atribuido o intento de acceso productivo.

### CEN-09 — Voz y experiencia de usuario

Entrada: conversación textual segura y hardware de audio medido.

Salida: entrada y salida de voz local para consultas.

Pruebas: ruido, palabras ambiguas, interrupciones, privacidad y ausencia de autorización por voz.

Rollback: volver a interfaz textual.

Detención: una frase pueda interpretarse como acción administrativa.

### CEN-10 — Administración controlada

Entrada: todas las fases read-only certificadas y catálogo formal aprobado.

Salida: conjunto mínimo de acciones administrativas cerradas y reversibles.

Pruebas: simulación, confirmación, expiración, parámetros inválidos, rollback, auditoría y denegación segura.

Evidencia: estado antes y después, identidad del autorizador, comando exacto, resultado y rollback.

Rollback: obligatorio por acción.

Detención: cualquier acción sin confirmación estructurada, evidencia previa o recuperación demostrada.

## 14. Regla global de entrada y salida

Ninguna fase puede comenzar sin:

* fase anterior cerrada;
* alcance definido;
* fuentes identificadas;
* riesgos aceptados;
* pruebas previstas;
* rollback definido;
* condiciones de detención registradas.

Ninguna fase puede cerrarse sin:

* pruebas aprobadas;
* evidencia;
* ausencia de cambios fuera del alcance;
* controles de seguridad intactos;
* resultado documentado;
* limitaciones declaradas;
* rollback verificable.

## 15. Estructura documental inicial

`CENTINELA LOCAL/`

`01_Fundacion/`

* `CEN-00-CARTA-FUNDACIONAL.md`
* `CEN-00-ALCANCE-Y-LIMITES.md`
* `CEN-00-ESTADO.md`
* `CEN-00-FUENTES-Y-PROCEDENCIA.md`

`02_Arquitectura/`

* `CEN-00-ARQUITECTURA-PRELIMINAR.md`
* `CEN-00-DOMINIOS-Y-FRONTERAS.md`
* `NEXO-V3-SYSTEM-REFERENCIA.md`

`03_Evidencia_Historica/`

* `INDEX.md`
* `MANIFEST-SHA256.md`
* `CENTINELA-FASE-I/`
* `NEXO-V2-V3/`
* `MAC-KUBUNTU/`
* `REFERENCIA-VISUAL/`

`04_Centinela_Runtime/`

* `README.md`
* `ALCANCE-READONLY.md`
* `PRESUPUESTO-DE-RECURSOS-PENDIENTE.md`

`05_Centinela_Engineer/`

* `README.md`
* `LIMITES-DE-REPOSITORIO.md`
* `FLUJO-DE-REVISION-PENDIENTE.md`

`06_Seguridad/`

* `CEN-00-INVARIANTES.md`
* `CEN-00-MATRIZ-DE-CAPACIDADES.md`
* `CEN-00-RIESGOS.md`
* `AGENTS-NEXO-V3-REFERENCIA.md`

`07_Interfaces/`

* `README.md`
* `REFERENCIA-DASHBOARD.png`
* `CRITERIOS-DE-INTEGRACION-PENDIENTES.md`

`08_Pruebas/`

* `CEN-00-ESTRATEGIA-DE-PRUEBAS.md`
* `CEN-00-CONDICIONES-DE-DETENCION.md`

`09_Roadmap/`

* `CEN-ROADMAP.md`
* `NEXO-V3-ROADMAP-REFERENCIA.md`

`10_Informes/`

* `CEN-00-INFORME-INICIAL.md`
* `ESTADO-NEXO-V2-V3.md`
* `V3-06-ADMINISTRADOR-CENTINELA.md`

No se crearán todavía carpetas de código, modelos, entornos virtuales, bases de datos, índices vectoriales, cachés ni paquetes de instalación.

## 16. Archivos mínimos que deben adjuntarse

Añadir solamente:

1. Roadmap vigente de NEXO V3.
2. Arquitectura vigente de NEXO V3.
3. `AGENTS.md` de NEXO V3.
4. Documentación de la antigua Fase I de Centinela.
5. Documentación V3-06 de integración del administrador Centinela.
6. Informe final de auditoría de la Mac con Kubuntu.
7. Imagen de referencia visual del dashboard.
8. Resumen vigente y fechado del estado de NEXO V2 y V3.

Para la antigua Fase I conviene conservar, si existen por separado:

* documento de arquitectura read-only;
* documento de operación local;
* referencia de las pruebas asociadas.

No adjuntar todavía:

* respaldos completos;
* SQLite;
* directorios de telemetría;
* repositorios completos;
* `node_modules`;
* entornos virtuales;
* builds;
* logs extensos;
* archivos de secretos;
* auditorías crudas de cientos de archivos;
* firmware histórico no seleccionado;
* ZIP completos sin manifiesto.

## 17. Registro mínimo por archivo

Cada archivo incorporado deberá registrar:

* nombre normalizado;
* nombre original;
* carpeta destino;
* fecha de incorporación;
* origen;
* SHA-256;
* clasificación;
* fase o versión relacionada;
* vigencia;
* contiene secretos: sí, no o pendiente;
* observaciones;
* documento que lo reemplaza, cuando corresponda.

## 18. Estado de CEN-00

Completado en borrador:

* carta fundacional;
* definición de Runtime;
* definición de Engineer;
* límites V2 y V3;
* arquitectura preliminar;
* matriz de capacidades;
* inventario requerido;
* riesgos;
* roadmap;
* estructura documental;
* lista mínima de fuentes.

Pendiente para cerrar CEN-00:

* incorporar físicamente las ocho fuentes;
* calcular y registrar sus hashes;
* verificar la arquitectura vigente completa;
* revisar el informe final de la Mac;
* registrar la imagen original;
* reconciliar contradicciones entre documentos;
* emitir el informe final `CEN-00_CERRADO`.

Hasta completar esos puntos, el estado oficial será:

`CEN-00_ABIERTO_CONTROLADO`

No se autoriza iniciar CEN-01.
