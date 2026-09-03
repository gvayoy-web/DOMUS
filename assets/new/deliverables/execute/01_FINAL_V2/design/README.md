# Diseño físico de PROJECT DOMUS

Todas las medidas del modelo están expresadas en milímetros.

## Medidas generales

| Módulo | Ancho | Fondo | Altura |
|---|---:|---:|---:|
| Base | 1000 | 650 | 12 |
| Vivienda de una planta | 430 | 325 | 254 total |
| Invernadero | 250 | 350 | 225 |
| Porche/entrada | 250 | 195 | 154 |
| Torre Jarvis | 105 | 118 | 302 |
| Gabinete técnico | 110 | 150 | 269 |
| Depósito | 92 | 92 | 100 |

## Distribución

- Vivienda de una sola planta: cocina y sala integradas, dormitorio y baño/ducha.
- Lado izquierdo: invernadero transparente con dos bancales, humedad de suelo, depósito y bomba.
- Frente: jardín, pasarela y porche cubierto.
- Lado derecho: torre Jarvis y gabinete electrónico transparente.
- Techo: dos paneles solares didácticos removibles.
- Canal frontal: distribución de 5 V, tierra y señales; sin cables de red ni comunicaciones móviles.

## Material recomendado

- Base: MDF de 12 mm.
- Paredes, pisos y módulos: plywood de 3 mm.
- Invernadero y frente de servicio: acrílico/acetato de 1–2 mm.
- Pestañas de corte: regenerar después de medir el espesor real con calibrador.

## Seguridad física

- Toda la maqueta opera a 5 V DC; no se usa tensión de red dentro de ella.
- La fuente queda fuera o dentro de una bahía aislada y accesible.
- El depósito está separado de la electrónica y usa bandeja de contención.
- La bomba se bloquea por nivel bajo y por tiempo máximo.
- El botón de emergencia y MIC OFF son físicos.
- Techo, torre y frente del gabinete técnico son removibles.

## Archivos

- `project_domus.obj` y `.mtl`: modelo editable.
- `modelo_3d_interactivo.html`: inspección inmediata en navegador, sin servidor.
- `project_domus_render.png`: vista general.
- `project_domus_cutaway.png`: vista sin techo para inspeccionar el único nivel.
- `project_domus_exploded.png`: módulos removibles separados para revisar la distribución.
- `plano_tecnico_domus.svg`: preview vectorial de implantación.
- `plano_tecnico_domus.pdf`: copia canónica compatible del juego multipágina.
- `../../../../../../output/pdf/planos_tecnicos_project_domus.pdf`: juego final A3 apaisado de 6 páginas.
- `visor_desktop_1440x900.png` y `visor_mobile_390x844.png`: comprobaciones visuales del visor.
- `verificacion_visor.json`: resultado reproducible de la prueba responsive.
- `piezas_modelo.csv`: inventario geométrico de cada pieza del modelo.
- `lista_corte.csv`: lista de corte estructural resumida.
- `bom_componentes.csv`: lista de materiales y electrónica.
- `GUIA_MONTAJE.md`: explicación completa de la maqueta.

## Regeneración

Desde la raíz del repositorio, ejecutar un único comando:

```powershell
python assets/new/deliverables/execute/01_FINAL_V2/design/generate_design.py
```

El generador vuelve a crear el visor autónomo, el inventario de 203 elementos, OBJ/MTL, tres renders, el SVG y el PDF técnico. Requiere Python con Pillow y ReportLab; no descarga recursos ni usa red.
