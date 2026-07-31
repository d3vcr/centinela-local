# NEXO Centinela v0.1

## Objetivo

Centinela es un observador determinista y exclusivamente readonly. Consolida
el estado de la API NEXO, ECU, GPS, servicios, Tailscale, seguridad y
almacenamiento sin controlar, reparar ni reiniciar componentes.

No publica MQTT, no conoce endpoints de control, no escribe SQLite, no cambia
el odómetro y no ejecuta acciones físicas.

## Arquitectura

```text
NEXO API 8080 ─┐
systemd readonly├─> collectors -> rules -> engine -> state/events
Tailscale status┘                            ├─> journal
                                             ├─> /var/lib/nexo/centinela
                                             └─> 127.0.0.1:8090

Orbital 8181 -> proxy GET allowlisted -> Centinela 8090
```

El código se divide en:

- `collectors.py`: adquisición readonly;
- `rules.py`: condiciones puras y umbrales;
- `engine.py`: histéresis, transiciones y estado consolidado;
- `persistence.py`: estado atómico y eventos acotados;
- `server.py`: API HTTP local GET-only;
- `main.py`: ciclo de sondeo y journal;
- `config.py` y `models.py`: configuración y contratos tipados.

## Fuentes

- `GET http://127.0.0.1:8080/health`
- `GET http://127.0.0.1:8080/live`
- `GET http://127.0.0.1:8080/odometer`
- `systemctl show`
- `systemctl --failed`
- `tailscale serve status`
- `ss -ltn`

El runtime se ejecuta como usuario `nexo`, sin sudo y sin capacidades Linux.

## Estado y severidades

Estados generales:

- `BOOTING`
- `HEALTHY`
- `DEGRADED`
- `ALERT`
- `OFFLINE`

Severidades:

- `INFO`
- `WARNING`
- `CRITICAL`

Cada observación mantiene `code`, `component`, `severity`, `active`,
`message`, `first_seen`, `last_seen`, `occurrences`, `evidence`,
`recoverable` y `source`.

ECU y GPS son componentes independientes. GPS offline no declara ECU offline
ni invalida su última muestra.

## Reglas v0.1

- `CENTINELA_API_UNREACHABLE`
- `CENTINELA_API_DEGRADED`
- `CENTINELA_SECURITY_INVARIANT_BROKEN`
- `CENTINELA_NEXO_SERVICE_DOWN`
- `CENTINELA_SERVICE_RESTARTING`
- `CENTINELA_ECU_STALE`
- `CENTINELA_ECU_OFFLINE`
- `CENTINELA_GPS_STALE`
- `CENTINELA_GPS_OFFLINE`
- `CENTINELA_SAMPLE_REGRESSION`
- `CENTINELA_TAILSCALE_TARGET_MISMATCH`
- `CENTINELA_LEGACY_REACTIVATED`
- `CENTINELA_BOOT_CHECK_FAILED`
- `CENTINELA_ODOMETER_REFERENCE_CHANGED`

El odómetro distinto de `10148.2 km` produce información observable, no una
alarma crítica, y nunca se modifica.

## Histéresis y eventos

Cada regla conserva contadores consecutivos de fallo y recuperación.

- API unreachable: activa tras 3 fallos y recupera tras 2 éxitos.
- Servicio down, ECU/GPS freshness y checks operativos: usan observaciones
  consecutivas.
- Seguridad: activación inmediata.
- Restarting: requiere al menos 3 reinicios nuevos en 10 minutos; un contador
  histórico no activa la regla.

Las transiciones posibles son `ACTIVATED`, `UPDATED` y `RECOVERED`. Una
condición repetida incrementa `occurrences`, pero no genera un evento idéntico
en cada ciclo.

## Persistencia

```text
/var/lib/nexo/centinela/state.json
/var/lib/nexo/centinela/events.jsonl
```

Los archivos usan UTF-8, modo `0600`, reemplazo atómico y un máximo
configurable de 500 eventos. Un archivo corrupto se ignora al arrancar y no
impide que el servicio reconstruya el estado mediante observaciones reales.

No se usa la base `/var/lib/nexo/db/nexo.sqlite3`.

## API local

Bind exclusivo: `127.0.0.1:8090`.

- `GET /health`
- `GET /state`
- `GET /events?limit=50`

El límite de eventos se restringe a `1..100`. Métodos de escritura devuelven
405. El puerto 8090 no se publica directamente por Tailscale.

## Integración Orbital

El servidor 8181 permite exclusivamente:

- `/api/centinela/health`
- `/api/centinela/state`
- `/api/centinela/events`

El navegador sondea `/api/centinela/state` de manera independiente. Si el
servicio no está disponible, conserva el dashboard y la telemetría ECU,
muestra `CENTINELA OFFLINE` y no desmonta componentes.

Portal, Cockpit/Street y Dashboard muestran el resumen usando componentes y
estilos existentes, sin botones ni controles.

## Systemd

Unidad: `deploy/systemd/nexo-centinela.service`.

- usuario/grupo `nexo`;
- loopback únicamente;
- `Restart=on-failure`;
- `NoNewPrivileges=true`;
- `PrivateTmp=true`;
- `ProtectSystem=strict`;
- `ProtectHome=true`;
- escritura limitada a `/var/lib/nexo/centinela`;
- `WantedBy=multi-user.target`.

## Despliegue y rollback

El despliegue valida el baseline, seguridad, servicios protegidos, legacy
retirado, SHA-256 y release frontend inmutable. Sólo habilita Centinela y
reinicia el frontend 8181 cuando instala su proxy.

El rollback detiene/deshabilita exclusivamente Centinela, restaura código,
unidad y frontend previos desde el backup y reinicia únicamente 8181.

## Limitaciones

Centinela v0.1 no implementa IA generativa, recomendaciones, reparación,
reinicios automáticos, comandos MQTT, control remoto, predicción, aprendizaje,
odómetro dinámico, alertas externas, firmware ni acciones sobre la
motocicleta.

Centinela observa, clasifica y alerta. No controla, no repara y no actúa
físicamente.
