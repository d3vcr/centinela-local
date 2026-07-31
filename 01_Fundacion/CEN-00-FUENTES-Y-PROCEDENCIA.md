# CEN-00 — Fuentes y procedencia

Fecha de incorporación inicial: 2026-07-30

Fecha de reparación CEN-00R: 2026-07-31

## Registro

| ID | Nombre normalizado | Origen | Clasificación | Rama/commit | Vigencia | Secretos |
|---|---|---|---|---|---|---|
| S00 | `CEN-00-CARTA-FUNDACIONAL.md` | Adjunto Codex `pasted-text.txt` | DOCUMENTADO / fundacional | No aplica | Vigente para CEN-00 | No detectados por patrones |
| S01 | `NEXO-V3-ROADMAP-REFERENCIA.md` | `docs/roadmap/NEXO-V3-ROADMAP.md` | DOCUMENTADO | `setup/nexo-v3-agent` / `3b56d11` | Baseline local; remota pendiente | No detectados por patrones |
| S02 | `NEXO-V3-SYSTEM-REFERENCIA.md` | `docs/architecture/NEXO-V3-SYSTEM.md` | DOCUMENTADO | `setup/nexo-v3-agent` / `3b56d11` | Baseline local; runtime pendiente | No detectados por patrones |
| S03 | `AGENTS-NEXO-V3-REFERENCIA.md` | `AGENTS.md` | DOCUMENTADO / política | `setup/nexo-v3-agent` / `3b56d11` | Vigente en commit de partida | No detectados por patrones |
| S04a | `PHASE_I_CENTINELA_READONLY.md` | worktree `nexo-phase-i-centinela` | FUENTE_PRIMARIA / COPIA_VERIFICABLE / HISTÓRICO | `claude/nexo-phase-i-centinela` / HEAD `a526e48b6c1c23f98b3a5008795e73609d0f786a` / sin commit del archivo | No certificado | `SIN_INDICIOS` |
| S04b | `PHASE_I_CENTINELA_LOCAL.md` | worktree `nexo-phase-i-centinela` | FUENTE_PRIMARIA / COPIA_VERIFICABLE / HISTÓRICO | `claude/nexo-phase-i-centinela` / HEAD `a526e48b6c1c23f98b3a5008795e73609d0f786a` / sin commit del archivo | No certificado | `FALSO_POSITIVO` por mención Tailscale |
| S04c | `NEXO-CENTINELA-v0.1.md` | `docs/centinela/` | HISTÓRICO | `setup/nexo-v3-agent` / `3b56d11` | Histórica | No detectados por patrones |
| S04d | `NEXO-CENTINELA-v0.2.md` | `docs/centinela/` | HISTÓRICO | `setup/nexo-v3-agent` / `3b56d11` | Histórica | No detectados por patrones |
| S04e | `NEXO-CENTINELA-10A-IMPLEMENTACION-20260727-004013.md` | `docs/evidencia/` | HISTÓRICO | `setup/nexo-v3-agent` / `3b56d11` | Válida para su fecha | No detectados por patrones |
| S05 | registro V3-06 en `CEN-00R-INFORME-DE-RECUPERACION.md` | referencia exacta al script local y su sidecar | FUENTE_PRIMARIA_LOCAL / NO_VERIFICADO | sin repositorio, rama o commit verificados | Vigencia desconocida; reutilización bloqueada | `FALSO_POSITIVO`; no hay valores literales detectados |
| S06 | Informe final Mac Kubuntu | búsqueda local dirigida; único ZIP candidato rechazado | AUSENTE_NO_LOCALIZADA | Desconocido | No determinable | Posible; ZIP no abierto |
| S07 | `REFERENCIA-DASHBOARD-ORIGINAL.png` | colección local `Motoguarana_V13_Multimedia` | FUENTE_PRIMARIA | No aplica | Vigente como referencia histórica de diseño | `SIN_INDICIOS` por revisión visual |
| S08 | `ESTADO-NEXO-V2-V3.md` | repositorios locales y estados históricos | DOCUMENTADO / HISTÓRICO | V2 `bc6299a`; V3 `3b56d11` | Vigencia documental resuelta; runtime no verificado | `SIN_INDICIOS` / falsos positivos de política |

## Registros de reparación

- Phase I: las secciones 5 y 6 de `10_Informes/CEN-00R-INFORME-DE-RECUPERACION.md` conservan rama, HEAD, estado de índice, hashes y comparación de copias.
- V3-06: las secciones 5, 6 y 11 del informe CEN-00R conservan ruta, tamaño, fecha, hash, sidecar y resultado de escaneo sin copiar el script.
- Dashboard: `07_Interfaces/REFERENCIA-DASHBOARD-ORIGINAL.png`, SHA-256 `46428b13259b21311a268487446a32c63bd1a9b95dd8beadfc9b65c8d3ce8e88`.
- Mac: `NEXO_AUDITORIA_GLOBAL_2026-07-26.zip`, SHA-256 `6292ebaa0039d4977f389326434276d5939cd7b8850f2828fa82af243c08b057`, fue registrado pero no abierto ni incorporado.
- NEXO V3: la arquitectura fuente tiene SHA-256 raw `cd008743865a285124e1154942b672ed37dbd113f9022329f30a2a1916315ba2`; la copia LF tiene SHA-256 `801d56e3a40b4f6a3fd3526e656db48b76824df197374a19e5cae426d906ed6a`. El contenido es idéntico al normalizar CRLF/LF.

## Reglas de procedencia

- Ninguna copia histórica se declara canónica por similitud de nombre.
- Las fechas de copia del worktree no sustituyen la fecha del contenido o del
  commit.
- El manifiesto SHA-256 registra las copias incorporadas; no certifica su
  vigencia.
- El script `nexo_admin_centinela_v2.py` no fue copiado ni ejecutado. Solo se
  registró su existencia local, tamaño y hash como antecedente.
- Las capturas visuales locales son candidatas, no la imagen original pedida.

La última regla queda supersedida únicamente para `07_ejemplo_del_tablero_a_desarrollar.png`, identificado en CEN-00R por nombre, contexto de colección y revisión visual como la referencia original de diseño. Las capturas `tests/visual/*` y `preview-screenshot.png` continúan rechazadas como sustitutos.

## Fuentes rechazadas como sustitutos

- `tests/visual/cockpit-*.png`: son capturas de prueba, no están identificadas
  como la referencia visual original.
- `docs/ux/wireframes/*.svg`: son wireframes, no la imagen original pedida.
- `docs/ESTADO_NEXO.md` y `docs/NEXO-ESTADO.md`: contienen estados fechados
  2026-06-27 y 2026-07-05 y se conservan como históricos, no como runtime
  vigente.
