# Plan vigente del firmware

## Dueño único

`firmware/casa_inteligente_v4` contiene toda la lógica. El directorio
`firmware/domus_esqueleto` únicamente selecciona el perfil 3 e incluye ese
mismo producto. La implementación anterior está archivada en `firmware/legacy`.

## Capacidades cerradas en software

- Sensores DHT11, suelo, nivel, LDR y PIR.
- LCD1602 I2C con cinco vistas y errores prioritarios.
- Luces, riego y ventilación manual/automática con histéresis.
- PARO, rearme, timeout de bomba, modo seguro y watchdog.
- Calibración validada y persistente en NVS.
- Mando IR de 21 teclas persistente, sin duplicados ni autoridad antes de ser
  aprendido.
- Jarvis como respuestas fijas a órdenes IR, visibles en Serial.
- Diagnóstico sin salidas para obtener dirección LCD, lecturas y códigos.
- Pruebas locales, nativas, semirreales, HIL preparado y CI Arduino.

## Audio

La reproducción audible está aplazada. El MAX98306 comprado necesita una
fuente analógica; no es un receptor I2S ni un reproductor. El núcleo no usa
micrófono ni reconocimiento de voz.

## Pendiente físico

Calibrar sensores reales, aprender el mando concreto, observar LCD, ejecutar
HIL, probar la bomba sumergida e integrar DRV8833/ventilador cuando lleguen.
Ver `firmware/PRUEBA_HOY.md` y la nota Obsidian 62.
