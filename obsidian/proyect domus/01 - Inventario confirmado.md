---
proyecto: PROJECT DOMUS
tipo: inventario
fuente: lista confirmada por Isaac
actualizado: 2026-09-07
---

# Inventario confirmado

> [!IMPORTANT]
> Esta nota es la fuente de verdad del inventario confirmado. La alimentación
> decidida es una fuente común regulada de 5 V; falta confirmar su corriente y
> medirla bajo carga. Batería y panel solar son decoración desconectada.

## Controladores

| Componente | Cant. | Estado en DOMUS | Uso real |
|---|---:|---|---|
| ESP32-S3, 16 MB flash + 8 MB PSRAM | 1 | YA TIENES · núcleo | Código oficial esperado `N16R8`; “N8R16” es la descripción memoria/RAM usada por el propietario. Confirmar texto del blindaje. |
| Raspberry Pi Pico | 1 | YA TIENES · reserva | No hace falta para la arquitectura actual. |
| ESP8266 | 1 | YA TIENES · reserva | No hace falta: el ESP32-S3 ya tiene Wi-Fi. |

## Pantallas e interacción

| Componente | Cant. | Estado | Decisión |
|---|---:|---|---|
| LCD1602 | 1 | YA TIENES | Pantalla oficial del proyecto. |
| Adaptador I2C para LCD | al menos 1 | YA TIENES | Necesario para usar solo dos señales I2C. La lista lo menciona dentro del kit y otra vez en una compra; comprobar si físicamente hay uno o dos. |
| OLED | 0 confirmado | NO COMPRAR | El soporte OLED fue retirado; LCD1602 es la única pantalla. |
| Matriz LED | 1 | YA TIENES · opcional | Decoración o estado secundario. |
| Display 7 segmentos, 1 dígito | 1 | YA TIENES · opcional | No requerido. |
| Display 4 dígitos | 1 | YA TIENES · opcional | No requerido. |
| Barra de LEDs | 1 | YA TIENES · opcional | Indicador adicional. |
| Keypad 4×4 | 1 | YA TIENES · opcional | Control de respaldo si se desea. |
| Joystick | 1 | YA TIENES · opcional | No requerido. |
| Botones cuadrados | 6 | YA TIENES | Controles manuales y MIC OFF. |
| Botones redondos | 10 | YA TIENES | Controles manuales. |
| Micro switch | 2 | YA TIENES | Puerta/fin de carrera opcional. |
| Slide switch | 2 | YA TIENES | Puede servir como selector de modo; no se usará como interruptor principal de potencia sin comprobar corriente. |
| Potenciómetros | 2 | YA TIENES | Calibración/volumen opcional. |
| Control y receptor IR | 1 kit | YA TIENES · opcional | Respaldo de control local. |
| RFID RC522 + tarjeta + llavero | 1 kit | YA TIENES · opcional | Demostración de acceso; aún no está en el firmware principal. |

## Sensores

| Componente | Cant. | Estado | Función / observación |
|---|---:|---|---|
| DHT11/DHT22 | 1 | YA TIENES · núcleo | Temperatura y humedad ambiental. Confirmar modelo real antes de configurar firmware. |
| Humedad de suelo resistiva + comparador | 1 set | YA TIENES · núcleo | Sirve para la feria; se corroe si queda energizada. El firmware ya la identifica como resistiva y requiere calibración física. |
| Nivel de agua | 1 | YA TIENES | Integrado en software con validación y bloqueo de bomba; falta calibración física. |
| PIR | 1 | YA TIENES | Integrado en software con retención de presencia; falta confirmar pin y nivel activo. |
| LDR | 2 | YA TIENES · núcleo | Una unidad con resistencia de 10 kΩ forma el divisor de luz. |
| HC-SR04 | 1 | YA TIENES · opcional | No requerido por el núcleo. Su pin ECHO es 5 V y necesita divisor antes del ESP32. |
| MPU6050 | 1 | YA TIENES · opcional | No requerido. |
| Reed switch | 2 | YA TIENES · opcional | Puertas/ventanas. |
| Termistor | 1 | YA TIENES · opcional | Redundante frente al DHT para la demo. |
| Tilt switch | 1 | YA TIENES · opcional | Alarma de inclinación/transporte. |

## Actuadores e iluminación

| Componente | Cant. | Estado | Uso real |
|---|---:|---|---|
| Relé 1 canal, 5 V | 1 | YA TIENES | Se asignará a la bomba. |
| Relé 4 canales | 0 | FALTA | Sala, dormitorio, ventilador e invernadero. |
| Mini bomba + tubo | 1 | YA TIENES · núcleo | Riego; límite de funcionamiento obligatorio. |
| Mini motor DC + aspa | 1 | YA TIENES · núcleo | Ventilador. Añadir diodo flyback si se conmuta mediante transistor/driver. |
| Servo SG90 | 1 | YA TIENES · opcional | Puerta o persiana; no es función esencial. |
| WS2812 RGB | 1 tira | YA TIENES · núcleo de Jarvis | Aro/indicador azul. |
| LEDs verdes, rojos, amarillos, azules y blancos | 5 de cada color | YA TIENES | Luces de habitaciones e indicadores. |
| LED RGB | 1 | YA TIENES · opcional | Indicador simple. |
| L293D | 1 | YA TIENES · opcional | Driver de motores; no sustituye automáticamente al módulo de relés. |
| 74HC595 | 1 | YA TIENES · opcional | Expansión de salidas; **no sustituye** al 74AHCT125 para adaptar WS2812 a 5 V. |

## Audio

| Componente | Cant. | Estado | Decisión |
|---|---:|---|---|
| DFPlayer Mini / MP3-TF-16P | 1 | YA TIENES · respaldo | Su ranura es exclusiva para pistas del reproductor; no es almacenamiento general del ESP32. |
| Buzzer activo | 1 | YA TIENES | Alarmas simples. |
| Buzzer pasivo | 1 | YA TIENES | Tonos simples. |
| INMP441 | 0 | FALTA | Micrófono digital para Jarvis. |
| MAX98357A | 0 | FALTA | Convierte I2S a audio amplificado. |
| Altavoz 4 Ω/3 W | 0 | FALTA | Salida hablada. |
| Lector microSD SPI | 0 confirmado | FALTA | Permite al ESP32 montar FAT16/FAT32 y abrir archivos directamente. |
| Tarjeta microSD | 0 confirmado | FALTA | Una para el ESP32; una segunda solo si también se activa el DFPlayer. 4 GB FAT32 preferida, 8–32 GB FAT32 aceptable. |

## Energía

| Componente | Cant. | Estado | Decisión |
|---|---:|---|---|
| TP4056 USB-C con protección | 2 | YA TIENES | Cada placa ya combina cargador USB 1S y protección. No se ponen dos en paralelo ni se apilan con CN3065+BMS en la misma ruta. |
| Módulo de fuente para protoboard | 1 | YA TIENES | Solo pruebas ligeras; no alimentar bomba, relés y audio desde él. |
| Cable Micro-USB | 1 | YA TIENES | Útil para Pico/otros módulos; confirmar el conector real del ESP32-S3. |
| Cable de batería de 9 V | 1 | YA TIENES · no usar en potencia | Una batería rectangular de 9 V no sirve para la casa. |
| Fuente regulada 5 V/3 A | 0 | FALTA | Fuente oficial para montaje y feria. |
| Panel solar | 0 | FALTA · fase posterior | No comprar la variante 3 V/110 mA. |
| 18650 y portaceldas | 0 | FALTA · fase posterior | Solo después de medir consumo. |
| Elevador estable a 5 V | 0 | FALTA · batería | El MT3608 es candidato, sujeto a prueba de caída/temperatura. |

## Componentes discretos y montaje electrónico

| Componente | Cant. | Observación |
|---|---:|---|
| Protoboard grande | 1 | YA TIENES; solo prototipo, no instalación final con agua. |
| Resistencias 10 Ω, 100 Ω, 220 Ω, 330 Ω, 1 kΩ, 2 kΩ, 5.1 kΩ, 10 kΩ, 100 kΩ, 1 MΩ | 10 de cada valor | YA TIENES. |
| Diodos 1N4007 | 5 | YA TIENES; útiles como flyback. |
| S8050 | 2 | YA TIENES; drivers pequeños. |
| S8550 | 2 | YA TIENES. |
| Electrolíticos 10 µF | 4 | YA TIENES; insuficientes como reserva principal de 5 V. |
| Cerámicos marcados 104 | 10 | YA TIENES; **104 significa 100 nF (0.1 µF), no 104 pF ni 10,000 pF**. |
| Jumpers H/M | 20 | YA TIENES. |
| Jumpers M/M | 65 | YA TIENES. |
| Jumpers H/H | 0 confirmado | FALTA o sustituir por conectores soldados. |
| Jumpers rígidos U-Shape | 1 caja | YA TIENES. |

## Piezas que tienes pero no son necesarias para el núcleo

Raspberry Pi Pico, ESP8266, MPU6050, HC-SR04, RFID, keypad, joystick, matriz LED, displays de siete segmentos, barra LED, servo, L293D, 74HC595, termistor, tilt switch y varios botones pueden enriquecer el proyecto, pero no deben retrasar las cinco funciones principales.
