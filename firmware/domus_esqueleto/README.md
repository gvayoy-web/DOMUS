# DOMUS — esqueleto actual

Este sketch es literalmente `casa_inteligente_v4` compilado con el perfil 3
`BANCO_COMPLETO_S8050_IR`. No existe una segunda lógica de control.

Incluye sensores, LCD, botones, tres LED, receptor IR, automatización,
calibración, PARO, watchdog y la minibomba por el único S8050. Mantiene
bloqueados ventilador, DRV8833, MAX98306, parlante, fuente externa y audio.

Para conexiones y pruebas usa `../PRUEBA_HOY.md`. La implementación anterior
se conserva sin autoridad de montaje en `firmware/legacy/domus_esqueleto/`.
