# PROJECT DOMUS — paquete offline de simulación y diseño

Este paquete reemplaza cualquier idea anterior de aplicación móvil o conexión inalámbrica.
El sistema definitivo usa un único ESP32-S3 N16R8 y funciona localmente mediante sensores,
botones físicos, pantalla, automatización y Jarvis local.

## Lo que incluye

- `simulator/domus_core.py`: gemelo digital de las reglas de la casa.
- `simulator/domus_simulator.py`: interfaz gráfica de escritorio, sin red y sin dependencias externas.
- `simulator/test_domus.py`: pruebas automáticas del riego, ventilación, iluminación, modos manuales y seguridad.
- `design/generate_design.py`: generador paramétrico del plano y modelo 3D.
- `design/plano_tecnico_domus.svg` y `.pdf`: plano acotado de fabricación.
- `design/project_domus.obj` y `.mtl`: modelo 3D importable en Blender, FreeCAD y otros programas.
- `design/project_domus_render.png`: vista isométrica del diseño.
- `design/project_domus_exploded.png`: vista 3D con los pisos separados.
- `design/modelo_3d_interactivo.html`: visor local interactivo, sin Internet.

## Ejecutar el simulador

Desde la carpeta raíz del paquete:

```bash
python simulator/domus_simulator.py
```

No abre puertos, no crea servidores y no usa Bluetooth ni Wi-Fi.

## Ejecutar las pruebas

```bash
python -m unittest discover -s simulator -p "test_*.py" -v
```

## Regenerar el diseño

```bash
python design/generate_design.py
```

El modelo usa milímetros. La base general mide 1000 × 700 mm y la vivienda tiene dos pisos.

## Alcance del simulador

El simulador verifica reglas, estados, tiempos, fallos y prioridades. No puede medir corriente,
caídas de voltaje, ruido de micrófono, precisión física de sensores ni comportamiento mecánico
de bombas y relés. Esas pruebas siguen requiriendo el hardware real.
