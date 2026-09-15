---
proyecto: PROJECT DOMUS
tipo: compras-verificadas
actualizado: 2026-09-09
estado: historico_cotizacion
moneda: HNL
---

# Compra nacional mínima y banco de soldadura

> [!DANGER]
> COTIZACIÓN HISTÓRICA. No representa exactamente la compra realizada y no
> autoriza conexiones. Ver [[63 - Auditoria total de Obsidian y estado real]].

> [!IMPORTANT]
> La cotización vigente cambió la fuente candidata a 5 V/5 A y eliminó toda
> compra UV. La lista cerrada está en [[42 - Solicitud final de cotizacion C&D]]
> y el montaje completo en [[43 - Manual final completo PROJECT DOMUS]].

Precios consultados el 09-09-2026. Confirmar existencia, variante y envío a
Choluteca antes de pagar. El inventario de [[01 - Inventario confirmado]] manda:
no se vuelve a comprar cable, resistencias, 1N4007, sensores, LCD, bomba, motor,
buzzer, ESP32, TP4056, protoboard ni jumpers ya disponibles.

## Compra funcional

| Prioridad | Pieza | Cant. | Tienda/precio | Razón |
|---|---|---:|---:|---|
| 1 | DRV8833, controlador doble de motores | 1 | C&D, L90 | Sustituye dos MOSFET; un canal para bomba y otro para ventilador. Comprar sujeto a medir que cada carga quede dentro de su corriente real. |
| 1 | Fuente cerrada 5 V/3 A | 1 | C&D, desde L248 | Alimentación común final. Confirmar el precio de la variante USB-C con switch. |
| 1 | Baquelita perforada 100×220 mm, oferta vista por Isaac | 1 | C&D, L120 | Mejor área para montaje final; confirmar medidas y precio al pagar. La protoboard queda para pruebas. |
| 1 | Borneras 2.54 mm, paquete de 4 | 1 | C&D, L45 | Conexiones desmontables de bomba, ventilador y energía. |
| 1 | Fusible 5×20 mm | 1 | C&D, L15 | Protección; su amperaje se elige después de medir corriente total. |
| 2 | MAX98357A I2S | 1 | C&D, L130 | Voz PicoTTS amplificada. |
| 2 | Parlante 4 ohm/3 W | 1 | C&D, L90 | Salida hablada de Jarvis. |
| 2 | INMP441 I2S | 1 | cotización local pendiente | Micrófono de Jarvis; no apareció oferta hondureña verificable. |

**Total nacional conocido del montaje: L738 + INMP441 + envío.** No incluye
microSD porque PicoTTS no la necesita, ni cuatro relés, ni cable, ni MOSFETs
separados. Sin la fuente final, el prototipo baja a L490 + micrófono + envío,
pero no se declara instalación final. Añadir L15 por cada portafusible aéreo;
el fusible suelto no debe quedar soldado permanentemente ni expuesto.

## Conexión exacta del DRV8833

La serigrafía de la placa comprada manda; fotografiar ambas caras antes de
cablear. El módulo típico se conecta así:

```text
FUENTE +5 V  -> VM/VCC motor del DRV8833
FUENTE GND   -> GND del DRV8833
ESP32 GND    -> el mismo GND común

GPIO4        -> AIN1              AOUT1/AO1 -> bomba cable 1
GND o GPIO   -> AIN2              AOUT2/AO2 -> bomba cable 2
GPIO7        -> BIN1              BOUT1/BO1 -> ventilador cable 1
GND o GPIO   -> BIN2              BOUT2/BO2 -> ventilador cable 2
nSLEEP/SLP   -> 3V3 (si la placa no trae pull-up)
```

Para encendido simple, `IN1=HIGH` e `IN2=LOW`; ambos `LOW` dejan la salida en
reposo. Si la placa tiene `VCC` lógico separado, ese VCC va a 3V3 y `VM` a 5V;
no asumirlo sin ver la serigrafía. La bomba nunca se conecta a `VCC/GND` del
driver: se conecta entre las dos salidas `AOUT`. El DRV8833 ya es puente H y no
requiere relé. Sus protecciones no sustituyen el fusible principal.

## Distribución, fusibles y switches

```text
Extensión 120 V
  -> adaptador cerrado 5 V
  -> switch MAESTRO DC >= 5 A
  -> portafusible principal
  -> barra +5 V / GND
       +-> ESP32
       +-> DRV8833 -> bomba y ventilador
       +-> MAX98357A

Switches de ZONA -> entradas GPIO a GND con INPUT_PULLUP
                  (no llevan corriente de motores)
```

- Un fusible necesita portafusible. Comprar dos portafusibles 5×20 mm permite
  uno principal y uno para el ramal de motores.
- Comprar dos unidades de cada valor elegido da un repuesto, no significa poner
  dos fusibles en paralelo. El valor se fija tras medir: debe permitir el pico
  normal y proteger el cable/placa.
- El switch maestro va en el positivo de 5 V después del adaptador, nunca se
  improvisa sobre 120 V. Debe estar marcado al menos 5 A DC.
- Los switches de zona son controles lógicos; el firmware decide qué salida
  activar. Así no necesitan soportar la bomba.

## Capacitores: reserva razonable

No comprar 7000 µF como regulador: un capacitor no regula voltaje y uno enorme
produce un pico de carga al encender. Punto de partida:

- 470–1000 µF, mínimo 10 V, junto a VM/GND del DRV8833;
- 100 nF cerámico `104` sobre los terminales de cada motor (ya hay disponibles);
- 470–1000 µF, mínimo 10 V, junto a 5 V/GND del MAX98357A si el audio reinicia
  el ESP32;
- 10 µF local donde indique cada módulo; muchas placas ya lo incorporan.

No sumar capacitancia “por si acaso”: se aumenta solamente si el osciloscopio o
las pruebas de caída/reinicio muestran que hace falta.

## Criterio real de la fuente

La fuente 5 V/3 A es candidata, no garantía. Se acepta únicamente si, con bomba,
ventilador, audio alto y ESP32 simultáneos, la tensión en la barra permanece
estable, la fuente no se calienta excesivamente y la corriente pico conserva
20–30 % de margen. Si el total sostenido supera aproximadamente 2.4 A o los
picos causan reinicios, pasar a una fuente cerrada 5 V/4–5 A certificada.

## TP4056: decisión de reutilización

El TP4056 probado puede mantenerse como adaptador temporal exclusivo del ramal
de bomba durante el banco, porque ya se verificó durante aproximadamente una
hora. Esto no convierte B+/B- y OUT+/OUT- en una entrada de distribución:

- es un cargador lineal para una celda Li-ion 1S, no una fuente USB-C de 5 V;
- unir B+ con OUT+ y B- con OUT- puentea la etapa de protección del módulo;
- no alimentar desde él simultáneamente ESP32, audio, motor y bomba;
- mantener el capacitor probado respetando polaridad y tensión nominal;
- medir tensión, corriente y temperatura; detener si cae el voltaje, se reinicia
  el ESP32 o el módulo se calienta claramente.

La regla `si funciona no se toca` aplica al banco reproducible; no reemplaza la
comprobación de límites antes de declarar el montaje final.

## Buzzer asociado a la bomba

El TMB12A05 es indicador, no driver. Puede sonar al arrancar la bomba o ante
nivel bajo/timeout. Se alimenta a 5 V y se conmuta con un S8050 identificado y
resistencia de base; no se conecta en serie con la bomba ni la sustituye.

## Organización y soldadura

Isaac confirmó que tercera mano, caja, tapete y accesorios equivalentes no son
necesarios para esta compra. La tabla se conserva solo como referencia y no se
suma al presupuesto vigente.

| Alcance | Compra | Tienda/precio | Decisión |
|---|---|---:|---|
| mínimo recomendado | Lupa/tercera mano TE-801 | C&D, L410 | Sujeta placa y cables mientras se suelda. |
| mínimo recomendado | Caja organizadora 18 divisiones HER-222 | Steren, L129.01 | Separa sensores, tornillos y discretos. |
| opcional útil | Tapete de silicón antiestático/magnético HER-108 | Steren, L479 | Protege mesa y organiza; no es necesario para terminar. |
| si falta | Soldadura 60/40, 17 g | Steren, L119 | Consumible básico; ventilar y lavarse las manos. |
| si falta | Malla desoldadora | Steren, L59 | Correcciones. |
| si falta | Base de cautín | Steren, L199 | Seguridad si el cautín no trae base. |

Organización mínima: **L539.01**. Con tapete: **L1,018.01**. Consumibles/base
se suman solo si no existen; no comprar la estación profesional de L1,090 salvo
que vaya a reutilizarse en otros proyectos.

## Totales claros

| Escenario | Total conocido |
|---|---:|
| Electrónica final, sin herramientas ni portafusibles | L738 + INMP441 + envío |
| Protección: dos portafusibles aéreos | +L30 |
| Electrónica final con dos portafusibles | L768 + INMP441 + envío |

## Enlaces de cotización

- [DRV8833 en catálogo C&D](https://sps.cdtechnologia.net/2-inicio?page=69)
- [Portafusible aéreo 5×20 mm C&D](https://sps.cdtechnologia.net/3685-portafusible-con-cable.html)
- [Fuente 5 V/3 A C&D](https://sps.cdtechnologia.net/2985-fuente-para-raspberry-pi3-pi4.html)
- [MAX98357A C&D](https://sps.cdtechnologia.net/5855-modulo-amplificador-de-audio-i2s-max98357.html)
- [Parlante 4 ohm/3 W C&D](https://sps.cdtechnologia.net/4094-parlante-4ohm-3w.html)
- [Tercera mano C&D](https://sps.cdtechnologia.net/3588-lupa-con-pinzas-sujetadoras-y-luz-led-te-801.html)
- [Herramientas y cajas Steren Honduras](https://www.steren.com.hn/linea-estudiantil/herramientas-para-proyectos)
- [Soldadura y accesorios Steren Honduras](https://www.steren.com.hn/linea-estudiantil/cautines-y-accesorios)

## Relaciones

- [[03 - Lista de compras definitiva]]
- [[40 - Presupuesto minimo Jarvis diagramas y migracion de firmware]]
