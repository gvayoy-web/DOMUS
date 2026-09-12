---
proyecto: PROJECT DOMUS
tipo: entrega-subagentes
actualizado: 2026-09-12
estado: integrado_verificado
---

# Integración: LCD final + backends + movimiento 1

Trabajo de dos subagentes especializados en worktrees aislados
(`task/lcd-final`, `task/driver-backends`), integrados por cherry-pick
(`82e63b9`, `1628a44`). Esqueleto congelado intacto.

## LCD final (`domus_pantalla.h`, clase `PantallaFinal`)

Splash no bloqueante, 5 vistas (temp/hum, suelo/nivel, luz/PIR, 5 salidas
`ON/OFF/AUTO/BLOQ/ERR`, emergencia prioritaria), campos `%-16.16s`, iconos
CGRAM, sombra `char[2][17]` con escritura diferencial, `clear()` solo en
`begin`/cambio de vista (2 ocurrencias), cero `delay()`, `ERR` ante sensor
inválido, LCD muerto = resto sigue. Desviación aceptada: MODO conmuta sala y
avanza vista en la misma pulsación (conserva lógica de control); truncados
`C:AUT` posibles en línea saturada (legibles, sin restos).

## Backends (`domus_drivers.h`)

`BackendMotor {NINGUNO, DRV8833, MX1508}`, `-DDOMUS_DRIVER=0/1/2` (default 0),
`static_assert` de rango, descriptores sin GPIO, `driverMotoresAplicar`
seguro (false). Compilaciones: 0/1/2 PASS (415562/415654/415654 B), 3 FAIL por
assert. `test_driver_backends.py` 7/7.

## Movimiento 1 (plan 54)

`hardware/` ← `plano_tecnico_domus.pdf`, `project_domus.mtl`,
`verificacion_geometria_v4.json` (los presentes en árbol; resto borrado por el
propietario, sin tocar). Enlaces `GUIA_MONTAJE.md` actualizados en el mismo
commit. Validadores verdes tras el movimiento.

## Relaciones

- [[54 - Plan de orden del repositorio]]
- [[56 - Orden fase 1 no destructiva]]
- [[53 - Definicion formal de firmware final y puertas]]
