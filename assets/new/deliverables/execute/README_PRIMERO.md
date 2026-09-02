# EXECUTE — paquete completo de PROJECT DOMUS

Este ZIP reúne los archivos aportados por el usuario y todos los entregables útiles creados durante este chat.

## Qué carpeta usar

La versión vigente es **`01_FINAL_V2`**. Su maqueta tiene una sola planta abierta al frente, invernadero a la izquierda, vivienda en el centro, porche delante, torre Jarvis y gabinete electrónico a la derecha.

La carpeta **`02_HISTORIAL_V1`** se conserva únicamente porque se pidió incluir todos los cambios realizados. Esa versión contiene la interpretación incorrecta de dos plantas y **no debe fabricarse ni presentarse como diseño final**.

## Contenido

- `01_FINAL_V2`: paquete final corregido con simulador, pruebas, planos, OBJ/MTL, renders, visores HTML, listas de corte y guía de montaje.
- `02_HISTORIAL_V1`: primera propuesta, conservada como historial.
- `03_ORIGINAL_USUARIO`: ZIP original entregado al comienzo de la conversación.
- `04_REFERENCIA`: imagen que define la apariencia y distribución correcta de la maqueta.
- `REQUISITOS_Y_DECISIONES.md`: fuente de verdad de todo lo acordado.
- `CHANGELOG_CHAT.md`: cambios efectuados durante la conversación.

## Inicio rápido

Abrir `01_FINAL_V2/design/modelo_3d_interactivo.html` para explorar el modelo sin Internet.

Ejecutar el simulador desde `01_FINAL_V2`:

```bash
python simulator/domus_simulator.py
```

Ejecutar las pruebas:

```bash
python -m unittest discover -s simulator -p "test_*.py" -v
```

El diseño final y el simulador no necesitan Wi-Fi, Bluetooth/BLE, teléfono, Kotlin, MQTT, servidor ni nube.
