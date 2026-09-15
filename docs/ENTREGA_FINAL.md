# PROJECT DOMUS — entrega de software

Estado: software listo para banco; validación física pendiente.

## Producto

- `firmware/casa_inteligente_v4/`: única implementación funcional.
- `firmware/domus_esqueleto/`: wrapper del producto con perfil 3 para el
  hardware disponible hoy.
- `firmware/diagnosticos/domus_banco_integracion/`: lector seguro de LCD,
  sensores, puntos de calibración y códigos IR; no acciona salidas.
- `firmware/legacy/domus_esqueleto/`: implementación anterior archivada.

## Garantías verificables por software

El firmware valida mapa GPIO, perfiles, calibración, histéresis, propiedad
manual/automática, nivel de agua, timeout, PARO, rearme, modo seguro y límites
de entrada Serial. El mando IR exige aprendizaje real y códigos únicos.

Jarvis funciona como interfaz por mando IR y texto de respuesta. No existe una
ruta de IA ni reconocimiento por micrófono. La salida audible se decidirá más
adelante y no bloquea esta entrega.

## Fuera del alcance de software

Quedan pendientes la observación del LCD y sensores reales, valores de
calibración, códigos del mando concreto, prueba HIL, bomba vigilada y la
integración del DRV8833, fuente, fusible, capacitores y audio cuando lleguen.

Ejecutar desde la raíz:

```powershell
python tools/validate_project.py
python tools/validate_markdown.py
```
