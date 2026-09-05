---
estado: robustez_implementada_voz_pendiente_de_datos
fecha: 2026-09-05
---

# Cierre de robustez y entrenamiento pendiente

## Implementado

- Watchdog: comprueba inicialización, reconfiguración, suscripción y alimentación.
  Si falla, las cargas quedan apagadas en modo seguro y RECUPERAR lo rechaza.
- I2C: consulta únicamente 0x27/0x3F, con timeout de 10 ms por transacción y
  tres intentos. El escaneo deja de recorrer 126 direcciones. La pantalla
  perdida se desactiva y el control sigue sin pantalla; recuperar LCD exige reinicio.
- Calibración: valores editables por Serial, guardados en NVS con versión,
  rangos y checksum. Una configuración inválida al arrancar conserva los
  valores provisionales y lo muestra en DIAGNOSTICO.
- microSD: una tarea exclusiva monta y escribe; cola limitada a ocho registros,
  envío sin espera desde el control, descarte contabilizado al llenarse y
  desactivación ante errores. Registros de más de 191 caracteres se descartan
  con contador; no se truncan para aparentar integridad.
- Registro SD: rota `/domus.log` antes de superar 256 KiB, conservando una
  generación `/domus.prev.log`. Al rotar se reemplaza la copia más antigua;
  el historial anterior no se conserva. Un fallo de escritura desactiva SD
  hasta reiniciar; no intenta montar continuamente una tarjeta averiada.
- SD_PRUEBA encola una comprobación y responde ENCOLADA, no éxito prematuro.
  Consultar SD_PRUEBA=1/-1 y SD_ERRORES en DIAGNOSTICO para su resultado.
- Pruebas C++: despachador y salidas reales del sketch conectados a GPIO
  simulados, paro/rearme, depósito inválido, timeout y recuperación juntos;
  además fallos de watchdog y validación/checksum de calibración.
- Audio aislado: formato Philips I2S del MAX98357A, timeout en milisegundos,
  corrección de opción Kconfig del micrófono, saturación y fallo al crear tarea.

## Calibrar sin recompilar

1. Medir valores crudos con ESTADO en seco/húmedo y oscuro/claro. Para nivel,
   medir el mínimo admisible con margen antes de que la bomba aspire aire.
2. Enviar `PARO` y confirmar todas las salidas apagadas.
3. Enviar por separado `CAL_SECO=valor`, `CAL_HUMEDO=valor`,
   `CAL_OSCURO=valor`, `CAL_CLARO=valor`, `CAL_NIVEL=valor`.
4. `CAL_VER` muestra la edición pendiente. `CAL_CANCELAR` descarta la edición.
5. `CAL_GUARDAR` valida el conjunto y confirma escritura. No rearma ni activa cargas.
6. Reiniciar y comprobar DIAGNOSTICO con CALIBRACION=NVS; después REARMAR y
   devolver explícitamente cada salida a AUTO cuando corresponda.

Los límites de fallo ADC siguen siendo fijos y conservadores. Si la lectura
real cae fuera de ellos, revisar alimentación y adaptar diseño/calibración;
no eliminar el bloqueo para que la bomba arranque. El software no identifica
con certeza todas las entradas flotantes.

## IA: qué existe y qué falta

`ai/train.py` implementa clasificación de clips por CNN y exportación int8.
`ai/dataset.py` comprueba WAV, etiquetas, saturación, duplicados, consentimiento
y separación por hablante entre train/validation/test. La evaluación genera
matriz de confusión, recall por clase, errores aceptados y checksum del modelo.

**No se ha entrenado Jarvis con voces reales:** no hay WAV ni manifiesto de
grabaciones en el proyecto. Se ejecutó la auditoría y devolvió explícitamente
ENTRENAMIENTO_NO_COMPLETADO. Los detalles y órdenes están en `ai/README.md`.
La prueba técnica del entrenador usa señales temporales, no se distribuye
ese modelo y no constituye reconocimiento de español.

Después de los datos todavía requieren cierre: frontend log-mel idéntico
en ESP32, intérprete/modelo, captura integrada, activación/ventana de órdenes,
confianza real, audio hablado y ensayo de eco. El indicador WS2812 sigue
pendiente de pin validado e integración. Estos puntos no se marcan terminados.
Las PoC de audio aisladas no equivalen a Jarvis integrado en el firmware Arduino.

## Evidencia disponible

- Firmware local N16R8: compilación correcta, 414,338 bytes de programa,
  25,092 bytes globales. Estos valores no son pico de RAM en funcionamiento.
- [Firmware Linux: cinco perfiles correctos](https://github.com/gvayoy-web/domusv1/actions/runs/33942958851).
- [Verificación del entrenador: siete pruebas PASS](https://github.com/gvayoy-web/domusv1/actions/runs/33943233493).
  Incluye ajuste de una época, conversión int8 y evaluación con ruido aleatorio
  temporal. Se elimina el candidato; no mide reconocimiento de español.
- [Compilaciones ESP-IDF de audio: ambas PASS](https://github.com/gvayoy-web/domusv1/actions/runs/33943233605).
- Windows: 42 pruebas del validador correctas; tres pruebas C++ omitidas por
  falta de compilador host y ejecutadas en Linux. Auditoría de dataset: seis
  pruebas correctas; prueba TensorFlow correcta en CI. Se añade además prueba
  C++ del escaneo I2C bloqueado, que comprueba exactamente dos transacciones.

No se han medido corriente, calentamiento, agua ni comportamiento de una
tarjeta física. Continúan [[19 - Plan de testeo despues de construccion]] y
[[21 - Simplificacion y reduccion de costos]]. Este estado reemplaza las
afirmaciones generales de «todo terminado» de documentos anteriores.
