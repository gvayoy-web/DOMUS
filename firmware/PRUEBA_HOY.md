# DOMUS — prueba del banco de hoy

## Qué cargar

Carga `firmware/casa_inteligente_v4/casa_inteligente_v4.ino` sin cambiar
banderas. Su valor predeterminado es el perfil 3
`BANCO_COMPLETO_S8050_IR`: éste es el esqueleto funcional actual y comparte el
mismo código que el producto. La carpeta `domus_esqueleto` queda como banco
histórico de regresión; no se usa para probar las funciones nuevas.

## Antes de energizar

- Bomba sumergida y conectada únicamente mediante S8050, resistencia de base,
  pull-down y diodo según el diagrama vigente.
- Ventilador desconectado de GPIO7.
- Bocinas desconectadas.
- GND del TP4056 y GND del ESP32 unidos.
- STOP, MODO y SILENCIO conectados a GND al pulsar.

## Cargar el firmware

```powershell
arduino-cli board list
arduino-cli compile --fqbn "esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB,CPUFreq=240,LoopCore=1" --build-property "compiler.cpp.extra_flags=-DDOMUS_PERFIL_CASA=3" firmware/casa_inteligente_v4
arduino-cli upload -p COM3 --fqbn "esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB,CPUFreq=240,LoopCore=1" firmware/casa_inteligente_v4
```

Sustituye `COM3` por el puerto real. El comando de carga modifica la placa; no
lo ejecutes sobre un puerto que no hayas identificado.

## Prueba automática sin motores

```powershell
python -m pip install -r firmware/tests/requirements-hil.txt
$env:DOMUS_PORT = "COM3"
python -m unittest firmware.tests.test_hil_producto -v
```

Resultado esperado: 8 pruebas PASS. Esta prueba cubre identidad del perfil,
diagnóstico, estado/sensores, bloque `PRUEBA`, rechazo de comandos inválidos,
tres LED, listado de 21 teclas IR y PARO/rearme. Nunca manda `RIEGO_ON` ni
`VENT_ON`.

## Prueba manual que debes copiar

Abre el monitor serie a 115200 y envía:

```text
PRUEBA
```

Copia todo desde `PRUEBA;INICIO` hasta `PRUEBA;FIN`. Después prueba físicamente
LDR, PIR, DHT11, suelo, nivel, botones, las cinco vistas LCD y cada tecla IR.
La bomba se prueba al final, sumergida: `RIEGO_ON`, luego `RIEGO_OFF` y `PARO`.

Las mediciones eléctricas permanecen `SKIP` por decisión del dueño. Tampoco se
pueden cerrar por software el DRV8833, el ventilador o el audio hasta que llegue
el hardware correspondiente.
