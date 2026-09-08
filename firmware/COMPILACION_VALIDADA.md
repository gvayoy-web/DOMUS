# Compilación del núcleo doméstico

> Para Arduino IDE, instalar `DHT sensor library` 1.4.7, `Adafruit Unified
> Sensor` 1.1.15 y `LiquidCrystal I2C` 1.1.2. Un error `DHT.h: No such file or
> directory` indica una biblioteca ausente en el sketchbook activo, no un fallo
> del código. Véase la nota 35 de Obsidian.

## Cierre local vigente (2026-09-06)

Arduino-ESP32 3.3.10 y Arduino CLI 1.5.1, todas con `--warnings all`:

| Objetivo | Programa | Globales | Resultado |
|---|---:|---:|---|
| Principal N16R8 original | 415,250 | 25,092 | PASS |
| Principal N16R8 económico | 415,250 | 25,092 | PASS |
| Principal N16R8 + microSD | 456,182 | 25,228 | PASS |
| Principal 4 MB sin PSRAM | 410,056 | 24,616 | PASS |
| Principal 8 MB QSPI | 412,942 | 24,692 | PASS |
| Base modular N16R8, relé bloqueado (`false`) | 374,190 | 24,388 | PASS 07-09-2026 |
| Base modular N16R8, solo GPIO4 habilitado (`true`) | 374,194 | 24,388 | PASS de compilación; no cargado |
| Autotest N16R8 | 417,913 | 24,556 | PASS |
| Animaciones N16R8 | 382,598 | 24,340 | PASS |

Las advertencias restantes proceden de LiquidCrystal I2C 1.1.2 y del core
ESP32, no de los sketches DOMUS. La compilación certifica software; no sustituye
la medición de GPIO, polaridades, fuente, bomba, motor y sensores en la placa.

## Actualización de robustez (2026-09-05)

Código `a81d07a`: watchdog comprobado, I2C acotado, calibración NVS y cola SD.
Windows N16R8: 414,338 bytes de programa y 25,092 bytes globales.
SHA-256 local: `F096E686F305820D85C5301D764145D6E904C2F20220072B5186F2F844C66998`.
[Cinco perfiles Linux correctos, incluido SD](https://github.com/gvayoy-web/domusv1/actions/runs/33942958851).
El registro siguiente corresponde a la versión anterior; la nota 23 de
Obsidian mantiene el estado de las nuevas pruebas y del entrenamiento pendiente.

## Registro anterior

Validación del 4 de septiembre de 2026, código `f811065`; ajuste de matriz
QSPI en `1f6b6a4`. La auditoría anterior detectó un fallo real de generación
de prototipos Arduino. Los tipos de órdenes ahora están en `domus_types.h`.
Esta evidencia sustituye las afirmaciones de compilación de versiones anteriores.

## Entorno reproducible

- Windows, Arduino CLI 1.5.1, Arduino-ESP32 3.3.10.
- LiquidCrystal I2C 1.1.2, DHT sensor library 1.4.7, Adafruit Unified Sensor 1.1.15.
- Voz, MP3 y microSD deshabilitados.
- FQBN producción: `esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB,CPUFreq=240,LoopCore=1`.

## Binario local N16R8 original, PASS

- Programa: 402,374 bytes / 3,145,728 disponibles.
- Memoria global: 25,020 bytes / 327,680 disponibles. No mide el pico de heap en ejecución.
- Archivo: `build/prod_n16r8_v2/casa_inteligente_v4.ino.bin`, 402,528 bytes.
- SHA-256: `F1C16A4DA8F88D81F559636ED81E9CA28D227393A22AEDEB896A99F8DF5FFCE1`.
- Perfil predeterminado `DOMUS_SALIDAS_ECONOMICAS=0`: cinco salidas activas LOW.

También compiló Windows 4 MB/sin PSRAM/160 MHz/Core 0: 397,180 bytes de
programa y 24,544 de memoria global. Estas variantes son pruebas de compilación;
no usar un binario de otra memoria/placa para la N16R8.

La compilación completa muestra advertencias de la biblioteca LCD
(arquitectura AVR declarada y constantes binarias obsoletas) y de inicializadores
en TinyUSB del core. No se modificaron bibliotecas instaladas para ocultarlas.

## Automatización

La matriz `.github/workflows/firmware-ci.yml` compila cinco perfiles en Ubuntu:
N16R8 original, N16R8 económico, N16R8 con microSD, 4 MB sin PSRAM y 8 MB QSPI
(`PSRAM=enabled`). Otra matriz compila base modular, autotest y animaciones.
[Ejecución de referencia](https://github.com/gvayoy-web/domusv1/actions/runs/33941659044).
El resultado consolidado está en la nota 22 de Obsidian.

El validador ejecuta 20 pruebas del simulador y los contratos del firmware.
Una prueba adicional compila y ejecuta funciones extraídas del sketch en C++
para ambos perfiles de salida, comprobando desbordamiento Serial, fragmentación,
límite por ciclo, recuperación ADC y polaridad. En Windows se omite explícitamente
si no existe compilador C++ de escritorio; en Ubuntu se ejecuta con g++.

## Carga y banco pendientes

La alternativa económica requiere adaptar el mazo según la nota 21 antes de
definir `DOMUS_SALIDAS_ECONOMICAS=1`. Comprobar arranques, corrientes, sensores,
paro y bomba en la placa real. Compilar no demuestra estabilidad eléctrica.
