---
fecha: 2026-09-06
estado: historico_superado_por_nota_33
---

# Metas y madurez de la base DOMUS

> **Registro histórico de metas.** M1 y M2 fueron implementadas después de esta
> nota. Consultar [[33 - Base modular funcional y plan de banco]] y
> [[34 - Cierre de software y matriz de verificacion]] para el estado vigente.

## Compromiso y alcance

Isaac pide una base seria, no un ejemplo desconectado del producto. El objetivo
es una arquitectura mantenible para su hardware económico: ESP32-S3, un relé
de bomba, tres LEDs, driver ventilador, sensores, LCD y voz local por fases.
Madurez significa contratos verificables, límites explícitos, fallos observables
y regresiones; no cambiar una etiqueta a «producción» sin pruebas.

La base vive en `firmware/domus_esqueleto`; el firmware principal
`firmware/casa_inteligente_v4` sigue siendo referencia de funciones domésticas.
No sustituirlo ni mantener indefinidamente dos productos divergentes: la base
debe alcanzar paridad demostrada antes de proponer una migración. Conservar
ambos mientras no haya paridad; retirada solo con decisión y respaldo.

## Mejoras de esta revisión

- Configuración separada `domus_config.h`: GPIO únicos, polaridades, activación
  explícita y nivel sin umbral ficticio (`-1` obliga a medir antes de calibrar).
- Protocolo separado `domus_protocol.h`: líneas completas, lista exacta de
  comandos, memoria fija de 48 bytes y descarte total al exceder longitud.
- Retiradas órdenes de una letra: texto pegado ya no se interpreta letra por letra.
- PARO `!` prioritario incluso en descarte; el sufijo no puede rearmar la misma línea.
- ACK/NACK y consulta ESTADO; TX saturada no detiene control y registra omisiones.
- ON limitado a una solicitud cada 250 ms; OFF/PARO conservan prioridad.
- Bomba bloqueada tras timeout o fallo de nivel; rearme explícito sin encender.
- Doce regresiones constexpr del parser real en `protocol_tests.cpp`.

Las órdenes serie corresponden a control manual, no a voz. La integración
futura de voz deberá pasar por el despachador y revalidar MIC OFF, confianza,
caducidad y modelo aprobado. No conectar inferencia directamente a GPIO.

## Metas con puertas de aceptación

| Etapa | Meta verificable | Estado |
|---|---|---|
| M1: base de control | Configuración validada, parser acotado, fallos observables, compilación N16R8 y regresiones de protocolo | Compilación y 12 regresiones de protocolo PASS; ejecución integrada en placa pendiente |
| M2: paridad doméstica | LCD/DHT, automatizaciones con histéresis y propiedad manual, calibración persistente, watchdog/salud y pruebas de integración equivalentes al principal | Pendiente |
| M3: integración eléctrica | Identificar fuente/cargas, confirmar polaridades y niveles, arranque OFF/reset, PARO y timeout bajo carga | Pendiente de hardware |
| M4: voz local | Corpus autorizado, modelo útil, captura, frontend equivalente, rechazo seguro y DFPlayer o PicoTTS según ruta elegida | Pendiente |
| M5: entrega estable | Ensayo 24 h/1000 ciclos, sin reinicios imprevistos ni crecimiento sostenido de memoria/colas; medidas y binario identificados | Pendiente |

No publicar porcentajes de completitud: cada fila se aprueba con evidencias.
M1 no concede M2–M5. Compilar con salidas deshabilitadas tampoco valida sus drivers.

## Próximo lote de implementación

1. Extraer del principal reglas de control a una unidad comprobable, sin copiar
   lógica en un tercer sitio; conservar su protocolo y pruebas de regresión.
2. Añadir adaptadores de LCD y DHT con tiempos acotados y sensor no disponible
   explícito. No fabricar valores ante fallos ni bloquear el control por pantalla.
3. Reutilizar esquema de calibración validada del principal; corrupción implica
   bloqueo de automatización afectada, nunca valores por defecto que activen bomba.
4. Integrar supervisor de recursos/watchdog ya existente y probar fallos de
   inicialización. Evitar crear tareas/audio antes de reservar memoria necesaria.
5. Comparar comportamiento con principal antes de cambiar el firmware recomendado.

Pruebas físicas obligatorias: orden durante PARO, liberación sin rearme,
timeout seguido de ON, nivel insuficiente, cable de sensor retirado, USB lleno,
reset durante riego y fallo de alimentación. ADC por rieles no detecta todo
cable abierto. El paro de software no sustituye corte físico de potencia.

## Evidencia y límites de esta revisión

La primera compilación se detuvo al limpiar la caché de Arduino, antes de
evaluar código. Se reintentó con carpeta propia `build/esqueleto_madurez_compile`,
sin borrar caché del usuario. Reintento PASS (salida 0): programa 307621 bytes,
globales 22676 bytes, con 12 static_assert de protocolo evaluados. Variación
frente a la base anterior: +1232 bytes de programa y +88 bytes de globales.
No son mediciones de heap, latencia ni pila en operación.
Validación del proyecto: 43 PASS, 5 C++ omitidas por falta de compilador host;
esas pruebas del principal no acreditan la lógica de bomba de la nueva base.
`git diff --check` PASS. Estado de madurez: desarrollo verificado por compilación
y contrato, no producción ni integración de hardware aprobada.
No flasheo, compras ni cambios de cableado. El README define protocolo nuevo;
los comandos de una letra quedan incompatibles intencionadamente por seguridad.
Ningún cliente de producción conocido dependía de ese ejemplo recién creado.

Referencias: [[31 - Esqueleto y decisiones consolidadas]],
[[26 - Avance Jarvis contrato entrenamiento y pruebas]],
[[25 - Plan ejecutable Jarvis offline fiable y entrenado]],
[[28 - Plan A DOMUS minimo desembolso]].
