---
proyecto: PROJECT DOMUS
tipo: jarvis
actualizado: 2026-09-03
---

# Jarvis, audio, pantalla y microSD

## Cadena final

```text
INMP441 → audio 16 kHz → detector “Jarvis” → clasificador TinyML
         → orden segura → texto de respuesta → PicoTTS → MAX98357A → altavoz
```

## Dónde se guarda cada cosa

| Elemento | Almacenamiento |
|---|---|
| Firmware | Flash de 16 MB del ESP32-S3. |
| Modelos TinyML int8 | Flash del ESP32-S3. |
| Recursos de PicoTTS | Flash del ESP32-S3. |
| Búfer de audio y tensores | PSRAM de 8 MB. |
| Calibraciones/credenciales | NVS interna. |
| Archivos del ESP32 | lector microSD SPI separado + tarjeta FAT32. |
| MP3 opcionales | segunda microSD dentro del DFPlayer. |

La microSD no vuelve inteligente a Jarvis ni sustituye la flash del modelo, pero sí permite al ESP32 abrir recursos, configuraciones y registros externos.

## Lo que ya tienes

- ESP32-S3 N16R8.
- Tira WS2812 para el aro azul.
- LCD1602 con I2C para estados y respaldo de texto.
- DFPlayer Mini con ranura microSD.
- Buzzers para alarmas.

## Lo que falta

- INMP441.
- MAX98357A.
- Altavoz 4 Ω/3 W.
- Lector/escritor microSD SPI.
- Tarjeta microSD FAT32 para el ESP32.
- Modelo de wake word “Jarvis”.
- Modelo español de intenciones.
- Integración final de PicoTTS.
- Pruebas de eco, ruido y falsos positivos.

## Pantalla

El LCD1602 es la única pantalla soportada. El código detecta automáticamente
las direcciones I2C 0x27/0x3F; OLED y sus dependencias ya fueron retirados.

## microSD y DFPlayer

- Comprar un módulo lector/escritor microSD SPI independiente para el ESP32.
- Comprar una tarjeta de 4 GB FAT32 si se consigue; 8, 16 o 32 GB FAT32 también funcionan y son más fáciles de encontrar.
- TinyML y PicoTTS pueden permanecer en flash/PSRAM; la tarjeta se usa para archivos, configuración, recursos y registros.
- La ranura del DFPlayer solo almacena las pistas que reproduce el propio módulo por órdenes UART.
- Si el DFPlayer se conserva como plan B, necesita otra tarjeta. No compartir una misma tarjeta entre los dos módulos.
- En la consulta actual: lector C&D L149 y microSD Steren 32 GB L159.

## Estado honesto de Jarvis

Los proyectos aislados de INMP441 y PicoTTS existen en el repositorio, pero Jarvis aún no escucha ni habla integrado en el firmware principal. `JARVIS_LOCAL_HABILITADO` debe permanecer en `false` hasta superar las pruebas.

Esto no deja la casa incompleta: el contrato de órdenes, el despachador seguro,
MIC OFF, control físico/Serial, rechazo por confianza y modo seguro ya existen.
La voz es un módulo opcional que puede fallar o deshabilitarse sin detener las
cinco funciones domésticas.

## Métricas mínimas

- 90 % de activaciones correctas a 50 cm en silencio.
- 80 % de órdenes correctas a 1 m con ruido moderado.
- Cero falsas activaciones en una hora.
- Jarvis pausa el micrófono mientras habla.
- Tres demostraciones completas consecutivas sin reinicio.
