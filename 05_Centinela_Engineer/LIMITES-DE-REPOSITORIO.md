# Centinela Engineer — límites de repositorio

- Verificar ruta, worktree, rama, HEAD, remotos y estado antes de escribir.
- No editar `/opt/nexo` ni usar la Pi como repositorio de desarrollo.
- No mezclar firmware, backend, frontend, SQLite, systemd y red.
- No modificar cambios previos no atribuidos.
- Preparar diff mínimo, pruebas y rollback.
- No crear commit, push, PR, merge ni despliegue sin autorización específica.
- Detectar y redactar secretos; nunca incorporarlos a memoria o evidencia.
- Un parche generado es `PROPUESTO` hasta revisión y prueba.

La rama CEN-00 fue creada en un worktree aislado porque el worktree original
estaba sucio.
