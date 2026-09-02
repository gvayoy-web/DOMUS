# Arquitectura definitiva: cero conexiones móviles

## Regla absoluta

PROJECT DOMUS no contiene aplicación, teléfono, Kotlin, Bluetooth/BLE, Wi-Fi, MQTT,
API, nube, servidor, panel remoto ni dependencia de Internet.

```text
Sensores físicos ─┐
Botones físicos ──┼─> ESP32-S3 N16R8 ─> reglas seguras ─> 5 relés / LCD / aro
Jarvis local ─────┘
```

## Entradas locales

- Humedad de tierra.
- DHT11: temperatura y humedad ambiental.
- LDR: luz ambiental.
- PIR: presencia en la entrada.
- Nivel del depósito.
- Micrófono INMP441, desconectable mediante MIC OFF físico.
- Botones físicos: bomba, sala, dormitorio, ventilador, invernadero, AUTO y emergencia.

Una pulsación cambia el actuador a control manual. Una pulsación prolongada o el botón
AUTO devuelve la función a automatización. `MANUAL_OFF` es un estado persistente y no
puede ser contradicho por las reglas automáticas.

## Salidas locales

1. Bomba de riego.
2. Luz de sala.
3. Luz de dormitorio.
4. Ventilador.
5. Luz de invernadero.
6. LCD1602 de estado.
7. Aro WS2812 de Jarvis.
8. MAX98357A y altavoz para respuestas locales.

## Reglas de seguridad

- Todas las salidas arrancan apagadas.
- La bomba necesita nivel de agua válido y suficiente.
- La bomba se apaga tras 120 segundos y exige rearme.
- Un sensor inválido produce estado seguro, no una activación.
- La ventilación y las luces usan histéresis.
- Las órdenes de voz de baja confianza no modifican salidas.
- MIC OFF corta la captura local del micrófono.
- El paro de emergencia apaga las cinco cargas y bloquea la automatización.

## Qué debe eliminarse del firmware anterior

- `NimBLEDevice` y todo el servicio GATT.
- Comandos y callbacks BLE.
- Estados `ORIGEN_WIFI` y cualquier futura capa MQTT/Wi-Fi.
- Textos del README que prometan Home Assistant, Spotify, OTA o paneles remotos.
- Ocho salidas lógicas: el sistema definitivo usa cinco.

## Fuente de verdad para la migración

`simulator/domus_core.py` define el comportamiento esperado. Las pruebas en
`simulator/test_domus.py` deben mantenerse verdes mientras las reglas se trasladan
al firmware C++ del ESP32-S3.
