# CEN-00 — Matriz de capacidades

| Clase | CEN-00 | Ejemplos |
|---|---|---|
| Permitida | Sí | Documentos, inventario, hashes, contradicciones, políticas |
| Futura read-only | No todavía | GET allowlisted, SQLite read-only, systemd/journal acotados |
| Restringida | No | Persistencia, ramas, parches, commits, modelos, Internet, SSH, instalaciones |
| Prohibida | Nunca | MQTT de control, relés, arranque, SQLite productiva, odómetro, firmware autónomo |

Excepción registrada: el usuario autorizó explícitamente una rama nueva para
este baseline documental. No autorizó commit, push, merge ni operación.

La voz o una respuesta generativa nunca sustituyen autorización estructurada.
