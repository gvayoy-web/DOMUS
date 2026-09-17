# Jarvis local — alcance vigente

Jarvis es la interfaz de personalidad de DOMUS, no un asistente de inteligencia
artificial. Recibe órdenes mediante el mando IR CAR MP3 y construye respuestas
fijas usando el estado real de la casa.

## Implementado

- Aprendizaje persistente de 21 teclas.
- Bloqueo de teclas no aprendidas y códigos duplicados.
- Rechazo de repeticiones para acciones críticas.
- Ejecución por el mismo despachador seguro usado por Serial y automatización.
- Respuestas de texto `JARVIS_TEXTO` para acciones IR aceptadas o rechazadas.
- Botón SILENCIO independiente de PARO y de la seguridad.

## Audio DFPlayer definido, integración aplazada

La fuente elegida es DFPlayer Mini con microSD FAT32, carpetas numéricas y
cuatro MP3 por evento. El ESP32 seleccionará una variante sin repetir la última
y enviará `playFolder(carpeta, pista)` por UART sin bloquear la casa. El catálogo,
prioridades y puertas físicas están en
`obsidian/proyect domus/65 - Arquitectura de audios Jarvis con DFPlayer.md`.

El MAX98306 comprado solo amplifica una señal analógica. No acepta I2S, no
decodifica MP3 y no genera frases. Hasta integrar DFPlayer, asignar GPIO libres
y validar microSD/parlante, las respuestas se observan por Serial y las
acciones siguen funcionando normalmente.

No se requiere micrófono, dataset, entrenamiento ni reconocimiento de voz.
Wi‑Fi y servicios externos tampoco forman parte del núcleo de DOMUS.
