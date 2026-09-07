# Entrenamiento de Jarvis: candidato local, aún sin corpus validado

No hay dataset ni modelo entrenado en el proyecto. El entrenador prepara un
**candidato**, nunca activa la voz ni afirma que funciona en ESP32. Requiere
Python 3.12 y `python -m pip install -r ai/requirements.txt` en un entorno aislado.
La prueba técnica puede entrenar y exportar señales aleatorias temporales;
eso no entrena reconocimiento español ni produce pesos para instalar.

## Dataset local

Crear `ai/data/manifest.csv` con columnas:

```csv
path,speaker,label,split,source,consent
audio/persona01/jarvis01.wav,persona01,JARVIS,train,real,yes
```

La fila es un ejemplo de formato, no una grabación existente. Audios PCM WAV
mono 16 kHz/16 bits, 0.5–2 s. Usar palabras de activación y órdenes cortas;
no cortar frases largas para que entren. `domus_intents.def` en el firmware define las
14 clases: Jarvis, diez órdenes, desconocido, ruido y silencio.

Grabar solo con permiso. Mantener una persona exclusivamente en `train`,
`validation` o `test`; nunca repartir sus grabaciones entre particiones.
Para ruido/silencio, usar identificadores de sesión distintos y no reutilizar
la misma habitación/grabación de fondo cortada en distintas particiones.
Se rechazan duplicados PCM exactos, audios saturados y metadatos incorrectos;
la procedencia de cada grabación debe verificarse al recopilarlas.

Mínimo de entrada: 20 ejemplos por clase para entrenamiento, 5 para validación
y 5 para prueba (420 audios). No es garantía de calidad; ampliar hablantes,
acentos, distancias y ruido si las métricas fallan. Preferir al menos 10
hablantes repartidos 6/2/2 y suficientes muestras por clase/persona.

```powershell
python ai/train.py --manifest ai/data/manifest.csv --audit-only
python ai/train.py --manifest ai/data/manifest.csv --output ai/runs/primer-candidato
```

La salida incluye modelo int8, etiquetas, checksum, matriz de confusión,
recall por clase, errores entre predicciones aceptadas y procedencia de datos.
No sobrescribe una ejecución anterior. No usa grabaciones test para entrenamiento,
early stopping ni calibración de cuantización. Las voces y pesos están ignorados
por Git; no se publican automáticamente.

## Síntesis autorizada y evaluación independiente

No necesitas aportar tu voz. Se permiten voces sintéticas autorizadas **solo
en train** usando `--allow-synthetic-train`. En ese modo todas las filas,
incluidas las reales, requieren además `license,source_url,origin_id,transcript`.
Registrar la licencia y autorización reales de la fuente, no inventarlas para
superar el auditor. La herramienta comprueba campos; no verifica permisos legales.
Una voz/hablante y un original no pueden aparecer en particiones distintas.
Los audios reales de validation/test siguen siendo obligatorios. El auditor
detecta duplicados exactos, no todas las variantes acústicamente similares.

Los umbrales por orden se eligen con validation: al menos 20 aciertos aceptados
y ningún error aceptado por clase en ese conjunto. Una clase sin evidencia queda
deshabilitada en el informe (`null`); no bajar el umbral para aparentar éxito.
El mínimo de cinco muestras de validación del auditor solo admite el corpus al
proceso: **no alcanza para habilitar una clase**. Test no selecciona umbrales.

También se guardan `checkpoint.keras`, `frontend_reference.npz`, historial y
hash del catálogo. `status.json` empieza como `INCOMPLETE`; solo al finalizar
cambia a `CANDIDATE_NOT_VALIDATED_ON_ESP32`. No equivale a aprobación física.
Presupuesto inicial: modelo <=1 MiB y caché estimada <=2 GiB.

Para probar el proceso en Windows o Linux, sin publicar un modelo ficticio:

```powershell
$env:TF_NUM_INTRAOP_THREADS='1'
$env:TF_NUM_INTEROP_THREADS='1'
$env:OMP_NUM_THREADS='1'
python -m unittest discover -s ai/tests -v
```

En Linux exportar esas mismas variables antes del comando Python. La CI tiene
matriz Windows/Linux; configurarla no significa que la ejecución remota haya pasado.

## Integración pendiente tras obtener un candidato

La entrada del modelo es log-mel, **no PCM**. Antes de integrarlo, reproducir
exactamente el frontend de `report.json` en ESP32 y contrastarlo con vectores
de referencia; añadir el intérprete y medir arena/latencia. Validar activación
Jarvis, ventana de órdenes, confianza real, desconocidos, MIC OFF y pausa de
captura durante audio. Ningún peso se instala por cambiar una bandera.

La clasificación por clips no demuestra cero falsas activaciones en audio
continuo. El plan 25 exige ocho horas de ruido y conversaciones sin órdenes,
además de pruebas a 50 cm/1 m y con ventilador/altavoz reales.

Referencias: [reconocimiento de palabras TensorFlow](https://www.tensorflow.org/tutorials/audio/simple_audio)
y [cuantización entera](https://ai.google.dev/edge/litert/models/post_training_integer_quant).
