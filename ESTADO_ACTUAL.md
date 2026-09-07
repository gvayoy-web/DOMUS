# Estado actual de PROJECT DOMUS

Actualizado: 6 de septiembre de 2026.

Esta es la fuente breve para saber que ejecutar. El inventario fisico sigue en
`obsidian/proyect domus/01 - Inventario confirmado.md` y el cableado detallado
en la nota 18.

## Firmware recomendado para banco

Usar `firmware/domus_esqueleto/domus_esqueleto.ino`. Integra el hardware
confirmado: sensores de suelo, nivel y luz, PIR, DHT11/22, LCD1602 I2C, boton,
PARO, un rele de bomba, tres LED y driver de ventilador.

Compila correctamente para ESP32-S3 N16R8. Las salidas permanecen deshabilitadas
por defecto porque todavia no se han verificado polaridades, fuente y etapas en
el montaje real. Seguir la nota 33 antes de cambiar esa proteccion.

## Referencias conservadas

- `firmware/casa_inteligente_v4`: referencia funcional completa y establecida.
- `firmware/domus_selftest`: diagnostico amplio; no es el firmware operativo.
- `firmware/domus_anim`: demostracion de pantallas; no controla la casa.
- `firmware/inmp441_poc` y `firmware/picotts_poc`: pruebas aisladas de audio.

No copiar logica nueva al firmware principal y a la base a la vez. Toda funcion
nueva debe entrar primero en la base modular y tener una prueba o contrato.

## Pendiente verificable

1. Confirmar placa y GPIO 2, 9 y 13.
2. Probar sensores y guardar calibracion real.
3. Validar niveles OFF/ON sin cargas y despues cada etapa individual.
4. Ejecutar cinco arranques y PARO/rearme bajo carga.
5. Completar la matriz de la nota 33 y ensayo prolongado.
6. Solo entonces considerar la base candidata a reemplazar el firmware principal.

Jarvis, microSD, bateria y solar no forman parte del cierre de banco actual.
