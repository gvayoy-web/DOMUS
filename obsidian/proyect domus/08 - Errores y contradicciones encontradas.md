---
proyecto: PROJECT DOMUS
tipo: auditoria
actualizado: 2026-09-03
---

# Errores y contradicciones encontradas

## Estado tras la primera implementación

- Corregidos en software: GPIO22, ocho relés lógicos, sensor de viento inexistente, identificación del sensor resistivo, PIR y nivel de agua.
- Pendientes de hardware: confirmar los pines provisionales GPIO13/GPIO9/GPIO2, calibrar sensores y validar las cinco cargas en placa.
- Jarvis, la fuente definitiva y la energía solar continúan pendientes según las fases del plan.

## Críticos

1. **GPIO22 no existe en ESP32-S3.** Corregido en software a GPIO13 provisional; falta confirmación física.
2. **El software declaraba ocho relés, pero solo hay uno y el diseño necesita cinco.** Corregido a cinco salidas; aún falta comprar el módulo de cuatro canales.
3. **PIR y nivel de agua no tenían pines ni lógica.** Integrados provisionalmente en GPIO9/GPIO2; no afirmar validación física hasta probarlos.
4. **La voz no está integrada.** Existen PoC separados, pero faltan INMP441, MAX98357A, altavoz y modelos.
5. **La fuente de protoboard no es una fuente general de alta corriente.** Puede causar resets si se conectan bomba, relés, audio y LEDs.

## Importantes

6. El firmware llamaba “capacitivo” al sensor de suelo, pero el inventario confirmado es resistivo. **Corregido en software**; aún debe calibrarse y, si el circuito lo permite, energizarse solo durante lecturas.
7. El firmware leía un supuesto sensor de viento en GPIO2. **Corregido:** esa función fue retirada y GPIO2 queda provisionalmente para nivel de agua.
8. El firmware incluía bibliotecas OLED aunque no hay OLED. **Corregido:** LCD1602 es la única pantalla y las dependencias OLED fueron retiradas.
9. La ranura del DFPlayer no es un sistema de archivos accesible por el ESP32. Falta un lector microSD SPI y una tarjeta propia; si se usa el DFPlayer, requiere una segunda tarjeta.
10. Los capacitores del kit descritos como “104 pF (10k pF)” están mal nombrados. Código 104 = 100,000 pF = 100 nF = 0.1 µF.
11. El 74HC595 existente no sirve como reemplazo directo del 74AHCT125 para la señal WS2812.
12. El cable de batería de 9 V no vuelve adecuada una batería rectangular de 9 V; esa batería no soporta los picos del proyecto.

## Energía

13. Se había mezclado TP4056, CN3065 y BMS como si todos fueran obligatorios. La corrección es elegir una arquitectura y usar una sola protección de batería.
14. Un panel de 3 V/110 mA no sirve para CN3065 ni para sostener la casa.
15. Un pack de 7,500 mAh cargado a 500 mA requiere muchas horas de sol; el solar es respaldo/enseñanza, no autosuficiencia demostrada.
16. El MT3608 debe probarse con la carga real. “2 A” comercial no garantiza 2 A continuos sin caída o calentamiento.

## Documentación

17. “OLED/LCD implementado” era incorrecto. **Corregido:** LCD disponible y único; OLED no requerido.
18. “Ocho relés implementados” era incorrecto. **Corregido:** cinco salidas lógicas para cinco cargas.
19. “Sistema solar” debe presentarse como fase posterior hasta medir generación, consumo y tiempo de carga.
20. El inventario menciona el adaptador I2C dos veces. Confirmar físicamente si hay una o dos placas; solo se necesita una.

## Decisiones corregidas

- Pantalla oficial: LCD1602 I2C.
- Relés: 1 canal existente + 4 canales nuevos.
- microSD: lector SPI + tarjeta obligatorios para almacenamiento directo del ESP32; segunda tarjeta opcional para DFPlayer.
- Fuente de feria: 5 V/3 A.
- Jarvis: TinyML/PicoTTS en flash/PSRAM; DFPlayer solo respaldo.
- Energía: pared primero, batería después, solar al final.
