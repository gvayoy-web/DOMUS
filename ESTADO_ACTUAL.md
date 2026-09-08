# Estado actual de PROJECT DOMUS

Actualizado: 7 de septiembre de 2026.

Esta es la fuente breve para saber que ejecutar. El inventario fisico sigue en
`obsidian/proyect domus/01 - Inventario confirmado.md` y el cableado detallado
en la nota 18.

## Firmware recomendado para banco

Usar `firmware/domus_esqueleto/domus_esqueleto.ino`. Integra el hardware
confirmado: sensores de suelo, nivel y luz, PIR, DHT11/22, LCD1602 I2C, boton,
PARO, un rele de bomba y un modulo de cuatro reles para sala, dormitorio,
ventilador e invernadero.

Compila correctamente para el ESP32-S3 N16R8 confirmado (16 MB flash + 8 MB
PSRAM): 373,694 bytes de programa y 24,388
bytes globales. Las salidas permanecen deshabilitadas
por defecto porque todavia no se han verificado polaridades, fuente y etapas en
el montaje real. La ronda B01-B05 se hace sin relés ni cargas y sin cambiar esa
protección; seguir las notas 33 y 37.

## Cierre de software local

El 6 de septiembre de 2026 pasaron los cinco perfiles del firmware principal,
la base modular, el autotest y la demostracion de pantallas. Tambien pasaron el
validador consolidado, las pruebas de IA y una campaña semirreal determinista
de 10,000 pasos. La evidencia y los tamanos exactos
estan en `obsidian/proyect domus/34 - Cierre de software y matriz de verificacion.md`.

## Referencias conservadas

- `firmware/casa_inteligente_v4`: referencia funcional completa y establecida.
- `firmware/domus_selftest`: diagnostico amplio; no es el firmware operativo.
- `firmware/domus_anim`: demostracion de pantallas; no controla la casa.
- `firmware/inmp441_poc` y `firmware/picotts_poc`: pruebas aisladas de audio.

No copiar logica nueva al firmware principal y a la base a la vez. Toda funcion
nueva debe entrar primero en la base modular y tener una prueba o contrato.

## Pendiente exclusivamente físico

1. Documentar la placa N16R8 confirmada y comprobar GPIO 2, 9 y 13.
2. Probar sensores y guardar calibracion real.
3. Validar que los cinco canales sean activos LOW, primero sin cargas y despues cada etapa individual.
4. Ejecutar cinco arranques y PARO/rearme bajo carga.
5. Completar la matriz de la nota 33 y ensayo prolongado.
6. Solo entonces considerar la base candidata a reemplazar el firmware principal.

La alimentación operativa será una fuente común regulada de 5 V; batería y
solar quedan como elementos estéticos, eléctricamente desconectados. Jarvis y
microSD no forman parte del cierre de banco actual.

Arduino IDE requiere `DHT sensor library`, `Adafruit Unified Sensor` y
`LiquidCrystal I2C`. La instalación y diagnóstico están en la nota 35.

## Primera carga física, 7 de septiembre de 2026

La placa apareció como `USB-Enhanced-SERIAL CH343` en COM9. `esptool` confirmó
ESP32-S3 revisión 0.2 y PSRAM embebida de 8 MB. `domus_esqueleto` fue escrito y
verificado por hash. El diagnóstico real respondió
`PLACA=ESP32-S3-N16R8`, `PERFIL=BANCO_SIN_ACTUADORES`, `SALIDAS=0`,
`OUT=00000`, `PARO=0` y `SEGURO=0`. Sensores, LCD, relés y cargas estaban
desconectados; sus lecturas no constituyen prueba de hardware.
