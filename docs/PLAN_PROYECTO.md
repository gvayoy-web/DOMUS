# Plan vigente de PROJECT DOMUS

DOMUS es una casa automática local basada en ESP32-S3. El controlador reúne
DHT11, humedad de suelo, nivel, LDR y PIR; muestra el estado en LCD y gobierna
luces, riego y ventilación mediante reglas automáticas o mando IR.

## Software terminado

- Un único firmware de producto con perfiles de hardware.
- Perfil de banco con sensores, LCD, botones, IR, tres LED y una bomba S8050.
- Arranque apagado, PARO prioritario, modo seguro, timeout de bomba y rearme.
- Calibración persistente con validación y checksum.
- Aprendizaje persistente de 21 teclas IR; una tecla no aprendida no acciona
  salidas y un código duplicado es rechazado.
- Diagnóstico seguro independiente para LCD, sensores, calibración e IR.
- Simulación, contratos, pruebas nativas y compilación multiconfiguración en CI.

## Alcance de Jarvis

Jarvis es el nombre de la interfaz: recibe órdenes del mando IR y genera frases
fijas observables por Serial. No usa micrófono, reconocimiento de voz ni modelos
de aprendizaje automático. La reproducción audible está aplazada.

El MAX98306 comprado es un amplificador analógico, no un decodificador ni una
entrada I2S. Antes de implementar audio debe elegirse una fuente de señal
compatible. Esto no bloquea sensores, automatización, LCD, IR ni seguridad.

## Únicos pendientes

Todo lo restante requiere hardware: capturar calibraciones reales, aprender el
mando concreto, observar el LCD, ejecutar HIL, integrar el DRV8833 cuando llegue
y validar el montaje final. Las mediciones eléctricas están registradas como
`SKIP por decisión del dueño`, no como PASS.
