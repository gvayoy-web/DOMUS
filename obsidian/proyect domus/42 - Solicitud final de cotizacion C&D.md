---
proyecto: PROJECT DOMUS
tipo: solicitud-cotizacion
actualizado: 2026-09-10
estado: lista_para_enviar_sin_uv
proveedor: C&D Technologia Honduras
---

# Solicitud final de cotización C&D

Lista cerrada tras revisar inventario, alimentación, motores, audio, LCD y
montaje. No cotizar cable, estaño, pines macho, herramientas, sensores, ESP32,
LCD, motores, TP4056, resistencias, diodos, LEDs, switches de zona ni jumpers:
ya existen.

## Texto listo para enviar

> Buen día. Necesito cotización y confirmación de existencia de los siguientes
> componentes para un proyecto con ESP32-S3. Favor indicar precio por unidad,
> variante exacta y costo de envío a Choluteca:
>
> 1. 1 módulo controlador doble de motores DRV8833, compatible con señales
>    lógicas de 3.3 V.
> 2. 1 fuente/adaptador cerrado de 5 V DC y 5 A, entrada 100–240 V AC, con
>    protección contra corto/sobrecorriente y salida utilizable mediante
>    terminales de tornillo. No fuente abierta con 120 V expuestos.
> 3. 1 módulo amplificador I2S MAX98357A de 3 W.
> 4. 1 parlante de 4 ohm, 3 W.
> 5. 1 baquelita PCB perforada de 100×220 mm, oferta publicada a L120.
> 6. 1 paquete de cuatro borneras PCB de 2 pines, paso 5.08 mm
>    (si solo hay 2.54 mm, confirmar corriente/AWG: se usarían solo
>    para señales y la potencia iría soldada directo).
> 7. 1 portafusible aéreo 5×20 mm y 2 fusibles de retardo de 4 A.
> 8. 1 paquete de cinco capacitores electrolíticos de 1000 µF, 25 V, 105 °C.
> Cotizar aparte, sin incluir todavía: 1 integrado 74AHCT125/74HCT125 DIP.
>
> Aclaración: INMP441 innecesario (Jarvis va por IR CAR MP3 + frases fijas,
> sin mic/entrenamiento). Conversor I2C innecesario (LCD ya probado a 3.3 V).
> No agregar relés (ya tienes desnudo fuera del núcleo), microSD/DFPlayer
> (ya tienes DFPlayer), MOSFETs, cable, estaño ni headers.
>
> Para el DRV8833, agradeceré foto de ambas caras o enlace del modelo exacto y
> confirmación de la corriente continua recomendada por canal para esa placa.
> No agregar relés, microSD, DFPlayer, MOSFETs, cable, estaño ni headers.

## Compra y reservas

Los fusibles no se instalan en paralelo. Dos de los 1000 µF quedan instalados
cerca del DRV8833 y MAX98357A; los demás son repuesto. El LCD y su backpack ya
fueron comprobados a 3.3 V, por lo que no se compra conversor I2C. El
74AHCT/HCT125 solo se instala si la tira WS2812 trabaja a 5 V.

El TP4056 queda como pieza de banco ya disponible, no en la alimentación final.
Los switches ya existentes se usan como entradas GPIO de zona y no transportan
corriente de motores. La lista no incluye caja porque la geometría final ya
reserva alojamiento dentro de la maqueta; la PCB se eleva con separadores y se
mantiene lejos de agua.

## Precios publicados ya comprobados

| Parte | Precio visto |
|---|---:|
| DRV8833 | L90 |
| Fuente 5 V/5 A | variante en página desde L200; cotizar exacta |
| MAX98357A | L130 |
| Parlante 4 ohm/3 W | L90 |
| Baquelita 100×220 mm | L120 oferta |
| 4 borneras de 2 pines 5.08 mm | L45 |
| 1 portafusible | L15 estimado desde el paquete visto |
| 2 fusibles de vidrio | L20 si cada uno conserva L10 |
| 5 capacitores 1000 µF/25 V | L35 |

Subtotal estimado del núcleo sin 74AHCT/HCT125 ni envío, usando
L200 como referencia de fuente: **L745**. El total real lo cierra C&D. Los
termocontraíbles y el paquete separado de conectores DC fueron retirados por
decisión de Isaac.

## Iluminación suplementaria representada

No se compra lámpara UV ni sensor UV. El LDR disponible mide iluminación
ambiental y GPIO8 enciende dos LED azules y uno rojo mediante un S8050. Cada LED
lleva su propia resistencia de 330 ohm. Se rotula `ILUMINACIÓN SUPLEMENTARIA DE
CULTIVO`: es una representación visible roja/azul, no radiación ultravioleta ni
un sistema agrícola de potencia.

## Relaciones

- [[01 - Inventario confirmado]]
- [[41 - Compra nacional minima y banco de soldadura]]
