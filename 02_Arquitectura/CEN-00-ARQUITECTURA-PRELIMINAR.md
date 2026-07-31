# CEN-00 — Arquitectura preliminar

Clasificación general: `PROPUESTO`.

## Plano NEXO

```text
ESP32/sensores
  -> transporte MQTT
  -> relay o broker autorizado
  -> ingesta
  -> SQLite oficial
  -> normalización
  -> API local
  -> Cockpit e interfaces
```

CENTINELA LOCAL no será una dependencia obligatoria de esta cadena.

## Plano de observación

```text
fuentes allowlisted
  -> centinela-observer
  -> centinela-tools
  -> centinela-policy
  -> centinela-core
  -> centinela-agent
  -> centinela-evidence
  -> API/interfaz/conversación
```

El agente interpreta resultados estructurados; no recibe shell general ni
autoridad directa.

## Plano de conocimiento

```text
documentación aprobada
  -> centinela-knowledge
  -> indexación controlada
  -> recuperación con procedencia
  -> explicación con evidencia
```

## Plano de memoria

La memoria futura debe distinguir hecho, evidencia histórica, hipótesis,
decisión, propuesta, prueba, certificación, experimento y dato supersedido.

## Plano de ingeniería

```text
repositorio autorizado
  -> lectura y análisis
  -> prueba local permitida
  -> propuesta
  -> revisión humana
  -> commit o PR autorizado
  -> despliegue externo a Centinela
```

## Propiedad y caída segura

Una caída de Centinela no puede interrumpir MQTT, ingesta, SQLite,
normalización, API, Cockpit ni servicios esenciales.
