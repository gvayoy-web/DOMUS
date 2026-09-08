---
fecha: 2026-09-06
estado: propuestas_no_montadas
---

# Comparador de planes: costo y versatilidad

Objetivo: aprovechar lo disponible sin obligar a montar todas las piezas.
Arquitectura: un ESP32-S3, cinco actuadores lógicos y etapas de potencia
intercambiables con configuración explícita. Tecnología: firmware Arduino
existente, LCD1602 y pruebas Python/C++. No se modifica código en esta entrega.
Base: [[01 - Inventario confirmado]], [[21 - Simplificacion y reduccion de costos]],
[[25 - Plan ejecutable Jarvis offline fiable y entrenado]] y [[26 - Avance Jarvis contrato entrenamiento y pruebas]].
Compatibilidad: conservar PARO, MIC OFF, nivel, timeout de bomba y control manual.
TDD: no aplicable a esta entrega documental; implementación futura requiere regresión.
Verificación documental: `.venv-ia/Scripts/python.exe scripts/validate_project.py`.

## Tres configuraciones, una casa

| Capacidad | A: mínimo desembolso | B: ampliable recomendada | C: Jarvis offline |
|---|---|---|---|
| Riego, ventilación y tres luces | Sí, luces LED individuales | Sí, etapas dimensionadas | Sí, hereda B |
| Sensores, LCD, botones y protecciones | Sí | Sí | Sí |
| Salida de audio | No requerida | DFPlayer opcional, frases grabadas | PicoTTS previsto, integración pendiente |
| Reconocimiento de voz | No | No por añadir DFPlayer | Pendiente de modelo y pruebas |
| Batería/solar | No | Ampliación independiente | Ampliación independiente |
| Registro microSD ESP32 | No | Opcional | No obligatorio para arranque |
| Dificultad de montaje | Baja, driver del motor condicionado | Media | Alta |
| Documento | [[28 - Plan A DOMUS minimo desembolso]] | [[29 - Plan B DOMUS ampliable y reutilizable]] | [[30 - Plan C Jarvis offline por etapas]] |

Decisión anterior (retirada): construir B con relé individual + módulo de cuatro
relés. La decisión vigente conserva la distribución desmontable y `planos/new`,
pero usa un solo relé desnudo para la bomba; véase la nota 36.
Añadir C cuando el núcleo esté probado. Posponer una función no significa conservarla gratis:
sin batería no hay autonomía; sin micrófono/modelo no hay reconocimiento.

## Destino de todo el inventario

| Grupo disponible según nota 01 | Destino razonado |
|---|---|
| ESP32-S3 | Único controlador principal en A/B/C |
| Pico y ESP8266 | Reserva y prácticas separadas; no añadir enlaces ni fuentes solo por usarlos |
| LCD1602 y backpack | Pantalla común; verificar niveles I2C antes de conexión |
| DHT, suelo, nivel, PIR, una LDR | Sensores del núcleo; confirmar DHT11/22 y calibrar |
| Bomba, tubo, relé individual | Riego en todos los planes; no retirar sensor de nivel |
| Motor/aspa, S8050, diodos | Ventilador condicionado a prueba de arranque y temperatura |
| LEDs y resistencias | Tres luces individuales; repuestos e indicadores |
| Botones y slide switches | DEMO, MIC OFF y controles de señal; no asumir capacidad de corte de potencia |
| Protoboard, jumpers, resistencias, capacitores, diodos | Prototipo y repuestos; mazo final firme y aislado |
| MB102 | Banco ligero, no fuente general; no conectar 19 V |
| TP4056 y clip de 9 V | Almacenados; no necesarios en versión de pared |
| DFPlayer y buzzers | Audio opcional; buzzer no sustituye habla ni micrófono |
| WS2812 y LED RGB | Estética opcional, no requisito de IA; LED simple evita driver/tira si solo se necesita estado |
| Keypad e IR | Alternativas de entrada, elegir una si aporta valor; integración pendiente |
| Reed y microswitches | Sensores opcionales de puerta; antes que RFID si solo se quiere detectar apertura |
| RFID y servo | Acceso demostrativo adicional; no afirmar cerradura de seguridad; integración pendiente |
| HC-SR04 | Experimento de distancia; no reemplazo directo del nivel sin rediseño y validación |
| MPU6050, termistor, tilt, joystick y potenciómetros | Reserva/prácticas; no duplicar sensores sin necesidad |
| Matriz, barra LED y displays de segmentos | Alternativas visuales, no pantallas simultáneas obligatorias |
| L293D, 74HC595 y S8550 | Reserva; no sustituciones automáticas de driver o adaptador lógico |

La foto es de un kit y confirma el tipo aparente del MB102 señalado, no la
cantidad ni variante física de cada componente. La nota 01 sigue siendo el
inventario; el cargador disponible no está homologado aún para DOMUS.

## Costos: evitar falsa precisión

Las cantidades L de notas 03/07/21 son referencias históricas del proyecto,
no cotizaciones vigentes. El 06-09-2026 la página de C&D de fuentes muestra
L248 para la opción base micro-USB y ofrece varias variantes: no demuestra
que USB-C con switch cueste lo mismo. Relé y MAX98357 no pudieron verificarse
en sus páginas durante esta consulta.

Modelo para comparar: costo pendiente = fuente apta + protección/distribución
+ driver necesario + opción de audio + envío + consumibles/herramientas faltantes.
Una pieza ya comprada cuenta L0 de compra adicional, no L0 de consumo o montaje.

| Ahorro potencial | Cuándo es real |
|---|---|
| Fuente nueva, referencia histórica L350 | Solo si el cargador existente pasa etiqueta, cable y carga simultánea |
| Relé cuatro canales, referencia L250 | Solo si LEDs individuales y driver ventilador apto sustituyen sus funciones |
| Lector SPI + tarjeta, referencia L308 | Si no se exige registro en tarjeta; no quitar la tarjeta al DFPlayer |
| Solar, referencia L1355 | Gasto pospuesto, no autonomía conservada |
| MAX98357 frente a DFPlayer ya disponible | Comparar altavoz + tarjeta + integración; no sumar ahorro y conservar TTS libre ficticio |

No sumar estas filas como descuento garantizado. Fusible, cable, adaptación
I2C, conectores, protección de motores y medición se mantienen según diseño.
El fusible se selecciona por cableado/cargas, no copiando 3 A sin revisión.

## Fuentes consultadas

- [C&D, variantes de fuente](https://sps.cdtechnologia.net/2985-fuente-para-raspberry-pi3-pi4.html).
- [SunFounder, módulo para protoboard](https://docs.sunfounder.com/projects/kepler-kit/en/latest/component/component_power_module.html): entrada DC 6.5–12 V, salidas 3.3/5 V, corriente anunciada inferior a 700 mA; comprobar variante real.
- [DFRobot, DFPlayer](https://www.dfrobot.com/product-1121.html): reproducción y amplificación integradas; no reconocimiento ni TTS.
- [TI, L293D](https://www.ti.com/product/L293D): driver bipolar hasta 600 mA por canal bajo condiciones especificadas; no asumir corriente de arranque admisible ni ausencia de caída de tensión.

## Regla de transición

Cada cambio de perfil exige apagar, identificar mazo/polaridad, compilar perfil
correcto y probar OFF/ON sin cargas antes de conectar motores. No autodetectar
un relé frente a transistor mediante pulsos. Ninguna propuesta autoriza compra,
flasheo ni montaje de batería. Volver al conjunto binario + mazo aprobado si falla.
