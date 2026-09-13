# Banco mínimo LCD + IR + DRV8833

Este firmware identifica el LCD I2C, registra hasta 21 teclas IR y permite
pulsos vigilados de 500 ms en cada canal del DRV8833. No es el firmware final.

## Dependencias Arduino IDE

- `LiquidCrystal_I2C`
- `IRremote` 4.x de Armin Joachimsmeyer
- Core ESP32 de Espressif

Monitor Serial: **115200**, final de línea **Nueva línea**.

## Orden seguro

1. Conectar únicamente ESP32 + LCD + receptor IR y cargar el firmware.
2. Anotar `LCD;DIRECCION;0x..`.
3. Pulsar cada tecla una sola vez; enviar `LISTA` y copiar las 21 líneas.
4. Desconectar USB antes de añadir el DRV8833.
5. Confirmar visualmente que la placa recibida dice `DRV8833` y tiene las
   etiquetas del diagrama. Si no coinciden, detenerse.
6. Probar primero `A_PULSE` y después `B_PULSE`. Nunca puentear salidas.

## Comandos

`HELP`, `LCD`, `LISTA`, `IR_CLEAR`, `A_PULSE`, `B_PULSE`, `STOP`.

## Decisión sobre mediciones

Las mediciones eléctricas quedan **SKIP por decisión del propietario**, no
`PASS`. El firmware limita cada prueba a 500 ms, pero eso no demuestra corriente,
caída de tensión ni temperatura segura.
