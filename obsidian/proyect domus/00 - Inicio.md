---
estado: vigente
fecha: 2026-09-16
autoridad: 64
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

1. [[64 - Sesion fisica COM9 LCD IR sensores y bomba]] — evidencia física más reciente.
2. [[65 - Arquitectura de audios Jarvis con DFPlayer]] — diseño de voz MP3.
3. [[63 - Auditoria total de Obsidian y estado real]] — clasificación completa.
4. [[62 - Cierre total de software no fisico]] — estado del software.
5. [[61 - Esqueleto literal y diagnostico IR calibracion]] — programas de hoy.
6. [[60 - Orden Git y pruebas multientorno]] — evidencia y límites.
7. [[59 - Firmware unico y perfil banco S8050 IR]] — mapa lógico del banco.
8. [[49 - Prueba de una carga con un S8050 y TP4056]] — prueba temporal.

El único diagrama cableable del banco es
`visualizaciones/domus-banco-final-s8050-ir.svg`. Ninguna nota histórica
autoriza cableado, compras o compilación por sí sola.

## Estado honesto

- Software no físico: cerrado y sometido a pruebas automatizadas.
- Banco: ESP32-S3 identificada en COM9 y firmware de perfil 3 cargado.
- Hardware: IR capturó las 21 teclas; LCD `0x27` estable y sin parpadeos con
  I²C a 50 kHz. DHT11 sigue pendiente, bomba no giró y suelo/nivel continúan
  inválidos. La placa y el bus I²C quedan descartados como causa del LCD.
- DRV8833, fuente, fusible y parte del audio esperan componentes/pruebas.
- Jarvis: mando IR y respuestas MP3 pregrabadas mediante DFPlayer; arquitectura
  definida, integración pendiente. No usa IA ni reconocimiento por voz.

Las mediciones eléctricas están `SKIP por decisión del dueño`; no son PASS.
