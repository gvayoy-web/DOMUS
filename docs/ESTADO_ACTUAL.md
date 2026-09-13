# Estado actual de PROJECT DOMUS

Actualizado: 13 de septiembre de 2026.

Esta es la fuente breve para saber que ejecutar. El inventario fisico sigue en
`obsidian/proyect domus/01 - Inventario confirmado.md` y el cableado detallado
en la nota 18.

## Firmware recomendado para banco

Usar `firmware/domus_esqueleto/domus_esqueleto.ino`. Es un envoltorio que
incluye literalmente `casa_inteligente_v4.ino` con el perfil 3
`BANCO_COMPLETO_S8050_IR`; banco y producto ya no tienen lógicas independientes.
Integra suelo, nivel, LDR, PIR, DHT11, LCD, botones, tres LED, IR y bomba por
S8050. Ventilador, driver doble y audio quedan bloqueados.

Para códigos IR crudos y muestras de calibración sin tocar ninguna salida usar
`firmware/diagnosticos/domus_banco_integracion`. El antiguo esqueleto modular
se conserva solamente en `firmware/legacy/domus_esqueleto` para regresión.

## Cierre de software local

El 6 de septiembre de 2026 pasaron los cinco perfiles del firmware principal,
la base modular, el autotest y la demostracion de pantallas. Tambien pasaron el
validador consolidado, las pruebas de IA y una campaña semirreal determinista
de 10,000 pasos. La evidencia y los tamanos exactos
estan en `obsidian/proyect domus/34 - Cierre de software y matriz de verificacion.md`.

## Referencias conservadas

- `firmware/casa_inteligente_v4`: referencia funcional completa y establecida.
- `firmware/diagnosticos/domus_banco_integracion`: diagnóstico vigente IR,
  LCD, DHT y ADC con GPIO4-8 sin configurar.
- `firmware/domus_selftest`: diagnóstico histórico de mapa antiguo; no usar
  para cablear el banco actual.
- `firmware/domus_anim`: demostracion de pantallas; no controla la casa.
- `firmware/inmp441_poc` y `firmware/picotts_poc`: pruebas aisladas de audio.

Toda función nueva entra únicamente en `casa_inteligente_v4`; el esqueleto la
recibe automáticamente mediante inclusión y debe tener una prueba o contrato.

## Pendiente exclusivamente físico

1. Documentar la placa N16R8 confirmada y comprobar GPIO 2, 9 y 13.
2. Probar sensores y guardar calibracion real.
3. Identificar las cinco patas del rele por esquema/continuidad y validar solo la etapa GPIO4-S8050-rele.
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
