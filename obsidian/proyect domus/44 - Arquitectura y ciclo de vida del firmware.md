---
proyecto: PROJECT DOMUS
tipo: arquitectura-firmware
actualizado: 2026-09-10
estado: vigente
placa: ESP32-S3 N16R8
---

# Arquitectura y ciclo de vida del firmware

Esta nota define qué función tiene cada firmware, cuál se carga en cada fase y
qué debe migrarse. No se mezclan pruebas destructivas, control final y pruebas
de periféricos en un único sketch improvisado.

## Mapa de firmwares

| Firmware | Propósito | Hardware permitido | Estado o destino |
|---|---|---|---|
| `domus_selftest` | comprobar placa, Serial, memoria y GPIO sin cargas | ESP32 solo | diagnóstico inicial |
| `domus_esqueleto` | sensores, LCD, calibración, seguridad y protocolo | ESP32 + sensores + LCD; salidas bloqueadas | banco actual estable |
| `domus_ir_learn` | registrar protocolo, dirección y comando de los 21 botones | ESP32 + HX1838 | crear siguiente |
| `domus_actuator_test` | probar una salida a la vez con timeout corto | DRV8833, LED y buzzers cableados | crear al recibir compras |
| `domus_audio_test` | tono y frases españolas desde flash | MAX98357A + parlante | crear al recibir audio |
| `casa_inteligente_v4` | producto integrado: automático + IR Jarvis + audio | montaje final aprobado | destino final |
| `domus_anim` | animación opcional | matriz o WS2812 | no bloquea la feria |
| `inmp441_poc` | experimento antiguo de micrófono | INMP441 | archivado; no comprar |
| `picotts_poc` | síntesis experimental | salida I2S | opcional; no bloquea respuestas grabadas |

## Perfil 1 ESP32 solo

Se carga `domus_selftest`. Nada salvo USB. Debe confirmar N16R8, heap, reinicios
y puerto serie. Ninguna salida puede activarse.

## Perfil 2 banco con casi todo lo disponible

Se carga `domus_esqueleto`. Se conectan LCD 3.3 V, DHT11, suelo, nivel, LDR, PIR,
paro y silencio. GPIO4-8 permanecen físicamente bloqueados. Se añade primero un
sketch separado `domus_ir_learn` para el HX1838 en GPIO12. Bomba, motor, relé y
TP4056 se prueban por separado, nunca desde el ESP32.

## Perfil 3 banco de actuadores

Después de recibir fuente y DRV8833 se crea `domus_actuator_test` con comandos
explícitos y timeouts: bomba GPIO4 máximo 2 s inicialmente, ventilador GPIO7,
luces GPIO5/6/8 y buzzer GPIO15. Solo una salida se habilita por compilación en
cada ensayo. El paro físico se revisa incluso durante la prueba.

## Perfil 4 audio Jarvis

`domus_audio_test` usa MAX98357A en GPIO16/17/18. Reproduce tono, después frases
PCM/WAV cortas desde flash y finalmente prueba volumen. GPIO11 silencia la salida.
No contiene micrófono ni reconocimiento de voz.

## Firmware final

`casa_inteligente_v4` integra módulos sin copiar bucles bloqueantes:

```text
drivers sensores -> estado validado -> reglas de seguridad -> automatización
receptor IR ------> despachador seguro ---------------------> acciones
acciones ---------> cola de eventos -> LCD + respuesta Jarvis
```

Tareas cooperativas:

- sensores rápidos cada 1 s;
- DHT cada 2.2 s o más;
- IR atendido continuamente, sin `delay()` largo;
- seguridad de bomba en cada ciclo;
- LCD a 1 s;
- audio por cola, cancelable por paro o silencio;
- watchdog alimentado solo si el ciclo principal conserva salud.

## Contrato del control IR

Los códigos se leen del mando real y se guardan en una tabla, no se copian de
internet. Cada entrada contiene protocolo, dirección, comando, acción y permiso
de repetición. Solo volumen admite repetición sostenida. Riego, rearme y apagado
requieren una trama nueva.

| Tecla | Acción |
|---|---|
| `CH-` | modo manual |
| `CH` | siguiente pantalla LCD |
| `CH+` | modo automático |
| anterior / siguiente | luz sala / dormitorio |
| pausa | detener audio actual |
| `VOL-` / `VOL+` | volumen |
| `EQ` | diagnóstico |
| `0` | apagar cargas |
| `100+` | silencio Jarvis |
| `200+` | rearme seguro |
| `1` / `2` / `3` | sala / dormitorio / cultivo |
| `4` / `5` | ventilador / solicitud de riego |
| `6` / `7` / `8` / `9` | temperatura / humedad / suelo-nivel / estado |

## Reglas que ningún firmware puede romper

1. Todas las cargas arrancan apagadas.
2. El control IR solicita acciones; no escribe GPIO directamente.
3. El riego siempre pasa por nivel, calibración, timeout y rearme.
4. Un código desconocido no hace nada.
5. Audio, LCD, animación o IR nunca bloquean la seguridad.
6. Ningún firmware alimenta bomba, motor o relé desde 3V3/5V de la placa.
7. Cada perfil declara en Serial qué salidas físicas están habilitadas.

## Orden de implementación

1. Conservar y volver a validar `domus_esqueleto`.
2. Crear `domus_ir_learn` y registrar el mando real.
3. Añadir parser IR al núcleo sin habilitar actuadores.
4. Crear y aprobar `domus_actuator_test` cuando llegue el DRV8833.
5. Migrar la salida física final por perfiles.
6. Crear `domus_audio_test` y seleccionar frases desde flash.
7. Integrar la cola de respuestas Jarvis.
8. Ejecutar pruebas unitarias, campaña simulada y una hora de banco vigilado.

## Evidencia mínima antes de la feria

- tabla completa de 21 códigos IR;
- cinco reinicios limpios;
- cero activaciones por códigos desconocidos o repetidos;
- diez cortes correctos por nivel bajo;
- diez cortes correctos por timeout;
- una hora sin reinicios con sensores y LCD;
- una hora final con actuadores y audio vigilados;
- plan manual de respaldo mediante botones y paro físico.

## Relaciones

- [[43 - Manual final completo PROJECT DOMUS]]
- [[42 - Solicitud final de cotizacion C&D]]
- [[34 - Cierre de software y matriz de verificacion]]

