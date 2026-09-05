---
estado: auditoria_completada_con_bloqueos
fecha: 2026-09-04
commit_base: 28227f41495e61bb166ae9f50b688eec983b78d7
---

# Super reporte de auditoría y pruebas multientorno

> Auditoría histórica del commit base. Las correcciones posteriores y sus
> resultados están en [[22 - Resultados de correcciones y regresion]].
> La alternativa económica está en [[21 - Simplificacion y reduccion de costos]].

## Veredicto ejecutivo

**REQUEST CHANGES / NO CONSTRUIR NI CARGAR COMO VERSIÓN FINAL.**

El gemelo digital, los contratos documentales, la geometría y la visualización
se comportan bien en los entornos probados. Sin embargo, el firmware principal
vigente **no compila** para la ESP32-S3. La misma falla fue reproducida en
Windows y en Ubuntu/GitHub Actions. Además, la detección de fallos de varios
sensores analógicos acepta como válidos prácticamente todos los valores posibles
del ADC, por lo que no garantiza detectar cable abierto o corto.

El proyecto puede continuar como diseño y simulación, pero el estado actual no
debe llamarse “firmware compilado”, “binario final” ni “listo para construir”.

## 1. Punto de respaldo antes de probar

- Repositorio: `https://github.com/gvayoy-web/domusv1.git`.
- Rama remota: `main`.
- Commit: `28227f41495e61bb166ae9f50b688eec983b78d7`.
- Mensaje: `Completar firmware, planes, planos y visualizaciones DOMUS`.
- El commit fue enviado correctamente antes de iniciar esta auditoría.
- Ejecución CI auditada:
  `https://github.com/gvayoy-web/domusv1/actions/runs/33896869731`.

## 2. Matriz real de pruebas ejecutadas

| Área | Entorno | Cantidad/alcance | Resultado |
|---|---|---:|---|
| Reglas domésticas | Windows, Python 3.12.14, `unittest` | 20 casos | PASS |
| Contratos de firmware | Windows, Python 3.12.14, `unittest` | 18 casos | PASS |
| Validador integral | Windows, Python 3.12.14 | planes 00–19, Wikilinks, pines y visualización | PASS |
| Geometría/paquete | Windows, Python 3.12.14 | 4 casos | PASS |
| Sintaxis Python | Windows, `compileall` | scripts, simulador y generadores | PASS |
| Estrés del gemelo | Windows, semilla fija | 100 000 operaciones | PASS |
| CI lógico | Ubuntu `latest`, Python 3.12 | simulador + contratos | PASS |
| Firmware producción | Windows, Arduino CLI 1.5.1, ESP32 core 3.3.10, N16R8 | 16 MB/OPI/240 MHz | **FAIL** |
| Firmware reducido | Windows, mismo compilador | 4 MB/sin PSRAM/160 MHz | **FAIL** |
| Firmware alterno | Windows, mismo compilador | 8 MB/QSPI/80 MHz | **FAIL** |
| Firmware CI | Ubuntu, Arduino CLI 1.x, ESP32 core 3.3.10 | N16R8 producción | **FAIL** |
| Visualizador | Chromium | escritorio/tableta/móvil | PASS |
| Visualizador | Firefox | escritorio/tableta/móvil | PASS con aviso menor de favicon/CSP |
| Visualizador | WebKit | escritorio/tableta/móvil | PASS |
| PicoTTS/MAX98357A | ESP-IDF | entorno `idf.py` no instalado | NO EJECUTADO |
| INMP441 | ESP-IDF | entorno `idf.py` no instalado | NO EJECUTADO |
| Cableado físico | placa, fuente, cargas y multímetro | hardware no conectado | NO EJECUTADO |

Total automatizado que sí terminó: **42 pruebas unitarias**, una campaña de
**100 000 operaciones aleatorias** y **9 combinaciones de navegador/tamaño**.
Las cuatro compilaciones reales de firmware fallaron.

## 3. Hallazgos priorizados

| Prioridad | Hallazgo | Ubicación principal |
|---|---|---|
| P1 | El firmware no compila; no existe binario vigente utilizable | `casa_inteligente_v4.ino:741`, `:766` |
| P1 | Los rangos ADC no detectan varios cortos/cables abiertos | `casa_inteligente_v4.ino:192-207`, `:882-940` |
| P1 | Un comando sobredimensionado puede hacer que su sufijo se procese como una orden nueva | `casa_inteligente_v4.ino:1326-1342` |
| P1 | Documentación afirma una compilación vigente que hoy es falsa | `COMPILACION_VALIDADA.md:32,45`; `ENTREGA_FINAL.md:23`; `PLAN_PROYECTO.md:18-20,65` |
| P1 | Jarvis, MAX98357A, WS2812 y microSD no forman un sistema final integrado | banderas y planes de firmware/audio |
| P2 | El registro de GPIO omite 40/41/42 del MAX98357A y no asigna WS2812 | `casa_inteligente_v4.ino:269-277`; manual 18 |
| P2 | GPIO3 es pin de strapping y está unido al divisor LDR sin prueba de arranque | mapa de pines y manual 18 |
| P2 | GPIO19 propuesto para DFPlayer también es USB D− en ESP32-S3 | firmware `:169-171`; manual 18 |
| P2 | BOM vigente contradice firmware/inventario sobre el sensor de suelo | `bom_componentes.csv:6` |
| P2 | El validador “PASS” busca textos, pero no compila el firmware | `test_firmware_contract.py`; `validate_project.py` |
| P2 | `pytest` no está declarado/disponible en el entorno entregado | entorno Python del proyecto |
| P2 | LiquidCrystal I2C 1.1.2 declara solo arquitectura AVR | salida del compilador |
| P3 | Firefox registra un aviso CSP al intentar cargar `favicon.ico` | visualizador público |

## 4. Detalle de fallas críticas

### P1 — El archivo `.ino` no compila

Los cuatro compiladores producen el mismo error:

```text
linea 741: 'OrdenActuador' does not name a type
linea 741: 'ResultadoOrden' does not name a type
linea 766: 'ResultadoOrden' does not name a type
```

Las estructuras existen en las líneas 340–352. El problema es el preprocesado
automático de prototipos de Arduino: genera declaraciones de funciones antes de
que esos tipos sean visibles.

Corrección recomendada:

1. Mover `OrigenOrden`, `OrdenActuador` y `ResultadoOrden` a un encabezado
   `domus_types.h` incluido al principio del sketch.
2. Declarar explícitamente, después de incluir el encabezado, los prototipos de
   `construirRespuestaJarvis()` y `ejecutarOrdenActuador()`.
3. Compilar con la configuración N16R8 de producción y con `--warnings all`.
4. No actualizar cifras de tamaño ni SHA hasta generar un binario nuevo.

### P1 — La protección de sensores analógicos da falsa seguridad

`NIVEL_AGUA_MIN_VALIDO=0`, `NIVEL_AGUA_MAX_VALIDO=4095`, `LDR_MIN_VALIDO=0` y
`LDR_MAX_VALIDO=4095` cubren todo el rango de un ADC de 12 bits. Por tanto, esas
comparaciones no pueden declarar inválido ningún valor normal del ADC. Para el
suelo, `4095` también se acepta aunque el comentario dice que el extremo puede
representar sensor desconectado.

Consecuencia más grave: un nivel de agua flotante o abierto que produzca un
valor superior a 600 puede autorizar la bomba.

Corrección recomendada:

- Medir mínimo, máximo, abierto y corto en el módulo real.
- Definir ventanas válidas con margen, no `0..4095`.
- Añadir resistencia física de polarización para que un cable abierto caiga en
  un estado conocido y seguro.
- Exigir varias muestras válidas consecutivas antes de habilitar la bomba.
- Añadir timeout de dato fresco; no reutilizar indefinidamente una lectura vieja.
- Crear pruebas de límites `0`, `1`, `4094`, `4095`, abierto, corto y ruido.

### P1 — Recuperación incorrecta después de desbordar Serial

Cuando el búfer llega a 40 caracteres, el firmware lo vacía, pero continúa
leyendo el resto de la misma línea. Un texto largo cuyo sufijo sea `RIEGO_ON`,
por ejemplo, puede convertir ese sufijo en una orden independiente al llegar el
salto de línea.

Corrección recomendada: añadir un estado `descartarHastaNuevaLinea`. Después de
un desbordamiento, ignorar todos los caracteres hasta `\n`; solo entonces
aceptar una nueva orden.

### P1 — Estado documental incompatible con la evidencia

La documentación registra tamaños y SHA de un binario anterior y afirma que el
archivo vigente fue recompilado correctamente. La ejecución de GitHub Actions
del commit auditado demuestra lo contrario y omite el paso de artefactos porque
la compilación falla.

Hasta corregir y recompilar, estas afirmaciones deben cambiar a `FAIL / BLOQUEADO`.

### P1 — Funciones anunciadas pero no integradas

- `JARVIS_LOCAL_HABILITADO=false`.
- `MICROSD_HABILITADA=false`.
- MAX98357A solo tiene un PoC separado; el firmware principal no define ni usa
  GPIO40/41/42.
- WS2812 no tiene GPIO asignado ni controlador en el firmware principal.
- Los modelos TinyML españoles, dataset y validación acústica no existen aún.

Esto es una degradación honesta y segura, pero significa que el código completo
de todas las funciones todavía no está terminado.

## 5. Auditoría de módulos y cableado

### Núcleo coherente en papel

- GPIO1: humedad de suelo.
- GPIO2: nivel de agua.
- GPIO3: LDR.
- GPIO4–8: cinco relés/cargas.
- GPIO9: PIR.
- GPIO10/11/12: PARO, MIC OFF y DEMO.
- GPIO13/21: SCL/SDA.
- GPIO14: DHT.
- GPIO15/16/17: INMP441 propuesto.
- GPIO18/19: DFPlayer deshabilitado.
- GPIO38/39/47/48: microSD propuesta.

No hay duplicados dentro del registro actual. El manual documenta GND común,
límites de 3.3 V, relés/cargas alimentados desde 5 V, adaptación bidireccional
para el LCD a 5 V, diodos en motores, fusible, interruptor y separación de agua.

### Bloqueos antes de fabricar el mazo

1. Confirmar en la placa exacta que todos esos GPIO están expuestos.
2. GPIO3 es un pin de strapping del ESP32-S3; medir el divisor LDR durante reset
   y ejecutar arranques con oscuridad y luz extrema.
3. No usar GPIO19 para DFPlayer si se necesita USB nativo; Espressif asigna
   GPIO19 a USB D− y GPIO20 a D+.
4. Reservar formalmente 40/41/42 si se mantiene MAX98357A, o elegir otros pines.
5. Asignar WS2812 y añadirlo al `static_assert` antes de cablearlo.
6. Resolver la contradicción “sensor capacitivo” del BOM frente al sensor
   resistivo que describen firmware e inventario.
7. El BOM dice siete pulsadores, pero el firmware principal implementa tres
   controles físicos; definir cuáles son realmente necesarios.
8. Medir corriente simultánea de ESP32, relés, bomba, ventilador, luces y audio.
   Una fuente rotulada 5 V/3 A no queda validada solo por documentación.

Fuentes técnicas primarias consultadas:

- Espressif, datasheet ESP32-S3:
  `https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf`
- Espressif, USB/JTAG de ESP32-S3:
  `https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/jtag-debugging/configure-builtin-jtag.html`

## 6. Resultado del gemelo digital y anti-colapso

La campaña determinista de 100 000 operaciones mezcló sensores nulos y fuera de
rango, comandos manuales y de voz, baja confianza, ráfagas, avance de tiempo,
paro, rearme, entrada y recuperación de modo seguro.

Invariantes mantenidas:

- ninguna salida activa bajo PARO o modo seguro;
- bomba nunca activa sin agua disponible en el modelo;
- bomba nunca supera 120 segundos;
- buffer de eventos limitado a 250;
- comandos abusivos limitados y PARO conservando prioridad.

Limitación: el gemelo usa porcentajes perfectos o `None`; no modela ADC flotante,
ruido eléctrico, rebote de relé, brownout, I2C colgado, pérdida de GND ni la
máquina de caracteres Serial. Por eso sus PASS no cubren las fallas P1 anteriores.

## 7. Resultado del visualizador

URL probada: `https://domus-visualizadores-publicos.vercel.app`.

En Chromium, Firefox y WebKit, a 1440×900, 768×1024 y 390×844:

- `/`, `/3d` y `/circuito` respondieron correctamente;
- la portada cambió de 3D a circuito;
- el modelo mostró 111 piezas y canvas visible;
- funcionaron tema nocturno y vista superior;
- el circuito mostró siete grupos de módulos y detalle INMP441;
- no hubo desbordamiento horizontal en portada, 3D o circuito.

Los `request aborted` observados durante la primera matriz provenían de cerrar o
navegar mientras un iframe terminaba de cargar; una prueba aislada confirmó que
`/3d` y `/circuito` no generan respuestas HTTP fallidas. Queda solo el aviso
menor de favicon/CSP en Firefox.

## 8. Calidad de las pruebas existentes

Aspectos positivos:

- CI separa lógica y compilación.
- Los 20 casos del gemelo cubren histéresis, propiedad manual, paro, timeout,
  sensores ausentes, microSD simulada, voz y límite de comandos.
- El compilador real sí detectó el fallo que los contratos de texto no detectan.

Mejoras necesarias:

1. Hacer que `scripts/validate_project.py` invoque también una compilación real
   o separar claramente `VALIDACION_LOGICA_OK` de `FIRMWARE_COMPILADO_OK`.
2. Dejar de usar `assertIn()` como prueba principal de seguridad: comprueba que
   existe una palabra, no que la ruta funcione.
3. Añadir pruebas del parser Serial, especialmente desbordamiento y sufijos.
4. Añadir pruebas de ADC en los extremos y de dato obsoleto.
5. Compilar los dos PoC ESP-IDF en CI; hoy no tienen job.
6. Fijar el entorno Python o declarar que solo se usa `unittest`; `pytest` no
   está instalado aunque es una forma habitual de ejecutar todo el árbol.
7. Agregar matriz web automatizada al CI para evitar regresiones del deploy.

## 9. Orden de corrección recomendado

1. Corregir los tipos/prototipos y lograr compilación N16R8 limpia.
2. Añadir el binario como artefacto CI y registrar un SHA nuevo.
3. Corregir ventanas ADC y el descarte de línea Serial.
4. Ampliar pruebas para que esas fallas no regresen.
5. Actualizar todas las afirmaciones de “compilación validada”.
6. Resolver BOM, pines provisionales y GPIO3/19/40–42/WS2812.
7. Compilar los PoC ESP-IDF.
8. Hacer pruebas de banco sin cargas y luego con una carga por vez.
9. Medir corriente, caída de tensión, ruido y temperatura.
10. Integrar audio, microSD y WS2812 por fases; nunca todos a la vez.

## 10. Criterio para cambiar este reporte a PASS

No marcar `APTO PARA CONSTRUCCIÓN` hasta cumplir simultáneamente:

- CI verde en lógica y compilación;
- firmware N16R8 generado desde el commit vigente;
- ventanas ADC obtenidas con medición real;
- pinout y pines de strapping/USB confirmados;
- cinco arranques sin pulsos de relé;
- PARO físico probado con cada carga;
- bomba cortada por nivel y por timeout;
- fuente estable bajo carga simultánea;
- PoC de cada módulo opcional compilado y probado aisladamente;
- documentación actualizada con mediciones y SHA reales.

## Relaciones

- [[13 - Plan de cierre de codigo]]
- [[14 - Protocolo anti-colapso IA y ESP32]]
- [[16 - Plan de testeo antes de construccion]]
- [[18 - Manual maestro de conexiones pin por pin]]
- [[19 - Plan de testeo despues de construccion]]
