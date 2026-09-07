---
proyecto: PROJECT DOMUS
tipo: matriz
actualizado: 2026-09-07
---

# Matriz de funciones y componentes

| Función prometida | Hardware necesario | ¿Está? | Trabajo pendiente |
|---|---|---|---|
| Control central | ESP32-S3 N16R8 | Sí | Cargar y validar firmware en placa real. |
| Pantalla de estado | LCD1602 + adaptador I2C | Sí | Código corregido a GPIO13 provisional y detección 0x27/0x3F; confirmar pin físicamente. |
| Luz sala | Canal 1 del módulo de 4 relés + luz DC | Parcial | GPIO5, activo LOW previsto; validar módulo y carga. |
| Luz dormitorio | Canal 2 del módulo de 4 relés + luz DC | Parcial | GPIO6, activo LOW previsto; validar módulo y carga. |
| Luz invernadero | Canal 4 del módulo de 4 relés + luz DC | Parcial | GPIO8, activo LOW previsto; validar módulo y carga. |
| Ventilación | Canal 3 del módulo de 4 relés + motor/aspa y diodo | Parcial | GPIO7, activo LOW previsto; medir arranque y temperatura. |
| Riego | Bomba+tubo, relé, depósito | Sí/Parcial | Usar relé de 1 canal existente; falta depósito físico y prueba de fugas. |
| Humedad de suelo | Sonda resistiva | Sí | Código e histéresis completos; calibrar seco/húmedo físicamente. |
| Temperatura/humedad de aire | DHT11/DHT22 | Sí | Confirmar modelo real y calibrar. |
| Luz ambiental | LDR + 10 kΩ | Sí | Montar divisor y calibrar. |
| Presencia | PIR | Sí | Código y retención implementados; confirmar GPIO9 y nivel activo. |
| Nivel de depósito | Sensor de nivel | Sí | Lectura, validación y bloqueo de bomba implementados; confirmar GPIO2, umbral y protección contra agua. |
| Jarvis escucha | INMP441 | No | Comprar/importar y probar PoC a 16 kHz. |
| Jarvis entiende | modelos TinyML int8 | No, es software | Grabar dataset, entrenar, medir precisión y guardar en flash. |
| Jarvis habla | PicoTTS + MAX98357A + altavoz | Parcial | PoC existe; falta hardware e integración. |
| Aro azul | WS2812 + 330 Ω + desacoplo | Sí/Parcial | Tira y resistencia sí; adaptar nivel lógico es recomendado. |
| Respaldo de voz MP3 | DFPlayer + microSD + altavoz | Parcial | DFPlayer sí; tarjeta y salida de audio no. Es opcional. |
| Diagnóstico local | USB Serial del ESP32-S3 | Sí | Estado, diagnóstico, paro, rearme, recuperación y limitación de ráfagas implementados. |
| Supervisor anti-colapso | ESP32-S3 | Sí | Modo seguro por memoria/reinicios, watchdog y recuperación explícita implementados. |
| Wi-Fi/MQTT | ESP32-S3 + router | Fuera de alcance | No pertenece al núcleo local decidido; solo sería una extensión futura. |
| Solar y batería | Elementos de maqueta | Estética | Permanecen eléctricamente desconectados. |

## Recuento correcto de relés

El diseño tiene **cinco cargas conmutadas**:

1. Bomba.
2. Luz de sala.
3. Luz de dormitorio.
4. Ventilador.
5. Luz de invernadero.

Asignación operativa elegida (1 + 4 relés):

| Hardware | GPIO/canal | Carga |
|---|---:|---|
| Relé de 1 canal que ya tienes | 1 | Bomba |
| Módulo de 4 relés, canal 1 | GPIO5 | Luz sala |
| Módulo de 4 relés, canal 2 | GPIO6 | Luz dormitorio |
| Módulo de 4 relés, canal 3 | GPIO7 | Ventilador |
| Módulo de 4 relés, canal 4 | GPIO8 | Luz invernadero |

**Conclusión:** comprar o confirmar un módulo de cuatro relés compatible con
lógica de 3.3 V. Junto al relé individual completa las cinco salidas físicas.

## Qué se mostrará aunque Jarvis aún no esté listo

La demostración mínima defendible funciona con LCD, DHT, LDR, humedad de suelo, bomba, ventilador, luces, botones/USB Serial y reglas locales. Jarvis se habilita únicamente después de validar micrófono, modelo y audio.
