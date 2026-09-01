# Jarvis local — estado de implementación

`casa_inteligente_v4/casa_inteligente_v4.ino` es la base autónoma de sensores, relés,
automatización y BLE.

## Qué está habilitado ahora

- Sensores y automatización local.
- Control de relés por BLE.
- Estado seguro al reiniciar.
- Pantalla y registro serial.
- Bloque de voz protegido por `JARVIS_LOCAL_HABILITADO`.

## Por qué Jarvis no se activa todavía

El código anterior usaba ESP-SR directamente, pero no incluía un modelo
español validado ni una cadena de captura I2S completa. No se debe activar
`JARVIS_LOCAL_HABILITADO` hasta disponer de:

1. INMP441 conectado y probado a 16 kHz, 16 bit, mono.
2. Dataset de frases “Jarvis + orden” grabado con varias personas.
3. Modelo TinyML español cuantizado (`int8`) y su checksum.
4. PicoTTS español validado con MAX98357A y altavoz.
5. Pruebas de falsos positivos y de eco con el altavoz.

## Contrato de intenciones

El modelo debe producir únicamente una de estas intenciones:

```text
LUZ_SALA_1_ON
LUZ_SALA_1_OFF
LUZ_CUARTO_ON
LUZ_CUARTO_OFF
RIEGO_ON
RIEGO_OFF
VENTILADOR_ON
VENTILADOR_OFF
INVERNADERO_ON
INVERNADERO_OFF
DESCONOCIDO
RUIDO
SILENCIO
```

Frases como “Jarvis, apaga la luz de la sala uno”, “Jarvis, desactiva la luz
de la sala uno” y “Jarvis, deja apagada la sala uno” deben mapear a
`LUZ_SALA_1_OFF`. La inferencia no debe modificar GPIO directamente: debe
crear una orden con origen `VOZ` y pasarla por el mismo despachador que BLE y
la automatización.

## Respuestas

Las respuestas se construirán como texto y PicoTTS las convertirá a PCM en el
ESP32-S3. El MAX98357A reproducirá el PCM por I2S; el DFPlayer queda como legado
opcional para efectos, no como dependencia. Mientras Jarvis habla, el micrófono
se pausa y entra en cooldown para evitar realimentación.

La voz será sintética. PicoTTS no convierte a Jarvis en un LLM: únicamente
pronuncia las respuestas generadas por las reglas y el estado real de la casa.

## Activación segura

No cambiar la bandera a `true` solo para aparentar que Jarvis funciona. La
versión de feria puede demostrar automatización local sin voz y activar la
voz únicamente cuando el modelo haya superado las métricas del plan:

- 90 % de aciertos a 50 cm en silencio.
- 80 % a 1 m con ruido moderado.
- Cero activaciones falsas durante una hora.
- Tres demos completas consecutivas sin reset ni bloqueo.

## Wi‑Fi y servicios

Wi‑Fi debe implementarse como capa opcional: el núcleo offline no puede
depender de internet. Spotify debe pasar por un gateway local con OAuth y
controlar un cliente Spotify existente; el ESP32 no debe intentar descargar
el catálogo ni guardar tokens en el código.
