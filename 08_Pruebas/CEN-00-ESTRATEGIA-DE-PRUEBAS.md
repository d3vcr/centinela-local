# CEN-00 — Estrategia de pruebas

## Pruebas documentales

1. Verificar que todos los enlaces relativos resuelvan.
2. Confirmar que cada fuente incorporada tenga SHA-256.
3. Comparar hash origen/destino de copias literales.
4. Detectar nombres duplicados y hashes duplicados.
5. Buscar patrones de secretos sin imprimir valores.
6. Verificar que no existan código, bases, modelos, cachés o binarios no
   autorizados en `CENTINELA LOCAL/`.
7. Confirmar etiquetas de procedencia y vigencia.
8. Revisar que `CEN-00_ABIERTO_CONTROLADO` sea consistente.

No se ejecutan pruebas de código, red, API, SQLite o runtime.

## Evidencia de salida

- `MANIFEST-SHA256.md`;
- diff limitado a `CENTINELA LOCAL/`;
- `git status`;
- informe inicial;
- lista de gates pendientes;
- rollback exacto.
