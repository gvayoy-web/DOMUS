# Validación del paquete offline v1

## Pruebas automáticas

Se ejecutaron 13 pruebas con `unittest`; todas finalizaron correctamente:

- Arranque seguro.
- Histéresis de riego.
- Bloqueo por depósito bajo.
- Corte máximo de bomba y rearme.
- Persistencia de `MANUAL_OFF`.
- Regreso explícito a `AUTO`.
- Histéresis de ventilación.
- Luz de sala condicionada por oscuridad y presencia.
- Expiración del tiempo de presencia.
- Histéresis de luz del invernadero.
- Estado seguro ante fallo de sensor.
- Rechazo de voz con confianza baja.
- Paro de emergencia.

## Diseño

- Modelo OBJ: 87 objetos, 696 vértices y 522 caras.
- Plano técnico: SVG y PDF de una página.
- Visor 3D: JavaScript validado sintácticamente; no usa recursos externos.
- Generador Python: sintaxis validada en Python 3.12.

## Límites

La validación es lógica y geométrica. Antes de cortar material deben medirse el espesor
real, los componentes y la placa. Antes de una exposición deben validarse corriente,
pinout, relés, sensores, bomba, audio y estabilidad de alimentación físicamente.
