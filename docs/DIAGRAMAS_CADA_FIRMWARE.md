# Diagramas de conexión de todos los firmware DOMUS

**Lee primero:** estos son los **seis sketches Arduino .ino** del repositorio. Un firmware se carga a la vez. Los números GPIO son los textos impresos en tu placa ESP32-S3; **no son la posición física del pin**. El mapa para montar el banco hoy es el de `casa_inteligente_v4` / `domus_esqueleto`. Los demás se explican para reconocerlos y no mezclar cables. Estado documental: [Obsidian 63](../obsidian/proyect%20domus/63%20-%20Auditoria%20total%20de%20Obsidian%20y%20estado%20real.md).

## Cómo leer las piezas

```text
DHT11 AZUL SUELTO, 4 PATAS
Mira su CARA CUADRICULADA de frente; patas hacia abajo:

    ┌──── cara cuadriculada ────┐
    └───────────────────────────┘
       1       2       3       4     (izquierda → derecha)
      3V3    DATA     nada     GND
              │
        resistencia 10 kΩ a 3V3
```

La pata 2 DATA cambia de GPIO según el firmware. La pata 3 es NC y se deja vacía. **Si tu DHT11 es un módulo de tres pines**, no uses esta numeración: sigue `+`, `S/OUT` y `-` impresos. La [hoja del fabricante AOSONG](https://www.haoyuelectronics.com/Attachment/DHT11/DHT11.pdf) confirma el orden del sensor suelto.

En las demás placas, **no hay un izquierda/derecha universal**. Busca las letras impresas junto a cada pin:

| Pieza | Pin impreso | Significado |
|---|---|---|
| PIR de domo | `VCC`, `OUT`, `GND` | Alimentación, señal, tierra. La foto de Obsidian no fija el orden de las tres patas. |
| Receptor IR en placa | `VCC/+`, `OUT/S`, `GND/-` | Alimentación 3V3, señal, tierra. **No copies un pinout numerado de otro receptor**: las familias cambian. |
| LCD1602 con mochila I²C | `VCC`, `GND`, `SDA`, `SCL` | Cuatro cables externos; la mochila ya está soldada al LCD. |
| Sensor de suelo con comparador | `VCC`, `GND`, `AO`, `DO` | Sonda al conector de dos pines; `AO` al ESP32, `DO` sin cable. |
| Nivel rojo | `+`, `-`, `S` | 3V3, GND, señal analógica; seguir letras, no posición. |

La **LDR no tiene polaridad**. En la protoboard usa una misma fila para el punto `●`:

```text
3V3 ── LDR ──●── resistencia 10 kΩ ── GND
             │
          GPIO indicado abajo
```

Cada botón pequeño debe cruzar la ranura central de la protoboard: un lado al GPIO indicado y el lado opuesto a GND. Cada LED: `GPIO → resistencia → pata larga (+)`; pata corta / borde plano `→ GND`. Cada LED lleva su propia resistencia. Para S8050 **identifica B, C y E en tu pieza** por marca y hoja de datos; no se puede numerar sus patas desde la foto disponible.

## 1. Producto: `firmware/casa_inteligente_v4/casa_inteligente_v4.ino`

Es la implementación única. Por defecto compila `DOMUS_PERFIL_CASA=3`, el banco con S8050 e IR. **Este sí es el mapa para conectar ahora.**

```text
ESP32-S3 (3V3 + GND común)
├─ GPIO3  ← punto ● del divisor LDR
├─ GPIO9  ← PIR OUT                 PIR VCC→3V3, GND→GND
├─ GPIO12 ← receptor IR OUT/S       IR VCC→3V3, GND→GND
├─ GPIO14 ↔ DHT11 pata 2 DATA      patas 1→3V3, 3→nada, 4→GND
├─ GPIO15 ← sensor de suelo AO      VCC→3V3, GND→GND, DO→nada
├─ GPIO16 ← sensor de nivel S       +→3V3, -→GND
├─ GPIO17 ↔ LCD SDA                LCD VCC→3V3, GND→GND
├─ GPIO13 ↔ LCD SCL
├─ GPIO10 ─ botón PARO ─ GND
├─ GPIO11 ─ botón SILENCIO ─ GND
├─ GPIO18 ─ botón MODO ─ GND
├─ GPIO5  → resistencia 330 Ω–1 kΩ → LED sala → GND
├─ GPIO6  → resistencia 330 Ω–1 kΩ → LED cuarto → GND
├─ GPIO8  → resistencia individual → LED(s) cultivo → GND
├─ GPIO4  → resistencia 1 kΩ → base B del único S8050 → BOMBA
└─ GPIO7  → VENTILADOR BLOQUEADO: dejar sin cable
```

**Bomba de este perfil, una sola carga:**

```text
GPIO4 ─ resistencia 1 kΩ ─●─ B del S8050
                         └─ resistencia 10 kΩ ─ GND
E del S8050 ─ GND común ─ ESP32 GND ─ TP4056 OUT−
C del S8050 ─ negativo (−) de la minibomba
TP4056 OUT+ ─ positivo (+) de la minibomba
1N4007 en paralelo con bomba: pata CON RAYA → OUT+;
                            pata SIN RAYA → negativo / C
```

Usa solamente la prueba vigilada descrita en [nota 49](../obsidian/proyect%20domus/49%20-%20Prueba%20de%20una%20carga%20con%20un%20S8050%20y%20TP4056.md). `OUT+` no va a 3V3 ni a ningún GPIO. El S8550 queda en reserva. El DRV8833, ventilador, microSD, micrófono y audio **no tienen conexión activa** en este firmware.

**Perfiles del mismo producto:** `0` mantiene GPIO4–8 sin salida física; `1` y `2` permiten los LED GPIO5/6/8, pero los motores siguen bloqueados; `3` habilita esos LED, la bomba GPIO4 y el IR GPIO12. Sensores, LCD y botones conservan los GPIO de arriba. No conectes la bomba esperando que un perfil 0, 1 o 2 la pruebe.

## 2. Banco actual: `firmware/domus_esqueleto/domus_esqueleto.ino`

**Mismo diagrama completo del punto 1.** Este archivo define perfil 3 e incluye literalmente `casa_inteligente_v4.ino`. No es un segundo circuito. DHT11 DATA→GPIO14, PIR OUT→GPIO9, IR OUT/S→GPIO12, LCD SDA→GPIO17/SCL→GPIO13, suelo AO→GPIO15, nivel S→GPIO16, LDR→GPIO3, botones 10/11/18, LED 5/6/8, bomba S8050→GPIO4 y GPIO7 vacío.

Para la primera carga y los comandos exactos usa [PRUEBA_HOY](../firmware/PRUEBA_HOY.md). El firmware arranca con bomba apagada; las 21 teclas del mando deben aprenderse en el propio banco antes de tener acciones.

## 3. Diagnóstico sin salidas: `firmware/diagnosticos/domus_banco_integracion/domus_banco_integracion.ino`

Sirve para leer sensores, buscar LCD, capturar códigos IR y tomar calibraciones. **No configura GPIO4, 5, 6, 7 ni 8.** Tampoco lee PIR ni botones.

```text
ESP32-S3
├─ GPIO3  ← ● del divisor LDR
├─ GPIO12 ← IR OUT/S        IR VCC→3V3, GND→GND
├─ GPIO13 ↔ LCD SCL         LCD VCC→3V3, GND→GND
├─ GPIO14 ↔ DHT11 pata 2    pata 1→3V3, 3→nada, 4→GND
├─ GPIO15 ← suelo AO        VCC→3V3, GND→GND, DO→nada
├─ GPIO16 ← nivel S         +→3V3, -→GND
└─ GPIO17 ↔ LCD SDA

GPIO4–8: sin cables hacia bomba, ventilador o LED para esta prueba.
PIR GPIO9 y botones: este sketch no los prueba.
```

En Serial a 115200, `LECTURAS`, `LCD`, `IR_LISTA` y `MUESTRA_...` muestran datos. Sus códigos IR solo viven en RAM; el producto los guarda con `IR_GRABAR_0` a `IR_GRABAR_20`.

## 4. Autotest histórico: `firmware/domus_selftest/domus_selftest.ino`

**No usar este mapa para el banco actual.** El archivo trae `PLACA_LIMITADA=1` por defecto: solo asume expuestos 3–13, 25–28 y 46. En este sketch GPIO12 es reloj I²C, no IR; GPIO9 es nivel, no PIR.

```text
PLACA_LIMITADA=1 (valor escrito en el sketch)
LCD + OLED I²C: SDA→GPIO11, SCL→GPIO12; LCD VCC→3V3, OLED VCC→3V3
Suelo AO→GPIO3       Nivel S→GPIO9       LDR ●→GPIO10
PIR OUT→GPIO13       DHT11 pata 2 DATA→GPIO25
PARO→GPIO26/GND      MIC OFF→GPIO27/GND  DEMO→GPIO28/GND
Salidas GPIO4/5/6/7/8: cinco pruebas lógicas activas LOW;
  no conectar directamente LED/S8050 del perfil actual.
TFT ST7789: CS→GPIO25, DC→GPIO26, RST→GPIO27,
             MOSI→GPIO28, SCLK→GPIO46; VCC/BLK según módulo.
```

**Alternativa obligatoria:** GPIO25–28 se repiten entre TFT y DHT/botones. Para probar TFT, desconecta DHT y botones. Para probar DHT y botones, desconecta TFT y desactiva sus pines en el sketch. No puede montarse todo simultáneamente. GPIO46 es pin de arranque delicado; no conectes una TFT sin verificar el módulo y el efecto al encender. Los bloques SD/micrófono/audio/MP3 están marcados SKIP en este modo. El OLED del autotest es histórico: el producto usa LCD, no OLED.

Si editas `PLACA_LIMITADA=0`, cambia **todo el mapa**: LCD/OLED SDA21/SCL13; suelo1, nivel2, LDR3, PIR9, DHT14, PARO10, MIC OFF11, DEMO12 y TFT CS33/DC34/RST35/MOSI36/SCLK37. Ese mapa completo también es histórico y sus GPIO1/2/21 no coinciden con el banco vigente. El autotest puede pulsar salidas si se ordena `R SI`; dejar cargas desconectadas.

## 5. Animación histórica: `firmware/domus_anim/domus_anim.ino`

Este sketch muestra `Hola` en LCD, OLED y TFT. **No lee DHT11, PIR, suelo, nivel, IR ni bomba.** GPIO4–8 son de la TFT y no se conectan al S8050 ni a los LED del banco.

```text
LCD1602 I²C: VCC→3V3, GND→GND, SDA→GPIO11, SCL→GPIO12
OLED I²C:    VCC→3V3, GND→GND, SDA→GPIO11, SCL→GPIO12
TFT ST7789:  CS→GPIO4, DC→GPIO5, RST→GPIO6,
             MOSI→GPIO7, SCLK→GPIO8, GND→GND
             VCC y BLK: solo según la serigrafía/hoja de TU módulo
```

El LCD y OLED comparten los dos cables I²C porque tienen direcciones distintas. La TFT debe identificarse como ST7789 compatible antes de conectar VCC/BLK: el orden de sus pines cambia entre placas. Este mapa **no permite dejar montada la bomba GPIO4 ni el receptor IR GPIO12** del perfil actual.

## 6. Esqueleto anterior: `firmware/legacy/domus_esqueleto/domus_esqueleto.ino`

Se conserva solo para regresiones. Por defecto `DOMUS_PERFIL_ALFA=0`: motores GPIO4/7 bloqueados, IR y buzzer GPIO12 deshabilitados. **No cargues este código para comprobar el banco IR actual.**

```text
ESP32-S3, perfil alfa histórico 0
LDR ●→GPIO3            PIR OUT→GPIO9
DHT11 pata 2→GPIO14    suelo AO→GPIO15     nivel S→GPIO16
LCD SCL→GPIO13         LCD SDA→GPIO17      LCD VCC→3V3
PARO→GPIO10/GND        SILENCIO→GPIO11/GND MODO→GPIO18/GND
LED sala→GPIO5         LED cuarto→GPIO6    LED cultivo→GPIO8
GPIO4 y GPIO7: sin motor en perfil 0
GPIO12: sin receptor IR ni buzzer en este legado
```

Solo si se recompila explícitamente con perfil alfa `1` se permite **bomba sola** en GPIO4 mediante el único S8050; con perfil `2`, **ventilador solo** en GPIO7 moviendo **el mismo** circuito S8050 y dejando la bomba totalmente desconectada. La nota 49 explica la etapa B/C/E y el diodo. Estos perfiles antiguos no sustituyen el perfil 3 del producto. DFPlayer GPIO18/17 choca con MODO/LCD y queda deshabilitado.

## Qué montaje elegir

| Quieres hacer | Cargar | Cablear |
|---|---|---|
| Probar la casa y mando IR | `domus_esqueleto` o producto perfil 3 | Diagrama 1/2 y [SVG vigente](../visualizaciones/domus-banco-final-s8050-ir.svg) |
| Leer pines sin activar salidas | `domus_banco_integracion` | Diagrama 3 |
| Revisar pruebas antiguas | `domus_selftest`, `domus_anim`, `legacy` | Diagramas 4–6, en montajes separados |

Antes de energizar: confirma la etiqueta exacta de cada módulo, GND común y que ninguna señal hacia el ESP32 supere 3.3 V. La bóveda confirma visualmente DHT11 suelto, LCD con mochila, sensor rojo de nivel, PIR tipo HC-SR501 y receptor IR, pero **no confirma orden físico de PIR/IR, patas B/C/E del S8050 ni pinout del DRV8833 que aún falta**. Por eso aquí se dan sus letras funcionales y no un orden físico inventado. El chip [DRV8833 de TI](https://www.ti.com/lit/ds/symlink/drv8833.pdf) no fija el orden de pines de la placa breakout que recibirás.
