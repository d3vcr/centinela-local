# CEN-01 — Procedencia y cadena de evidencia

**Estado:** `CEN-01_CERRADO_CON_PENDIENTES_DOCUMENTADOS`
**Corte:** 2026-07-31
**Commit examinado:** `3cf6df909401da9395cc897625768dce849b1f35`

## 1. Regla de procedencia

Cada afirmación debe distinguir entre archivo presente, descripción histórica, síntesis y fuente ausente. Un hash confirma identidad de bytes; no confirma vigencia, comportamiento ni certificación. Un resultado histórico de pruebas no se presenta como prueba ejecutada durante CEN-01.

## 2. Fuentes primarias y estado

| ID | Fuente registrada en CEN-00 | Identidad / procedencia documentada | Estado CEN-01 |
|---|---|---|---|
| S01 | Roadmap NEXO V3 | rama `setup/nexo-v3-agent`, commit `3b56d11`, SHA-256 `d26c56bc0806469a611d3d46eaa684eae9176494e5d9e8739a474c90ab0f29fe` | Incorporada; vigencia remota no verificada |
| S02 | Arquitectura NEXO V3 | misma rama/commit, SHA-256 `801d56e3a40b4f6a3fd3526e656db48b76824df197374a19e5cae426d906ed6a` | Incorporada; runtime no verificado |
| S03 | `AGENTS.md` NEXO V3 | misma rama/commit, SHA-256 `228e0cc29e23409a977d7cff5e79ab9fe0190da1258693e32241cb747d64ac25` | Incorporada como regla histórica |
| S04a | Phase I readonly | worktree/rama informados; SHA-256 `4bba876fb036318ec3d4e1b0413db9d0e231d1ee8c90b70953d38a85a08424e7` | Archivo descrito como intent-to-add; commit no verificado |
| S04b | Phase I local | misma procedencia; SHA-256 `6f80241dcc504e63de735420be8964cfddc1a3e43940666e8b1c063a7e5dbe78` | Archivo descrito como intent-to-add; commit no verificado |
| S04c | Centinela v0.1 | rama `setup/nexo-v3-agent`, commit `3b56d11`, SHA-256 `f2f194c3959964c8dbecce65bae247d10606299dd59546e11b88be2118440024` | Evidencia histórica incorporada |
| S04d | Centinela v0.2 | misma rama/commit, SHA-256 `b1af0982dd43e31bab2f85385b02af4fa1cba432348cf48e06e919231f740d8f` | Evidencia histórica incorporada |
| S04e | Evidencia de implementación 10A | misma rama/commit, SHA-256 `21bc903bed20d135d8bb127565a0eacf6a0c95e2a2d318a614b6316147e2cc23` | Resultado histórico, no reejecutado |
| S05 | Síntesis V3-06 | SHA-256 `e46693e107256c10b77f820396658c4c99829389fd9b6bb0ad9c96acf0076793` | Síntesis; fuente dedicada ausente |
| S06 | Auditoría final Mac | placeholder SHA-256 `472236211a0a01f5d75dd8f7035b599d2edaf7ba2d166eaeefcd551e8bdd8efb` | Fuente original ausente |
| S07 | Referencia visual | placeholder SHA-256 `abac818dabee2ea2f5a291bfe19c041a7a14707d64932908bbde34408e707ec1` | Imagen original ausente |
| S08 | Síntesis de estado NEXO V2/V3 | SHA-256 `48456415286281d98da0133f02d9662ee7d16481343cfe4d091242e8eac43c1f` | Síntesis local; vigencia runtime no verificada |

La carta fundacional incorporada tiene SHA-256 `eaa982b35d4df7b7cedacb8f8b4277d3725209156b33ab4f67d70f27bde78f2c`.

## 3. Evidencia por familia

### A. Phase I

- **Se puede afirmar:** los documentos describen ocho módulos, siete rutas GET loopback, doce reglas, JSON por stdout, códigos 0/1/2/3 y ausencia intencional de escrituras/MQTT.
- **No se puede afirmar:** que el árbol fuente esté comprometido, que las pruebas pasen hoy o que sea idéntico a un artefacto desplegado.
- **Brecha:** falta commit fuente verificable y caracterización independiente.

### B. NEXO-11 v0.1/v0.2

- **Se puede afirmar:** documentos fechados describen ocho módulos, servicio, API 8090, persistencia JSON/JSONL, reglas, lectura SQLite readonly en v0.2 y resultados históricos de pruebas.
- **No se puede afirmar:** servicio activo hoy, correspondencia exacta entre documentación y artefacto actual, o aptitud directa para reutilización.
- **Brecha:** código fuente y runtime actual no observados.

### C. V3-06

- **Se puede afirmar:** la síntesis registra requisitos y la identidad informada de un script externo de 52,811 bytes, SHA-256 `8f2242116d36e113292713f7d2004db4503224be793d1a86928513efc1509820`.
- **No se puede afirmar:** contenido, seguridad, imports, acciones, calidad ni conformidad del script.
- **Brecha:** fuente dedicada ausente.

### D. Visual

- **Se puede afirmar:** existe documentación de integración Orbital 8181 → Centinela 8090 y presentación segura de offline.
- **No se puede afirmar:** existencia de un paquete independiente o motor diagnóstico visual.
- **Brecha:** código y captura original ausentes.

### E. Centinela Local

- **Se puede afirmar:** el commit raíz contiene 39 archivos documentales; el manifiesto contiene 38 entradas y coincide con los blobs de HEAD, excluyéndose a sí mismo; no hay binarios ni blobs duplicados.
- **No se puede afirmar:** existencia de Runtime, Engineer o UI implementados.
- **Brecha:** las implementaciones están deliberadamente fuera de CEN-00/CEN-01.

## 4. Validación del commit documental

El commit raíz fue inspeccionado con mecanismos compatibles con root commits. Los 39 archivos aparecen como adiciones. El manifiesto de hashes coincide en sus 38 entradas contra los blobs de HEAD y no incluye su propio hash.

`git diff-tree --root --check -r HEAD` produjo diagnósticos exclusivamente en `01_Fundacion/CEN-00-CARTA-FUNDACIONAL.md`. La causa documentada es la preservación intencional CRLF byte por byte mediante `.gitattributes`; no se observó la misma clase de hallazgo en los demás archivos.

Una búsqueda textual básica de patrones sensibles sobre HEAD produjo referencias de políticas y negaciones, sin candidatos de credenciales. Este resultado es un control limitado y no demuestra ausencia absoluta de secretos.

## 5. Límites de esta cadena

- No se consultaron remotos para probar vigencia de las fuentes NEXO.
- No se abrió conexión SSH ni se inspeccionó Raspberry Pi.
- No se ejecutó, importó ni probó código histórico.
- No se instalaron dependencias.
- No se validó la identidad de fuentes ausentes contra sus hashes informados.
- No se transformaron resultados históricos en evidencia actual.

## 6. Requisitos para elevar confianza

Una fuente sólo puede pasar de histórica/documental a candidata caracterizada si se obtiene de forma controlada con ruta, branch, commit, hash, licencia/dependencias, inventario de archivos, pruebas aisladas y revisión de efectos laterales. La observación de runtime requiere autorización separada y nunca se infiere del estado documental.
