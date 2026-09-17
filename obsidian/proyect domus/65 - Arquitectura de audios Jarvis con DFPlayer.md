---
estado: arquitectura_aprobada_pendiente_hardware
fecha: 2026-09-16
autoridad: audio_jarvis
---

# Arquitectura de audios Jarvis con DFPlayer

## Decisión

Jarvis hablará con pistas MP3 pregrabadas en la microSD exclusiva del DFPlayer
Mini. El mando IR seguirá enviando órdenes al ESP32; el ESP32 decide la acción,
aplica todas las protecciones y, solo después de conocer el resultado, solicita
una frase al DFPlayer. El reproductor nunca controla bomba, luces ni seguridad.

No se implementa reconocimiento de voz ni IA. “Jarvis” describe la personalidad
de las respuestas locales y la selección de frases.

## Restricción real de carpetas

Aunque conceptualmente exista una categoría `tierra`, la tarjeta no usará
`tierra/1.mp3`. Para `playFolder()` se usarán carpetas `01`–`99` y pistas con
tres dígitos `001.mp3`–`255.mp3`. La biblioteca oficial expone
`playFolder(folderNumber, fileNumber)`.

Estructura exacta:

```text
microSD FAT32/
├── 01/001.mp3  002.mp3  003.mp3  004.mp3
├── 02/001.mp3  002.mp3  003.mp3  004.mp3
├── 03/001.mp3  002.mp3  003.mp3  004.mp3
├── ...
└── 14/001.mp3  002.mp3  003.mp3  004.mp3
```

No añadir portadas, listas, archivos ocultos ni pistas sueltas. Formatear FAT32
y copiar las carpetas en orden numérico después de vaciar la tarjeta.

## Catálogo: cuatro frases por evento

| Carpeta | Evento | 001 | 002 | 003 | 004 |
|---:|---|---|---|---|---|
| `01` | Sistema listo | Sistemas en línea. | DOMUS operativo. | Inicialización completa. | Casa preparada. |
| `02` | Orden aceptada | Entendido. | Orden confirmada. | Ejecutando instrucción. | Como ordene. |
| `03` | Orden rechazada | Orden no permitida. | No puedo ejecutar eso. | Solicitud bloqueada. | Acción denegada por seguridad. |
| `04` | Luz encendida | Iluminación activada. | Luz encendida. | He iluminado el área. | Circuito de luz activo. |
| `05` | Luz apagada | Iluminación desactivada. | Luz apagada. | Área en modo oscuro. | Circuito de luz detenido. |
| `06` | Riego iniciado | Iniciando riego. | Bomba de agua activada. | Regando el cultivo. | Ciclo de riego en marcha. |
| `07` | Riego detenido | Riego detenido. | Bomba desactivada. | Ciclo de agua finalizado. | He detenido el riego. |
| `08` | Tierra seca | La tierra está seca. | Humedad del suelo baja. | El cultivo necesita agua. | Suelo por debajo del nivel ideal. |
| `09` | Tierra húmeda | Humedad adecuada. | La tierra está húmeda. | Suelo dentro del nivel esperado. | El cultivo tiene suficiente humedad. |
| `10` | Agua baja | Nivel de agua bajo. | Depósito insuficiente. | Riego bloqueado por falta de agua. | Recargue el depósito. |
| `11` | Temperatura alta | Temperatura elevada. | El ambiente está caliente. | Recomiendo ventilación. | Umbral térmico superado. |
| `12` | Presencia | Presencia detectada. | Movimiento registrado. | Hay actividad en la casa. | Sensor de presencia activado. |
| `13` | Emergencia | Emergencia activada. | Todas las salidas fueron detenidas. | Sistema bloqueado por seguridad. | Paro de emergencia activo. |
| `14` | Error de sensor | Sensor sin respuesta. | Lectura no válida. | Revise las conexiones del sensor. | Diagnóstico requerido. |

Las frases deben durar aproximadamente 1–3 segundos. Exportar MP3 mono,
32–44.1 kHz y 64–96 kbps para que sean ligeras. Usar la misma voz y volumen,
con compresión suave y un efecto robótico discreto; la voz debe seguir siendo
entendible en la exposición. Normalizar todas las pistas al mismo nivel para
evitar saltos bruscos.

## Selección aleatoria

Cada evento apunta a una carpeta y siempre tiene exactamente cuatro pistas. El
ESP32 elige `1..4` con `esp_random()`. Guarda la última pista usada por carpeta;
si vuelve a salir la misma, avanza circularmente a la siguiente. Así hay
variedad sin repetir dos veces seguidas.

Pseudocódigo:

```cpp
uint8_t elegirPista(uint8_t carpeta) {
  uint8_t pista = 1 + (esp_random() % 4);
  if (pista == ultimaPista[carpeta]) pista = (pista % 4) + 1;
  ultimaPista[carpeta] = pista;
  return pista;
}

reproducirJarvis(carpeta) {
  dfPlayer.playFolder(carpeta, elegirPista(carpeta));
}
```

## Cuándo habla

- Una orden IR aceptada reproduce el resultado específico, no una confirmación
  genérica adicional. Ejemplo: botón de riego aceptado → carpeta `06`.
- Una orden rechazada reproduce `03`; nivel bajo durante riego usa `10`.
- PARO usa siempre `13` y puede interrumpir cualquier frase.
- Alertas automáticas hablan solo al cambiar de estado, no en cada lectura.
- Tierra, agua, temperatura, presencia y errores tienen enfriamiento de 30 s.
- Mientras una frase normal suena, otra frase normal se descarta. Una alerta de
  emergencia la interrumpe. La lógica doméstica nunca espera a que termine MP3.
- MIC OFF/SILENCIO también silencia Jarvis, pero no desactiva LCD ni seguridad.

## Estado y volumen

- UART del DFPlayer: 9600 baudios, puerto dedicado.
- Volumen inicial propuesto: 18 de 30; VOL-/VOL+ cambian de uno en uno.
- EQ inicial: normal. No usar ecualización “bass” con parlante pequeño.
- El pin `BUSY` es recomendable para saber cuándo terminó una pista sin usar
  pausas bloqueantes. Si no está disponible, se procesan los mensajes UART.
- Si el DFPlayer, microSD o pista fallan, la orden doméstica conserva su
  resultado y se informa por LCD/Serial. El audio nunca es una dependencia.

## Conexión pendiente de auditoría

El DFPlayer ya está en inventario, pero el mapa vigente GPIO3–18 está ocupado.
No se asignarán RX/TX improvisados ni se reutilizarán GPIO17/18, porque son LCD
SDA y MODO. Antes de cablear se deben confirmar dos GPIO UART expuestos y libres
en la placa real y actualizar `MAPA_CASA`.

Alimentación y salida:

- DFPlayer VCC desde una rama de 5 V estable y GND común con el ESP32.
- ESP32 TX → resistencia serie de 1 kΩ → DFPlayer RX.
- DFPlayer TX → ESP32 RX; validar nivel del módulo antes del montaje final.
- Capacitor local recomendado cerca del módulo; audio separado de la bomba.
- Usar parlante compatible de 4–8 Ω entre `SPK1` y `SPK2`, o las salidas DAC
  hacia un amplificador compatible. No conectar las bocinas de 1–2 Ω existentes
  directamente al DFPlayer, GPIO o 3V3.

El MAX98306 no reproduce MP3: solo sería una etapa amplificadora analógica desde
`DAC_L/DAC_R`. Para la primera prueba basta DFPlayer más un parlante 4–8 Ω de
baja potencia; MAX98306 queda como ampliación si su salida y parlante se validan.

## Puertas antes de habilitarlo

1. Confirmar microSD FAT32 y reproducir manualmente `01/001.mp3`.
2. Confirmar GPIO UART libres sin conflicto con LCD, IR, botones ni sensores.
3. Probar UART, volumen bajo, BUSY y cuatro pistas de una sola carpeta.
4. Probar selección aleatoria sin repetición y funcionamiento no bloqueante.
5. Integrar una orden inocua, como luz, antes de riego o emergencia.
6. Verificar que desconectar DFPlayer no afecta control, PARO ni LCD.
7. Habilitar el catálogo completo solo después de esas pruebas.

## Fuentes técnicas

- DFRobot, biblioteca oficial `DFRobotDFPlayerMini`, API `playFolder()`:
  https://github.com/DFRobot/DFRobotDFPlayerMini
- DFRobot, producto y diagrama oficial DFPlayer Mini DFR0299:
  https://wiki.dfrobot.com/DFPlayer_Mini_SKU_DFR0299

Relacionadas: [[00 - Inicio]], [[01 - Inventario confirmado]],
[[59 - Firmware unico y perfil banco S8050 IR]] y
[[64 - Sesion fisica COM9 LCD IR sensores y bomba]].
