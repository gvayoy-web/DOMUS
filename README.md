# Casa inteligente — Jarvis local v5

Proyecto de feria basado únicamente en ESP32-S3 N16R8. El firmware controla sensores, relés, automatización, BLE y la futura voz local de Jarvis. No hay aplicación móvil ni dependencia de internet para las funciones críticas.

## Estado actual

- Firmware: [`firmware/casa_inteligente_v4/casa_inteligente_v4.ino`](firmware/casa_inteligente_v4/casa_inteligente_v4.ino)
- Voz local: [`firmware/JARVIS_LOCAL.md`](firmware/JARVIS_LOCAL.md)
- Plan completo: [`PLAN_PROYECTO.md`](PLAN_PROYECTO.md)
- Guía para exposición: [`EXPOSICION_PROYECTO.txt`](EXPOSICION_PROYECTO.txt)
- Prueba de micrófono: [`firmware/inmp441_poc`](firmware/inmp441_poc)
- Prueba de voz española: [`firmware/picotts_poc`](firmware/picotts_poc)
- `JARVIS_LOCAL_HABILITADO=false` hasta tener micrófono, modelos TinyML, PicoTTS y pruebas reales.

## Meta de Jarvis

```text
Jarvis, apaga la luz de la sala uno
Jarvis, desactiva la luz de la sala uno
```

Ambas frases producen `LUZ_SALA_1_OFF`, apagan el relé y generan una respuesta española con PicoTTS. No se promete conversación libre ni un LLM.

## Hardware de voz

- INMP441 a 3.3 V, I2S mono a 16 kHz.
- MAX98357A I2S y altavoz de 4 Ω/3 W para la voz generada.
- Tira WS2812B de 8 LEDs como indicador azul.
- Fuente regulada de 5 V/2 A para pruebas.
- 74AHCT125/74HCT14 recomendado para datos del WS2812B.

Confirma el pinout de la placa antes de soldar. No alimentes altavoz o relés desde 3.3 V del ESP32.

## Compilación

El firmware base se compila automáticamente en GitHub Actions para un
`ESP32S3 Dev Module`, con 16 MB de flash y PSRAM OPI. La compilación usa el
core Arduino-ESP32 3.3.10 y mantiene `JARVIS_LOCAL_HABILITADO=false`.

Para compilar localmente con Arduino CLI:

```powershell
arduino-cli compile --fqbn "esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=default_16MB" firmware/casa_inteligente_v4
```

La compilación comprueba el software; el pinout, los relés y los sensores aún
deben validarse físicamente con fuente regulada antes de conectar la fase solar.

## Servicios Wi‑Fi opcionales

El núcleo offline no depende de ellos. La capa Wi‑Fi podrá integrar MQTT local, Home Assistant, Node-RED, webhooks, NTP, clima y OTA firmada. Spotify se controlará mediante un gateway local y su Web API; el ESP32 no reproducirá directamente el catálogo ni guardará tokens OAuth.

## Limitaciones honestas

- Los modelos Hugging Face de cientos de megabytes no caben en esta placa.
- ESP-SR oficial ofrece comandos en inglés/chino y TTS chino, no un Jarvis español general.
- La voz española local será TinyML de intenciones y PicoTTS. Será entendible pero sintética.
- Riego y ventilación siguen funcionando sin Wi‑Fi.
