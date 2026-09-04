# PROJECT DOMUS · revisión 4 compacta

Paquete de fabricación de la **maqueta en crudo**, pensado para enviarse al
equipo que construirá la estructura antes de integrar el circuito.

| Módulo | Ancho (mm) | Fondo (mm) | Alto total (mm) |
|---|---:|---:|---:|
| Base | 800 | 520 | 12 |
| Vivienda de una planta | 344 | 260 | 254 |
| Invernadero | 200 | 280 | 225 |
| Porche | 200 | 156 | 154 |
| Carcasa Jarvis | 84 | 94.4 | 302 |
| Gabinete vacío | 88 | 120 | 269 |

La huella fue reducida linealmente un 20 %, pasando de 1000 × 650 a
800 × 520 mm. Eso representa 36 % menos superficie. Las alturas se conservaron
y también se mantienen las dimensiones mínimas de listones y espesores.

## Alcance

El modelo no contiene componentes instalados ni rutas de cableado o agua. Las
figuras transparentes de la capa `Reservas futuras` indican espacio disponible
para la integración posterior y no forman parte de la lista de corte.

El equipo debe entregar:

- estructura terminada y escuadrada;
- carcasas Jarvis y gabinete vacías;
- canal técnico vacío con tapa;
- techo y frentes removibles;
- reservas marcadas a lápiz;
- ninguna conexión o perforación final.

## Entregables

- `plano_tecnico_domus.pdf` y `.svg`
- `modelo_3d_interactivo.html`
- `project_domus_render.png`, `project_domus_cutaway.png` y `project_domus_exploded.png`
- `project_domus.obj` y `.mtl`
- `lista_corte.csv`
- `piezas_modelo.csv`
- `GUIA_MONTAJE.md`
- `verificacion_geometria_v4.json`

El visor funciona offline y permite girar, medir, seleccionar, buscar, ocultar
capas, aislar piezas, mostrar reservas, separar módulos y guardar una captura.

## Regeneración reproducible

Desde esta carpeta:

```powershell
python -m pip install -r requirements.txt
python generate_design.py
python -m unittest discover -s tests -v
```

El generador escribe exclusivamente dentro de `planos/`. Antes de terminar,
comprueba nombres duplicados, materiales, dimensiones, límites de la base y la
coincidencia básica entre el inventario canónico, CSV, OBJ, visor, SVG, PDF y
vista previa. Al finalizar también reconstruye
`PROJECT_DOMUS_MAQUETA_CRUDA_800x520_V4.zip` con el manifiesto vigente.
