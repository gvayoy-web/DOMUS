# Compilación validada del firmware doméstico

Fecha: 1 de septiembre de 2026.

La fase de compilación del núcleo doméstico se validó en GitHub Actions para
la placa ESP32-S3 N16R8. Esta prueba confirma que el programa y sus dependencias
son compatibles; no sustituye las pruebas eléctricas con la placa conectada.

## Configuración verificada

- Placa: `ESP32S3 Dev Module`.
- FQBN: `esp32:esp32:esp32s3`.
- Flash: 16 MB.
- PSRAM: OPI, 8 MB en el módulo N16R8.
- Partición: `app3M_fat9M_16MB`.
- Arduino CLI: rama estable 1.x.
- Arduino-ESP32: 3.3.10.
- Jarvis local: desactivado durante esta fase.

## Dependencias fijadas

- NimBLE-Arduino 2.5.1.
- LiquidCrystal I2C 1.1.2.
- Adafruit GFX Library 1.12.6.
- Adafruit SSD1306 2.5.17.
- DHT sensor library 1.4.7.
- Adafruit Unified Sensor 1.1.15.

## Resultado

- Programa: 650,223 bytes de 3,145,728 bytes disponibles, aproximadamente 20 %.
- Memoria dinámica global: 35,200 bytes de 327,680, aproximadamente 10 %.
- Resultado de GitHub Actions: compilación y generación de binarios correctas.
- Ejecución de referencia: https://github.com/gvayoy-web/proyecto-domus/actions/runs/33523336979

Los avisos restantes proceden de LiquidCrystal I2C y del core de Espressif al
compilar con `--warnings all`; no impiden generar el firmware. La llamada
obsoleta `NimBLEService::start()` sí pertenecía al proyecto y fue eliminada.

## Siguiente prueba física

1. Alimentar el ESP32-S3 por USB o fuente regulada, sin panel solar.
2. Cargar los binarios o compilar desde Arduino IDE con la misma configuración.
3. Confirmar cinco arranques consecutivos sin pulsos visibles en los relés.
4. Probar cada salida, prioridad manual, corte de bomba y lecturas de sensores.
5. Anotar el pinout real y cualquier canal activo en HIGH en lugar de LOW.
