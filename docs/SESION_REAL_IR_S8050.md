# Sesión real: control IR, sensores y bomba con un S8050

Esta sesión usa **solo** `firmware/casa_inteligente_v4` en perfil 3 o su envoltorio `firmware/domus_esqueleto`. El [diagrama pin por pin](DIAGRAMAS_CADA_FIRMWARE.md) y el [SVG del banco](../visualizaciones/domus-banco-final-s8050-ir.svg) son el mapa de conexión. No uses `domus_selftest` ni `domus_anim`: sus pines son diferentes.

**Si ahora solo tienes la placa conectada por USB:** puedes comprobar por Serial
`DIAGNOSTICO`, `ESTADO` y `PRUEBA`, pero verás sensores ausentes. Para el
primer test real del mando, desconecta el USB y añade **solo tres cables** del
receptor IR: `VCC/+`→`3V3`, `GND/-`→`GND`, `OUT/S`→`GPIO12`.
Vuelve a conectar USB y prueba los códigos antes de montar el S8050. El mando
CAR MP3 es un **emisor**: no se cablea al ESP32; se apunta al receptor.

**Comprobación USB del 15-09-2026:** la ESP32-S3 apareció como COM9, se cargó
`domus_esqueleto` y la escritura fue verificada por hash. `DIAGNOSTICO`
respondió `PERFIL_CANDIDATO=BANCO_COMPLETO_S8050_IR`, `IR=ON`,
`BOMBA_ETAPA=S8050_GPIO4`, `PANTALLA=NINGUNA`. `ESTADO` indicó las cinco
salidas en 0. El DHT11 no respondió y el bus I²C no encontró pantalla: en esa
sesión no había ningún componente conectado a los GPIO. Es **prueba de arranque
y Serial**, no prueba física de sensores, IR ni bomba.

## Antes de conectar USB o batería

1. Comprueba que el receptor IR dice `VCC/+`→3V3, `GND/-`→GND y `OUT/S`→GPIO12. El PIR dice `VCC`→3V3, `GND`→GND y `OUT`→GPIO9. No deduzcas izquierda/derecha: lee las letras de **tus** módulos.
2. DHT11 suelto mirando la cara cuadriculada: pata 1→3V3, pata 2→GPIO14, pata 3 vacía, pata 4→GND; 10 kΩ entre 1 y 2. Suelo `AO`→GPIO15, nivel `S`→GPIO16, LDR en divisor→GPIO3, LCD `SDA`→GPIO17 y `SCL`→GPIO13.
3. Botones: STOP→GPIO10/GND, SILENCIO→GPIO11/GND, MODO→GPIO18/GND. LED sala GPIO5, cuarto GPIO6 y cultivo GPIO8, cada uno con resistencia.
4. **Primera etapa: deja la minibomba y la alimentación del TP4056 desconectadas.** Puedes tener montados el S8050, su resistencia de base 1 kΩ, pull-down 10 kΩ y diodo, pero evita que una tecla `5` ya aprendida mueva la bomba durante el registro IR. GPIO7 y ventilador vacíos.
5. Antes de conectar la bomba, confirma B/C/E del transistor real, la orientación del 1N4007 (raya hacia `OUT+`), GND común con el ESP32 y la minibomba sumergida. El TP4056 se usa solo para la prueba supervisada de nota 49; no es la fuente final.

## Puerto y monitor

`COM3` y `COM4` pueden aparecer como «Unknown». No cargues hasta identificar cuál llega **al conectar esta ESP32**: ejecuta `arduino-cli board list` con la placa desconectada, conecta la placa y repite; usa el puerto nuevo. Si ambos persisten o no aparece uno nuevo, identifica el dispositivo en el Administrador de dispositivos o con la serigrafía/USB de la placa. Monitor Serial: **115200 baudios y envío con nueva línea**. Solo un programa puede abrir el puerto a la vez: cierra el monitor antes de cargar o de correr HIL.

## Etapa A — códigos crudos, sin salidas

El firmware de producto muestra directamente cada pulsación en el LCD durante
5 segundos: arriba `IR P7 A00FF` (protocolo y dirección) y abajo `CMD 0x0019`.
Pulsa una tecla a la vez y copia ambos renglones. Conecta el LCD antes de
encender o reiniciar, porque la pantalla se detecta durante el arranque. También
puedes usar temporalmente `firmware/diagnosticos/domus_banco_integracion`, que
no configura GPIO4–8. Por Serial copia cada línea
`IR;PROTO=...;DIR=...;CMD=...;REPEAT=0`; `REPEAT=1` indica una tecla sostenida.
`LECTURAS` y `MUESTRA_SECO/HUMEDO/OSCURO/CLARO/NIVEL` permiten observar sensores
sin activar la bomba.

| Índice | Tecla física | PROTO / DIR / CMD observado | ¿Respondió? |
|---:|---|---|---|
| 0 | CH- | | |
| 1 | CH | | |
| 2 | CH+ | | |
| 3 | Anterior | | |
| 4 | PLAY | | |
| 5 | Siguiente | | |
| 6 | VOL- | | |
| 7 | VOL+ | | |
| 8 | EQ | | |
| 9 | 0 | | |
| 10 | 100+ | | |
| 11 | 200+ | | |
| 12 | 1 | | |
| 13 | 2 | | |
| 14 | 3 | | |
| 15 | 4 | | |
| 16 | 5 | | |
| 17 | 6 | | |
| 18 | 7 | | |
| 19 | 8 | | |
| 20 | 9 | | |

**Dos teclas físicas no deben entregar el mismo CMD** para este firmware: el producto rechaza duplicados. La lista del diagnóstico vive solo en RAM; no aprende acciones todavía.

## Etapa B — cargar el producto y aprender

Carga el producto perfil 3 o `domus_esqueleto` en el mismo puerto identificado. Comprueba `DIAGNOSTICO`: debe contener `PERFIL_CANDIDATO=BANCO_COMPLETO_S8050_IR`, `IR=ON` y `BOMBA_ETAPA=S8050_GPIO4`. Si muestra otro perfil, detente y corrige la carga.

Para cada fila anterior, escribe `IR_GRABAR_N` reemplazando N por 0…20, espera la línea `ACK;IR_GRABAR;PULSA=...` y presiona **solo esa tecla**. La línea final debe decir `ACK;IR_GRABAR;TECLA;CMD=0x...;ok`. Repite una por una. `NACK;...;codigo_duplicado` significa que debes revisar las dos teclas, no repetirlas a ciegas. `IR_LISTA` debe terminar en `APRENDIDAS=21/21;ESTADO=COMPLETO`. El producto guarda esto en NVS. `IR_BORRAR` quita la autoridad de todas las teclas y exige aprender de nuevo.

**Durante el aprendizaje, deja la alimentación de bomba desconectada.** Después prueba las acciones sin bomba:

| Teclas | Resultado esperado |
|---|---|
| CH- / CH | Cambian vista LCD |
| CH+ / 6 / 7 / 8 / 9 | Reportan ESTADO |
| EQ | Reporta DIAGNOSTICO |
| Anterior o 1 | Alterna LED sala |
| Siguiente o 2 | Alterna LED cuarto |
| 3 | Alterna LED cultivo |
| 4 | Ventilador bloqueado (`NACK`); GPIO7 sin cable |
| 0 | Apaga las salidas |
| 200+ | Rearma tras PARO y deja salidas apagadas |
| PLAY, VOL-/VOL+, 100+ | Audio deshabilitado (`NACK`) |
| 5 | Orden de riego; **no presionar hasta etapa D** |

Prueba también que mantener una tecla de luz no causa varios cambios rápidos. Si una tecla desconocida responde `NACK;IR;TECLA_DESCONOCIDA`, ninguna salida debe cambiar.

## Etapa C — casa sin motor

En Serial envía `PRUEBA` y guarda el bloque de `PRUEBA;INICIO` a `PRUEBA;FIN`. Después:

| Acción física | Mirar en Serial/LCD |
|---|---|
| Tapar y destapar LDR | Cambia `LUZ_PCT` o el crudo ADC; porcentajes requieren calibración real |
| Mover la mano frente al PIR | Cambia `PIR` después de estabilizarse |
| DHT11 conectado | Temperatura y humedad de aire razonables, sin INVALIDO |
| Sensor de suelo seco/húmedo | ADC cambia; `MUESTRA_SECO` y `MUESTRA_HUMEDO` en diagnóstico |
| Nivel vacío/con agua | ADC cambia; registrar `MUESTRA_NIVEL` |
| Pulsar MODO | Cambia vista, no modo de control |
| Pulsar STOP | PARO, todas las salidas OFF; `LUZ1_ON` debe recibir NACK |
| Liberar STOP y `REARMAR` | ACK; ninguna salida se vuelve a encender sola |

Para HIL automatizado sin motor, el test existente `firmware/tests/test_hil_producto.py` exige `pyserial`, un puerto inequívoco y el perfil 3 ya cargado. **Nunca ordena `RIEGO_ON`**; sí prueba los tres LED y PARO/rearme. Un SKIP por falta de placa o dependencia no es PASS.

## Etapa D — bomba con el único S8050, al final

Con todo apagado, conecta bomba sumergida al circuito del [diagrama](DIAGRAMAS_CADA_FIRMWARE.md) y comprueba que **no arranca sola**. El circuito del banco usa `GPIO4 → 1 kΩ → B`, `B → 10 kΩ → GND`, `E → GND común`, `C → negativo de bomba`, `TP4056 OUT+ → positivo de bomba`, diodo en paralelo con raya hacia OUT+. No uses el S8550 como sustituto.

Mantén el monitor abierto y el apagado preparado. Comprueba `ESTADO`, `DIAGNOSTICO`, nivel válido y STOP liberado. Envía `RIEGO_ON`, observa un pulso **muy breve** y envía inmediatamente `RIEGO_OFF`; verifica que la bomba se detiene y `Bomba=0` en `ESTADO`. Si no arranca, lee el `NACK` (por ejemplo nivel bajo) en lugar de puentear protecciones. Después envía `PARO` y comprueba que `RIEGO_ON` se rechaza; libera/rearma con `REARMAR` y confirma que sigue apagada. La tecla IR `5` manda `IR_RIEGO_ON`: pruébala solo con bomba sumergida y la orden `RIEGO_OFF` lista. Deja `RIEGO_AUTO` para otra sesión, tras calibración real y nivel comprobado.

Al terminar: `RIEGO_OFF`, `VENT_OFF`, `LUZ1_OFF`, `LUZ2_OFF`, `INVER_OFF`, `ESTADO`; desconecta la alimentación de la bomba. Anota códigos, puerto, lectura de sensores, dirección LCD y cualquier NACK/reinicio. Los PASS de software no sustituyen estas observaciones físicas.
