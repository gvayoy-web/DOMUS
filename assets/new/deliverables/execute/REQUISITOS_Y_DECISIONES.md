# PROJECT DOMUS — requisitos y decisiones acordadas

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

## Trabajo de firmware pendiente

El proyecto original todavía debe migrarse para eliminar NimBLE/BLE y trasladar la lógica probada de `01_FINAL_V2/simulator/domus_core.py` al firmware C++ del ESP32-S3. Estimación discutida: aproximadamente 48–88 horas entre migración, drivers, controles físicos, integración, calibración y pruebas reales.

## Precaución antes del corte

Las medidas son una propuesta de maqueta coherente. Antes de cortar definitivamente deben medirse la placa ESP32-S3, pantalla, aro LED, relés, paneles solares y espesor real del MDF, plywood y acrílico.
