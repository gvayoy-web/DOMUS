# DOMUS: base modular funcional para banco

Controlador recomendado para probar el hardware confirmado sin voz, red, SD,
bateria ni solar. Integra sensores, LCD, DHT, automatizaciones, calibracion
persistente, propiedad manual, PARO, watchdog y modo seguro. Aun requiere
validacion fisica supervisada y no sustituye al firmware principal hasta pasar
la matriz de pruebas de la nota 33. No se ha grabado ninguna placa.

La ronda inicial B01-B05 no necesita conectar
bomba, motor o luces. El perfil compilado se identifica como
`ESP32-S3-N16R8 / BANCO_SIN_ACTUADORES`; `HABILITAR_RELE_BOMBA=false` debe
permanecer asi durante toda esa ronda.

## Dependencias Arduino

Instalar desde **Programa > Incluir libreria > Administrar bibliotecas**:

- `DHT sensor library` de Adafruit, version 1.4.7 o compatible.
- `Adafruit Unified Sensor`, dependencia del DHT.
- `LiquidCrystal I2C` 1.1.2 o compatible.

Si aparece `DHT.h: No such file or directory`, falta instalar esas dos
bibliotecas en el mismo sketchbook utilizado por Arduino IDE; reiniciar el IDE
despues de instalarlas. No se sustituyen lecturas ambientales con valores falsos.

## Inicio seguro

Mantener motores, rele y otras cargas desconectados. Por defecto las salidas
estan deshabilitadas y sus pines en entrada. Alta impedancia no asegura que un
rele conectado este apagado: el driver necesita polarizacion externa adecuada.
No conectar 5 V a GPIO. Usar la alimentacion y etapas verificadas de la nota 21.

Abrir `domus_esqueleto.ino` con placa ESP32-S3. Monitor serie: 115200 baudios.
El informe muestra ADC crudo y, despues de calibrar, porcentajes. MIC es lectura del
interruptor (0 bloqueado, 1 habilitado), no reconocimiento de voz.

| Funcion | GPIO | Etapa |
|---|---:|---|
| Bomba | 4 | GPIO4 -> 1 kOhm -> base S8050; transistor controla rele desnudo de 5 V |
| Sala/cuarto/ventilador/invernadero | 5/6/7/8 | Sin etapa fisica; bloqueados por software |
| Suelo/nivel/luz | 1/2/3 | Senales analogicas <=3.3 V |
| PIR | 9 | Senal compatible <=3.3 V |
| PARO / MIC OFF / boton sala | 10/11/12 | Contacto a GND, pull-up interno |

Configuracion en `domus_config.h`. Solo despues de verificar el driver se cambia
exactamente `constexpr bool HABILITAR_RELE_BOMBA = false;` a `true`. Esto habilita
GPIO4 y no habilita GPIO5-8. Para regresar al banco seguro, volverlo a `false` y
cargar otra vez el sketch.

El rele azul de cinco patas no es un modulo. No tiene entrada logica y su bobina
no puede conectarse directamente a GPIO4. Usar un S8050, resistencia de 1 kOhm
en base y 1N4007 en antiparalelo con la bobina. Confirmar E/B/C del transistor y
bobina/COM/NO/NC del rele por referencia o multimetro; no deducir por posicion.
La bomba exige ademas una calibracion valida guardada en NVS. Se asume que nivel
mayor significa mas agua; verificarlo antes de guardar el umbral.
Los limites ADC detectan rieles, **no garantizan detectar un cable abierto**.

## Ordenes manuales de prueba

Enviar una orden exacta en mayusculas por linea (LF o CRLF):

```text
SALA ON
SALA OFF
CUARTO ON
INVERNADERO OFF
VENTILADOR ON
BOMBA OFF
ESTADO
DIAGNOSTICO
PARO
REARMAR
RECUPERAR
```

Todas las cinco salidas admiten ON/OFF. Los comandos antiguos de una letra
estan retirados por riesgo de activacion accidental al pegar texto.
`!` enclava PARO sin esperar fin de linea e invalida el resto de esa linea.
`REARMAR` solo funciona con PARO fisico liberado y deja todas las salidas OFF.
`RECUPERAR` libera el modo seguro solo con watchdog y memoria suficientes.
Entradas con mas de 47 caracteres o bytes de control se descartan completas.
Se procesan hasta 16 bytes por ciclo, con protecciones entre bytes.
ON tiene limite de una solicitud cada 250 ms; OFF y PARO no comparten ese limite.
El boton fisico mantiene su antirrebote y no depende del puerto serie.

Se responde ACK/NACK. `ESTADO` informa salidas logicas, bloqueo y mensajes TX
omitidos; no confirma electricamente que un rele haya conmutado. Si no cabe
la respuesta, se omite sin esperar y se cuenta: ausencia de ACK no prueba que
una orden no se ejecuto. No reintentar ON a ciegas; consultar ESTADO.

Cada linea `SENSORES` incluye indicadores de validez: `VS` suelo, `VN` nivel,
`VL` luz y `VA` ambiente. `1` significa lectura aceptada por el filtro basico;
no significa que el sensor ya este calibrado. `DIAGNOSTICO` imprime además el
perfil de placa y los GPIO usados en la ronda.

Cada salida admite `NOMBRE AUTO`. Una orden manual toma propiedad y la
automatizacion no la contradice hasta recibir AUTO, que primero apaga la salida.
La bomba se apaga por nivel insuficiente/invalido o a los 10 segundos; repetir
ON mientras funciona no reinicia ese tiempo. Al cortar por fallo de nivel o
timeout queda bloqueada hasta REARMAR. Rearmar no elimina la comprobacion de
nivel ni arranca el riego. No hay reinicio automatico del riego.

## Calibracion segura

Con las salidas apagadas, enviar `PARO` y registrar lecturas crudas en seco,
humedo, oscuridad, claridad y deposito en el minimo seguro. Luego:

```text
CAL SECO=2800
CAL HUMEDO=1200
CAL OSCURO=300
CAL CLARO=3000
CAL NIVEL=600
CAL VER
CAL GUARDAR
REARMAR
```

Los numeros son ejemplos de sintaxis, no valores para copiar. Los extremos de
suelo y luz deben separarse al menos 100 cuentas ADC. La configuracion se guarda
con version y checksum; una configuracion corrupta deja la automatizacion bloqueada.

## Lo incluido y lo que falta

Incluye LCD en 0x27/0x3F, DHT11 o DHT22 seleccionable, ADC/PIR, boton con
antirrebote, cinco salidas, automatizaciones con histeresis, calibracion NVS,
paro, timeout de bomba, watchdog, vigilancia de heap y diagnostico.

No incluye DFPlayer, reconocimiento de voz, microSD, Wi-Fi, bateria ni solar.
Una lectura impresa o compilacion no valida un sensor ni una etapa de potencia.

## Verificacion

Compilar sin conectar placa:

```powershell
.local-tools/arduino-cli/bin/arduino-cli.exe compile --config-file .arduino-local/arduino-cli.yaml --fqbn esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB,CPUFreq=240,LoopCore=1 --build-path build/esqueleto_madurez_compile --output-dir build/esqueleto_madurez firmware/domus_esqueleto
```

Antes de cargas: comprobar niveles de salida, arranque/reset, PARO y rearme.
Con montaje validado: probar bloqueo por nivel, timeout de 10 s y ON repetido.
Probar boton con rebotes y desconexion de USB. Estas pruebas fisicas siguen
pendientes; compilar no demuestra proteccion electrica ni estabilidad real.

`protocol_tests.cpp` contiene 12 regresiones constexpr: se evalua el parser
real y falla la compilacion si no se cumple el contrato. No requieren compilador
host ni consumen tiempo de placa. No prueban GPIO, tiempos reales o potencia.
`domus_config.h` verifica duplicados de pines, umbral y limite de bomba.
