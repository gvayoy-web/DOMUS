# Diagnóstico seguro del banco actual

Este sketch prueba exclusivamente LCD, DHT11, suelo, nivel, LDR y receptor IR.
No configura ni acciona bomba, ventilador, LEDs ni DRV8833.

## Pines

- LDR: GPIO3.
- IR HX1838: GPIO12.
- LCD: SCL GPIO13 y SDA GPIO17.
- DHT11: GPIO14.
- Suelo: GPIO15.
- Nivel: GPIO16.

## Comandos a 115200 baudios

- `LECTURAS`: muestra ADC y DHT.
- `LCD`: escanea I2C desde `0x08` hasta `0x77`.
- `IR_LISTA`: lista hasta 21 códigos únicos capturados.
- `IR_CLEAR`: vacía la lista temporal.
- `MUESTRA_SECO`, `MUESTRA_HUMEDO`, `MUESTRA_OSCURO`, `MUESTRA_CLARO` y
  `MUESTRA_NIVEL`: producen comandos `CAL_*` para copiar al firmware principal.
- `HELP`: muestra el resumen.

La captura de este diagnóstico vive solo en RAM. El firmware principal guarda
calibración mediante `CAL_GUARDAR` y el mando mediante `IR_GRABAR_0` a
`IR_GRABAR_20`.
