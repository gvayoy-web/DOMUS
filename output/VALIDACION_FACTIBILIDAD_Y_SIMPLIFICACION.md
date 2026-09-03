# PROJECT DOMUS — Validación de factibilidad y simplificación

**Fecha:** 2 de septiembre de 2026  
**Objeto:** auditar las recomendaciones de la conversación proporcionada y contrastarlas con el proyecto, pruebas ejecutables, cálculos conservadores y documentación técnica.

## Veredicto ejecutivo

El proyecto **sí es factible como maqueta funcional**, pero no todas las conclusiones de la conversación son intercambiables ni están probadas al mismo nivel.

- El núcleo de automatización es real: el simulador pasó **18/18 pruebas**, el contrato del firmware pasó **9/9 pruebas** y el programa compiló para el ESP32-S3 N16R8.
- Una fuente regulada de **5 V/3 A** es la opción simple y segura para construir y demostrar la maqueta. Un cargador de 5 V/2 A puede funcionar en estados normales, pero no deja margen suficiente para el pico modelado.
- La batería y el panel solar son factibles como fase posterior, pero no están validados físicamente. Antes de comprarlos hay que medir el consumo real.
- “Jarvis local” todavía es una línea de investigación, no una función terminada: faltan el micrófono y el amplificador físicos, el modelo de voz y pruebas de eco/falsos positivos.
- La conversación acierta en varias simplificaciones, pero se equivoca al presentar ciertos módulos de batería como sustitutos completos entre sí.

## Evidencia reproducible del proyecto

| Verificación | Resultado | Qué demuestra | Qué no demuestra |
|---|---:|---|---|
| Simulador doméstico | 18/18 | Reglas, prioridades y estados del núcleo | Cableado y potencia reales |
| Contrato del firmware | 9/9 | Invariantes de seguridad y configuración | Funcionamiento de sensores físicos |
| Compilación ESP32-S3 N16R8 | Correcta | Código y dependencias compatibles | Estabilidad eléctrica |
| Tamaño del programa | 399,078 B, 12 % | Hay margen de flash | Que Jarvis quepa o funcione |
| Variables globales | 24,948 B, 7 % | Hay margen de RAM base | Memoria requerida por un modelo de voz |

La compilación actual tiene `JARVIS_LOCAL_HABILITADO`, `MICROSD_HABILITADA` y `MP3_HABILITADO` desactivados. Por eso la compilación válida no debe anunciarse como prueba de Jarvis o reproducción de voz.

## Auditoría de las afirmaciones de la conversación

### Correctas o aplicables

1. **Se puede reutilizar un cargador de teléfono**, si entrega 5 V regulados, tiene capacidad real cercana a 3 A y se prueba también el cable. Así se evita comprar una fuente nueva.
2. **Un solo altavoz basta.** El MAX98357A es mono y puede entregar hasta 3.2 W en 4 ohmios a 5 V; comprar cuatro altavoces no aporta al objetivo actual.
3. **DFPlayer y una segunda microSD se pueden omitir.** El diseño actual plantea audio I2S con MAX98357A, no necesita dos reproductores.
4. **Conviene posponer batería y solar hasta medir corriente.** Es la mayor simplificación segura.
5. **CN3065 es apropiado para una fuente solar limitada.** Está diseñado para entradas de 4.4–6 V y ajusta la corriente de carga cuando la fuente no puede mantenerla.
6. **Una celda 21700 de 5,000 mAh puede superar dos horas**, según el consumo medio. No obstante, debe usarse con portacelda o terminales soldados por puntos, protección 1S y un elevador de 5 V suficiente.

### Parciales o incorrectas

1. **“TP4056 reemplaza al BMS” es incompleto.** El TP4056 es un cargador. Sólo una placa que además incluya protección —por ejemplo DW01A y MOSFETs— protege la celda. Tampoco proporciona por sí misma reparto de carga ni salida de 5 V.
2. **El TP4056 no es la mejor interfaz directa para un panel.** Puede llegar a cargar si la tensión permanece estable, pero el CN3065 está diseñado específicamente para fuentes limitadas como paneles solares.
3. **Un módulo integrado con salida máxima de 1 A no sirve para toda la casa.** Puede alimentar una carga ligera, no el pico combinado modelado.
4. **HX-1S es protección, no solución completa.** No carga desde el panel y no eleva la batería a 5 V.
5. **5,000 mAh no equivalen a 7,500 mAh.** Una 21700 puede cumplir la autonomía mínima, pero no conserva la misma energía que tres celdas de 2,500 mAh en paralelo.
6. **Una batería LiFePO4 no usa TP4056/CN3065 configurados a 4.2 V.** Requiere cargador y protección específicos para 3.65 V por celda.
7. **La microSD no es obligatoria ahora.** En el firmware actual está desactivada. Una tarjeta de 2 GB FAT16 es técnicamente utilizable; el riesgo real es su edad, disponibilidad y fiabilidad.
8. **El adaptador de nivel del WS2812 depende de la tira real.** La revisión WS2812B-V5 especifica VIH mínimo de 2.7 V y acepta 3.3 V; una revisión antigua o desconocida puede exigir cerca de 0.7·VDD. Debe probarse la tira concreta.
9. **Un módulo IRF540 no debe comprarse a ciegas para control desde 3.3 V.** El IRF540 no es un MOSFET de nivel lógico; aunque una tienda anuncie entrada de 3.3 V, hay que comprobar caída de tensión y temperatura bajo carga.

## Ensayo de presupuesto de potencia

Estos valores son una **simulación de envolvente**, no mediciones del prototipo:

| Estado modelado a 5 V | Corriente | Potencia |
|---|---:|---:|
| Reposo | 0.22 A | 1.10 W |
| Demostración normal | 0.65 A | 3.25 W |
| Pico combinado | 1.85 A | 9.25 W |
| Pico con margen del 25 % | 2.31 A | 11.56 W |

Resultado:

- **5 V/2 A:** válido para el estado normal, insuficiente como garantía de pico.
- **5 V/3 A:** pasa los tres estados modelados con margen razonable.
- **Elevador de batería de 1 A:** descartado para la casa completa.
- **UPS/elevador anunciado como 3 A:** plausible, pero debe sostener 2 A y el pico transitorio sin caída ni calentamiento excesivo.

### Autonomía calculada

Supuestos conservadores: 85 % de eficiencia del elevador y 20 % de reserva no utilizada.

| Batería | 0.4 A a 5 V | 0.7 A a 5 V | 1.0 A a 5 V |
|---|---:|---:|---:|
| 1×21700, 5,000 mAh, 3.6 V | 6.12 h | 3.50 h | 2.45 h |
| 2×18650, 2,500 mAh en paralelo | 6.29 h | 3.59 h | 2.52 h |
| 3×18650, 2,500 mAh en paralelo | 9.44 h | 5.39 h | 3.77 h |

Una sola 21700 tiene energía suficiente en el papel para la meta de dos horas. La incógnita no es principalmente la capacidad, sino si el elevador y la protección soportan la corriente instantánea.

## Simplificación recomendada

### Fase 1 — maqueta funcional con red eléctrica

- Usar el cargador existente sólo si su etiqueta indica **5 V/3 A** y supera una prueba bajo carga.
- Conservar el relé de un canal para la bomba.
- Para las otras salidas, elegir entre:
  - relé de cuatro canales: menor riesgo de integración, mayor consumo y ruido;
  - driver MOSFET realmente lógico: mejor eficiencia, pero debe verificarse el modelo exacto y añadir diodo flyback al motor.
- Usar un único altavoz reciclado de 4–8 ohmios si está en buen estado.
- No comprar todavía batería, panel, CN3065, gran condensador ni portaceldas.
- No comprar microSD salvo que el registro de datos sea un requisito explícito.
- Probar primero la tira WS2812 directamente a 3.3 V; añadir 74AHCT125 sólo si falla o es inestable.

### Fase 2 — respaldo con batería, sin solar

La ruta más compacta es un módulo UPS 1S con portaceldas, carga, protección y elevador integrados, más dos celdas iguales y sanas. El módulo LX-2BUPS resulta prometedor, pero su ficha comercial contiene cifras contradictorias; antes de adoptarlo debe probarse a 1 A, 2 A y con el pico de arranque de bomba/ventilador.

Alternativa: TP4056 protegido ya disponible + 1×21700 + portacelda 21700 + elevador verificado de 5 V/3 A. En esta arquitectura es preferible cargar con la casa apagada si no se añade un circuito de reparto de carga.

### Fase 3 — solar

Arquitectura mínima correcta:

`panel de 5–6 V → CN3065 → batería 1S protegida → elevador de 5 V → casa`

No comprar el panel hasta conocer Wh/día consumidos y horas solares útiles. El panel no se dimensiona sólo por el voltaje; debe reponer la energía diaria y cubrir pérdidas.

## Pruebas físicas mínimas antes de declarar “funciona”

1. Medir corriente en reposo, uso normal y todas las cargas activas.
2. Registrar el voltaje de 5 V durante el arranque de la bomba, motor y audio; límite sugerido: no caer por debajo de 4.75 V.
3. Ejecutar cinco arranques consecutivos y confirmar que ningún relé o motor se activa accidentalmente.
4. Mantener cada driver de potencia encendido 10 minutos y comprobar temperatura y caída de tensión.
5. Hacer una descarga completa cronometrada de la batería con la carga real.
6. Para solar, medir energía recogida durante varios días, no sólo voltaje en vacío.
7. Para Jarvis, medir tasa de aciertos, falsos positivos y comportamiento con el altavoz activo.

## Decisión de compra

**Comprar o confirmar ahora:** fusible y portafusible, conectores seguros, fuente/cargador 5 V/3 A si el existente no cumple, y un sistema de conmutación validado. Comprar INMP441 y MAX98357A únicamente si se acepta que Jarvis será una fase experimental.

**No comprar todavía:** módulo elevador de 1 A, batería/solar, condensador de 6,800 µF, varias bocinas, segunda microSD, BMS adicional si ya se usa un TP4056 protegido, ni un módulo IRF540 sin prueba.

## Fuentes técnicas y de producto

- [TP4056 — hoja técnica](https://datasheet.lcsc.com/lcsc/1809261820_TOPPOWER-Nanjing-Extension-Microelectronics-TP4056-42-ESOP8_C16581.pdf)
- [CN3065 — hoja técnica](https://files.seeedstudio.com/wiki/Solar_Charger_Shield_V2.2/res/DSE-CN3065.pdf)
- [MAX98357A — Analog Devices](https://www.analog.com/en/products/MAX98357A.html)
- [ESP32-S3 — hoja técnica de Espressif](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)
- [WS2812B-V5 — hoja técnica de Worldsemi](https://datasheet.lcsc.com/lcsc/2106062036_Worldsemi-WS2812B-B-W_C2761795.pdf)
- [Celda Samsung INR21700-50E2](https://cdtechnologia.net/3710-bateria-recargable-samsung-inr21700-37v-4900mah-98a.html)
- [Módulo integrado de batería con salida máxima de 1 A](https://cdtechnologia.net/5562-modulo-integrado-de-carga-y-descarga-de-bateria-de-litio-18650-de-37-v-a-9-v-y-5-v-usb-c.html)
- [Protección HX-1S-3576](https://cdtechnologia.net/3379-modulo-de-proteccion-y-carga-bms-para-baterias-de-litio-18650-12a-hx-1s-3576.html)
- [Módulo UPS LX-2BUPS](https://cdtechnologia.net/3699-modulo-de-refuerzo-de-carga-de-2-baterias-de-litio-18650-usb-c-5v9v12v-3a-para-ups-lx-2bups.html)
- [Módulo MOSFET IRF540 de cuatro canales](https://cdtechnologia.net/5561-modulo-de-conmutador-mosfet-de-4-canales-irf540.html)

## Conclusión

La simplificación más sólida no consiste en encontrar una batería “mágicamente equivalente”, sino en cerrar primero la maqueta a 5 V/3 A, quitar almacenamiento y audio redundantes, y medir. Con ese enfoque, el núcleo de DOMUS es realizable ahora; la autonomía, el solar y Jarvis deben tratarse como tres validaciones posteriores e independientes.
