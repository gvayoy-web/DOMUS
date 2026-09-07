---
fecha: 2026-09-05
estado: implementacion_parcial_contrato_y_entrenador_verificados_datos_y_audio_pendientes
objetivo: Jarvis local fiable en ESP32-S3 N16R8
---

# Plan ejecutable: Jarvis offline fiable y entrenado

## Decisión de diseño y límite honesto

Avance de implementación y evidencia: [[26 - Avance Jarvis contrato entrenamiento y pruebas]].
Los casilleros siguientes son puertas completas: un avance parcial no los aprueba.

Priorizar una versión local de alcance acotado: reconocimiento español de intenciones, respuestas construidas con datos reales y personalidad mediante frases variadas, y PicoTTS español aunque suene robótico. Sin API, computadora de acompañamiento ni teléfono; la computadora solo prepara y entrena los modelos.

**Esta versión no será conversación libre de un LLM.** Reconocerá las órdenes/preguntas previstas y algunas variantes entrenadas, rechazando lo demás. Esta es una reducción explícita del objetivo conversacional inicial para priorizar fiabilidad; no se quitan funciones domésticas existentes. No se considera aceptada la conversación abierta ni se marca terminada por conseguir comandos.

Barista se conserva como investigación opcional en [[24 - Viabilidad Barista DOMUS memoria voz y entrenamiento]], deshabilitada en la versión estable. No gastar RAM ni entrenamiento generativo en él hasta aprobar reconocimiento y audio. El usuario acepta voz robótica; esto no resuelve automáticamente el reconocimiento.

No se puede prometer cero errores. Cada versión se aprueba contra métricas y condiciones documentadas, con fallos conocidos y modo seguro. Este documento es un plan: no contiene un modelo ya entrenado ni resultados físicos inventados.

## Experiencia prevista

Primera versión: pulsar para hablar con entrada física propia validada, pronunciar una frase breve, escuchar confirmación y volver a reposo. Mantener MIC OFF y PARO independientes. No reutilizar silenciosamente el botón DEMO: asignar un pin libre después de auditar el mazo. Alternativa sin botón nuevo: añadir la palabra de activación solo cuando su modelo pase pruebas continuas.

Secuencia: REPOSO -> CAPTURA -> CLASIFICACIÓN -> VALIDACIÓN -> RESPUESTA -> VOZ -> COOLDOWN -> REPOSO. Cualquier fallo vuelve a reposo o deshabilita voz, sin bloquear el supervisor doméstico. MIC OFF cancela captura y órdenes de voz pendientes.

| Grupo | Intenciones propuestas | Respuesta/acción |
|---|---|---|
| Control existente | Las diez ON/OFF de luces, bomba, ventilador e invernadero | Pasan por el despachador existente y sus bloqueos |
| Consulta | Temperatura, humedad ambiental, humedad del suelo, nivel, estado general | Valores reales con unidades/antigüedad; informar sensor no disponible |
| Personalidad | Saludo, presentación del proyecto, chiste, agradecimiento, elogio | Catálogo corto de variantes revisadas, sin repetición inmediata |
| Protección | Desconocido, ruido, silencio | No actuar; pedir repetir solo cuando corresponde |

Ejemplos de frases objetivo, no capacidades existentes: «temperatura», «estado de la casa», «cuenta un chiste», «qué bonita casa». Preguntas largas como «¿cómo le haces para tener un proyecto tan hermoso?» solo se admitirán tras ampliar y evaluar duración/variantes: nunca recortar el audio y suponer que se entendió.

Para la bomba, exigir confirmación física o confirmación explícita acotada según evaluación de riesgo; mantener depósito válido, temporizador y PARO. La confirmación verbal no es un dispositivo de seguridad. La salida hablada nunca se vuelve a interpretar como orden.

## Fases y entregables

### 0. Congelar línea base y medir recursos

- [ ] Guardar commit, configuración, versiones, mapa, checksum y resultados de DOMUS sin voz; preservar cambios del usuario.
- [ ] Confirmar N16R8 real, PSRAM OPI, pines expuestos y alimentación; no identificar placa solo por COM.
- [ ] Medir heap interno/PSRAM libres y mínimos, bloque contiguo mayor y pilas. Mantener métricas durante pruebas.
- [ ] Inventariar componentes disponibles antes de montaje: INMP441, MAX98357A, altavoz y alimentación no se dan por comprados.

Base de referencia de la nota 24: 414338 bytes de programa, 25092 globales; no son consumo de la futura versión hablada. Los binarios aislados de audio no se suman como si fueran tamaño final.

### 1. Contrato único de intenciones y audio

- [ ] Crear catálogo versionado único que genere etiquetas Python/C++, ejemplos y tabla de acciones; conservar todas las intenciones existentes.
- [ ] Separar respuestas informativas, órdenes y desconocidos; no activar GPIO desde inferencia ni TTS.
- [ ] Comenzar con clips 16 kHz PCM16 mono de hasta 2 s, coherentes con `ai/dataset.py`; rechazar exceso y pedir frase corta.
- [ ] Si preguntas requieren más duración, cambiar conjuntamente dataset, frontend, entrenamiento, captura y pruebas antes de admitirlas. No concatenar clasificaciones para aparentar dictado.
- [ ] Entrenar primero diez órdenes + clases de rechazo; ampliar consultas/persona solo tras superar evaluación base.

### 2. Datos sin exigir grabaciones de Isaac

- [ ] Buscar y verificar licencias de voces/datasets españoles que permitan el uso previsto, descarga y entrenamiento; registrar URL, versión, licencia y atribución. No considerar que «público» significa consentimiento ilimitado.
- [ ] Crear corpus sintético con diversas voces españolas autorizadas, ritmos, pronunciaciones y frases. Mantener muestras reales externas para validación independiente.
- [ ] No clonar voces identificables sin autorización. Isaac no necesita grabar el entrenamiento; sí se requieren voces reales autorizadas para evaluar generalización.
- [x] Adaptar el auditor: admite `synthetic` solo en train con opción explícita y campos de procedencia; pruebas incluidas. No certifica automáticamente licencias ni similitud entre audios.
- [ ] Separar por identidad/voz, grabación original y familia de frases antes de aumentar datos. Augmentaciones, recortes y duplicados próximos no cruzan particiones.
- [ ] Test final real y reservado; fuentes sintéticas solo en entrenamiento o validación separada claramente identificada. No usar test para elegir umbrales ni calibrar int8.
- [ ] Incluir negaciones, frases parecidas, conversaciones ajenas, silencio, ruido, ventilador y reproducción del propio altavoz.

Presupuesto inicial de exploración, no garantía estadística: 200 clips por intención de entrenamiento, distintas voces por partición y al menos 50 ejemplos reales reservados por intención para evaluación final. Aumentar datos según errores, sin inflar resultados con miles de versiones del mismo audio. Si no hay fuentes legales suficientes, marcar fase bloqueada y no publicar un modelo «validado».

### 3. Entrenamiento y exportación realizados por el agente

- [ ] Inspeccionar CPU/GPU, RAM, espacio y herramientas locales antes de estimar duración. No contratar cómputo ni servicios pagados sin autorización.
- [ ] Reutilizar `ai/train.py` como referencia; comparar CNN actual con una CNN compacta separable solo si mejora calidad/memoria medidas. No añadir modelos grandes por nombre.
- [ ] Ejecutar entrenamiento real con manifiesto trazable, semilla, configuración y curva de pérdida; separar prueba técnica con ruido de entrenamiento útil.
- [ ] Registrar recall/precisión por clase, matriz de confusión, tasa de órdenes incorrectas aceptadas y cobertura frente al rechazo.
- [ ] Elegir umbrales por clase en validación y congelarlos antes del test. Mecanismo implementado y probado; falta ejecutarlo con corpus útil. Softmax alto no garantiza corrección.
- [ ] Exportar int8 con datos de calibración del entrenamiento y comprobar pérdida de calidad; conservar checkpoint, modelo, etiquetas, frontend, hashes y licencias.
- [ ] Crear vectores PCM/log-mel/logits de referencia y comprobar equivalencia host/ESP32 con tolerancias declaradas.

El entrenamiento corre en computadora, la inferencia final en ESP32. No hay entrenamiento continuo en la placa ni cambios de pesos por conversar.

### 4. Captura e inferencia integrada

- [ ] Unificar versiones de Arduino/ESP-IDF y controladores I2S; las PoC separadas no se fusionan copiando sus `app_main`.
- [ ] Reutilizar INMP441: GPIO15 WS, 16 SD, 17 SCK; validar placa/voltajes antes de conectar. Captura por DMA, buffers fijos y control explícito de pérdida de muestras.
- [ ] Reservar memoria antes de activar voz. No reservar grandes buffers o crear tareas por cada pregunta.
- [ ] Una captura/inferencia activa y cola acotada; cancelar sobrecarga en lugar de acumular retraso.
- [ ] Mantener tareas de control por encima de voz. Medir latencia real y cesión al sistema; ninguna espera de audio/inferencia dentro del loop de seguridad.
- [ ] Si falta memoria, falla el modelo o hay errores repetidos, apagar la función de voz y mantener el modo doméstico seguro correspondiente.

### 5. Voz robótica fiable y personalidad

- [ ] Integrar PicoTTS español con texto breve y longitud máxima fija; variables solo de sensores válidos. «No puedo medirlo» es preferible a inventar un valor.
- [ ] MAX98357A en GPIO40/41/42 provisionales: confirmar exposición y añadirlos al registro central de pines únicos; no sustituir LCD1602 por OLED.
- [ ] Cola TTS limitada, timeout y recuperación I2S; ninguna espera infinita ni reinicialización repetida ante amplificador ausente.
- [ ] Pausar escucha durante reproducción y aplicar cooldown configurable medido; MIC OFF y controles físicos siguen disponibles.
- [ ] Catálogo versionado de respuestas y chistes; variación por estado/turno sin atribuir comprensión de texto libre.
- [ ] Si PicoTTS no cumple memoria/latencia, evaluar clips robóticos pregenerados en flash para el catálogo finito; valores numéricos requieren una estrategia evaluada de composición. No quitar consultas dinámicas para esconder una limitación.

No requiere microSD para arrancar. El registro SD existente sigue opcional e independiente; los fallos de tarjeta nunca bloquean control o voz. Audios pregenerados son un respaldo condicionado, no un segundo motor obligatorio.

### 6. Optimización con límites medidos

Objetivos iniciales, ajustables solo con justificación registrada:

| Recurso | Presupuesto/meta inicial |
|---|---|
| Pesos clasificador int8 | <=1 MiB; si no alcanza precisión, revisar arquitectura/datos antes de ampliar |
| Arena de inferencia | <=512 KiB; medir memoria interna y externa requerida por operadores |
| Captura de 2 s | 64000 bytes PCM en PSRAM más DMA/pilas; no duplicar sin necesidad |
| Reserva interna tras inicialización | Meta >=64 KiB y bloque mayor suficiente para DMA/operación pendiente |
| Reserva PSRAM bajo carga | Meta >=1 MiB; margen adicional según mayor reserva real |
| Flash | >=20% de margen en cada partición de aplicación; comprobar recursos/modelo por separado |
| Respuesta tras fin de frase | P95 <=1.5 s hasta confirmación/inicio de voz, sobre frases admitidas |
| Respuesta a PARO físico leída por firmware | Máximo <=100 ms bajo carga; corte de energía independiente cuando corresponda |

Un modelo no pasa solo por caber en estas cifras. No reducir reservas del control para alcanzar metas de IA. Preservar las particiones de actualización y NVS existentes cuando sea viable; cualquier migración necesita respaldo y validación, no escritura a offsets de ejemplos externos.

### 7. Pruebas y criterio de entrega

- [ ] Windows y Linux: contratos y entrenamiento/evaluación; pruebas nativas con compilador host, omisiones explícitas donde falte.
- [ ] ESP32 N16R8 real: comparación de frontend/logits, memoria, errores I2S, latencias y registros con modelo/configuración identificados.
- [ ] Otros perfiles existentes: siguen compilando con voz deshabilitada; no presentar eso como ejecución del modelo en placas sin PSRAM.
- [ ] Meta de reconocimiento: >=95% de recall por intención en silencio a 50 cm y >=90% a 1 m con ruido de prueba definido; reportar precisión y rechazos, no solo accuracy global.
- [ ] Cero activaciones de actuadores incorrectas observadas en 8 h de conversaciones/ruido sin órdenes y al menos 500 ejemplos negativos reservados; cero observado no garantiza tasa cero futura.
- [ ] Cien ensayos de PARO durante captura, inferencia y TTS; ninguna reactivación sin rearme autorizado.
- [ ] 24 h y 1000 ciclos mixtos sin reinicios no previstos, fugas sostenidas ni crecimiento de colas; medir pilas y bloques libres durante toda la prueba.
- [ ] Inyectar pesos corruptos, asignación fallida, sensor perdido, LCD bloqueada, SD ausente/llena, micrófono desconectado y TTS detenido.
- [ ] Medir caídas de alimentación al conmutar cargas y reproducir audio. No alimentar potencia desde GPIO; no afirmar seguridad eléctrica por pruebas simuladas.
- [ ] Mantener todas las pruebas domésticas anteriores y repetir calibración/seguridad física tras integración.

Si falla una puerta, corregir y repetir con nuevo identificador de versión; no convertir objetivos incumplidos en PASS cambiando el texto del reporte.

## Entregables de implementación posteriores

1. Catálogo de intenciones y respuestas, frontend compartido y adaptador de órdenes.
2. Dataset trazable, entrenamiento ejecutable, checkpoint candidato y modelo int8.
3. Firmware de voz integrado con feature flag y binario doméstico de respaldo.
4. Informe host + placa con métricas crudas, hashes y limitaciones.
5. Guía de conexión definitiva y procedimiento de instalación/recuperación.

El agente puede preparar datos autorizados, entrenar, integrar y automatizar pruebas de software. La aprobación de micrófono, altavoz, alimentación y estabilidad exige hardware conectado y mediciones reales. No se presume acceso a esa placa ni se empieza a flashear sin verificar destino.

## Estado al crear este plan

- [x] Arquitectura de entrega estable elegida y alcance limitado explícito.
- [x] Fases, presupuestos, pruebas, entregables y condiciones de rechazo definidos.
- [ ] Corpus acústico preparado y auditado.
- [ ] Entrenamiento español ejecutado con datos útiles.
- [ ] Firmware integrado y pruebas físicas aprobadas.
- [ ] Barista experimental evaluado por separado, si se retoma conversación generativa.

Referencias del proyecto: [[14 - Protocolo anti-colapso IA y ESP32]], [[18 - Manual maestro de conexiones pin por pin]], [[19 - Plan de testeo despues de construccion]], [[23 - Cierre de robustez y entrenamiento pendiente]], [[24 - Viabilidad Barista DOMUS memoria voz y entrenamiento]]. Este plan dirige la versión fiable y no borra las investigaciones anteriores.
