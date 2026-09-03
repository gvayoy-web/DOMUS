# Compilación validada del firmware doméstico

Fecha de última validación: 2 de septiembre de 2026.

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

- LiquidCrystal I2C 1.1.2.
- DHT sensor library 1.4.7.
- Adafruit Unified Sensor 1.1.15.

## Resultado actual

- Programa: 399,078 bytes de 3,145,728 bytes disponibles, aproximadamente 12 %.
- Memoria dinámica global: 24,948 bytes de 327,680, aproximadamente 7 %.
- Binario principal: 399,232 bytes.
- SHA-256: `FBF52C10664BBF1400045FF52B11EC98F894AFFCC543D5DACAF2EF280D5F3D10`.
- Resultado de GitHub Actions: compilación y generación de binarios correctas.
- Ejecución final de referencia: https://github.com/gvayoy-web/proyecto-domus/actions/runs/33523880928

La versión actual incluye cinco cargas, PIR, nivel de agua, `MANUAL_OFF`, paro
de emergencia, MIC OFF, control por USB Serial y soporte microSD. Se compiló
localmente con Arduino CLI 1.5.1 y Arduino-ESP32 3.3.10. Los binarios quedaron
en `build/firmware/`.

El aviso final procede de los metadatos de LiquidCrystal I2C 1.1.2, que declara
solo arquitectura AVR aunque compila para ESP32. No quedaron advertencias del
archivo principal al repetir la compilación con `--warnings all`.

## Siguiente prueba física

1. Alimentar el ESP32-S3 por USB o fuente regulada, sin panel solar.
2. Cargar los binarios o compilar desde Arduino IDE con la misma configuración.
3. Confirmar cinco arranques consecutivos sin pulsos visibles en los relés.
4. Probar cada salida, prioridad manual, corte de bomba y lecturas de sensores.
5. Anotar el pinout real y cualquier canal activo en HIGH en lugar de LOW.
