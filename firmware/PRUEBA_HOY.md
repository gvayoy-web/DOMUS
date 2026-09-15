# DOMUS — prueba del banco de hoy

## Qué cargar

Carga `firmware/domus_esqueleto/domus_esqueleto.ino`: este archivo define el
perfil 3 `BANCO_COMPLETO_S8050_IR` e incluye literalmente
`firmware/casa_inteligente_v4/casa_inteligente_v4.ino`. El esqueleto anterior
de regresión está en `firmware/legacy/domus_esqueleto`.

Para aprender las 21 teclas y probar sensores y bomba por etapas, sigue la
[sesión real IR + S8050](../docs/SESION_REAL_IR_S8050.md).

Para averiguar los códigos exactos del mando y obtener números crudos de
calibración sin posibilidad de accionar salidas, carga temporalmente
`firmware/diagnosticos/domus_banco_integracion`. Escribe `HELP`: `IR_LISTA`
muestra protocolo/dirección/comando, y `MUESTRA_SECO`, `MUESTRA_HUMEDO`,
`MUESTRA_OSCURO`, `MUESTRA_CLARO`, `MUESTRA_NIVEL` generan líneas `CAL_*` para
copiar luego al firmware principal. Este diagnóstico nunca configura GPIO4-8.

## Antes de energizar

- Bomba sumergida y conectada únicamente mediante S8050, resistencia de base,
  pull-down y diodo según el diagrama vigente.
- Ventilador desconectado de GPIO7.
- Bocinas desconectadas.
- GND del TP4056 y GND del ESP32 unidos.
- STOP, MODO y SILENCIO conectados a GND al pulsar.

## Compras que NO participan hoy

Nada de esta lista ha llegado y, por tanto, nada se conecta ni se declara
probado en esta sesión:

- fuente externa de 5 V / 2 A;
- módulo controlador DRV8833;
- amplificador estéreo MAX98306;
- parlante de 4 ohmios / 3 W;
- baquelita perforada de 100 × 220 mm;
- portafusible con cable de 5 × 20 mm;
- fusibles cerámicos de 250 V, 4 A, formato anunciado 5 × 20 mm;
- cinco capacitores electrolíticos de 100 µF / 25 V.

La prueba de hoy usa únicamente el ESP32 y los componentes que ya estaban en
mano: sensores, LCD, botones, LED, receptor IR y, sólo en la prueba manual
final, un S8050 con TP4056 y la minibomba. El ventilador y todas las funciones
de audio permanecen desconectados.

El portafusible y los fusibles son del mismo formato 5 × 20 mm; la medida
anterior de 6 × 20 mm fue una anotación equivocada del dueño.

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
pueden cerrar por software el DRV8833, la fuente externa, el ventilador o el
audio hasta que llegue el hardware correspondiente.
