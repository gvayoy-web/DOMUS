---
proyecto: PROJECT DOMUS
tipo: ola-migracion
actualizado: 2026-09-12
estado: aplicado_ola_3
---

# Ola 3 — migración SalidaDomus y diagrama final

Autoridad: [[46 - Plan maestro de consolidacion un costado]] (Fase E).
Olas previas: [[50 - Ola 1 buffers Jarvis GPIO12 y validacion por perfil]],
[[51 - Ola 2 cierre casa historica planos y sim]].

## 1. Migración mecánica (cero comportamiento)

Renombres puros en `casa_inteligente_v4.ino` y `domus_selftest.ino`:

| Antes | Ahora |
|---|---|
| `CANTIDAD_RELES` | `TOTAL_SALIDAS` |
| `PINES_RELES` | `PINES_SALIDAS` |
| `NOMBRES_RELES` | `NOMBRES_SALIDAS` |
| `SALIDA_ACTIVA_EN_LOW` / `RELE_ACTIVO_LOW` | `SALIDA_ACTIVA_EN_BAJO` |
| `PIN_RELE_*` | `PIN_SALIDA_*` |
| `estadoReles` | `estadoSalidas` |
| `propietarioReles` | `propietarioSalidas` |
| `encenderRele` | `solicitarSalida` |
| `apagarRele` | `desactivarSalida` |
| `verificarEstadoLogicoGpio` | `verificarNivelLogicoSalida` |
| `fallosVerificacionRele` | `fallosVerificacionSalida` |
| `nivelRele` (selftest) | `nivelSalida` |

`nivelSalida` se conserva (ya era neutro). Desviación honesta de la nota 46:
en vez de `pinMap.salidas` (estructura que llegará con los drivers FINAL) se
usa `PINES_SALIDAS`, para no inventar arquitectura antes del hardware.

Prueba: `test_relay_abstraction_is_gone` (cero restos) + compilación de los 5
perfiles CI con tamaños idénticos a la nota 34 → comportamiento intacto.
El contrato de cableado del validador (`PIN_SALIDA_*`) y los harness nativos
siguen el renombre; `planos/tests` intactos.

## 2. Diagramas: arquitectura general + guía final pin por pin

`visualizaciones/domus-arquitectura-feria.svg` (antes `domus-final-feria.svg`):
diagrama general con energía en 2 ramas y TBD explícitos. No es guía de montaje.
`visualizaciones/domus-final-guia-principiantes.svg`: guía autónoma pin por
pin (DHT orientado, LCD 4 hilos, LDR, botones, LED, S8050 + diodo, TP4056,
checklist) + recuadro NO CONECTAR TODAVÍA. Estado FINAL formal y sus puertas
en [[53 - Definicion formal de firmware final y puertas]].

## 3. Pendiente con puerta física (no software)

Driver (foto + chip + tabla), audio (pines sin duplicar), 21 códigos IR,
HIL/B01-B10, 1 h vigilada. Puertas en nota 46 fases D–F.

## Relaciones

- [[46 - Plan maestro de consolidacion un costado]]
- [[50 - Ola 1 buffers Jarvis GPIO12 y validacion por perfil]]
- [[51 - Ola 2 cierre casa historica planos y sim]]
