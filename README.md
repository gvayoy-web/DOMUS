# PROJECT DOMUS

Casa inteligente local para una maqueta con ESP32-S3 N16R8. El firmware reúne sensores, LCD1602, luces, riego y control IR. El estado del software y los límites de las pruebas están en la [auditoría vigente](obsidian/proyect%20domus/63%20-%20Auditoria%20total%20de%20Obsidian%20y%20estado%20real.md).

## Empezar

1. Leer [el inicio de la bóveda](obsidian/proyect%20domus/00%20-%20Inicio.md) y el [índice de rutas](docs/INDICE.md).
2. Para el banco actual, abrir [firmware/domus_esqueleto](firmware/domus_esqueleto/README.md). Es un envoltorio literal del [firmware de producto](firmware/casa_inteligente_v4/README.md) con el perfil BANCO_COMPLETO_S8050_IR.
3. Seguir la [prueba de hoy](firmware/PRUEBA_HOY.md) y el [diagrama vigente del banco](visualizaciones/domus-banco-final-s8050-ir.svg). Para capturar códigos IR y calibraciones sin activar salidas, usar firmware/diagnosticos/domus_banco_integracion/.

El producto vive únicamente en firmware/casa_inteligente_v4/. firmware/legacy/ conserva el esqueleto anterior para regresiones. Jarvis es el mando IR con respuestas fijas de texto; no hay reconocimiento de voz ni IA en el producto.

## Organización

| Carpeta | Contenido |
|---|---|
| firmware/ | Producto, envoltorio de banco, diagnósticos y pruebas |
| hardware/planos/ | Planos y fuentes constructivas canónicas |
| visualizaciones/ | Diagramas SVG y vistas web; el SVG del banco indicado arriba manda para cablear |
| obsidian/proyect domus/ | Decisiones, estado y bitácora; la nota 63 clasifica qué está vigente |
| docs/ | Índice y documentos generales de entrega |
| tools/ | Validadores y generadores |
| assets/new/ y documentos/ | Entregables y documentos históricos; consultar sus índices antes de reutilizarlos |
| output/ | Exportaciones generadas para consulta o impresión |

## Validación local

```powershell
python tools/validate_project.py
python tools/validate_markdown.py
python tools/check_perfil_matrix.py
```

La compilación de producto para ESP32-S3 usa Arduino-ESP32 3.3.10 y las bibliotecas declaradas en la [guía de firmware](firmware/casa_inteligente_v4/README.md). La CI compila varias configuraciones. Simulación y compilación prueban lógica, no el montaje: LCD, sensores, mando real, bomba, calibraciones y HIL siguen pendientes de observación física. El DRV8833, la fuente, el fusible y el audio esperan componentes. No se ha declarado el producto FINAL.
