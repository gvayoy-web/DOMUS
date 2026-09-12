---
proyecto: PROJECT DOMUS
tipo: plano alfa de montaje
actualizado: 2026-09-10
estado: borrador_superado_ver_nota_50
---

# Diagrama ASCII alfa sin control IR

> [!WARNING]
> **Borrador superado (corrección 2026-09-12, nota 50).** Usa GPIO1/2/21 del
> lado tapado. El mapa vigente por un solo costado está en
> [[46 - Plan maestro de consolidacion un costado]] y la guía para cablear en
> [[47 - Guia visual principiante conexiones alfa]].

> [!IMPORTANT]
> Este plano usa solo el núcleo confirmado que ya está en mano. El control CAR
> MP3/HX1838 queda desconectado. El módulo de motores pedido todavía no se usa.
> La foto del anuncio parece una placa MX1508 (`IN1-IN4`, `OUT1-OUT4`) aunque la
> tienda la llama DRV8833; se identificará físicamente cuando llegue.

## 1. Límites de esta alfa

- ESP32-S3 N16R8 alimentado por su USB.
- Sensores, LCD, botones y LED usan 3.3 V/GND del ESP32.
- Bomba y ventilador requieren un **bus 5 V de motores separado y estable**.
- El negativo del bus de motores se une a GND del ESP32.
- No usar el TP4056 como fuente permanente sin batería ni el módulo de
  protoboard averiado.
- No alimentar bomba o motor desde GPIO, 3V3 ni desde el pin 5V del ESP32.
- Si hoy no hay una fuente 5 V adecuada, montar las dos etapas S8050 pero dejar
  desconectados los cables `+5V_MOTORES`.

## 2. Mapa general

```text
                         +-----------------------+
 USB ------------------->| ESP32-S3 N16R8        |
                         |                       |
  LCD SDA -------------->| GPIO21                |
  LCD SCL -------------->| GPIO13                |
  suelo AO ------------->| GPIO1                 |
  nivel S/AO ----------->| GPIO2                 |
  LDR nodo ------------->| GPIO3                 |
  PIR OUT -------------->| GPIO9                 |
  DHT11 DATA ----------->| GPIO14                |
  STOP ----------------->| GPIO10 (INPUT_PULLUP) |
  MODO ----------------->| GPIO12 (INPUT_PULLUP) |
  LUZ SALA --------------| GPIO5                 |
  LUZ CUARTO ------------| GPIO6                 |
  CULTIVO ---------------| GPIO8                 |
  BOMBA ---------------->| GPIO4                 |
  VENTILADOR ----------->| GPIO7                 |
                         +----------+------------+
                                    |
 ESP GND ----------------------------+---------------- GND COMUN

 FUENTE 5 V MOTORES (+) --------+---------------------+
                                |                     |
                         etapa S8050 bomba      etapa S8050 ventilador
```

## 3. LCD1602 con backpack I2C: solo cuatro cables

```text
 LCD I2C                 ESP32-S3
 +---------+             +--------+
 | GND  o  |------------>| GND    |
 | VCC  o  |------------>| 3V3    |
 | SDA  o  |------------>| GPIO21 |
 | SCL  o  |------------>| GPIO13 |
 +---------+             +--------+
```

No conectar además los 16 pines paralelos. Si enciende sin letras, ajustar el
potenciómetro azul del backpack y probar direcciones `0x27` y `0x3F`.

## 4. DHT11 azul suelto

```text
 Mirando la rejilla frontal, patas hacia abajo:

       +----------+
       |  DHT11   |
       +----------+
        1  2  3  4
        |  |  X  |
       3V3 |     GND
           +---------- GPIO14
           |
          [10 kOhm]
           |
          3V3
```

La pata 3 no se conecta. Confirmar orientación física antes de energizar.

## 5. Sensor de humedad de suelo con comparador

```text
 Sonda de dos puntas ---- módulo comparador

 módulo              ESP32
 VCC --------------- 3V3
 GND --------------- GND
 AO ---------------- GPIO1
 DO ---------------- sin conectar
```

Energizarlo solo al medir si se añade un pin de alimentación conmutada; dejarlo
mojado permanentemente acelera la corrosión.

## 6. Sensor de nivel de agua

```text
 sensor              ESP32
  + / VCC ----------- 3V3
  - / GND ----------- GND
  S / AO ------------ GPIO2
```

No sumergir la zona de pines ni el conector.

## 7. Fotoresistor LDR

```text
 3V3 ----[ LDR ]----+---- GPIO3
                    |
                 [10 kOhm]
                    |
 GND ----------------+
```

Registrar el valor iluminado y cubierto. El firmware puede invertir la
comparación si este divisor crece en oscuridad.

## 8. PIR

```text
 PIR                  ESP32
 VCC ---------------- 3V3
 OUT ---------------- GPIO9
 GND ---------------- GND
```

Leer la serigrafía del módulo: el orden físico cambia entre clones. Esperar
30-60 segundos de estabilización al encender.

## 9. Botones de banco, sin control remoto

```text
 GPIO10 ----[ STOP normalmente abierto ]---- GND
 GPIO12 ----[ MODO normalmente abierto ]---- GND
```

Configurar ambos como `INPUT_PULLUP`: sin pulsar = HIGH; pulsado = LOW. STOP
apaga salidas y exige rearme. GPIO12 se reutiliza temporalmente porque hoy no se
conecta el HX1838.

## 10. LED de sala y dormitorio

```text
 GPIO5 ----[330 Ohm]----|>|---- GND     LED sala
 GPIO6 ----[330 Ohm]----|>|---- GND     LED dormitorio
                         A K
```

`A` es ánodo: normalmente pata larga. `K` es cátodo: pata corta/lado plano.

## 11. Tres LED de cultivo, variante alfa sin tercer transistor

```text
 GPIO8 --+--[1 kOhm]-->|-- GND   azul
         +--[1 kOhm]-->|-- GND   azul
         `--[1 kOhm]-->|-- GND   rojo
```

Un resistor por LED. Se usan 1 kOhm para mantener baja la suma de corriente del
GPIO. Es representación visual, no luz UV ni iluminación agrícola real. En la
versión final se vuelve a usar una etapa de potencia si se necesitan más LED.

## 12. Bomba con S8050 número 1

```text
                                      +5V_MOTORES
                                           |
                         +-----------------+---- bomba (+)
                         |                      bomba (-) ----+
                         |                                    |
                         +----|<|----+                        C
                              1N4007 |                    +---|  S8050 #1
                         raya/cátodo |                    |   E
                         hacia +5 V  +--------------------+   |
                                                            GND COMUN

 GPIO4 --------[1 kOhm]-------- B
                                 |
                              [10 kOhm]
                                 |
                                GND
```

El diodo va en paralelo con la bomba: raya al positivo. Verificar las patas
E/B/C del S8050 real; el orden depende del fabricante. Probar primero con pulsos
de 0.5 s y la bomba sumergida. Si el transistor se calienta, parar.

## 13. Ventilador con S8050 número 2

```text
                                      +5V_MOTORES
                                           |
                         +-----------------+---- motor (+)
                         |                      motor (-) ----+
                         |                                    |
                         +----|<|----+                        C
                              1N4007 |                    +---|  S8050 #2
                         raya/cátodo |                    |   E
                         hacia +5 V  +--------------------+   |
                                                            GND COMUN

 GPIO7 --------[1 kOhm]-------- B
                                 |
                              [10 kOhm]
                                 |
                                GND
```

Este montaje solo da encendido/apagado y una dirección. No probar bomba y
ventilador juntos hasta medir la corriente de arranque de cada uno y verificar
que la fuente no cae.

## 14. Buzzers

Los dos S8050 disponibles están ocupados por los motores. Por eso el buzzer
activo de 5 V **no se conecta todavía** sin medir su corriente. Para señal de
banco se puede probar el buzzer pasivo de forma breve:

```text
 GPIO15 ----[100 Ohm]---- buzzer pasivo ---- GND
```

Usar PWM/tono, volumen moderado y prueba corta. Si el componente marcado
`TMB12A05` solo suena con DC, es el activo y se reserva para una etapa con
transistor, no se pone directo al GPIO.

## 15. Relé desnudo

```text
 NO CONECTAR EN EL MONTAJE ALFA.
```

Solo hay dos S8050 y ambos protegen cargas útiles. El relé no aporta ventaja a
la bomba/ventilador DC y su pinout de cinco patas no se adivina.

## 16. Partes opcionales que no entran al núcleo simultáneo

```text
 HC-SR04      -> requiere divisor en ECHO; prueba separada
 RFID RC522   -> prueba SPI separada
 MPU6050      -> comparte I2C, pero primero escanear dirección
 Servo SG90   -> necesita fuente 5 V capaz de soportar su pico
 WS2812       -> esperar adaptación y fuente final
 DFPlayer     -> requiere microSD y altavoz; prueba separada
 L293D        -> alternativa segura a los S8050 para motores
 displays,
 matriz, barra,
 joystick,
 keypad       -> extras; no meter todos porque agotan pines y dificultan fallos
```

"Usar todo" debe significar montar todo el **núcleo útil**, no conectar cada
pieza del kit al mismo tiempo. Las piezas opcionales se validan con sketches
aislados y se agregan solo si aportan a la exposición.

## 17. El módulo pedido de la foto: conectar solo al llegar

```text
 FOTO / SERIGRAFÍA OBSERVADA

 lado entradas                 lado salidas
 IN4  o ---------------------- o OUT1
 IN3  o ---------------------- o OUT2
 GND  o      [ CONTROL ]       o OUT3
 VCC  o      [ 2 CANALES ]     o OUT4
 IN2  o
 IN1  o
```

Esta distribución coincide más con una placa MX1508 que con el DRV8833 típico.
Cuando llegue:

1. Fotografiar ambas caras y leer el código del integrado.
2. Medir continuidad para identificar GND y VCC.
3. No buscar ni conectar `SLEEP`: la placa fotografiada no lo expone.
4. Si se confirma MX1508: IN1/IN2 controlan OUT1/OUT2 y IN3/IN4 controlan
   OUT3/OUT4; VCC recibe la fuente de motores y GND es común.
5. Probar sin motores, luego una carga, luego la otra.

## 18. Orden de montaje hoy

1. Todo sin corriente; colocar primero GND y 3V3.
2. Medir que no haya corto entre 3V3-GND ni 5V_MOTORES-GND.
3. Cargar firmware con salidas en LOW antes de conectar actuadores.
4. LCD; después DHT; suelo; nivel; LDR; PIR, uno por uno.
5. Botones STOP y MODO.
6. LED sala, dormitorio y cultivo.
7. Montar S8050, resistencias y diodos sin conectar +5V_MOTORES.
8. Verificar E/B/C con multímetro.
9. Conectar fuente de motores solo si entrega 5 V estable y tiene corriente
   suficiente; GND común antes que señales.
10. Probar ventilador 0.5 s, después bomba 0.5 s dentro de agua.
11. Probar por separado; no simultáneo hasta medir corriente y temperatura.
12. Ejecutar 15 minutos vigilados antes de ampliar la prueba.

## 19. Firmware correspondiente

- `domus_selftest`: ESP32 solo.
- `domus_esqueleto`: sensores, LCD, botones, LED y salidas bloqueadas.
- `domus_alpha_transistores`: **pendiente de crear**; GPIO4 bomba, GPIO7
  ventilador, GPIO12 botón MODO y sin receptor IR.
- `domus_ir_learn`: futuro, cuando se retome el control.
- `domus_driver_test`: futuro, cuando llegue y se identifique la placa pedida.
- `casa_inteligente_v4`: final, solo después de aprobar todas las etapas.

No activar bomba y ventilador en el esqueleto actual: su configuración todavía
está preparada para el driver final y no sustituye las pruebas del transistor.

## 20. PASS mínimo

- Arranque con bomba, ventilador y LED apagados.
- STOP apaga GPIO4, 5, 6, 7, 8 y 15.
- Sensor desconectado no activa un motor.
- Nivel bajo bloquea la bomba.
- Bomba se corta por timeout aunque el botón quede pulsado.
- Ningún S8050, diodo o cable se calienta.
- El ESP32 no se reinicia al arrancar una carga.
- LCD sigue actualizando mientras cambian los sensores.

