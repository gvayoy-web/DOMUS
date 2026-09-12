---
proyecto: PROJECT DOMUS
tipo: definicion-firmware-final
actualizado: 2026-09-12
estado: vigente_definicion
---

# Firmware final: definición formal y puertas

Resuelve la contradicción “histórico y final a la vez”: `casa_inteligente_v4`
no es ninguno de los dos. Estados oficiales:

| Estado | Firmware | Condición |
|---|---|---|
| `BANCO` (vigente) | `domus_esqueleto`, perfil `ALFA_UN_COSTADO_SIN_IR` (+ `ALFA_BOMBA_1` / `ALFA_VENTILADOR_1` vigilados) | Siempre compilable y testeable sin compras |
| `CANDIDATO` | `casa_inteligente_v4` migrada a SalidaDomus | Reglas preservadas, sin drivers/IR/audio; prohibido presentarla como final |
| `FINAL` | `casa_inteligente_v4` + drivers/IR/audio | Solo cuando TODAS las puertas estén en PASS medido |

## Puertas a FINAL (todas con evidencia, ninguna por fecha)

| # | Puerta | Dueño | Evidencia |
|---|---|---|---|
| F1 | Driver identificado | Isaac | Foto ambas caras + referencia del chip + tabla de verdad medida |
| F2 | Fuente confirmada | Isaac | 3 A o 5 A con caída/corriente/temperatura bajo bomba+ventilador+audio |
| F3 | Mapa GPIO FINAL sin colisiones | Empleado | `funcionesActivasSinAlias()` + matriz compilable extendida en verde |
| F4 | Tabla 21 códigos IR del mando real | Isaac + empleado | `IR LISTA` registrada, 0 falsos por desconocidas/repeticiones |
| F5 | Audio sin duplicar pines | Empleado | MAX98357A en pines libres + MUTE sin bloquear seguridad |
| F6 | HIL por perfil (sensores, bomba, vent, IR) | Isaac + empleado | B01-B10 + 10 bloqueos nivel + 10 timeouts + 1 h vigilada |
| F7 | `validate_project.py` + CI en verde | Empleado | Incluye matriz y sim del esqueleto |

## Reglas inamovibles

1. Ningún TBD se cablea sin su puerta (nota 46 fases D–F).
2. `PERFIL_PRUEBA` diagnosticado debe describir el binario real.
3. IR/audio/LCD nunca bloquean seguridad, PARO ni rearme.
4. Sin F1–F7 en PASS, el estado sigue siendo `BANCO`/`CANDIDATO`.

## Relaciones

- [[46 - Plan maestro de consolidacion un costado]]
- [[50 - Ola 1 buffers Jarvis GPIO12 y validacion por perfil]]
- [[51 - Ola 2 cierre casa historica planos y sim]]
- [[52 - Ola 3 migracion SalidaDomus y diagrama final]]
