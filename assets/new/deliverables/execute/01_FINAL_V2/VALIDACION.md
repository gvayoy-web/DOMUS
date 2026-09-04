# Validación del paquete offline v2

## Pruebas automáticas

Se ejecutaron 20 pruebas de comportamiento con `unittest`; todas finalizaron correctamente:

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
- Control manual ON/OFF de las cinco cargas.
- MIC OFF bloquea voz sin bloquear controles físicos.
- Contrato de montaje, lectura y escritura de microSD.
- Respuesta de Jarvis coherente con la acción o el bloqueo de seguridad.
- El paro de emergencia bloquea reactivaciones hasta un rearme explícito.
- El modo seguro bloquea salidas hasta una recuperación explícita y segura.
- El límite de órdenes rechaza ráfagas sin bloquear el paro de emergencia.

Además se ejecutaron 14 pruebas de contrato sobre el firmware:

- exactamente cinco cargas lógicas;
- ausencia de GPIO22 y del falso sensor de viento;
- ausencia de BLE y dependencias de red;
- LCD1602 como única pantalla;
- interlocks de nivel y timeout de bomba;
- paro de emergencia y rearme;
- MIC OFF y botón físico de respaldo;
- prueba real de lectura/escritura preparada para microSD;
- voz y microSD deshabilitadas mientras su hardware no esté validado.
- histéresis separada para riego y ventilación;
- supervisor de memoria, brownout y reinicios críticos sin bucle automático;
- límite de frecuencia Serial con prioridad de emergencia;
- corte de actuadores automáticos ante sensores críticos inválidos;
- disyuntor de voz ante inicialización parcial, fallos o tiempo excesivo.

Total de pruebas automáticas: **34**, todas correctas. El verificador también
comprueba que existen las notas Obsidian 00–14 y que sus Wikilinks resuelven.

## Compilación ESP32-S3

La versión offline se compiló con Arduino CLI 1.5.1, Arduino-ESP32 3.3.10,
flash de 16 MB, PSRAM OPI y `--warnings all`:

- programa: 402,218 bytes de 3,145,728 (12 %);
- memoria global: 25,020 bytes de 327,680 (7 %);
- binario principal: 402,368 bytes;
- SHA-256: `86D7E20080F4239615D638FC4BB7741FE6DAC62C1709C23E1A2043B74B96ECF0`.

## Diseño

- Modelo OBJ: 99 objetos, 792 vértices y 594 caras.
- Plano técnico: SVG y PDF de una página.
- Visor 3D: JavaScript validado sintácticamente; no usa recursos externos.
- Generador Python: sintaxis validada en Python 3.12.
- Geometría corregida a una sola planta y confrontada visualmente con la referencia.

## Límites

La validación es lógica y geométrica. Antes de cortar material deben medirse el espesor
real, los componentes y la placa. Antes de una exposición deben validarse corriente,
pinout, relés, sensores, bomba, audio y estabilidad de alimentación físicamente.
