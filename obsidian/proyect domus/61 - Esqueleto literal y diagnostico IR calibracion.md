---
estado: vigente
fecha: 2026-09-13
autoridad: 59
---

# Esqueleto literal y diagnóstico IR/calibración

`firmware/domus_esqueleto/domus_esqueleto.ino` dejó de ser una implementación
paralela. Ahora define el perfil 3 `BANCO_COMPLETO_S8050_IR` e incluye
literalmente `../casa_inteligente_v4/casa_inteligente_v4.ino`.

El esqueleto tiene exactamente la lógica del producto limitada al hardware
disponible: sensores, LCD, botones, tres LED, IR y una bomba mediante S8050.
DRV8833, ventilador y audio siguen bloqueados. El código anterior pasó a
`firmware/legacy/domus_esqueleto/` sólo para regresión y no autoriza montaje.

## Diagnóstico avanzado seguro

`firmware/diagnosticos/domus_banco_integracion` ya no asume un DRV8833 ni pulsa
GPIO4/GPIO7. No configura ni escribe GPIO4-8. Usa LDR GPIO3, IR GPIO12, LCD
SCL13/SDA17, DHT11 GPIO14, suelo GPIO15 y nivel GPIO16.

Cada botón del mando imprime `PROTO`, `DIR`, `CMD` y `REPEAT`; `IR_LISTA`
entrega hasta 21 códigos únicos. `MUESTRA_SECO`, `MUESTRA_HUMEDO`,
`MUESTRA_OSCURO`, `MUESTRA_CLARO` y `MUESTRA_NIVEL` producen órdenes `CAL_*`
listas para copiar al firmware principal.

El diagnóstico no guarda NVS ni asigna acciones. Eso se hace en el producto
con `CAL_GUARDAR` e `IR_GRABAR_0` a `IR_GRABAR_20`. Tampoco prueba bomba,
ventilador, DRV8833, fuente, fusible ni audio.
