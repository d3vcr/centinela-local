# CEN-00 — Fuentes y procedencia

Fecha de incorporación: 2026-07-30

## Registro

| ID | Nombre normalizado | Origen | Clasificación | Rama/commit | Vigencia | Secretos |
|---|---|---|---|---|---|---|
| S00 | `CEN-00-CARTA-FUNDACIONAL.md` | Adjunto Codex `pasted-text.txt` | DOCUMENTADO / fundacional | No aplica | Vigente para CEN-00 | No detectados por patrones |
| S01 | `NEXO-V3-ROADMAP-REFERENCIA.md` | `docs/roadmap/NEXO-V3-ROADMAP.md` | DOCUMENTADO | `setup/nexo-v3-agent` / `3b56d11` | Baseline local; remota pendiente | No detectados por patrones |
| S02 | `NEXO-V3-SYSTEM-REFERENCIA.md` | `docs/architecture/NEXO-V3-SYSTEM.md` | DOCUMENTADO | `setup/nexo-v3-agent` / `3b56d11` | Baseline local; runtime pendiente | No detectados por patrones |
| S03 | `AGENTS-NEXO-V3-REFERENCIA.md` | `AGENTS.md` | DOCUMENTADO / política | `setup/nexo-v3-agent` / `3b56d11` | Vigente en commit de partida | No detectados por patrones |
| S04a | `PHASE_I_CENTINELA_READONLY.md` | worktree `nexo-phase-i-centinela` | HISTÓRICO | `claude/nexo-phase-i-centinela` / archivo intent-to-add | No certificado | No detectados por patrones |
| S04b | `PHASE_I_CENTINELA_LOCAL.md` | worktree `nexo-phase-i-centinela` | HISTÓRICO | `claude/nexo-phase-i-centinela` / archivo intent-to-add | No certificado | No detectados por patrones |
| S04c | `NEXO-CENTINELA-v0.1.md` | `docs/centinela/` | HISTÓRICO | `setup/nexo-v3-agent` / `3b56d11` | Histórica | No detectados por patrones |
| S04d | `NEXO-CENTINELA-v0.2.md` | `docs/centinela/` | HISTÓRICO | `setup/nexo-v3-agent` / `3b56d11` | Histórica | No detectados por patrones |
| S04e | `NEXO-CENTINELA-10A-IMPLEMENTACION-20260727-004013.md` | `docs/evidencia/` | HISTÓRICO | `setup/nexo-v3-agent` / `3b56d11` | Válida para su fecha | No detectados por patrones |
| S05 | `V3-06-ADMINISTRADOR-CENTINELA.md` | Síntesis de AGENTS, roadmap y hash local del script | PROPUESTO | CEN-00 | No sustituye fuente dedicada | No contiene el script |
| S06 | Informe final Mac Kubuntu | No localizado | FALTANTE | Desconocido | No determinable | Pendiente |
| S07 | Imagen original dashboard | No identificada | FALTANTE | Desconocido | No determinable | Pendiente |
| S08 | `ESTADO-NEXO-V2-V3.md` | Síntesis local y dos estados históricos | DOCUMENTADO / HISTÓRICO | CEN-00 | Runtime pendiente | Sin secretos copiados |

## Reglas de procedencia

- Ninguna copia histórica se declara canónica por similitud de nombre.
- Las fechas de copia del worktree no sustituyen la fecha del contenido o del
  commit.
- El manifiesto SHA-256 registra las copias incorporadas; no certifica su
  vigencia.
- El script `nexo_admin_centinela_v2.py` no fue copiado ni ejecutado. Solo se
  registró su existencia local, tamaño y hash como antecedente.
- Las capturas visuales locales son candidatas, no la imagen original pedida.

## Fuentes rechazadas como sustitutos

- `tests/visual/cockpit-*.png`: son capturas de prueba, no están identificadas
  como la referencia visual original.
- `docs/ux/wireframes/*.svg`: son wireframes, no la imagen original pedida.
- `docs/ESTADO_NEXO.md` y `docs/NEXO-ESTADO.md`: contienen estados fechados
  2026-06-27 y 2026-07-05 y se conservan como históricos, no como runtime
  vigente.
