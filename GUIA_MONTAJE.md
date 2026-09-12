# Guía de armado · PROJECT DOMUS · maqueta cruda

## Objetivo de esta entrega

Construir únicamente la maqueta física sobre una base de **800 × 520 mm**. El
equipo de armado no debe instalar sensores, placas, luces, bomba, tubería,
cables, fuente ni conexiones. Esos elementos se integrarán después.

La reducción es del 20 % en ancho y fondo frente a la propuesta anterior. Las
alturas se conservaron para mantener una presentación clara y suficiente espacio
vertical. El área ocupada baja un 36 %.

## Qué sí deben construir

1. Base, faldón frontal y marcas de ubicación.
2. Vivienda de una planta con frente abierto.
3. Mobiliario y divisiones interiores indicados.
4. Porche, pasarela e invernadero.
5. Carcasa Jarvis vacía y con frente accesible.
6. Gabinete técnico vacío y removible.
7. Canal técnico inferior vacío y con tapa.
8. Techo y paneles de servicio removibles.

## Qué no deben instalar

- ESP32, relés, fusible, borneras o fuente.
- Sensores, pantalla, micrófono, altavoz, LEDs o paneles solares.
- Bomba, depósito definitivo, mangueras o conexiones de agua.
- Cableado, perforaciones finales o pegamento dentro de las reservas.

Las zonas moradas o transparentes del visor son **reservas**, no piezas que se
deban fabricar. Solo deben marcarse suavemente a lápiz.

## Orden de armado

1. Cortar la base de 800 × 520 mm y comprobar escuadra.
2. Transferir las huellas del plano a lápiz sin pegar nada.
3. Presentar en seco la vivienda, sus tabiques y el mobiliario.
4. Montar porche e invernadero y comprobar la vista frontal.
5. Construir las carcasas de Jarvis y del gabinete completamente vacías.
6. Colocar el canal técnico vacío y fabricar una tapa removible.
7. Comprobar que techo, gabinete y frentes se desmontan sin forzar.
8. Lijar, limpiar y entregar sin instalaciones ni perforaciones definitivas.

## Control de calidad antes de entregar

- Base plana, sin torsión y de 800 × 520 mm.
- Todos los módulos dentro de la base.
- Fachada abierta y vivienda de una sola planta.
- Techo y tapas removibles.
- Invernadero alineado y paneles transparentes sin tensión.
- Jarvis, gabinete y canal técnico completamente vacíos.
- Reservas visibles a lápiz y claramente rotuladas.
- Ninguna conexión eléctrica o hidráulica instalada.

## Archivos principales

- `hardware/plano_tecnico_domus.pdf`: juego de planos para el equipo de armado.
- `lista_corte.csv`: medidas de las piezas estructurales.
- `modelo_3d_interactivo.html`: visor offline con cotas y reservas.
- `project_domus.obj` y `hardware/project_domus.mtl`: modelo editable.
- `hardware/verificacion_geometria_v4.json`: validación automática de la geometría.

Todas las cotas, renders, el OBJ, el CSV de geometría y el visor se regeneran
desde `generate_design.py`. No deben modificarse por separado.
