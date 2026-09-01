# Prueba PicoTTS español + MAX98357A

Esta prueba aislada verifica la parte más incierta del proyecto antes de
mezclarla con relés, BLE y micrófono. Usa ESP-IDF 5.1 o posterior y descarga el
componente `jmattsson/picotts` 1.1.3 mediante el Component Manager.

## Cableado

Los GPIO 40/41/42 son valores iniciales, no un pinout definitivo. Confirma que
estén expuestos y libres en tu DevKitC; puedes cambiarlos en `idf.py menuconfig`.

```text
ESP32-S3 5V   -> MAX98357A VIN
ESP32-S3 GND  -> MAX98357A GND
GPIO BCLK     -> MAX98357A BCLK
GPIO WS       -> MAX98357A LRC
GPIO DOUT     -> MAX98357A DIN
Altavoz       -> MAX98357A SPK+ / SPK-
```

No conectes ninguna salida del altavoz a GND.

## Compilación

```text
idf.py set-target esp32s3
idf.py menuconfig
idf.py build
idf.py flash monitor
```

El resultado aceptable es escuchar: “Hola, soy Jarvis. El sistema de voz local
está funcionando.” La calidad será sintética. Esta prueba no reconoce voz ni
controla relés.
