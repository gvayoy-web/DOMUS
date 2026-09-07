---
fecha: 2026-09-05
estado: viable_para_prototipo_condicionado_no_integrado
hardware: ESP32-S3 N16R8
---

# Barista + DOMUS: viabilidad, memoria, voz y entrenamiento

> Estudio histórico de viabilidad. El estado ejecutable vigente está en
> [[34 - Cierre de software y matriz de verificacion]].

## Decisión

**Sí merece un prototipo de integración por texto. No está aprobada todavía la conversación hablada libre en español.** Hay margen aparente de almacenamiento, pero no existe un binario combinado ni medición conjunta de memoria y latencia. No activar `JARVIS_LOCAL_HABILITADO` ni cargar el ejemplo externo sobre DOMUS para aparentar integración.

Se propone reutilizar la arquitectura y el motor de Barista; los pesos de café no son un Jarvis español. Esta nota complementa [[23 - Cierre de robustez y entrenamiento pendiente]], no marca sus pendientes como resueltos.

## Evidencia de tamaño

Base auditada: commit `cb193013de5b991d6f77b3b2ddc6ca9b38dd4ab1`, árbol inicialmente limpio.

| Elemento | Bytes | Qué demuestra |
|---|---:|---|
| DOMUS: programa informado en compilación registrada | 414338 | Núcleo sin voz, MP3 ni SD |
| DOMUS: archivo de aplicación local verificado | 414496 | Archivo `build/prod_n16r8_v2/casa_inteligente_v4.ino.bin` |
| DOMUS: variables globales registradas | 25092 | RAM estática, NO pico de RAM |
| Micrófono aislado: binario CI | 245440 | `0x3bec0`, captura/VAD, no reconocimiento |
| PicoTTS español aislado: binario CI | 1287712 | `0x13a620`, recursos españoles embebidos |
| Barista: pesos publicados | 4600186 | Excluye el firmware del motor |
| Capacidad nominal flash N16R8 | 16777216 | 16 MiB; no toda es partición de aplicación |
| Capacidad nominal PSRAM N16R8 | 8388608 | 8 MiB; no equivale a SRAM ni a DMA interno |

SHA-256 verificado del binario DOMUS local:
`F096E686F305820D85C5301D764145D6E904C2F20220072B5186F2F844C66998`.

Los tamaños de audio se consultaron en el [registro CI existente](https://github.com/gvayoy-web/domusv1/actions/runs/33943233605), no se midieron en una placa. Los binarios aislados NO se suman para obtener un firmware integrado: duplican bibliotecas y faltan motor LLM, reconocimiento, colas y adaptación. La suma orientativa de esos tres binarios y pesos es 6547834 bytes (6.24 MiB), **ni tamaño final ni cota garantizada**.

El archivo `merged.bin` de 16 MiB es una imagen con relleno; NO significa que el programa consuma toda la flash. El ELF incluye información de enlace/depuración y tampoco equivale al tamaño de aplicación.

## Memoria de Barista: referencia externa

El autor publica una ejecución N16R8 con 5.55 MiB de PSRAM libres y aproximadamente 288 KiB de SRAM interna libre en un punto del arranque; no son mínimos bajo carga conjunta. El modelo ocupa 4.6 MB en flash y trabaja con tablas mapeadas, cachés y pesos preparados en RAM. [Firmware del autor](https://github.com/slvDev/esp32-ai/blob/main/firmware/esp32_barista/README.md).

No sumar memoria libre de dos programas independientes. Medir un único firmware después de iniciar DOMUS, motor, captura y TTS, y durante cada fase. Registrar por separado RAM interna, PSRAM, bloque libre mayor, mínimo histórico y margen de pila de cada tarea. El `esp_get_free_heap_size()` actual no permite decidir por sí solo si una reserva interna/DMA concreta cabe.

## Particiones: cambio necesario, no aplicado

DOMUS usa `app3M_fat9M_16MB`: dos aplicaciones de 3 MiB, FAT desde `0x610000` y coredump final. No tiene partición de pesos LLM. La PoC TTS usa otro mapa (aplicación de 6 MiB). No copiar ninguno sin diseñar el mapa combinado.

El ejemplo externo busca `model`, subtipo `0x40`. La rama ESP-SR de DOMUS también usa el nombre `model` para otro formato. **Reservar nombres distintos**, por ejemplo `llm_model` y `srmodels`, y adaptar explícitamente los cargadores. No escribir pesos en offsets de un tutorial: pueden pisar aplicaciones o archivos.

Primero medir aplicación integrada y recursos. Después diseñar y validar offsets, alineación, tamaño, OTA y coredump; conservar NVS/calibración y respaldar archivos antes de cualquier reparticionado. Mantener actualizaciones es un requisito a decidir con espacio medido, no quitar OTA silenciosamente para que quepa.

## Riesgos de bloqueo o reinicio

Inspección del [sketch Barista](https://github.com/slvDev/esp32-ai/blob/main/firmware/esp32_barista/esp32_barista.ino): `answer()` es síncrono, la coordinación entre núcleos usa espera indefinida y una reserva fallida puede entrar en bucle permanente. Son incompatibilidades de integración con un controlador, no pruebas de que la demostración aislada falle.

| Riesgo al combinar | Protección requerida |
|---|---|
| Generación dentro del loop doméstico retrasa PARO y sensores | Tarea IA independiente, prioridad inferior al control, sin GPIO directos |
| Ambos núcleos ocupados y watchdog de DOMUS de 8 s | Probar inicialmente un núcleo para IA; cesión real y cancelación entre unidades de trabajo |
| Trabajador bloqueado o reserva fallida | Esperas acotadas, salida con error y limpieza; no matar una tarea que aún comparte buffers |
| SRAM/DMA agotada aunque quede PSRAM | Reservas explícitas, comprobación de cada asignación y métricas por tipo de memoria |
| Fragmentación o muchas preguntas | Una inferencia activa, cola de una solicitud, buffers preasignados y rechazo al saturarse |
| Texto generado se interpreta como orden | Salida LLM exclusivamente informativa; actuadores solo por despachador validado |
| Pantalla compite por I2C | Un propietario del bus; usar LCD1602 existente, no añadir OLED ni su pinout |
| Amplificador/bomba provocan caída de alimentación | Banco de alimentación y picos de carga; el watchdog no corrige un brownout |

Si falla solamente IA, deshabilitar IA y conservar el control que siga sano. Si falla el supervisor doméstico, conservar su modo seguro y apagado de cargas. No ocultar falta de memoria elevando límites ni alimentar el watchdog desde una tarea distinta para disimular un control detenido.

## Micrófono y salida hablada

Cadena necesaria:

```text
INMP441 -> PCM -> reconocimiento voz/texto -> pregunta -> modelo DOMUS -> texto -> PicoTTS -> MAX98357A
                       PENDIENTE            PENDIENTE adaptación/integración
Órdenes autorizadas ----------------------> despachador DOMUS -> actuadores
```

Barista acepta texto, no muestras de audio. `ai/train.py` entrena un clasificador de 14 clases, no un transcriptor ni un LLM. Detectar una orden conocida NO permite transcribir «¿cómo hiciste un proyecto tan hermoso?». La conversación por voz libre queda bloqueada hasta seleccionar y demostrar un reconocedor español local que quepa. Una demostración por órdenes limitadas debe declararlo y no presentarse como transcripción libre.

La PoC INMP441 reserva 64000 bytes para dos segundos PCM16 mono a 16 kHz en PSRAM, 2048 bytes de bloque crudo interno, pila de 4096 bytes y DMA adicional. Dos segundos de anillo no conservan una pregunta larga: se sobrescriben. Diseñar captura acotada o procesamiento incremental antes de usar frases completas.

| Conexión de pruebas existente | Pin |
|---|---|
| INMP441 VDD / GND / L-R | 3.3 V / GND / GND |
| INMP441 WS / SD / SCK | GPIO15 / GPIO16 / GPIO17 |
| MAX98357A BCLK / LRC / DIN | GPIO40 / GPIO41 / GPIO42, provisionales |
| MAX98357A VIN / GND | Alimentación 5 V prevista / masa común |
| Altavoz | Entre SPK+ y SPK-, nunca a masa |
| LCD1602 SDA / SCL | GPIO21 / GPIO13, SCL pendiente de confirmar físicamente |

No flashear estas conexiones como pinout definitivo. Los pines TX 40/41/42 todavía deben añadirse a la comprobación central de pines únicos. Auditar módulos, niveles del bus y placa real con [[18 - Manual maestro de conexiones pin por pin]].

Las PoC usan ESP-IDF y DOMUS Arduino: requieren unificar versión/componentes y asignación de controladores I2S. `I2S_NUM_AUTO` de ejemplos separados no demuestra convivencia. Elegir inicialmente escuchar -> procesar -> hablar, sin captura durante TTS, con cooldown y respeto de MIC OFF. Esto reduce solapamiento y eco, pero no libera automáticamente memoria ya reservada.

## Entrenamiento de Jarvis: alcance real

Barista publicado es inglés, ASCII, vocabulario de salida restringido, contexto de 128 tokens y sin historial conversacional. Los datos y checkpoints de entrenamiento no están publicados. Los pesos desplegables no son un checkpoint listo para ajuste convencional. [Ficha y limitaciones](https://huggingface.co/slvDev/esp32-ai-barista).

Ruta propuesta, no ejecutada:

1. Reproducir inferencia de Barista en host y medir versión aislada en placa.
2. Verificar y adaptar la ruta de entrenamiento de la arquitectura del repositorio; no asumir que reproduce Barista automáticamente. Estimar equipo, duración y recursos antes de entrenar.
3. Preparar corpus propio de preguntas/respuestas españolas sobre DOMUS, humor moderado, desconocidos y respuestas breves. Textos sintéticos revisados; sin audios personales ni API en funcionamiento.
4. Separar entrenamiento, validación y test por familias de preguntas/paráfrasis para evitar evaluar memorización. Reservar preguntas inéditas y mal escritas.
5. Diseñar vocabulario/tokenizador español y tratamiento explícito de ñ/tildes; ajustar embeddings, salida y tablas conjuntamente. No basta un prompt español. Mostrar valores reales de sensores mediante formato determinista, no números inventados por el modelo.
6. Entrenar en computadora; exportar cuantizado, vocabulario, tablas, configuración, licencia/procedencia y SHA-256. Volver a medir tamaño: el modelo español no tiene por qué pesar lo mismo.
7. Comparar respuestas antes/después de cuantizar, límites, rechazo de entradas y consumo. No activar automáticamente un candidato por haber terminado una época.
8. Entrenamiento/validación de voz es una pista separada. No exige audios del dueño para el modelo de texto, pero reconocimiento acústico sí exige datos adecuados y pruebas de voces reales autorizadas.

No prometer conversación general ni memoria larga con esta arquitectura. Mantener el alcance inicial pregunta-respuesta breve y evaluar si cumple la personalidad deseada antes de invertir en audio libre.

## Puertas de aceptación propuestas

Estos son objetivos de ingeniería, NO resultados obtenidos:

- [ ] Binario combinado reproducible, mapa y margen de cada partición; sin sobreescritura de NVS/modelos.
- [ ] Métricas de RAM interna/PSRAM y mayor bloque antes/después de cada subsistema y bajo carga; establecer mínimos a partir de reservas reales.
- [ ] IA desactivable sin cambiar automatización ni quitar funciones existentes.
- [ ] Al menos 1000 preguntas y dos horas de carga mixta, sin reset, fuga sostenida ni errores de heap/pila.
- [ ] PARO atendido en menos de 100 ms bajo IA+audio; registrar máximo, no solo promedio. El paro físico de energía no debe depender del LLM.
- [ ] Medir primera respuesta, prefilling y respuesta completa P50/P95/máximo. Objetivo inicial de primera salida <=2 s para preguntas cortas; revisar viabilidad medida.
- [ ] Cancelación en límite global configurable (objetivo inicial 10 s), entrada/contexto/salida acotados y errores observables.
- [ ] Inyectar falta de memoria, modelo/tablas corruptos, cola llena, pantalla ausente, fallo I2S y trabajador detenido; control doméstico preservado cuando siga sano.
- [ ] Micrófono a 50 cm/1 m con ventilador, MIC OFF, audio propio sin autoactivación y pérdida de dispositivos.
- [ ] Español sobre conjunto reservado: respuestas pertinentes, desconocidos rechazados y cero órdenes ejecutadas desde salida generada.
- [ ] Medir tensión durante altavoz y cargas, reinicios y causa de reset; no confundir PASS de compilación con prueba eléctrica.

## Estado de esta auditoría

Recompilación local actual: PASS, Arduino N16R8/OPI/240 MHz, aplicación 3 MiB,
414338 bytes de programa y 25092 bytes globales, salida en
`build/barista_audit_domus`. Persiste la advertencia de arquitectura declarada
AVR de LiquidCrystal I2C. El primer intento aislado no accedió al enlace de
herramientas instalado; la repetición autorizada compiló correctamente.
Esto confirma el núcleo actual, no el firmware combinado.

Archivo recompilado: 414496 bytes, SHA-256
`92C44F4FC7B81F0C7F17FB5E9E7043362223DD8A702BE50628447A39FD011619`.
Tiene el mismo tamaño que el anterior pero distinto hash; no se afirma
reproducibilidad bit a bit entre ambas compilaciones.
Validador actual: 42 pruebas correctas (20 simulador + 22 contratos), cuatro
pruebas nativas omitidas por falta de compilador C++ host. No son pruebas de
Barista ni del hardware. `git diff --check` sin errores de espacios.

- [x] Inspección de firmware, flags, watchdog, memoria, pines y PoC de audio.
- [x] Comprobación del tamaño y checksum del binario existente y logs CI de audio.
- [x] Revisión de implementación y límites publicados de Barista.
- [ ] Compilación y banco de DOMUS + Barista + audio como una sola aplicación.
- [ ] Entrenamiento español y reconocimiento libre de preguntas.

No se ha flasheado ningún puerto ni activado voz. Los puertos enumerados no identifican por sí solos una N16R8 conectada. Esta nota es aprobación de una investigación/prototipo por etapas, no certificación de estabilidad.
