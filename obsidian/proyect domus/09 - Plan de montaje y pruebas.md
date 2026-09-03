---
proyecto: PROJECT DOMUS
tipo: pruebas
actualizado: 2026-09-01
---

# Plan de montaje y pruebas

## Fase 0 — antes de comprar más

- [ ] Confirmar físicamente el modelo DHT11 o DHT22.
- [ ] Confirmar cuántos adaptadores I2C LCD hay.
- [ ] Fotografiar ambos lados del ESP32-S3 y su serigrafía de pines.
- [ ] Medir corriente nominal de bomba y ventilador a su voltaje de trabajo.
- [ ] Confirmar voltaje de la tira WS2812.
- [ ] Comprobar el relé de un canal: activo LOW/HIGH y control real con 3.3 V.

## Fase 1 — energía de pared

- [ ] Comprar fuente 5 V/3 A, relé de 4 canales, fusible, capacitores y conectores.
- [ ] Construir barra 5 V/GND en estrella.
- [ ] Verificar 5.0 V sin carga y con bomba/ventilador encendidos.
- [ ] No permitir agua sobre protoboard o fuente.

## Fase 2 — corregir firmware base

- [ ] Sustituir GPIO22 por un pin válido confirmado en la placa.
- [x] Cambiar de ocho relés a cinco en software.
- [x] Eliminar/deshabilitar sensor de viento inexistente.
- [x] Adaptar el firmware al sensor de humedad de suelo resistivo; calibración física pendiente.
- [x] Añadir lógica PIR con GPIO9 provisional; prueba física pendiente.
- [x] Añadir nivel de agua con GPIO2 y umbral provisionales; prueba física pendiente.
- [x] Compilar con LCD1602 como única pantalla; prueba física pendiente.

## Fase 3 — pruebas de cinco funciones

- [ ] Cinco reinicios sin pulsos en relés.
- [ ] Luz sala ON/OFF.
- [ ] Luz dormitorio ON/OFF.
- [ ] Luz invernadero ON/OFF.
- [ ] Ventilador manual y automático.
- [ ] Bomba manual/automática con corte máximo.
- [ ] Una orden manual no es anulada inmediatamente por automatización.
- [ ] Tres ciclos completos sin reset.

## Fase 4 — Jarvis

- [ ] Comprar INMP441, MAX98357A y altavoz.
- [ ] Probar INMP441 aislado.
- [ ] Probar PicoTTS/MAX98357A aislado.
- [ ] Elegir pinout de audio sin conflictos.
- [ ] Entrenar wake word e intenciones.
- [ ] Integrar modo half-duplex y aro WS2812.
- [ ] Montar lector microSD SPI independiente, formatear la tarjeta y verificar lectura/escritura desde el ESP32.
- [ ] Añadir DFPlayer con una segunda tarjeta solo como respaldo si se desea.

## Fase 5 — batería y solar

- [ ] Medir corriente media durante 30 minutos de demo.
- [ ] Registrar pico con bomba, relés, voz y LEDs.
- [ ] Elegir capacidad con la fórmula de [[04 - Energia bateria y solar]].
- [ ] Probar batería con carga electrónica o montaje real.
- [ ] Integrar panel/CN3065 solo al final.
- [ ] Medir tiempo real de carga y no prometer autosuficiencia sin datos.

## Prueba previa a exposición

- [ ] Fuente de respaldo y cables USB.
- [ ] Dos fusibles de repuesto.
- [ ] Multímetro.
- [ ] Jumpers, cinta, bridas y destornillador.
- [ ] Paño absorbente y bandeja bajo depósito.
- [ ] Firmware y video corto de respaldo.
- [ ] LCD muestra estado aunque falle Jarvis.
- [x] Botón/USB Serial usa el mismo despachador si falla el micrófono; prueba física pendiente.
