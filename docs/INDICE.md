# Índice de PROJECT DOMUS

La [nota 63](../obsidian/proyect%20domus/63%20-%20Auditoria%20total%20de%20Obsidian%20y%20estado%20real.md) clasifica la bóveda y prevalece sobre los planes antiguos. El código define el comportamiento y el [diagrama vigente](../visualizaciones/domus-banco-final-s8050-ir.svg) define el cableado del banco.

| Para | Abrir |
|---|---|
| Entender estado y alcance | [Inicio](../obsidian/proyect%20domus/00%20-%20Inicio.md) y [auditoría 63](../obsidian/proyect%20domus/63%20-%20Auditoria%20total%20de%20Obsidian%20y%20estado%20real.md) |
| Preparar el banco | [Prueba de hoy](../firmware/PRUEBA_HOY.md), nota 61 y SVG del banco |
| Ver DHT11, PIR, IR y cada sketch pin por pin | [Diagramas de todos los firmware](DIAGRAMAS_CADA_FIRMWARE.md) |
| Cargar el firmware | firmware/domus_esqueleto/ para banco; firmware/casa_inteligente_v4/ para producto |
| Consultar pruebas y límites | Nota 60 y [estado breve](ESTADO_ACTUAL.md) |
| Construir la maqueta | hardware/planos/ y hardware/GUIA_MONTAJE.md; confirmar antes el perfil físico |
| Consultar entregables antiguos | [Archivo de entregables](../assets/new/README.md) y [documentos](../documentos/README.md) |

## Rutas estables

- firmware/casa_inteligente_v4/: una implementación de producto; firmware/domus_esqueleto/ la incluye literalmente para el banco.
- firmware/diagnosticos/domus_banco_integracion/: lector seguro de sensores, LCD, IR y calibración, sin accionar salidas.
- firmware/legacy/: código anterior conservado para regresión.
- firmware/tests/: contratos, simulación, nativas y HIL.
- hardware/planos/: planos constructivos canónicos, sus fuentes y pruebas.
- visualizaciones/: diagramas fuente y vistas web.
- obsidian/proyect domus/: autoridad, operación y bitácora; las notas antiguas quedan para trazabilidad.
- tools/: validadores y generadores; output/: exportaciones.

La [entrega de software](ENTREGA_FINAL.md) describe lo comprobado por código. La prueba física y las mediciones eléctricas conservan su estado pendiente o SKIP en la nota 63.
