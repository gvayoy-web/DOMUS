# Estado actual de PROJECT DOMUS

Actualizado: 15 de septiembre de 2026. La [auditoría de Obsidian 63](../obsidian/proyect%20domus/63%20-%20Auditoria%20total%20de%20Obsidian%20y%20estado%20real.md) es la autoridad documental; esta página resume sus conclusiones.

El firmware/casa_inteligente_v4/ concentra el producto. firmware/domus_esqueleto/ incluye esa misma implementación con el perfil BANCO_COMPLETO_S8050_IR. Para escanear I2C, tomar lecturas y capturar códigos IR sin activar salidas, usar firmware/diagnosticos/domus_banco_integracion/.

Los contratos, simulaciones, compilaciones y CI verifican el comportamiento de software. Aún requieren prueba física el LCD, sensores, calibraciones, 21 teclas IR, bomba S8050 vigilada y HIL. El ventilador con DRV8833, la fuente, el fusible, capacitores y audio esperan componentes. Las mediciones eléctricas siguen SKIP por decisión del dueño, no PASS. Jarvis usa mando IR y texto fijo; IA y reconocimiento de voz fueron retirados.

Preparar el banco con [PRUEBA_HOY](../firmware/PRUEBA_HOY.md) y el [diagrama vigente](../visualizaciones/domus-banco-final-s8050-ir.svg). Las notas antiguas y los DOCX se conservan para trazabilidad, sin autoridad para cablear o comprar.
