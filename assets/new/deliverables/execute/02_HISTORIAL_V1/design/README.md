# Diseño físico de PROJECT DOMUS

Todas las medidas del modelo están expresadas en milímetros.

## Medidas generales

| Módulo | Ancho | Fondo | Altura |
|---|---:|---:|---:|
| Base | 1000 | 700 | 9 |
| Vivienda | 620 | 380 | ≈460 total |
| Planta baja | 620 | 380 | 220 |
| Planta alta | 620 | 380 | 210 |
| Invernadero | 290 | 450 | 225 |
| Entrada | 270 | 205 | abierta/cubierta |
| Torre Jarvis | 140 | 220 | 320 |
| Bahía técnica | 160 | 220 | 280 |
| Depósito | 110 | 95 | 120 |

## Distribución

- Planta baja: sala, cocina con barra y escalera compacta.
- Planta alta: dormitorio principal y baño/ducha.
- Lado izquierdo: invernadero con cama de cultivo, humedad de suelo, depósito y bomba.
- Frente: entrada, PIR, torre Jarvis y bahía electrónica.
- Techo: un panel solar didáctico removible.
- Canal frontal: distribución de 5 V, tierra y señales; sin cables de red ni comunicaciones móviles.

## Material recomendado

- Base: plywood o MDF de 9 mm.
- Paredes, pisos y módulos: plywood de 3 mm.
- Invernadero y frente de servicio: acrílico/acetato de 1–2 mm.
- Pestañas de corte: regenerar después de medir el espesor real con calibrador.

## Seguridad física

- Toda la maqueta opera a 5 V DC; no se usa tensión de red dentro de ella.
- La fuente queda fuera o dentro de una bahía aislada y accesible.
- El depósito está separado de la electrónica y usa bandeja de contención.
- La bomba se bloquea por nivel bajo y por tiempo máximo.
- El botón de emergencia y MIC OFF son físicos.
- Techo, entrepiso, torre y frente técnico son removibles.

## Archivos

- `project_domus.obj` y `.mtl`: modelo editable.
- `modelo_3d_interactivo.html`: inspección inmediata en navegador, sin servidor.
- `project_domus_render.png`: vista general.
- `project_domus_cutaway.png`: vista sin techo para inspeccionar los dos pisos.
- `project_domus_exploded.png`: niveles separados verticalmente para revisar la distribución.
- `plano_tecnico_domus.svg` y `.pdf`: plano acotado.
- `piezas_modelo.csv`: inventario geométrico de cada pieza del modelo.
