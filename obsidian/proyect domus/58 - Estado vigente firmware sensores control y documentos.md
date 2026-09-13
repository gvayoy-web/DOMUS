---
proyecto: PROJECT DOMUS
tipo: estado_vigente
actualizado: 2026-09-12
estado: autoridad_operativa
---

# Estado vigente: firmware, sensores, control y documentos

> [!IMPORTANT]
> La decisión más reciente de firmware y banco es [[59 - Firmware unico y perfil banco S8050 IR]]. Para el montaje actual manda su diagrama `visualizaciones/domus-banco-final-s8050-ir.svg` junto con [[49 - Prueba de una carga con un S8050 y TP4056]].

## Qué hace DOMUS

El ESP32-S3 reúne las mediciones del DHT11, humedad de suelo, nivel de agua, LDR y PIR. El control automático evalúa esos datos y solicita luces, ventilación o riego; el control manual puede solicitar acciones sin anular PARO, nivel mínimo, timeout ni bloqueos de seguridad.

El PIR se comporta como un interruptor automático por presencia: informa movimiento durante una ventana de retención. En una casa real permitiría encender una luz de pasillo al detectar una persona y apagarla después de un tiempo sin movimiento.

## Estado del firmware

| Elemento | Estado comprobado |
|---|---|
| Firmware principal | `firmware/casa_inteligente_v4/`, única base funcional; todavía no validado físicamente como FINAL |
| Perfil de banco vigente | `BANCO_COMPLETO_S8050_IR`: sensores, LCD, luces, bomba S8050 e IR |
| Firmware esqueleto anterior | Referencia histórica y pruebas heredadas; no recibe nuevas funciones |
| Pantalla LCD1602 | Cinco vistas, prioridad de alertas y actualización diferencial |
| Sensores y control | Implementados en software; requieren calibración y HIL físico |
| Bomba | Habilitada en GPIO4 mediante el único S8050; ventilador bloqueado |
| Control IR | Implementado en GPIO12; pendiente aprender los 21 códigos reales |
| Voz/audio | Aplazado; no bloquea la demostración principal |
| TinyML/IA | Fuera del alcance operativo de DOMUS; los documentos existentes son históricos |

Un `ACK` de salida certifica únicamente que el ESP32 aplicó y releyó el nivel
GPIO. No demuestra que una bomba giró, que un ventilador arrancó ni que un
contacto físico conmutó; eso pertenece a la validación HIL.

## Automatización prevista

- Suelo seco + nivel suficiente: permite riego, con histéresis, timeout y rearme seguro.
- Temperatura alta: solicita ventilación cuando exista un driver validado.
- Oscuridad: permite automatizar iluminación según el modo seleccionado.
- Movimiento PIR: presencia temporal para iluminación o aviso; no identifica personas.
- STOP: apaga y bloquea todas las salidas prioritariamente.

Los umbrales no se consideran definitivos hasta ejecutar calibración real en seco/húmedo, vacío/lleno y oscuro/claro.

## Energía vigente

Hay dos ramas:

1. USB alimenta ESP32, sensores, LCD y LEDs.
2. Una fuente externa de 5 V alimenta solamente bomba y ventilador mediante fusible y driver.

Ambas ramas comparten GND. Las mediciones de corriente, caída y temperatura
quedan **SKIP por decisión del propietario (2026-09-12)**, no `PASS`; por tanto
la capacidad de 3 A o 5 A no se declara validada.

Banco mínimo para capturar evidencia restante:
`firmware/domus_banco_integracion/` y
`visualizaciones/domus-banco-lcd-ir-drv8833.svg`.

## GPIO del costado accesible

| Función | GPIO |
|---|---:|
| LDR | 3 |
| Bomba S8050 | 4 |
| Sala | 5 |
| Dormitorio | 6 |
| Ventilador bloqueado | 7 |
| Cultivo LED | 8 |
| PIR | 9 |
| STOP | 10 |
| SILENCIO | 11 |
| Receptor IR | 12 |
| LCD SCL | 13 |
| DHT11 DATA | 14 |
| Suelo AO | 15 |
| Nivel S | 16 |
| LCD SDA | 17 |
| MODO | 18 |

En el perfil vigente, GPIO12 pertenece al receptor IR y GPIO4 controla la bomba
mediante el único S8050. GPIO7 permanece bloqueado y sin ventilador.

## Puertas para validar físicamente el producto

La definición y evidencia exigida está en [[53 - Definicion formal de firmware final y puertas]]. Para el banco actual siguen pendientes la calibración física, los códigos IR y la prueba HIL. El driver doble, ventilador y audio se validarán cuando llegue el hardware; no bloquean probar ahora el núcleo completo con una bomba S8050. Un test simulado no sustituye esas pruebas.

## Documentos vigentes

- Inicio e índice: [[00 - Inicio]]
- Plan maestro: [[46 - Plan maestro de consolidacion un costado]]
- Guía de conexiones: [[47 - Guia visual principiante conexiones alfa]]
- Potencia de una carga: [[49 - Prueba de una carga con un S8050 y TP4056]]
- Definición de FINAL: [[53 - Definicion formal de firmware final y puertas]]
- Orden del repositorio: [[54 - Plan de orden del repositorio]]
- Integración LCD y drivers: [[57 - Integracion LCD backends movimiento 1]]
- Firmware único y banco S8050 + IR: [[59 - Firmware unico y perfil banco S8050 IR]]
- Planos y pruebas canónicos: `hardware/planos/`
- Vista conceptual del LCD: `visualizaciones/domus-lcd-final-mockup.png`

## Regla de honestidad

DOMUS puede aspirar a una evaluación 10/10, pero no se etiqueta como FINAL hasta aportar evidencia física. La puntuación de IA/TinyML se excluye porque no forma parte del alcance aprobado.
