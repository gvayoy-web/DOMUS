# DOMUS — firmware único y perfil de banco

`casa_inteligente_v4.ino` es la única base funcional. El perfil predeterminado
actual es `DOMUS_PERFIL_CASA=3` (`BANCO_COMPLETO_S8050_IR`): conserva sensores,
LCD, automatización, control manual, PARO e infrarrojo, pero adapta las salidas
al hardware disponible.

## Hardware habilitado en el perfil 3

- Bomba: GPIO4 → 1 kΩ → base del único S8050; activa en HIGH.
- Sala, cuarto y cultivo: LED con resistencia en GPIO5, GPIO6 y GPIO8.
- Ventilador GPIO7: bloqueado y configurado como entrada.
- IR HX1838: señal en GPIO12; VCC a 3V3 y GND común.
- Audio, micrófono, microSD y driver doble: deshabilitados.
- Sensores: LDR GPIO3, PIR GPIO9, DHT11 GPIO14, suelo GPIO15 y nivel GPIO16.
- LCD: SDA GPIO17, SCL GPIO13, VCC 3V3 y GND.
- Botones a GND con pull-up interno: PARO GPIO10, SILENCIO GPIO11 y MODO GPIO18.

La bomba usa TP4056 `OUT+` para el positivo y su negativo va al colector del
S8050. `OUT-` se une con GND del ESP32. El emisor va a GND, la base lleva
resistencia de 1 kΩ desde GPIO4 y pull-down de 10 kΩ a GND. El 1N4007 va en
paralelo con la bomba, con la raya hacia `OUT+`.

## Aprender el mando IR

Monitor Serial a 115200. Para cada índice de 0 a 20:

```text
IR_GRABAR_0
```

Pulsa la tecla física indicada y continúa hasta `IR_GRABAR_20`. Consulta el
mapa con `IR_LISTA`, el último código con `IR_LEER` y restaura el mapa inicial
con `IR_BORRAR`.

Acciones principales: 1/Anterior sala, 2/Siguiente cuarto, 3 cultivo, 4
ventilador (responde bloqueado), 5 riego, 0 todo apagado, 200+ rearme, CH/CH-
cambian la pantalla y EQ muestra diagnóstico.

## Primera prueba completa

La bomba arranca apagada y bloqueada en `MANUAL_OFF`; ninguna lectura
provisional la enciende al conectar la alimentación. Abre Serial a 115200,
espera unos segundos y envía `PRUEBA`. Copia desde `PRUEBA;INICIO` hasta
`PRUEBA;FIN`.

### Ejecutor automático seguro (Windows)

El HIL vigente prueba este firmware, no el esqueleto legado. No flashea y no
enciende bomba ni ventilador; sólo consulta el banco, conmuta los tres LED y
comprueba PARO/rearme. Desde la raíz del repositorio:

```powershell
python -m pip install -r firmware/tests/requirements-hil.txt
arduino-cli board list
$env:DOMUS_PORT = "COM3" # sustituir por el puerto que muestre tu ESP32
python -m unittest firmware.tests.test_hil_producto -v
```

Si aparece más de un puerto, desconecta la placa, ejecuta `arduino-cli board
list`, vuelve a conectarla y repite: el puerto nuevo es el que debes escribir.
Un `SKIP` significa que falta puerto, placa, dependencia o perfil 3 cargado; no
significa PASS. Al terminar, el ejecutor ordena apagar las cinco salidas.

Para probar la bomba manualmente, colócala primero dentro del agua y envía
`RIEGO_ON`; apágala con `RIEGO_OFF`. Para permitir que humedad y nivel gobiernen
el riego envía `RIEGO_AUTO`. El LCD escanea todo el rango I2C `0x08–0x77` y
reporta la dirección detectada.

## Bocinas disponibles

No conectar bocinas de 1–2 ohmios directamente a ningún GPIO, 3V3 ni al S8050
de la bomba. El audio permanece deshabilitado hasta disponer de un amplificador
compatible y confirmar la impedancia admitida por este.
