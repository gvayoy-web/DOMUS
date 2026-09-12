# DOMUS: base modular para banco alfa por un solo costado

Controlador recomendado para probar el hardware confirmado sin red, SD,
batería, solar, IR ni controlador de motores supuesto. Integra sensores,
LCD, DHT, automatizaciones,
calibración persistente, propiedad manual, PARO, watchdog y modo seguro.
Aún requiere validación física supervisada.

El perfil se identifica como `ESP32-S3-N16R8` + `PERFIL_PRUEBA` diagnosticado
(`ALFA_UN_COSTADO_SIN_IR` en banco normal, `ALFA_BOMBA_1` o `ALFA_VENTILADOR_1`
en prueba vigilada). La selección vive en una sola línea,
`PERFIL_HARDWARE` en `domus_config.h` (o bandera `-DDOMUS_PERFIL_ALFA=0/1/2`);
`CONTROLADOR_DOBLE_IDENTIFICADO=false` e `IR_HABILITADO=false` permanecen así
hasta superar las puertas físicas de la nota 46.

## Seguridad 120 V

El 120 V vive SOLO en una extensión externa: de ella salen el cargador USB
del ESP32-S3 y la fuente cerrada 5 V/5 A. El 120 V NUNCA entra a la maqueta,
protoboard ni PCB. Orden: fuente 5 V/5 A -> portafusible 4 A lento ->
switch 5 A DC -> bus 5 V. Medir 5 V antes de conectar.

## Dependencias Arduino

Instalar desde **Programa > Incluir librería > Administrar bibliotecas**:

- `DHT sensor library` de Adafruit, versión 1.4.7 o compatible.
- `Adafruit Unified Sensor`, dependencia del DHT.
- `LiquidCrystal I2C` 1.1.2 o compatible.
- `IRremote` 4.x (shirriff/z3t0/ArminJo) para el CAR MP3 NEC.

Si aparece `DHT.h` o `IRremote.hpp: No such file`, falta instalar en el
mismo sketchbook de Arduino IDE; reiniciar el IDE después.

## Mapa alfa por el costado accesible

| Función | GPIO | Etapa |
|---|---:|---|
| Bomba (solo `ALFA_BOMBA_1`) | 4 | Un solo S8050 como interruptor lado bajo; ventilador desconectado |
| Sala LED | 5 | LED + 330 Ω a GND |
| Cuarto LED | 6 | LED + 330 Ω a GND |
| Ventilador (solo `ALFA_VENTILADOR_1`) | 7 | El MISMO S8050 movido al otro circuito; bomba desconectada |
| Cultivo LED directo | 8 | GPIO8 -> 1 kΩ por LED -> ánodo; cátodo a GND (sin transistor en alfa) |
| Suelo/nivel/luz | 15/16/3 | Analógicas <=3.3 V |
| PIR | 9 | Señal <=3.3 V (si el módulo es 5 V, medir OUT) |
| PARO | 10 | Contacto a GND, pull-up interno. Manda sobre el IR siempre |
| SILENCIO Jarvis | 11 | Contacto a GND = mute hardware |
| IR HX1838 | — | No montar en este perfil |
| GPIO12 | reservado | Sin conectar (`BUZZER_HABILITADO=false` en alfa; IR fuera del perfil) |
| Botón MODO | 18 | Contacto temporal a GND |
| LCD I2C | SDA 17 / SCL 13 | Alimentar a 3.3 V; el arranque escanea 0x08-0x77 |
| DHT | 14 | DATA + 10 k a 3V3 |

GPIO1, GPIO2 y GPIO21 quedan fuera porque están en el costado tapado.

> Inventario real: **un S8050 NPN + un S8550 PNP en reserva**. Bomba y
> ventilador son usos ALTERNATIVOS del mismo S8050 (una carga por vez,
> ver nota 49); el S8550 no se conecta copiando este esquema. Cultivo son
> LED directos a GPIO8, uno con su 1 kΩ; la etapa con transistor es final,
> no alfa.

## Control IR CAR MP3 (fase final, no montar ahora)

Mapa: CH- manual, CH página LCD, CH+ auto, Anterior/1 sala, Play pausa voz,
Siguiente/2 dormitorio, VOL∓ volumen, EQ diagnóstico, 0 todo off,
100+ mute, 200+ rearme, 3 cultivo, 4 ventilador, 5 riego, 6 temp,
7 humedad, 8 suelo+nivel, 9 estado.

Antifallos: cada pulsación vale una vez; se ignoran repeats salvo VOL;
riego exige pulsación nueva; remoto nunca sustituye PARO GPIO10;
nivel bajo/timeout rechazan riego; desconocida no ejecuta nada;
último código siempre por Serial `IR;CMD=0x..`.

Primera vez con tu control (códigos varían por lote):

```text
IR LEER
(pulsa las 21 teclas, una por una)
IR LISTA
```

Si alguna tecla sale `?`, fíjala:

```text
IR GRABAR 16
(pulsa 5)
IR LISTA
IR BORRAR   (vuelve a Keyes por defecto)
```

## LCD bonito (16x2, 4 páginas)

CH cambia página. Botón físico o IR muestra las letras de la acción y
después una animación (barra + spinner). Páginas:

- 0 HOME: `T:25.3C H:60%` + `AUTO V20 SSCVI` (R/S/C/V/I).
- 1 sensores: suelo % + nivel crudo, luz % + PIR.
- 2 salidas: `R S C V I` con bloque lleno = ON.
- 3 Jarvis/IR: mute/pausa/vol + frase con scroll o `IR:00XX`.

Splash `PROJECT DOMUS` con barra al arrancar. Iconos: gota, sol,
termómetro, nivel, voz, candado.

## Jarvis (frases fijas, sin IA)

`JARVIS;<frase>` sale siempre por Serial + scroll en LCD pág. 3.
Con `DFPLAYER_HABILITADO=true` + microSD con `0001.mp3...` suena la pista;
sin DFPlayer y con buzzer habilitado, beep + Serial + LCD (no bloquea).
En alfa (`BUZZER_HABILITADO=false`, GPIO12 reservado) es solo Serial + LCD.

Pistas sugeridas: 1 sala on, 2 sala off, 3 dorm on, 4 dorm off,
5 cultivo on, 6 cultivo off, 7 vent on, 8 vent off, 9 riego,
10 todo off, 11 temp, 12 hum, 13 suelo/nivel, 14 estado,
30 manual, 31 auto, 32 voz, 33 diagnóstico, 34 sonido, 35 rearme.

```text
MODO AUTO / MODO MANUAL
VOL+ / VOL- / MUTE ON / MUTE OFF / VOZ ON / VOZ OFF
PAGINA / PAGINA 0..3
ESTADO / DIAGNOSTICO / PARO / REARMAR
IR LEER / IR LISTA / IR GRABAR <0-20> / IR BORRAR
```

## Órdenes serie (mayúsculas, LF/CRLF)

```text
SALA ON / CUARTO ON / INVERNADERO ON / VENTILADOR ON / BOMBA ON
... OFF / ... AUTO
ESTADO / DIAGNOSTICO / PARO / REARMAR / RECUPERAR
```

`!` enclava PARO sin esperar fin de línea. ON limitado a 1/250 ms.
`REARMAR` exige PARO físico liberado y deja todo OFF.

## Calibración (con PARO y todo OFF)

```text
CAL SECO=2800 / CAL HUMEDO=1200 / CAL OSCURO=300 / CAL CLARO=3000
CAL NIVEL=600 / CAL VER / CAL GUARDAR / REARMAR
```

Números de ejemplo, no copiar. Suelo/luz separados ≥100 cuentas.

## Verificación

```powershell
.local-tools/arduino-cli/bin/arduino-cli.exe compile --config-file .arduino-local/arduino-cli.yaml --fqbn esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB,CPUFreq=240,LoopCore=1 --build-path build/esqueleto_v2 --output-dir build/esqueleto_v2-out firmware/domus_esqueleto
```

v2 verificado: 405637 bytes programa, 25652 globales, N16R8.
`protocol_tests.cpp` trae regresiones constexpr (parser + nuevos comandos).
Compilar no prueba electricidad: medir 5 V, PARO, rearme y bloqueo por
nivel/timeout 10 s antes de pensar en DRV.
