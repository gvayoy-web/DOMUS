---
proyecto: PROJECT DOMUS
tipo: optimizacion
actualizado: 2026-09-04
estado: plan_terminado_pendiente_mediciones
depende_de: mediciones_reales
---

# Plan de optimización de código

## Objetivo

Reducir consumo de memoria, latencia y complejidad **sin quitar ninguna
función**. Cada cambio debe conservar el comportamiento actual y superar las
38 pruebas, la compilación ESP32 y el test físico correspondiente.

## Funciones que no se pueden eliminar

- Cinco cargas: bomba, sala, dormitorio, ventilador e invernadero.
- Modos `AUTO`, `MANUAL_ON` y `MANUAL_OFF` persistente.
- Histéresis, PIR, DHT, LDR, humedad de suelo y nivel de agua.
- Paro físico, MIC OFF, botón local, USB Serial y LCD1602.
- Corte de bomba por nivel, sensor y 120 segundos.
- Watchdog, modo seguro, diagnóstico, recuperación y límite de órdenes.
- microSD, INMP441, PicoTTS/MAX98357A y Jarvis como módulos opcionales.
- Simulador, pruebas automáticas y validación de Obsidian.

## Ruta de optimización

| Fase | Cambio | Condición para aplicarlo | Funciones preservadas |
|---|---|---|---|
| 1. Medición | Registrar heap mínimo, tiempo máximo de ciclo, errores y reinicios durante 60 min. | Obtener una línea base reproducible. | Todas. |
| 2. Memoria | Cambiar `String` frecuentes por buffers fijos únicamente en rutas calientes. | La medición muestra fragmentación o caída sostenida. | Protocolo Serial idéntico. |
| 3. Entrada/salida | Agrupar escritura microSD y emitir eventos solo al cambiar de estado. | Se observa latencia o exceso de registros. | No se pierde ningún evento crítico. |
| 4. Estructura | Separar pines, sensores, actuadores y seguridad en módulos pequeños. | Pinout físico confirmado. | Mismos comandos y reglas. |
| 5. Jarvis | Versionar modelos, medir PSRAM/inferencia y activar half-duplex. | Hardware y modelos int8 validados. | La casa funciona si la voz falla. |
| 6. Resistencia | Pruebas C++ nativas, `millis()` desbordado, brownout, ráfagas y ejecución de 8 h. | Después de superar [[16 - Plan de testeo antes de construccion]]. | Seguridad y respuesta local. |

## Orden de trabajo

1. Ejecutar la línea base sin modificar el firmware.
2. Elegir un solo cuello de botella medido.
3. Añadir primero una prueba que reproduzca el problema.
4. Realizar el cambio mínimo.
5. Ejecutar `python tools/validate_project.py`.
6. Compilar para ESP32-S3 N16R8.
7. Repetir la misma medición y comparar.
8. Revertir el cambio si empeora memoria, tiempo o seguridad.

## Límites obligatorios

- No introducir BLE, Kotlin, MQTT, nube ni dependencia de Internet.
- No activar voz o microSD sin hardware validado.
- No reemplazar el modo seguro por reinicios automáticos.
- No reducir validaciones para ahorrar memoria.
- No cambiar simultáneamente software y cableado durante una comparación.
- No modificar `planos/new`.

## Criterios de salida

- 38/38 pruebas y compilación correctas.
- Ocho horas sin reset ni descenso sostenido de `MEM_MIN`.
- `PARO` responde incluso bajo ráfaga Serial.
- Pantalla/registro no retrasan el corte de bomba.
- Fallar Jarvis, microSD o un sensor no bloquea el núcleo.
- Cada optimización tiene medición antes/después en
  [[12 - Bitacora de implementacion]].

## Relaciones

- [[13 - Plan de cierre de codigo]]
- [[14 - Protocolo anti-colapso IA y ESP32]]
- [[16 - Plan de testeo antes de construccion]]
- [[17 - Diagramas generales de conexiones]]
