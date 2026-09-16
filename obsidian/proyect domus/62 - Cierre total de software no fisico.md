---
estado: vigente
fecha: 2026-09-16
autoridad: software
---

# Cierre total de software no físico

Todo lo que puede completarse sin observar hardware queda cerrado en software.

## Cerrado

- `casa_inteligente_v4` es la única implementación funcional.
- `domus_esqueleto` compila literalmente ese producto con perfil 3.
- El diagnóstico independiente lee LCD, DHT11, suelo, nivel, LDR e IR sin
  configurar salidas.
- Calibración: captura asistida, validación, conversión con polaridad invertida,
  checksum, persistencia NVS, cancelar y guardar.
- IR: 21 posiciones persistentes, máscara de aprendizaje real, códigos únicos,
  rechazo de repetición y salidas bloqueadas para teclas no aprendidas.
- Seguridad: arranque OFF, PARO, rearme OFF, nivel, timeout, modo seguro,
  watchdog, sensores inválidos y límite Serial.
- LCD: cinco vistas, lector temporal IR, porcentajes de suelo/agua, prioridad
  de seguridad y escritura diferencial.
- Automatización: riego, ventilación y luces con histéresis y propiedad manual.
- CI: simulación, contratos, compilación nativa y matrices Arduino.

## Retirado del producto

Se eliminó el entrenador, CI y PoCs del antiguo plan de reconocimiento por
micrófono. DOMUS no usa IA. Jarvis significa mando IR más respuestas fijas; la
reproducción audible se resolverá posteriormente sin cambiar la seguridad.

El MAX98306 comprado amplifica una señal analógica y no recibe I2S ni reproduce
archivos por sí mismo. Elegir su fuente de audio es una decisión futura, no una
tarea incompleta del núcleo doméstico.

## Único trabajo restante

Requiere el mundo físico: valores reales de calibración, estabilidad del LCD,
reparación del DHT11, HIL, bomba vigilada, DRV8833/ventilador y montaje final.
La dirección LCD `0x27` y los 21 códigos IR ya fueron capturados. Las mediciones
eléctricas siguen `SKIP por decisión del dueño`.
No se convierten en PASS mediante simulación.

La primera sesión física ya comenzó y está registrada en
[[64 - Sesion fisica COM9 LCD IR sensores y bomba]]. Sus fallos observados no
reabren el cierre de software, pero sí mantienen abiertas las puertas físicas.

Relacionada: [[59 - Firmware unico y perfil banco S8050 IR]],
[[60 - Orden Git y pruebas multientorno]] y
[[61 - Esqueleto literal y diagnostico IR calibracion]].
