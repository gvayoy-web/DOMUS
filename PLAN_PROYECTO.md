# Plan definitivo — Casa inteligente con Jarvis local

## Decisiones cerradas

- Una sola placa principal: ESP32-S3 N16R8.
- Sin Kotlin ni aplicación Android.
- Sensores, automatización, relés y órdenes domésticas funcionan sin internet.
- “Jarvis” activa un clasificador TinyML español de intenciones limitadas.
- PicoTTS genera respuestas en español; MAX98357A las reproduce por I2S.
- El DFPlayer queda desactivado y solo podrá usarse para efectos opcionales.
- Wi-Fi, MQTT y Spotify son extensiones; nunca bloquean la casa.
- No se presenta el sistema como un LLM o chatbot general.

## Estado real

### Implementado

- Compilación reproducible del firmware doméstico en GitHub Actions para
  ESP32-S3 N16R8: Arduino-ESP32 3.3.10, flash de 16 MB y PSRAM OPI.
- Binarios generados correctamente: 402,218 bytes de programa y 25,020 bytes
  de memoria dinámica global con Jarvis y microSD desactivados hasta disponer
  del hardware validado.
- Cinco cargas lógicas, LCD, riego, ventilación y luces automáticas. La
  validación física de relés y sensores sigue pendiente.
- Estado seguro de relés durante el arranque.
- Despachador común `OrdenActuador` para manual, automatización, voz y Wi-Fi.
- Propiedad manual/automática por actuador.
- Corte de seguridad de la bomba tras dos minutos continuos.
- Rechazo de órdenes de voz con confianza inferior a 0.75.
- BLE, Wi-Fi y aplicación móvil retirados del núcleo; diagnóstico por USB Serial.
- LCD1602 como única pantalla; soporte OLED retirado.
- DFPlayer desactivado como salida principal.
- Paro físico, MIC OFF, botón local de demostración y contrato microSD integrados.
- Prueba ESP-IDF de PicoTTS español con salida I2S configurable.
- Prueba ESP-IDF del INMP441 a 16 kHz, con búfer de dos segundos en PSRAM,
  medición RMS/pico/DC/saturación y VAD inicial.
- Histéresis coherente entre firmware y gemelo digital para riego,
  ventilación e iluminación.
- Supervisor de salud con modo seguro por memoria crítica o tres reinicios
  críticos consecutivos, sin reinicio automático en bucle.
- Límite de 12 comandos por segundo; `PARO` conserva prioridad absoluta.
- Corte inmediato de salidas automáticas si falla su sensor crítico.
- 20 pruebas de comportamiento y 18 contratos de firmware ejecutados en CI.

### Pendiente de hardware y modelos

- Validación física de la captura desde INMP441.
- Detector local de “Jarvis”.
- Clasificador TinyML español cuantizado `int8`.
- Port y datos españoles de PicoTTS.
- Salida I2S mediante MAX98357A.
- Estados del aro WS2812B.
- Wi-Fi, MQTT y servicios externos quedan fuera del producto base por decisión
  de arquitectura; no son trabajo faltante del núcleo offline.

`JARVIS_LOCAL_HABILITADO` permanecerá en `false` hasta validar micrófono y
modelos en la placa. El bloque ESP-SR antiguo no constituye una implementación
española funcional y será sustituido, no activado.

## Orden de implementación

1. Confirmar el pinout exacto y adquirir INMP441, MAX98357A y altavoz 4 Ω/3 W.
2. **Completado en software:** compilar el firmware doméstico sin módulos de
   voz y generar binarios para ESP32-S3 N16R8. La versión actual de cinco
   relés, PIR y nivel de agua fue recompilada correctamente.
3. **Siguiente fase física:** cargarlo en la placa y validar cinco arranques,
   relés, prioridad manual, corte de bomba y sensores.
4. Compilar, cablear y validar la prueba preparada del INMP441 a 16 kHz.
5. Compilar, cablear y validar la prueba preparada del MAX98357A/PicoTTS.
6. Integrar PicoTTS y pronunciar “Hola, soy Jarvis” en español.
7. Entrenar el detector “Jarvis” y el clasificador de intenciones.
8. Guardar ambos modelos en flash y usar PSRAM para tensores y audio.
9. Integrar el flujo half-duplex: despertar, escuchar, ejecutar, hablar y cooldown.
10. Añadir WS2812B y estados visuales.
11. Medir consumo e integrar la alimentación solar al final.

El cierre verificable por software y la separación de tareas físicas están en
`obsidian/proyect domus/13 - Plan de cierre de codigo.md`.

Los planes ejecutables ya están separados por etapa:

- `16 - Plan de testeo antes de construccion.md` evita fijar un cableado no probado.
- `17 - Diagramas generales de conexiones.md` presenta la arquitectura completa.
- `18 - Manual maestro de conexiones pin por pin.md` define cada borne y GPIO.
- `19 - Plan de testeo despues de construccion.md` acepta o rechaza el montaje final.
- `visualizaciones/sistema-domus.html` permite explorar rutas de energía y conexiones.

## Contrato de voz inicial

```text
LUZ_SALA_1_ON / LUZ_SALA_1_OFF
LUZ_CUARTO_ON / LUZ_CUARTO_OFF
RIEGO_ON / RIEGO_OFF
VENTILADOR_ON / VENTILADOR_OFF
INVERNADERO_ON / INVERNADERO_OFF
ESTADO_TEMPERATURA / ESTADO_HUMEDAD / ESTADO_CASA
DESCONOCIDO / RUIDO / SILENCIO
```

Variantes como “apaga”, “desactiva” y “deja apagada” deben producir la misma
intención. Una intención desconocida o de baja confianza nunca modifica GPIO.

## Criterios de aceptación

- Cinco reinicios sin pulsos visibles en relés.
- Una orden produce como máximo una conmutación.
- Una orden manual no es revertida por automatización.
- La bomba siempre se detiene al llegar al límite de seguridad.
- La casa funciona sin Wi-Fi.
- 90 % de activaciones correctas a 50 cm en silencio.
- 80 % de órdenes correctas a un metro con ruido moderado.
- Cero falsas activaciones durante una hora.
- Jarvis no se escucha a sí mismo mientras habla.
- Tres demostraciones completas consecutivas sin reset ni bloqueo.

## Límites honestos

Jarvis podrá controlar la maqueta y responder usando datos reales, pero no
mantendrá conversación libre. PicoTTS aporta voz dinámica, no inteligencia. Los
servicios Spotify requieren internet, autorización y un dispositivo reproductor;
el ESP32 no descarga el catálogo musical.
