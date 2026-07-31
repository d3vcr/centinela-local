# CEN-00 — Invariantes de seguridad

Deben permanecer:

```text
physical_outputs_enabled=false
relay_outputs_enabled=false
remote_start_locked=true
```

CENTINELA LOCAL no puede arrancar la motocicleta, controlar relés, publicar
MQTT de control, modificar odómetro o calibraciones, escribir SQLite
productiva, cambiar punteros, reiniciar servicios, instalar, desplegar, cargar
firmware, cambiar red/Tailscale, revelar secretos ni actuar solo por texto de
un modelo.

En CEN-00 estos invariantes son política documental. Fases posteriores deberán
convertirlos en controles estructurales externos al modelo.
