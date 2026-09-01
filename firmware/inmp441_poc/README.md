# Prueba aislada del micrófono INMP441

Esta fase comprueba que el ESP32-S3 recibe audio real antes de entrenar o
integrar modelos. Captura audio mono a 16 kHz, guarda los últimos dos segundos
en PSRAM y muestra por Serial RMS, pico, componente DC, saturación y una decisión
VAD básica.

## Cableado inicial

```text
INMP441 VDD -> 3.3 V
INMP441 GND -> GND
INMP441 WS  -> GPIO15
INMP441 SD  -> GPIO16
INMP441 SCK -> GPIO17
INMP441 L/R -> GND para canal izquierdo
```

Los GPIO se cambian mediante `idf.py menuconfig`. Nunca conectes VDD a 5 V.

## Uso

```text
idf.py set-target esp32s3
idf.py menuconfig
idf.py build
idf.py flash monitor
```

Haz tres mediciones de 30 segundos: silencio, habla a 50 cm y habla a un metro
con el ventilador activo. Ajusta el umbral VAD para que el silencio indique
`voz=NO` y el habla indique `voz=SI`. Si RMS y pico permanecen en cero, revisa
canal L/R y cableado. Si aparecen muchas muestras saturadas, reduce la ganancia
digital modificando el desplazamiento de `convertir_muestra()`.
