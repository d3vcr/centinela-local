# Centinela Runtime — alcance read-only

## Futuro permitido después de certificación

- HTTP GET contra endpoints exactos allowlisted;
- consultas SQLite abiertas explícitamente en modo read-only;
- lectura acotada de propiedades systemd y journal;
- lectura de archivos exactos allowlisted;
- normalización de observaciones y reglas deterministas;
- evidencia con timestamp, fuente y hash.

## No permitido

- escritura en SQLite o archivos productivos;
- MQTT;
- restart, enable, disable o cambios systemd;
- instalación, actualización o despliegue;
- red, Tailscale, firmware, calibración, odómetro o salidas físicas;
- shell general accesible al modelo.

Toda ausencia de señal debe conservarse como `unknown`, `stale`, `offline` o
`SIN SEÑAL`, nunca como cero inventado.
