---
fecha: 2026-09-05
estado: parcial_no_aprobado_para_voz_en_placa
---

# Avance de Jarvis: contrato, entrenamiento y pruebas

> Registro histórico de avance. Los conteos de pruebas vigentes están en
> [[34 - Cierre de software y matriz de verificacion]].

Continúa [[25 - Plan ejecutable Jarvis offline fiable y entrenado]]. No declara
terminado el reconocimiento español, PicoTTS integrado ni el plan completo.

## Cambios aplicados

- Catálogo único de 14 etiquetas en `firmware/casa_inteligente_v4/domus_intents.def`;
  Python y C++ comparten orden y asociación de diez órdenes a cinco actuadores.
- El despachador del firmware rechaza confianza NaN, infinita, negativa y >1.
  Antes una comparación exclusiva `<0.75` dejaba pasar NaN.
- Diagnóstico separado de memoria interna/PSRAM, mínimos y mayor bloque libre.
  Son métricas disponibles, no mediciones realizadas sobre una placa.
- Reserva central de GPIO40/41/42 para futura salida TTS; no implica audio operativo.
- Puerta acotada de una orden con caducidad, cancelación y consumo único.
  **Preparada, no conectada aún a inferencia real ni segura para compartir entre tareas.**
- Auditor permite síntesis autorizada solo en entrenamiento, con procedencia explícita.
  Evaluación exige grabaciones reales; detecta duplicados exactos y cruce de hablantes/originales.
- Entrenador conserva checkpoint, historial, referencia frontend y hash de etiquetas.
  Selecciona umbrales usando validation, no test; deshabilita clases sin evidencia suficiente.
- Informe corregido: predicciones ambiguas cuentan como fallos, sin dividir entre cero
  ni generar NaN. La serialización rechaza métricas no finitas.
- CI del entrenador configurada para Windows y Linux; ejecución remota nueva pendiente.

## Evidencia y límites

Referencia Git al iniciar esta continuación: `cb193013de5b991d6f77b3b2ddc6ca9b38dd4ab1`,
rama `proyecdomus`, upstream `origin/proyecdomus`. Árbol con cambios previos;
sin staging inicial. Se preservan `firmware/domus_anim` y `firmware/domus_selftest`,
que aparecieron sin seguimiento y no forman parte de esta revisión.

Compilación local Arduino core 3.3.10, ESP32-S3, 16M flash, PSRAM OPI,
partición app3M_fat9M_16MB, CPU240, LoopCore1: salida 0.

| Elemento | Resultado |
|---|---|
| Programa | 415170 bytes / 3145728 de partición (13.2%) |
| Globales estáticas | 25092 bytes; no incluye heap/pilas/DMA futuros |
| Binario aplicación | 415328 bytes |
| Variación frente a base | +832 bytes de programa; globales sin cambio |
| Simulador doméstico | 20 pruebas PASS |
| Contratos firmware | 22 pruebas PASS |
| Entrenador Windows / TensorFlow 2.20 | 16 pruebas PASS, incluida exportación int8 y métricas finitas |
| C++ nativo | 5 OMITIDAS: falta compilador host; no contarlas como PASS |
| Pruebas físicas | No ejecutadas |

Binario `build/jarvis_phase1/casa_inteligente_v4.ino.bin`, SHA256:
`5FFFFFF45D385DCD8041BF8CEED41D632F694E397F32031D0A44AF413C208B32`.
La imagen fusionada de 16 MiB incluye relleno/particiones: no es tamaño de código.
Aviso de LiquidCrystal I2C sobre arquitectura AVR permanece: compilar no acredita
que la LCD física funcione. No se grabó ni reinició ninguna placa.

TensorFlow 2.20 instalado en `.venv-ia`. La primera ejecución se interrumpió
por falta de avance observable; importación aislada posterior exitosa.
La repetición con un hilo intra/inter/OMP completó fit, int8 y evaluación sobre
42 señales aleatorias (14 clases por partición), generando 12792 bytes temporales.
No son palabras españolas: **no se conserva ni instala ese modelo**.
Se detectó el informe NaN y se corrigió; la repetición final pasó las 16 pruebas
en 15.651 s y reportó accuracy 0.0 sobre ruido, sin NaN. Total: 58 PASS y 5 omitidas.
Quedan avisos de conversión/deprecación de TensorFlow; no se ocultan ni equivalen
a validación del intérprete micro en ESP32.

## Punto de continuación

- Hecho: contrato base, controles de confianza, diagnóstico, auditor y mejoras del entrenador.
- Pendiente: corpus español legal y suficiente; entrenamiento útil y evaluación real.
- Pendiente: consultas/persona, frontend equivalente en placa, captura I2S, intérprete
  micro y PicoTTS dentro de DOMUS, colas entre tareas y pruebas bajo carga.
- Pendiente: confirmar placa, módulos, alimentación y mediciones del protocolo 25.
- Siguiente paso: obtener corpus de frases compatible con las diez órdenes y
  voces externas para evaluación, sin exigir grabaciones de Isaac. No sustituir
  ese requisito por ruido o síntesis marcada como real.

El firmware principal supera 1800 líneas: estos cambios son acotados, no añaden
el motor de audio al mismo archivo. Conviene separar la integración de voz por
responsabilidad al implementarla, con pruebas, evitando otro bloque monolítico.
No se retiran funciones domésticas ni se activa Barista. Cierre: parcial.

## Continuación 2026-09-06: cancelación MIC OFF

Alcance: protección de órdenes de voz en el despachador existente; alimentación
aplazada por el usuario. No cambia modelos ni activa el motor experimental.
El despachador consulta tanto el estado lógico como el pin físico MIC OFF antes
de aceptar una orden de voz. Al apagar MIC se cierra la ventana de escucha;
las órdenes manuales conservan su funcionamiento. Se añadieron regresiones
para bloqueo ON/OFF, control manual y discrepancia entre pin y estado lógico.

Verificación local: 20 pruebas del simulador y 23 contratos PASS; cinco pruebas
C++ omitidas por falta de compilador host, incluida la regresión de ejecución.
No equivale a prueba física. Compilación de esta continuación: PASS (salida 0),
415250 bytes de programa y 25092 de globales, mismo perfil N16R8 de la tabla.
Binarios en `build/jarvis_mic_guard`; no se grabó la placa. `git diff --check` PASS.
Cambios sin commit: se conserva el árbol previo y no se declara terminada la
integración de voz. Próximo trabajo pendiente: corpus útil e integración de
captura/frontend/intérprete/TTS, conforme al plan 25.
