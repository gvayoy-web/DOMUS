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
- El receptor infrarrojo produjo los 21 comandos del mando CAR MP3. Protocolo
  observado: `P7`; dirección: `A0000`. La tabla completa está abajo.
- En una prueba anterior de esta sesión el LCD respondió en dirección `0x27`.
  Después fue desconectado; el diagnóstico posterior dice `PANTALLA=NINGUNA`.
- Un pulso de prueba de 250 ms en GPIO4 se ejecutó sin reiniciar la placa.

## Tabla física del mando CAR MP3

| Botón | Código |
|---|---:|
| CH- | `0x0045` |
| CH | `0x0046` |
| CH+ | `0x0047` |
| Anterior | `0x0044` |
| Pausa/Play | `0x0043` |
| Siguiente | `0x0040` |
| Volumen - | `0x0007` |
| Volumen + | `0x0015` |
| EQ | `0x0009` |
| 0 | `0x0016` |
| 100+ | `0x0019` |
| 200+ | `0x000D` |
| 1 | `0x000C` |
| 2 | `0x0018` |
| 3 | `0x005E` |
| 4 | `0x0008` |
| 5 | `0x001C` |
| 6 | `0x005A` |
| 7 | `0x0042` |
| 8 | `0x0052` |
| 9 | `0x004A` |

La captura reveló que `Pausa/Play` y `Siguiente` estaban intercambiados en la
tabla inicial del firmware. Se corrigió antes de conceder autoridad al mando.

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

### Diagnóstico pasivo posterior

Se tomaron seis muestras sin activar salidas. La bomba y los cuatro canales
permanecieron en 0. LDR fue estable en 76–77%, PIR pasó a 1, mientras DHT11,
suelo y nivel permanecieron inválidos. Después apareció un
`Interrupt watchdog timeout` y la placa reinició. El backtrace localizó el
bloqueo en `DHT::expectPulse()` desde `leerAmbiente()`, no en I2C. Para evitar
reinicios repetidos con el DHT mal conectado, el firmware suspende sus lecturas
tras tres respuestas NaN y exige corregir el sensor y reiniciar.

El aparente apagado del LCD también coincidía con los cinco segundos de la
vista temporal IR. Se eliminó `lcd.clear()` de los cambios de vista; ahora se
sobrescriben las 32 celdas sin un intervalo blanco.

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

1. Confirmar que el LCD muestra ambas páginas de sensores sin destellos.
2. Reparar DHT11 y registrar temperatura/humedad estables.
3. Registrar ADC de suelo seco/húmedo y agua vacío/lleno.
4. Importar/aprender la tabla únicamente durante una prueba supervisada: el
   botón 5 tiene autoridad para solicitar riego cuando el mapa está aprendido.
5. Revisar la etapa S8050 sin energizar; luego repetir una prueba breve y
   vigilada antes de intentar automatización.

Relacionadas: [[63 - Auditoria total de Obsidian y estado real]],
[[59 - Firmware unico y perfil banco S8050 IR]] y
`docs/SESION_REAL_IR_S8050.md`.
