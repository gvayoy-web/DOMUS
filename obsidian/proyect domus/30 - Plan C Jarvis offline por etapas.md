# Plan C: Jarvis offline por etapas

**Objetivo:** añadir audio y después reconocimiento, sin hacer depender el riego de IA.
**Arquitectura:** núcleo B intacto; elegir un motor de salida de audio, no comprar
dos por defecto. **Tecnología:** DFPlayer como alternativa finita o PicoTTS/I2S
según plan 25; clasificador español aún pendiente.
**Base:** [[25 - Plan ejecutable Jarvis offline fiable y entrenado]],
[[26 - Avance Jarvis contrato entrenamiento y pruebas]], [[27 - Comparador de planes costo y versatilidad]].
**Compatibilidad:** PARO, MIC OFF, límite de memoria/colas y control manual prioritarios.
**TDD:** no impuesto; la integración posterior requiere regresiones y banco.
**Verificación:** pruebas del entrenador, compilación y aceptación física de nota 25.
**Estado:** alternativas propuestas; no se afirma que la voz esté integrada.

## C1: respuestas grabadas, reutilizar DFPlayer

Ya tienes el reproductor. Faltan altavoz compatible y tarjeta si no hay una
disponible. Su amplificador integrado puede evitar MAX98357 para este modo:
[documentación DFRobot](https://www.dfrobot.com/product-1121.html).
No requiere lector SPI del ESP32 para reproducir las pistas de su propia tarjeta.

Puede confirmar acciones y reproducir presentación/chistes pregrabados sin tu
voz, usando síntesis autorizada preparada en computadora. No reconoce órdenes,
no es un LLM ni pronuncia cualquier texto. Números variables requieren catálogo
de segmentos y secuenciación probada; no declararlos resueltos por tener pistas.

Pasos antes de activar `MP3_HABILITADO`:

1. Confirmar módulo físico, altavoz y tarjeta; revisar conexiones UART en nota 18,
   incluyendo conflicto de GPIO19 con USB nativo según puerto/placa usados.
2. Definir tabla pista→evento sin anunciar éxito si la acción fue rechazada.
3. Revisar `reproducirPista` e inicialización en el sketch: tarjeta ausente o
   reproductor detenido no deben bloquear control ni reiniciar continuamente.
4. Preparar y verificar pistas con licencia; volumen inicial bajo y cola limitada.
5. Probar desconexión, saturación de peticiones, PARO durante reproducción y
   consumo simultáneo antes de activar el perfil. Se requieren cambios/probado
   de integración; la bandera actual false no es aprobación pendiente de pulsar.

Costo incremental = altavoz + tarjeta + conexión, descontando solo lo confirmado
disponible. No comprar además lector SPI ni MAX98357 para la misma tarea.

## C2: texto hablado con PicoTTS

Añadir MAX98357A + altavoz compatible; mantener DFPlayer guardado. INMP441
solo es necesario para escuchar, no para pronunciar texto generado por sensores.
Sin microSD obligatoria para arrancar según plan 25: medir flash real antes de
decidir almacenamiento. No sumar tamaños de PoC como si fueran firmware final.

1. Seguir fases 4/5 del plan 25 para integrar controladores y salida I2S.
2. Conservar `responderJarvis` como punto de entrada; motor en unidad separada,
   texto limitado y cola acotada, sin esperas dentro del supervisor.
3. Probar memoria interna/PSRAM, timeout, inicialización fallida y recuperación.
4. Validar consultas con sensores ausentes; nunca inventar un valor para hablar.

Costo incremental = MAX98357 + altavoz + ramal. Compararlo con C1 incluyendo
tarjeta y trabajo de catálogo; tener DFPlayer no garantiza que C1 cueste menos.

## C3: escuchar español, solo tras aprobar la base

Añadir INMP441, corpus autorizado, entrenamiento y frontend/intérprete de nota 25.
El circuito no gana reconocimiento comprando micrófono. Mantener inferencia
desactivada hasta que modelo, memoria, latencia y falsos disparos pasen pruebas.
La salida de audio elegida C1 o C2 pausa captura y aplica cooldown; no dos motores
obligatorios. Barista permanece investigación separada, no requisito ni compra.

Verificación del proceso de entrenamiento (no sustituye datos útiles):

```powershell
$env:TF_NUM_INTRAOP_THREADS='1'
$env:TF_NUM_INTEROP_THREADS='1'
$env:OMP_NUM_THREADS='1'
.venv-ia/Scripts/python.exe -m unittest discover -s ai/tests -v
.venv-ia/Scripts/python.exe tools/validate_project.py
```

La aceptación requiere métricas reales y pruebas 24 h/1000 ciclos del plan 25.
Si falla voz, se deshabilita y el núcleo B conserva funcionamiento; no se
rebajan umbrales ni se entrenan señales aleatorias como supuesto español.
Los precios locales de altavoz/MAX/tarjeta de nota 07 siguen siendo históricos,
no presupuesto final. No comprar C1 y C2 simultáneamente para cubrir incertidumbre.
