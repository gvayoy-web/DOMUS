---
estado: evidencia_fisica_vigente
fecha: 2026-09-16
autoridad: sesion_de_banco
---

# Sesión física: COM9, LCD, IR, sensores y bomba

Esta nota separa observación real, inferencia y trabajo pendiente. Un mensaje
Serial demuestra lo que vio el ESP32; no certifica por sí solo un componente.

## Confirmado

- La placa conectada es una ESP32-S3 N16R8 y aparece en **COM9**.
- El perfil cargado es `BANCO_COMPLETO_S8050_IR`.
- La carga por USB terminó y el hash de flash fue verificado.
- `DIAGNOSTICO` respondió con `IR=ON`, watchdog activo y bomba declarada como
  `S8050_GPIO4`.
- El receptor infrarrojo produjo al menos un comando real: `0x19` al pulsar el
  control. Esto confirma recepción básica, no la tabla completa.
- En una prueba anterior de esta sesión el LCD respondió en dirección `0x27`.
  Después fue desconectado; el diagnóstico posterior dice `PANTALLA=NINGUNA`.
- Un pulso de prueba de 250 ms en GPIO4 se ejecutó sin reiniciar la placa.

## Falló o sigue abierto

- La minibomba no giró durante el pulso GPIO4. La etapa S8050, alimentación,
  masa común, pinout real del transistor, diodo y continuidad siguen pendientes.
- El DHT11 devuelve NaN en GPIO14. Montaje esperado mirando la cara cuadriculada,
  patas abajo: 1→3V3, 2→GPIO14, 3 libre, 4→GND; resistencia de 5.1–10 kΩ entre
  patas 1 y 2, nunca en serie con DATA.
- Suelo y nivel han dado lecturas inválidas/intermitentes. No existe calibración
  seca/húmeda ni vacío/lleno aprobada.
- PIR leyó HIGH, pero falta una prueba controlada de reposo, movimiento y tiempo
  de retención. LDR sí reaccionó a cambios de luz, aún sin calibración final.
- No se ejecutó el HIL completo y no se aprendieron las 21 teclas del mando.

## Firmware instalado para la prueba actual

Commit `9bb9684` en `DOMUS/main`:

- cada tecla IR aparece cinco segundos en el LCD como
  `IR P<protocolo> A<direccion>` y `CMD 0x<codigo>`;
- Serial emite `IR;PROTO=...;ADDR=...;CMD=...`;
- vista 0: temperatura y humedad ambiental;
- vista 1: humedad de suelo y porcentaje de agua;
- agua usa provisionalmente 600 ADC = 0% y 2500 ADC = 100%.

El LCD se escanea al arrancar. Debe conectarse a 3V3, GND, SDA GPIO17 y SCL
GPIO13 **antes** de encender o pulsar RESET. El botón MODO entre GPIO18 y GND
cambia de página.

## Próxima evidencia a capturar

1. Anotar las 21 teclas: nombre físico, protocolo, dirección y comando.
2. Confirmar que el LCD muestra cada código y ambas páginas de sensores.
3. Reparar DHT11 y registrar temperatura/humedad estables.
4. Registrar ADC de suelo seco/húmedo y agua vacío/lleno.
5. Revisar la etapa S8050 sin energizar; luego repetir una prueba breve y
   vigilada antes de intentar automatización.

Relacionadas: [[63 - Auditoria total de Obsidian y estado real]],
[[59 - Firmware unico y perfil banco S8050 IR]] y
`docs/SESION_REAL_IR_S8050.md`.
