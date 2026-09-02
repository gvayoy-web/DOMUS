---
proyecto: PROJECT DOMUS
tipo: matriz
actualizado: 2026-09-01
---

# Matriz de funciones y componentes

| Función prometida | Hardware necesario | ¿Está? | Trabajo pendiente |
|---|---|---|---|
| Control central | ESP32-S3 N16R8 | Sí | Cargar y validar firmware en placa real. |
| Pantalla de estado | LCD1602 + adaptador I2C | Sí | Corregir pin SCL inválido y probar dirección 0x27/0x3F. |
| Luz sala | LED(s), resistencia, relé | Parcial | LED/resistencia sí; canal de relé vendrá del módulo de 4 canales. |
| Luz dormitorio | LED(s), resistencia, relé | Parcial | Igual que sala. |
| Luz invernadero | LED(s), resistencia, relé | Parcial | Igual que sala. |
| Ventilación | Motor+aspa, relé o driver, diodo | Sí/Parcial | Motor y diodo sí; canal en relé de 4 canales. Medir corriente. |
| Riego | Bomba+tubo, relé, depósito | Sí/Parcial | Usar relé de 1 canal existente; falta depósito físico y prueba de fugas. |
| Humedad de suelo | Sonda resistiva | Sí | Adaptar comentarios/calibración del firmware; energizar solo durante lectura si es posible. |
| Temperatura/humedad de aire | DHT11/DHT22 | Sí | Confirmar modelo real y calibrar. |
| Luz ambiental | LDR + 10 kΩ | Sí | Montar divisor y calibrar. |
| Presencia | PIR | Sí | Falta código y pin definitivo. |
| Nivel de depósito | Sensor de nivel | Sí | Falta código, pin y protección contra agua. |
| Jarvis escucha | INMP441 | No | Comprar/importar y probar PoC a 16 kHz. |
| Jarvis entiende | modelos TinyML int8 | No, es software | Grabar dataset, entrenar, medir precisión y guardar en flash. |
| Jarvis habla | PicoTTS + MAX98357A + altavoz | Parcial | PoC existe; falta hardware e integración. |
| Aro azul | WS2812 + 330 Ω + desacoplo | Sí/Parcial | Tira y resistencia sí; adaptar nivel lógico es recomendado. |
| Respaldo de voz MP3 | DFPlayer + microSD + altavoz | Parcial | DFPlayer sí; tarjeta y salida de audio no. Es opcional. |
| BLE | ESP32-S3 | Sí | Firmware preparado; validar con cliente BLE. |
| Wi-Fi/MQTT | ESP32-S3 + router | Sí en hardware | Software opcional pendiente. |
| Solar | panel, cargador solar, batería, protección y elevador | No | Fase posterior a medición. |

## Recuento correcto de relés

El diseño tiene **cinco cargas conmutadas**:

1. Bomba.
2. Luz de sala.
3. Luz de dormitorio.
4. Ventilador.
5. Luz de invernadero.

Asignación recomendada:

| Hardware | Canal | Carga |
|---|---:|---|
| Relé de 1 canal que ya tienes | 1 | Bomba |
| Nuevo relé de 4 canales | 1 | Luz sala |
| Nuevo relé de 4 canales | 2 | Luz dormitorio |
| Nuevo relé de 4 canales | 3 | Ventilador |
| Nuevo relé de 4 canales | 4 | Luz invernadero |

**Conclusión:** el relé de 8 canales no es necesario. Solo conviene si se decide añadir tres cargas nuevas reales. El firmware debe cambiarse de ocho salidas lógicas a cinco o marcar claramente las tres salidas sin hardware.

## Qué se mostrará aunque Jarvis aún no esté listo

La demostración mínima defendible funciona con LCD, DHT, LDR, humedad de suelo, bomba, ventilador, luces, botones/BLE y reglas locales. Jarvis se habilita únicamente después de validar micrófono, modelo y audio.

