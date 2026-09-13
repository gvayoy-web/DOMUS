# PROJECT DOMUS — requisitos y decisiones acordadas

> Snapshot histórico de requisitos visuales. La decisión vigente usa fuente
> común de 5 V; batería y solar son estética desconectada. Véase
> `../../../../docs/ESTADO_ACTUAL.md`.

## Regla principal

PROJECT DOMUS será un sistema completamente local. No tendrá aplicación móvil, Kotlin, Bluetooth, BLE, Wi-Fi, MQTT, API, nube, servidor, Home Assistant, control remoto ni dependencia de Internet.

## Controlador

- Un solo ESP32-S3 N16R8.
- No se utilizará Raspberry Pi, ESP-01 ni coprocesador.
- Los radios del ESP32-S3 no forman parte del funcionamiento.
- Alimentación interna a 5 V DC; no habrá inversor ni tensión de red dentro de la maqueta.

## Entradas locales previstas

- DHT11 para temperatura y humedad.
- LDR para iluminación ambiental.
- PIR para presencia en la entrada.
- Sensor capacitivo de humedad de suelo.
- Sensor de nivel del depósito.
- Micrófono INMP441 con interruptor MIC OFF físico.
- Pulsadores físicos para cargas, modo automático y emergencia.

## Salidas locales previstas

- Bomba de riego de 5 V.
- Luz de sala.
- Luz de dormitorio.
- Luz de invernadero.
- Ventilador de 5 V.
- Pantalla local.
- Aro WS2812 de Jarvis.
- MAX98357A y altavoz para respuestas locales.

## Distribución física final

La maqueta correcta es de **una sola planta** y debe parecerse a la imagen incluida en `04_REFERENCIA`.

- Base negra de 1000 × 650 mm.
- Invernadero transparente y sistema de agua en el lado izquierdo.
- Casa abierta al frente en la zona central posterior.
- Cocina/sala, dormitorio y baño en el mismo nivel.
- Porche, jardín y pasarela en el centro frontal.
- Torre Jarvis a la derecha de la casa.
- Gabinete transparente de electrónica en el extremo derecho.
- Techo removible con dos paneles solares didácticos.

## Automatización simulada

- Arranque con todas las cargas apagadas.
- Riego con histéresis.
- Bloqueo de la bomba por nivel bajo.
- Tiempo máximo de bomba de 120 segundos y rearme obligatorio.
- Modos AUTO, MANUAL_ON y MANUAL_OFF persistente.
- Ventilación e iluminación con histéresis.
- Iluminación de sala condicionada por oscuridad y presencia.
- Estado seguro ante sensores inválidos.
- Rechazo de órdenes de voz con confianza insuficiente.
- Parada de emergencia que apaga y bloquea las cargas.

## Alcance real del simulador

El simulador permite comprobar reglas, prioridades, estados, tiempos y fallos sin comprar todavía el hardware. No puede validar consumo eléctrico, caída de tensión, precisión de sensores, ruido del micrófono, caudal de la bomba, calentamiento, compatibilidad real de relés ni autonomía solar.

## Estado del firmware

La migración de NimBLE/BLE al núcleo local está completada. El firmware C++ y
`01_FINAL_V2/simulator/domus_core.py` comparten cinco actuadores, modos
AUTO/MANUAL, histéresis, bloqueos de bomba, emergencia y modo seguro. Las
pruebas automatizadas se ejecutan antes de compilar. Permanecen fuera del cierre
por software la calibración, el pinout definitivo, la prueba con cargas reales
y los modelos de voz, porque requieren hardware o datos que no existen todavía.

## Precaución antes del corte

Las medidas son una propuesta de maqueta coherente. Antes de cortar definitivamente deben medirse la placa ESP32-S3, pantalla, aro LED, relés, paneles solares y espesor real del MDF, plywood y acrílico.
