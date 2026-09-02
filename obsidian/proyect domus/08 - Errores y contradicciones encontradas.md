---
proyecto: PROJECT DOMUS
tipo: auditoria
actualizado: 2026-09-01
---

# Errores y contradicciones encontradas

## Críticos

1. **GPIO22 no existe en ESP32-S3.** El firmware lo usa como I2C SCL; el LCD no puede cablearse así.
2. **El software declara ocho relés, pero solo hay uno y el diseño necesita cinco.** Comprar un módulo de cuatro canales y corregir la cuenta lógica.
3. **PIR y nivel de agua aparecen en la documentación, pero no tienen pines ni lógica en el firmware principal.** No afirmar que funcionan hasta integrarlos.
4. **La voz no está integrada.** Existen PoC separados, pero faltan INMP441, MAX98357A, altavoz y modelos.
5. **La fuente de protoboard no es una fuente general de alta corriente.** Puede causar resets si se conectan bomba, relés, audio y LEDs.

## Importantes

6. El firmware llama “capacitivo” al sensor de suelo, pero el inventario confirmado es resistivo. Debe calibrarse como el módulo real y, para reducir corrosión, energizarse solo durante lecturas si el circuito lo permite.
7. El firmware lee un supuesto sensor de viento en GPIO2, pero no existe uno confirmado. El motor con aspa es un ventilador, no un sensor calibrado.
8. El firmware incluye bibliotecas OLED aunque no hay OLED. No obliga a comprarla; el LCD es suficiente.
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

17. “OLED/LCD implementado” describe capacidad del código, no hardware disponible. Debe decir “LCD disponible; OLED no requerido”.
18. “Ocho relés implementados” describe ocho GPIO, no ocho relés físicos.
19. “Sistema solar” debe presentarse como fase posterior hasta medir generación, consumo y tiempo de carga.
20. El inventario menciona el adaptador I2C dos veces. Confirmar físicamente si hay una o dos placas; solo se necesita una.

## Decisiones corregidas

- Pantalla oficial: LCD1602 I2C.
- Relés: 1 canal existente + 4 canales nuevos.
- microSD: lector SPI + tarjeta obligatorios para almacenamiento directo del ESP32; segunda tarjeta opcional para DFPlayer.
- Fuente de feria: 5 V/3 A.
- Jarvis: TinyML/PicoTTS en flash/PSRAM; DFPlayer solo respaldo.
- Energía: pared primero, batería después, solar al final.
