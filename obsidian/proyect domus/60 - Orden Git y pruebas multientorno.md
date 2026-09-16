---
estado: vigente
fecha: 2026-09-12
autoridad: pruebas_y_repositorio
---

# Orden Git y pruebas multientorno

## Repositorio

- Rama de trabajo: `proyecdomus`.
- Destino publicado: `origin/main`.
- `hardware/planos/` es la ubicación canónica de planos.
- `tools/` es la ubicación canónica de validadores y generadores.
- `docs/` contiene los documentos generales que antes estaban sueltos en raíz.
- `firmware/casa_inteligente_v4/` es el producto.
- `firmware/domus_esqueleto/` es banco heredado.
- `firmware/diagnosticos/domus_banco_integracion/` es una utilidad temporal para
  LCD + IR + DRV8833; no sustituye al producto.

## Evidencia local del 2026-09-12

| Entorno | Resultado | Alcance |
|---|---:|---|
| Validador integral Python | PASS | 20 pruebas núcleo, 83 firmware (9 SKIP), 7 planos |
| Gemelo semirreal | PASS | 10,000 pasos, 40,027 invariantes, fallos y reinicios inyectados |
| Arduino ESP32-S3 N16R8, perfiles CASA 0/1/2 | PASS | 422,310 B programa; 26,172 B RAM global |
| Arduino ESP32-S3 N16R8, perfil CASA 3 | PASS | 444,901 B programa; 26,388 B RAM global |
| Matriz esqueleto | PASS | 3 perfiles permitidos compilan; 3 configuraciones peligrosas se rechazan |
| Diagnóstico LCD+IR+DRV8833 | PASS de compilación | 369,361 B programa; 25,140 B RAM global |
| HIL físico | NO EJECUTADO | COM3/COM4 aparecen como puertos desconocidos; falta identificar placa, `pyserial` y banco conectado |

Ubuntu CI reveló dos desajustes de harness y una dependencia de planos no
declarada. Se sincronizaron `DOMUS_PERFIL_CASA`, `BOMBA_DIRECTA_S8050` y el
conteo del escaneo I2C de 112 direcciones; además se añadió el requirements
canónico de Pillow/ReportLab al job remoto. El resultado verde se registra
únicamente cuando termine la ejecución del commit corregido.

Resultado remoto confirmado: **PASS** en GitHub Actions, ejecución
`34734848082`, con pruebas nativas Ubuntu y todas las matrices Arduino verdes.
Las notas de Obsidian dejan de disparar compilaciones por sí solas; los cambios
de firmware, tests, herramientas, README y del propio workflow sí las disparan.

La segunda pasada remota confirmó los tests nativos, pero descubrió que los
jobs Arduino instalaban LCD y DHT sin declarar `IRremote`, aunque el producto
ya incluye `domus_ir_casa.h`. CI instala ahora `IRremote@4.7.1` en todas las
familias de compilación.

El sketch auxiliar histórico `domus_anim` requería además GFX, SSD1306 y
ST7789. Esas dependencias quedaron fijadas únicamente en su familia de CI;
no se añadieron al firmware de producto.

La campaña semirreal no certifica voltajes, corriente, polaridad ni temperatura.
Las mediciones eléctricas se mantienen marcadas como `SKIP por decisión del dueño`;
no deben presentarse como PASS. Tampoco se cargó firmware ni se accionó una bomba
sin supervisión física.

## Avisos que no bloquean

`LiquidCrystal I2C 1.1.2` declara arquitectura AVR en sus metadatos, por eso
Arduino emite un warning. Aun así, todas las compilaciones ESP32 terminaron con
código 0. Debe confirmarse el comportamiento del LCD en el banco real.

El shell normal no tiene `python` en `PATH`; las pruebas se ejecutaron con el
runtime Python empaquetado de Codex. Las pruebas C++ nativas reservadas para
Ubuntu CI se omiten localmente porque no hay compilador host.

## Qué dijeron realmente los tests

### Control y seguridad

Los tests confirmaron en software que:

- todas las salidas arrancan apagadas;
- PARO tiene prioridad y bloquea nuevas órdenes de encendido;
- un rearme no vuelve a encender cargas automáticamente;
- el modo seguro corta las salidas y exige recuperación explícita;
- la bomba rechaza el encendido si el nivel de agua es bajo o inválido;
- el límite de tiempo de la bomba la apaga y deja el riego bloqueado hasta el
  rearme;
- una orden manual conserva la propiedad de la salida y no es anulada
  silenciosamente por el modo automático;
- el control automático de riego, ventilación y luces usa umbrales separados e
  histéresis para evitar encendidos y apagados rápidos;
- los fallos de sensores llevan el sistema a un estado conservador;
- las órdenes por voz deshabilitadas no impiden usar controles físicos;
- el límite de comandos serie no puede retrasar el PARO de emergencia;
- líneas serie demasiado largas se descartan completas.

Esto demuestra comportamiento lógico. No demuestra que un transistor, driver,
motor, bomba o sensor físico soporte la corriente o entregue la señal esperada.

### Sensores y calibración

Los tests confirmaron que:

- lecturas ADC pegadas a los extremos se rechazan como inválidas;
- la conversión calibrada a porcentaje funciona aunque los puntos seco/húmedo
  u oscuro/claro estén invertidos;
- el DHT, suelo, nivel, LDR y PIR tienen rutas de diagnóstico;
- la calibración se valida, se guarda con checksum y no se acepta durante una
  condición insegura;
- el PIR mantiene presencia durante un intervalo y después la libera;
- el escaneo I2C recorre `0x08` a `0x77`, es decir, 112 direcciones;
- si sólo aparece un dispositivo I2C puede adoptarse su dirección; si aparecen
  varios sin `0x27` o `0x3F`, el firmware reporta ambigüedad.

Sigue faltando obtener valores reales de seco, húmedo, vacío, lleno, oscuro y
claro. Sin esos datos, los porcentajes y decisiones automáticas sólo están
validados contra valores simulados.

### GPIO, perfiles y actuadores

La compilación y los contratos confirmaron:

- un mapa central evita que el firmware tenga distintas fuentes de pines;
- el perfil actual de banco usa bomba S8050 en GPIO4, luces en GPIO5/6/8,
  infrarrojo en GPIO12 y mantiene el ventilador GPIO7 bloqueado;
- bomba y ventilador no pueden habilitarse simultáneamente con un único S8050;
- tres perfiles alfa permitidos compilan;
- perfil inexistente, IR+buzzer compartiendo GPIO12 y DFPlayer sobre GPIO17/18
  son rechazados en compilación;
- el backend de motor permanece bloqueado mientras el driver no se declare
  validado;
- los cuatro perfiles CASA compilaron localmente para ESP32-S3 N16R8;
- GitHub compiló además variantes N16R8 normal/económica/SD, 4 MB sin PSRAM y
  8 MB QSPI, junto con esqueleto, selftest y animación.

La compilación del perfil no prueba que la carga esté conectada correctamente.
El firmware diagnóstico DRV8833 sólo quedó compilado; no se ejecutó porque el
módulo todavía no ha llegado.

### LCD e infrarrojo

Los tests confirmaron que:

- el producto depende de LCD1602 I2C, no de OLED;
- el formateador genera exactamente 16 caracteres por fila, limpia sobrantes y
  evita escrituras idénticas repetidas;
- existe prioridad visual para errores y estados de seguridad;
- cambiar de página con MODO no cambia también el modo de control;
- el receptor IR ignora repeticiones y limita el mapa a 21 códigos;
- aprender, listar y borrar códigos tiene contrato de firmware.

Falta ver el LCD real. El warning de arquitectura de `LiquidCrystal I2C` no
impidió compilar, pero sólo una prueba física confirma iluminación, contraste,
dirección, caracteres y ausencia de parpadeo. También faltan los 21 códigos
reales del mando; los tests prueban la lógica del mapa, no conocen todavía las
teclas del control concreto.

### Campaña semirreal

Con semilla `20260906` se ejecutaron:

- 10,000 pasos;
- 40,027 comprobaciones de invariantes;
- 40 emergencias;
- 22 entradas a modo seguro;
- 28 reinicios simulados;
- 134 fallos de sensores.

Resultado: **PASS**. El registro permaneció acotado y ninguna inyección rompió
los enclavamientos modelados. Su alcance es un gemelo digital; no reproduce
ruido eléctrico, falsos contactos, caída de fuente, calentamiento ni diferencias
entre ejemplares físicos.

## Problemas que las pruebas descubrieron y se corrigieron

1. Los harness C++ de Ubuntu no definían `DOMUS_PERFIL_CASA` ni
   `BOMBA_DIRECTA_S8050` después de incorporar el perfil 3. Se sincronizaron con
   el firmware vigente.
2. La prueba nativa I2C esperaba dos consultas históricas (`0x27/0x3F`) aunque
   el firmware ya escaneaba 112 direcciones. Se actualizó al comportamiento real.
3. El entorno CI no instalaba Pillow ni ReportLab para validar los planos. Se
   creó `hardware/planos/requirements.txt` y se instala antes del validador.
4. El firmware ya incluía `IRremote.hpp`, pero los runners limpios no instalaban
   `IRremote`. Se fijó `IRremote@4.7.1`.
5. `domus_anim` dependía de GFX, SSD1306 y ST7789 sin declararlas en CI. Se
   añadieron sólo a la familia del sketch auxiliar.
6. Un test prohibía SSD1306 en todo el workflow, confundiendo el producto LCD
   con la animación histórica. Ahora comprueba únicamente el job del producto.

Tras esas correcciones, GitHub Actions `34735050016` terminó completamente en
verde sobre el commit publicado.

## Lo faltante

### Necesario para afirmar “probado en hardware”

- Identificar cuál de COM3/COM4 es el ESP32-S3.
- Instalar `pyserial` en el entorno que ejecutará HIL.
- Cargar el perfil 3 en la placa correcta y guardar el arranque serie.
- Ejecutar `PRUEBA` y conservar el bloque desde `PRUEBA;INICIO` hasta
  `PRUEBA;FIN`.
- Confirmar dirección real del LCD, contraste, retroiluminación y las cinco
  vistas sin parpadeo.
- Probar DHT, suelo, nivel, LDR y PIR conectados según el diagrama vigente.
- Obtener y guardar los seis puntos de calibración reales.
- Aprender y registrar las 21 teclas del mando IR; comprobar cero acciones
  dobles al mantener una tecla presionada.
- Con la minibomba sumergida y bajo vigilancia, comprobar arranque OFF, nivel
  bajo, pulso/encendido autorizado, timeout, PARO y rearme.
- Cuando llegue el DRV8833, verificar visualmente sus etiquetas y probar bomba y
  ventilador por separado antes de permitir automatización conjunta.
- Ejecutar una sesión HIL prolongada vigilada para detectar reinicios, falsos
  accionamientos y pérdida de sensores.

### Marcado como SKIP por decisión del dueño

- medición de corriente de arranque y régimen de bomba/ventilador;
- caída de tensión de la fuente bajo carga;
- temperatura del S8050 y del driver;
- validación eléctrica de alimentación y polaridad.

Estos puntos están omitidos, no aprobados. El software puede considerarse
probado en simulación, compilación y CI; el montaje no debe describirse todavía
como validado eléctricamente.

### No bloqueante por ahora

- audio y voces, aplazados por decisión del dueño;
- aviso de metadatos AVR de `LiquidCrystal I2C`;
- actualización futura de acciones GitHub que todavía anuncian deprecación de
  Node.js 20 aunque el runner las ejecute con Node.js 24;
- validación del DRV8833, imposible hasta recibir el módulo.

## Dictamen

Estado del código: **PASS multientorno**.

Estado de compilación ESP32: **PASS multiconfiguración**.

Estado de simulación de seguridad: **PASS**.

Estado de hardware físico: **PENDIENTE / NO EJECUTADO**.

Estado de mediciones eléctricas: **SKIP por decisión del dueño**.

No hay un error de software conocido que impida comenzar el banco. Lo que falta
es evidencia física: conectar, cargar, registrar `PRUEBA`, calibrar y ejecutar
HIL con supervisión.

## Addendum 2026-09-13 — banco listo para probar hoy

- El HIL histórico `test_hil_esqueleto.py`, atado a COM9 y al protocolo viejo,
  fue sustituido por `firmware/tests/test_hil_producto.py`.
- El ejecutor vigente identifica el perfil 3 `BANCO_COMPLETO_S8050_IR`, puede
  descubrir un único puerto USB compatible y exige `DOMUS_PORT` si hay duda.
- Sus 8 pruebas nunca encienden bomba ni ventilador. Comprueban diagnóstico,
  sensores, bloque `PRUEBA`, comandos inválidos, tres LED, 21 entradas IR y
  PARO/rearme, dejando todo apagado al salir.
- `firmware/tests/requirements-hil.txt` declara `pyserial`; ya no es una
  dependencia implícita.
- `firmware/PRUEBA_HOY.md` contiene los comandos exactos de compilación, carga
  y ejecución para Windows.

El esqueleto funcional de hoy es el perfil 3 del firmware de producto. El
directorio `firmware/domus_esqueleto` lo incluye literalmente; la implementación
anterior vive en `firmware/legacy/domus_esqueleto` solamente para regresión.
Así se conserva un solo cerebro y se evita probar por error el mapa antiguo.

Todo lo cerrable sin hardware queda cerrado. Lo restante requiere observación
física: puerto real, salida del LCD/sensores/botones/IR y bomba sumergida. El
DRV8833, ventilador y audio esperan sus módulos. Las mediciones eléctricas
siguen en `SKIP` por decisión del dueño, no en PASS.

### Corrección de alcance del banco de hoy

La prueba física inmediata no utiliza ningún artículo de la compra pendiente.
La lista real aún no recibida es: fuente 5 V/2 A, DRV8833, MAX98306 estéreo,
parlante 4 Ω/3 W, baquelita perforada 100 × 220 mm, portafusible
5 × 20 mm, fusibles cerámicos 250 V/4 A de 5 × 20 mm y cinco
capacitores electrolíticos 100 µF/25 V.

Hasta su llegada, fuente externa, driver, fusible, capacitores, parlante y
amplificador quedan físicamente fuera del banco y no pueden recibir PASS. Hoy
se prueban sólo ESP32, sensores, LCD, botones, LED, IR y la minibomba mediante
el S8050/TP4056 ya disponibles. El ventilador y el audio quedan desconectados.

Portafusible y fusibles coinciden en formato 5 × 20 mm. La mención anterior de
6 × 20 mm fue corregida por el dueño.

## Addendum — cierre de software no físico

Se retiraron el entrenador, su CI y las PoC del antiguo plan de reconocimiento
por micrófono. También se eliminó el bloque ESP-SR inactivo del producto. El IR
ahora exige aprendizaje persistido y códigos únicos antes de ejecutar acciones.
Ver [[62 - Cierre total de software no fisico]].

## Addendum 2026-09-16 — primera sesión física

La ESP32-S3 fue identificada definitivamente como **COM9**. Se cargó el perfil
3 y la escritura fue verificada por hash. El diagnóstico respondió, el receptor
IR captó al menos `CMD 0x19` y el LCD había sido detectado anteriormente en
`0x27`; en la lectura más reciente estaba desconectado y reportó
`PANTALLA=NINGUNA`.

El DHT11 sigue en NaN, suelo/nivel no tienen calibración estable y un pulso
GPIO4 de 250 ms no hizo girar la bomba. Por tanto, las líneas antiguas de esta
nota que dicen COM3/COM4 o “hardware no ejecutado” son evidencia histórica del
corte anterior. El estado vigente y detallado está en
[[64 - Sesion fisica COM9 LCD IR sensores y bomba]].
