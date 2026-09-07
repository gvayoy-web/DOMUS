---
proyecto: PROJECT DOMUS
tipo: migracion
actualizado: 2026-09-01
fuente: assets/new/deliverables/execute
---

# Migración de deliverables y del historial del chat

> [!WARNING]
> Snapshot histórico del diseño v3. Para fabricar usar exclusivamente
> `planos/new` y [[36 - Configuracion final 1 mas 4 reles y planos v4]].

## Resultado histórico de la revisión

La carpeta `assets/new/deliverables/execute` fue el paquete más completo de la
versión v3. No todo tiene el mismo nivel de autoridad. `01_FINAL_V2` se conserva
como referencia histórica; la fuente constructiva vigente es `planos/new`.

## Qué sí se puede usar

| Recurso | Uso recomendado | Estado |
|---|---|---|
| `output/pdf/planos_tecnicos_project_domus.pdf` y `01_FINAL_V2/design/plano_tecnico_domus.svg` | Juego v3 A3: planta, elevaciones, electricidad, riego y montaje | Usar como propuesta; medir componentes reales primero |
| `01_FINAL_V2/design/lista_corte.csv` | Comprar/cortar base, paredes, techo, torre y gabinete | Usar; ajustar al espesor real |
| `01_FINAL_V2/design/bom_componentes.csv` | Comparar electrónica prevista con el inventario confirmado | Usar como BOM de diseño, no como inventario de compras |
| `01_FINAL_V2/design/GUIA_MONTAJE.md` | Orden físico, separación de agua/electrónica y pruebas | Usar |
| `01_FINAL_V2/design/modelo_3d_interactivo.html` | Gemelo digital v3 con ocho vistas, 20 capas e inspector | Usar offline; verificado en escritorio y móvil |
| `01_FINAL_V2/design/project_domus.obj/.mtl` | Editar o mostrar el modelo 3D | Usar |
| `01_FINAL_V2/design/project_domus_render.png`, `project_domus_cutaway.png` y `project_domus_exploded.png` | Banner, interior y secuencia de montaje | Usar |
| `01_FINAL_V2/simulator/domus_core.py` | Fuente de comportamiento para migrar reglas al ESP32 | Usar como especificación lógica |
| `01_FINAL_V2/simulator/test_domus.py` | Pruebas de regresión de riego, luces, ventilador y seguridad | Mantener verdes y ampliar |
| `01_FINAL_V2/ARQUITECTURA_OFFLINE.md` | Decisiones de operación local | Usar, con las correcciones de inventario de esta bóveda |
| `01_FINAL_V2/VALIDACION.md` | Evidencia de 17 pruebas lógicas y geométricas | Usar con sus límites explícitos |

## Qué no debe tomarse como diseño final

| Recurso | Motivo |
|---|---|
| `02_HISTORIAL_V1/**` | Tiene dos plantas, entrepiso y escalera; contradice la casa abierta de una sola planta elegida |
| `03_ORIGINAL_USUARIO/**` | Es material de entrada sin la corrección posterior; sirve para comparar, no para cortar |
| `04_REFERENCIA/**` | Imagen de inspiración y composición, no plano con cotas ni lista de conexiones |
| Cualquier texto que prometa Kotlin, aplicación móvil, BLE, MQTT, nube o Home Assistant | El alcance vigente es local y no debe reintroducir dependencias eliminadas |

## Correcciones necesarias antes de reutilizar el BOM

El BOM de `01_FINAL_V2` describe un sensor capacitivo de suelo y un aro WS2812 de 16 LED. El inventario confirmado del proyecto tiene un sensor resistivo y una tira WS2812 cuya cantidad exacta debe contarse. Por tanto:

- usar el sensor resistivo que ya existe para la primera demo y documentar que requiere calibración y se corroe más rápido;
- no comprar un sensor capacitivo salvo que se quiera mejorar la versión final;
- contar físicamente los LED de la tira antes de dimensionar corriente y decidir si el aro será de 8, 16 o una pieza decorativa;
- el BOM también presupone INMP441, MAX98357A, altavoz, fuente regulada, fusible y dos paneles: siguen siendo faltantes hasta que se confirmen físicamente;
- el lector microSD SPI y una tarjeta FAT32 son compras separadas para el ESP32. La ranura del DFPlayer solo sirve para las pistas del DFPlayer; si ambos se usan, son dos funciones y preferiblemente dos tarjetas.

## Plan de implementación de las ideas útiles

### Fase 0 — congelar la fuente de verdad

1. Conservar `01_FINAL_V2` como referencia histórica; fabricar únicamente desde `planos/new`.
2. Mantener esta bóveda como registro de decisiones y no editar decisiones técnicas solo en un chat.
3. Etiquetar cada cambio como `DECIDIDO`, `PENDIENTE`, `MEDIDO` o `DESCARTADO`.

### Fase 1 — simulador como contrato

1. Ejecutar las 17 pruebas de `simulator/test_domus.py`.
2. Casos para los cinco relés, MIC OFF, lectura/escritura microSD y respuestas de Jarvis: completados en software.
3. No añadir una regla al firmware si antes no existe un caso reproducible en el simulador.

### Fase 2 — migración al ESP32-S3

1. Crear módulos C++ separados: `sensors`, `actuators`, `safety`, `ui_lcd`, `jarvis_audio`, `storage_sd` y `main`.
2. Copiar primero estados, umbrales, histéresis, timeout de bomba, `MANUAL_OFF`, `AUTO` y paro de emergencia.
3. Reasignar GPIO22: no existe en el ESP32-S3. Validar también que UART, I2C, SPI, USB y relés no compartan pines.
4. Montar la microSD del ESP32 por SPI con FAT16/FAT32; reservar la tarjeta del DFPlayer para audio, si se conserva.
5. Probar cada sensor y carga por separado antes de activar automatización.

### Fase 3 — Jarvis local incremental

1. Primero aro azul + botón MIC OFF + LCD de estado.
2. Después INMP441 por I2S y detector de palabra de activación.
3. Luego clasificador de intenciones limitado (sala, dormitorio, invernadero, ventilador y riego).
4. Finalmente PicoTTS/MAX98357A o un conjunto pequeño de frases de respaldo en DFPlayer.
5. Rechazar confianza baja, pausar captura mientras habla y conservar botones físicos como respaldo.

### Fase 4 — maqueta y exposición

1. Cortar base de 800 × 520 mm y vivienda de 344 × 260 mm solo después de medir espesores.
2. Mantener depósito y mangueras en el extremo izquierdo, gabinete transparente a la derecha y techo removible.
3. Etiquetar cada sensor, relé, fusible, switch y flujo de agua.
4. Preparar una demostración repetible: arranque seguro, luz por presencia, ventilación por temperatura, riego bloqueado por nivel bajo y una orden local de Jarvis.

## Ideas que sí sirven frente a ideas que no sirven

### Sí sirven

- gemelo digital offline y pruebas automáticas;
- plano acotado y piezas desmontables;
- separación física entre agua y electrónica;
- límites de seguridad y paro de emergencia;
- lector microSD dedicado para archivos del ESP32;
- botones físicos de respaldo y MIC OFF;
- identidad visual: torre azul, aro luminoso y gabinete transparente.

### No sirven para la versión escolar actual

- fabricar la versión de dos plantas de V1;
- reintroducir Kotlin, aplicación móvil, BLE, MQTT o nube;
- prometer que el simulador demuestra autonomía solar o reconocimiento de voz real;
- usar el DFPlayer como si fuera una unidad de almacenamiento que el ESP32 puede montar;
- comprar otro ESP32, OLED o relé de ocho canales sin una función concreta;
- mezclar baterías recicladas de capacidades o estados desconocidos.

## Migración del chat: decisiones preservadas

Estas son las decisiones que deben sobrevivir a cualquier conversación nueva:

1. Nombre: **PROJECT DOMUS**.
2. Control principal: un ESP32-S3 N16R8.
3. Funcionamiento: local; Kotlin y la aplicación móvil quedan eliminados.
4. Casa: una planta, abierta al frente, con invernadero a la izquierda, vivienda al centro, torre Jarvis y gabinete a la derecha.
5. Cinco cargas: bomba, luz de sala, luz de dormitorio, luz de invernadero y ventilador.
6. Seguridad: arranque apagado, histéresis, bloqueo por nivel, timeout de bomba de 120 s, `MANUAL_OFF` persistente y emergencia.
7. Audio: INMP441 + clasificación limitada + PicoTTS/MAX98357A si el hardware y el tiempo lo permiten; DFPlayer como respaldo opcional.
8. Almacenamiento: lector microSD SPI + tarjeta propia para el ESP32; tarjeta separada para DFPlayer si se utiliza.
9. Estado: el simulador está validado; el firmware físico, audio, energía y calibración siguen pendientes.

## Cómo iniciar un chat futuro sin perder contexto

Copiar este resumen inicial:

> Estoy trabajando en PROJECT DOMUS. Usa como fuente de verdad las notas 00 y 36. El diseño físico vigente es `planos/new`, 800 × 520 mm. La salida elegida usa un relé individual más un módulo de cuatro relés. El sistema es local en ESP32-S3, sin Kotlin, app, BLE, MQTT ni nube. Distingue siempre entre “ya tengo”, “falta comprar”, “pendiente de medir” y “descartado”.

Antes de proponer una compra o cambiar el plano, comprobar esta bóveda y el inventario confirmado. Si una idea contradice estas decisiones, marcarla como propuesta y no como cambio aprobado.

## Próximo paso recomendado

Usar `planos/new` v4 para fabricar, pero cerrar el mapa de GPIO y medir
espesores/componentes físicos antes de cortar o cablear. Comprar primero fuente
5 V, módulo de cuatro relés, fusible y cableado. microSD, Jarvis y solar quedan
detrás de esa prueba.
