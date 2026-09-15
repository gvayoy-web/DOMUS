---
estado: vigente
fecha: 2026-09-14
autoridad: 63
---

# PROJECT DOMUS — inicio

DOMUS es una casa automática local con ESP32-S3. Reúne datos de DHT11, suelo,
nivel de agua, LDR y PIR; muestra el estado en LCD y controla luces, bomba y
ventilación en modo automático o manual mediante mando IR.

## Qué usar hoy

- Firmware de producto: `firmware/casa_inteligente_v4/`.
- Esqueleto del banco: `firmware/domus_esqueleto/`; es el producto literal con
  perfil `BANCO_COMPLETO_S8050_IR`.
- Diagnóstico sin salidas: `firmware/diagnosticos/domus_banco_integracion/`.
- Guía de prueba: `firmware/PRUEBA_HOY.md`.
- Diagrama del banco: `visualizaciones/domus-banco-final-s8050-ir.svg`.

## Autoridad vigente

1. [[63 - Auditoria total de Obsidian y estado real]] — clasificación completa.
2. [[62 - Cierre total de software no fisico]] — estado del software.
3. [[61 - Esqueleto literal y diagnostico IR calibracion]] — programas de hoy.
4. [[60 - Orden Git y pruebas multientorno]] — evidencia y límites.
5. [[59 - Firmware unico y perfil banco S8050 IR]] — mapa lógico del banco.
6. [[49 - Prueba de una carga con un S8050 y TP4056]] — prueba temporal.

El único diagrama cableable del banco es
`visualizaciones/domus-banco-final-s8050-ir.svg`. Ninguna nota histórica
autoriza cableado, compras o compilación por sí sola.

## Estado honesto

- Software no físico: cerrado y sometido a pruebas automatizadas.
- Banco: listo para comenzar pruebas con el hardware disponible.
- Hardware: todavía no validado; faltan calibraciones, mando real, LCD y HIL.
- DRV8833, fuente, fusible, capacitores y audio: esperan las compras.
- Jarvis: mando IR y respuestas fijas. No usa IA ni reconocimiento por voz.

Las mediciones eléctricas están `SKIP por decisión del dueño`; no son PASS.
