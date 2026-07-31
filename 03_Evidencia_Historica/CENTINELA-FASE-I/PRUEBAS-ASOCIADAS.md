# Fase I — Referencia de pruebas asociadas

Clasificación: `OBSERVADO` en el worktree histórico,
`NO_EJECUTADO` durante CEN-00.

Origen:
`C:\Users\edzab\Documents\NEXO\nexo-phase-i-centinela\tests\centinela`

Archivos observados:

- `centinela_testkit.py`
- `conftest.py`
- `test_centinela_cli.py`
- `test_centinela_client.py`
- `test_centinela_engine.py`
- `test_centinela_rules.py`

También se observaron los módulos históricos bajo
`apps/centinela/nexo_centinela/`.

No se copiaron ni ejecutaron archivos Python. Los archivos aparecen como
`intent-to-add` sin commit en el worktree histórico, por lo que una revisión
futura debe:

1. confirmar su autoría y commit de destino;
2. calcular hashes de código y pruebas;
3. revisar que el cliente sea GET-only y loopback-only;
4. ejecutar caracterización en un entorno local aislado;
5. comparar el prototipo con `NEXO-CENTINELA-v0.1` y `v0.2`.
