# Casa inteligente — Jarvis local v6

> Estado y ruta recomendada: [`ESTADO_ACTUAL.md`](ESTADO_ACTUAL.md). Para probar
> las piezas confirmadas usar la base modular, no los PoC de audio o pantallas.

Proyecto de feria basado únicamente en ESP32-S3 N16R8. El firmware controla cinco cargas, sensores, automatización local y la futura voz local de Jarvis. No hay aplicación móvil, BLE ni dependencia de internet para las funciones críticas. Los comandos de diagnóstico se aceptan localmente por USB Serial.

## Estado actual

- Firmware: [`firmware/casa_inteligente_v4/casa_inteligente_v4.ino`](firmware/casa_inteligente_v4/casa_inteligente_v4.ino)
- Firmware recomendado para banco: [`firmware/domus_esqueleto`](firmware/domus_esqueleto)
- Voz local: [`firmware/JARVIS_LOCAL.md`](firmware/JARVIS_LOCAL.md)
- Plan completo: [`PLAN_PROYECTO.md`](PLAN_PROYECTO.md)
- Entrega consolidada: [`ENTREGA_FINAL.md`](ENTREGA_FINAL.md)
- Guía para exposición: [`EXPOSICION_PROYECTO.txt`](EXPOSICION_PROYECTO.txt)
- Prueba de micrófono: [`firmware/inmp441_poc`](firmware/inmp441_poc)
- Prueba de voz española: [`firmware/picotts_poc`](firmware/picotts_poc)
- Compilación verificada: [`firmware/COMPILACION_VALIDADA.md`](firmware/COMPILACION_VALIDADA.md)
- Pruebas antes de construir: [`obsidian/proyect domus/16 - Plan de testeo antes de construccion.md`](obsidian/proyect%20domus/16%20-%20Plan%20de%20testeo%20antes%20de%20construccion.md)
- Diagramas generales: [`obsidian/proyect domus/17 - Diagramas generales de conexiones.md`](obsidian/proyect%20domus/17%20-%20Diagramas%20generales%20de%20conexiones.md)
- Cableado pin por pin: [`obsidian/proyect domus/18 - Manual maestro de conexiones pin por pin.md`](obsidian/proyect%20domus/18%20-%20Manual%20maestro%20de%20conexiones%20pin%20por%20pin.md)
- Pruebas después de construir: [`obsidian/proyect domus/19 - Plan de testeo despues de construccion.md`](obsidian/proyect%20domus/19%20-%20Plan%20de%20testeo%20despues%20de%20construccion.md)
- Visualización completa: [`visualizaciones/sistema-domus.html`](visualizaciones/sistema-domus.html)
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
- Fuente regulada de 5 V/3 A para el conjunto; probar audio primero de forma aislada.
- 74AHCT125/74HCT14 recomendado para datos del WS2812B.

Confirma el pinout de la placa antes de soldar. GPIO13 (SCL), GPIO9 (PIR) y GPIO2 (nivel de agua) son asignaciones provisionales. No alimentes altavoz o relés desde 3.3 V del ESP32.

## Compilación

El firmware base se compila automáticamente en GitHub Actions para un
`ESP32S3 Dev Module`, con 16 MB de flash y PSRAM OPI. La compilación usa el
core Arduino-ESP32 3.3.10 y mantiene `JARVIS_LOCAL_HABILITADO=false`.

Para compilar localmente con Arduino CLI:

```powershell
arduino-cli compile --fqbn "esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB" firmware/casa_inteligente_v4
```

La compilación comprueba el software; el pinout, los relés y los sensores aún
deben validarse físicamente con fuente regulada antes de conectar la fase solar.

La compilación offline actual ocupa 402,218 bytes de programa y 25,020 bytes
de memoria global. Los binarios generados están en
`.arduino-local/build/firmware-current/`.

## Comandos locales por USB

El monitor Serial debe usar 115200 baudios y enviar cada orden con salto de línea.
Admite las órdenes ON/OFF/AUTO de las cinco cargas, además de `ESTADO`,
`DIAGNOSTICO`, `PARO`, `REARMAR`, `RECUPERAR`, `MIC_ESTADO` y `SD_PRUEBA`.

## Protección contra bloqueos

El watchdog cubre bloqueos duros. Un supervisor adicional vigila memoria,
reinicios críticos, sensores y ráfagas de comandos. Ante riesgo no intenta
reiniciar indefinidamente: apaga las cargas, suspende automatización/voz y deja
Serial disponible. `DIAGNOSTICO` muestra la causa y `RECUPERAR` libera el modo
seguro únicamente con memoria suficiente; las cargas permanecen apagadas hasta
una orden explícita. Véase el protocolo en
[`obsidian/proyect domus/14 - Protocolo anti-colapso IA y ESP32.md`](obsidian/proyect%20domus/14%20-%20Protocolo%20anti-colapso%20IA%20y%20ESP32.md).

## Servicios Wi‑Fi opcionales

El núcleo offline no depende de ellos. La capa Wi‑Fi podrá integrar MQTT local, Home Assistant, Node-RED, webhooks, NTP, clima y OTA firmada. Spotify se controlará mediante un gateway local y su Web API; el ESP32 no reproducirá directamente el catálogo ni guardará tokens OAuth.

## Limitaciones honestas

- Los modelos Hugging Face de cientos de megabytes no caben en esta placa.
- ESP-SR oficial ofrece comandos en inglés/chino y TTS chino, no un Jarvis español general.
- La voz española local será TinyML de intenciones y PicoTTS. Será entendible pero sintética.
- Riego y ventilación siguen funcionando sin Wi‑Fi.
