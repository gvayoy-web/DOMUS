---
fecha: 2026-09-06
estado: historico_superado_por_nota_33
---

# Esqueleto y decisiones consolidadas

> **Registro histórico.** La implementación vigente está en [[33 - Base modular funcional y plan de banco]] y la verificación más reciente en [[34 - Cierre de software y matriz de verificacion]].

> Revisión posterior: [[32 - Metas y madurez de la base DOMUS]] sustituye el
> carácter didáctico por una base modular en desarrollo. El umbral 600 y las
> órdenes de una letra descritos históricamente quedan retirados. Consultar
> README actual; los tamaños siguientes pertenecen a la primera versión.

> La configuración económica LED/S8050 descrita abajo también es histórica.
> La elección vigente es [[36 - Configuracion final 1 mas 4 reles y planos v4]].

## Archivo creado

- [Sketch educativo](../../firmware/domus_esqueleto/domus_esqueleto.ino).
- [Instrucciones y conexiones](../../firmware/domus_esqueleto/README.md).

Separado del firmware principal: sirve para aprender estructura y probar
componentes progresivamente. No es sustituto del supervisor doméstico completo.
Compilación Arduino ESP32-S3 N16R8/OPI, partición app3M_fat9M_16MB, CPU240,
LoopCore1: PASS, salida 0; programa 306389 bytes y globales 22588 bytes.
Binarios en `build/esqueleto`. No se grabó la placa ni se probaron cargas.

Incluye ADC suelo/nivel/luz, PIR, control manual, botón con antirrebote,
cinco salidas, PARO enclavado, rearme sin encender y límite de bomba de 10 s.
ON repetido no alarga una ejecución. LCD, DHT, DFPlayer, voz y automatizaciones
no están implementados en este ejemplo; sí se documentan pines reservados.

Por defecto `HABILITAR_BOMBA=false` y `NIVEL_CALIBRADO=false`. Solo esa
constante puede pasar a `true` tras montar y medir el driver del relé; GPIO5-8
siguen bloqueados en `SALIDA_FISICA_HABILITADA`.
Las cargas deben permanecer desconectadas: pines en entrada no garantizan OFF
en un relé sin polarización externa. No cambiar banderas para omitir pruebas.
El umbral de nivel 600 es ilustrativo, requiere calibración real y dirección
de lectura confirmada. ADC fuera de rieles no garantiza detectar cable abierto.

## Qué tiene Isaac y qué se reutiliza

Fuente de inventario: [[01 - Inventario confirmado]]. Núcleo disponible:
ESP32-S3, bomba/tubo, un relé, motor/aspa, LEDs, resistencias, S8050, diodos,
LCD/backpack, sensores y controles. Pico/ESP8266 y otros extras quedan de reserva;
usar todas las piezas no es requisito. La fotografía de un kit no prueba
variantes/cantidades. DHT11/22, motor y cargador requieren identificación física.

## Configuración económica histórica no elegida

| Elemento | Función | Condición |
|---|---|---|
| Un relé, GPIO4 | Interruptor de la minibomba, no fuente de energía | Compatible con lógica 3.3 V y polaridad prevista |
| LEDs GPIO5/6/8 | Sala, dormitorio, invernadero | Uno con resistencia por salida; no tiras directas |
| Driver GPIO7 | Conmutar ventilador | S8050 candidato, comprobar arranque/temperatura o sustituir etapa |
| LCD y sensores | Información y automatizaciones del firmware principal | Calibración y niveles eléctricos |
| Una fuente | Alimentar ramales de control y potencia | Selección aplazada, no aprobada |
| DFPlayer | Respuestas grabadas | Faltan altavoz/tarjeta confirmados e integración validada |

El firmware principal ya tiene `DOMUS_SALIDAS_ECONOMICAS=1` para este patrón
de polaridades. Por defecto conserva perfil 0 de relés. No intercambiar binarios
sin cambiar/verificar mazo; no se eliminan funciones para ahorrar una etapa.

## Planos y aspecto físico

Se conservan los planos reales en `planos/new`, base 800 × 520 mm: depósito e
invernadero a la izquierda, casa al fondo, porche delante, Jarvis/gabinete a la
derecha. La ruta existente es `casa_inteligente_v4/planos/new`, no la escrita con
subcarpetas `casa/_inteligente/_v4`.
Guía y CSV mandan sobre renders. Los planos son para estructura en crudo,
sin electrónica instalada. Pasos H01–H05 vacíos, H08 sin abrir hasta medir sonda.
El gabinete debe comprobarse con placas reales antes de fijar agujeros.

La imagen económica generada era conceptual, no respetaba esta distribución;
su corrección fue interrumpida. Tenía flechas y valores no confirmados: no usarla
como plano eléctrico ni para elegir fusible/altavoz. No modificar arquitectura
de la casa para acomodar ese render. Tres luces económicas no equivalen a toda
la iluminación decorativa mostrada en el concepto original.

## Jarvis: decisiones y límites

Isaac desea órdenes por voz, sin API, teléfono, Raspberry ni laptop durante
la demostración; acepta sonido robótico. La computadora puede preparar modelos.
Propuesta inicial: botón para hablar, INMP441, reconocimiento de intenciones
en ESP32, despachador seguro y respuesta por LCD/DFPlayer. El botón de hablar
no tiene GPIO asignado todavía; no confundir con botón DEMO del esqueleto.
Una tarjeta microSD almacena, no ejecuta IA por sí sola.

DFPlayer ya disponible puede reproducir pistas sintéticas autorizadas sin audios
de Isaac. No ofrece TTS libre ni reconocimiento. PicoTTS es otra salida de audio,
no ASR; requeriría integración y MAX98357A. Elegir una ruta, no comprar ambas.
Barista queda experimental: no hay conversación libre española validada en DOMUS.
Se mantienen [[24 - Viabilidad Barista DOMUS memoria voz y entrenamiento]],
[[25 - Plan ejecutable Jarvis offline fiable y entrenado]] y [[30 - Plan C Jarvis offline por etapas]].

Entrenador preparado y prueba técnica int8 con ruido realizada: no modelo útil
entrenado. No prometer cero errores. Validar corpus, falsos disparos, memoria,
latencia, micrófono/altavoz y 24 h/1000 ciclos según plan 25 antes de aprobar voz.

## Gasto tratado en conversación

Se propuso L180 orientativos para protección/distribución/cable/interruptor
sin fuente, y desde L428 sumando la fuente base micro-USB de referencia L248.
No son precio final ni garantía de suficiencia. Adaptación I2C, driver motor,
adaptador de alimentación, herramientas, envío y maqueta pueden sumar gastos.
Un cargador existente solo descuenta compra si pasa etiqueta y prueba de carga.
No usar 19 V en MB102 ni conectar potencia a GPIO. Paneles decorativos deben
presentarse como representación; no afirmar autonomía solar inexistente.
Comparativas y fuentes: [[27 - Comparador de planes costo y versatilidad]],
[[28 - Plan A DOMUS minimo desembolso]], [[29 - Plan B DOMUS ampliable y reutilizable]].

## Próximos pasos, sin mezclar versiones

1. Leer README del esqueleto y compilar sin cargas; no flashear destino desconocido.
2. Confirmar componentes físicos, fuente y etapas antes de energizar motores.
3. Probar esqueleto supervisado, sensores crudos y controles; registrar resultados.
4. Usar firmware principal para automatizaciones/supervisión completas, no
   copiar el ejemplo como sustituto de todas sus protecciones.
5. Continuar voz por plan 25/30; no marcarla terminada por tener estructura de código.

Esta nota consolida lo hablado y distingue propuestas de hechos comprobados.
No compra componentes, no despliega visualizadores ni certifica cableado.
