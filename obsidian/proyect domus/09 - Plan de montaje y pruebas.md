---
proyecto: PROJECT DOMUS
tipo: pruebas
actualizado: 2026-09-07
---

# Plan de montaje y pruebas

> [!IMPORTANT]
> La puerta obligatoria antes de cualquier montaje permanente está detallada en
> [[16 - Plan de testeo antes de construccion]]. Después de aprobarla, usar
> [[17 - Diagramas generales de conexiones]].

## Fase 0 — antes de comprar más

- [ ] Confirmar físicamente el modelo DHT11 o DHT22.
- [ ] Confirmar cuántos adaptadores I2C LCD hay.
- [ ] Fotografiar ambos lados del ESP32-S3 y su serigrafía de pines.
- [ ] Medir corriente nominal de bomba y ventilador a su voltaje de trabajo.
- [ ] Confirmar voltaje de la tira WS2812.
- [ ] Comprobar el relé de un canal: activo LOW/HIGH y control real con 3.3 V.

## Fase 1 — energía de pared

- [ ] Confirmar fuente común regulada de 5 V; usar 3 A o más hasta medir consumo.
- [ ] Comprar o confirmar módulo de 4 relés, activo LOW y compatible con lógica de 3.3 V.
- [ ] Construir barra 5 V/GND en estrella.
- [ ] Verificar 5.0 V sin carga y con bomba/ventilador encendidos.
- [ ] No permitir agua sobre protoboard o fuente.

## Fase 2 — corregir firmware base

- [x] Sustituir GPIO22 en software por GPIO13 provisional; confirmación física pendiente.
- [x] Cambiar de ocho relés a cinco en software.
- [x] Eliminar/deshabilitar sensor de viento inexistente.
- [x] Adaptar el firmware al sensor de humedad de suelo resistivo; calibración física pendiente.
- [x] Añadir lógica PIR con GPIO9 provisional; prueba física pendiente.
- [x] Añadir nivel de agua con GPIO2 y umbral provisionales; prueba física pendiente.
- [x] Compilar con LCD1602 como única pantalla; prueba física pendiente.
- [x] Añadir histéresis separada de encendido/apagado para riego y ventilación.
- [x] Añadir supervisor de memoria, reinicios críticos y modo seguro.
- [x] Limitar ráfagas Serial conservando prioridad absoluta para `PARO`.
- [x] Cortar salidas automáticas cuando falla su sensor crítico.
- [x] Ejecutar pruebas de simulador y contratos antes de la compilación en CI.

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

## Fase 5 — batería y solar decorativos

- [ ] Fijar batería y panel sin conexión eléctrica.
- [ ] Aislar y cubrir todos sus terminales.
- [ ] Rotularlos como representación estética.
- [ ] No conectar panel, batería, cargador ni elevador al `5V_BUS`.

## Prueba previa a exposición

- [ ] Fuente de respaldo y cables USB.
- [ ] Dos fusibles de repuesto.
- [ ] Multímetro.
- [ ] Jumpers, cinta, bridas y destornillador.
- [ ] Paño absorbente y bandeja bajo depósito.
- [ ] Firmware y video corto de respaldo.
- [ ] LCD muestra estado aunque falle Jarvis.
- [x] Botón/USB Serial usa el mismo despachador si falla el micrófono; prueba física pendiente.
