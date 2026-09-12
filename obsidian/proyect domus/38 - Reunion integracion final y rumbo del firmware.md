---
proyecto: PROJECT DOMUS
tipo: plan-de-integracion
actualizado: 2026-09-09
estado: listo_para_reunion
placa: ESP32-S3 N16R8
perfil_final: economico_mas_modulo_4_reles
---

# Reunión: integración final y rumbo del firmware

> [!WARNING]
> **Arquitectura de cinco relés archivada.** Se conserva como historial. Para
> comprar, cablear o programar se usa [[43 - Manual final completo PROJECT DOMUS]].

Evidencia física y límites de lo que puede inferirse de la foto:
[[39 - Inventario fotografiado y pines visibles]].

Esta nota es la guía vigente para la reunión. La decisión final se interpreta así:

- `GPIO4`: S8050 acciona la bobina del relé desnudo; sus contactos conmutan la bomba.
- `GPIO5-8`: cuatro relés adicionales con base/borneras, un canal por carga.
- Total final: cinco relés. Los cuatro adicionales no se usan hoy porque son compra futura.
- Sensores, LCD y botones se prueban primero con `firmware/domus_esqueleto`.
- Batería, solar, audio y Jarvis no entran en esta reunión.

> [!DANGER]
> El módulo de protoboard no se considera fuente de 3 A. No alimentar desde él
> ESP32, cuatro relés, bomba y motor a la vez. No unir los positivos de dos USB.
> Todo GPIO del ESP32 debe permanecer entre 0 y 3.3 V.

## Qué faltaba en el diagrama y el PDF

La revisión encontró riesgos que no podían quedar implícitos:

1. El capacitor electrolítico debía mostrar la franja exactamente en el terminal negativo.
2. La ruta LCD 3.3 V y la ruta LCD 5 V con conversor deben ser alternativas excluyentes.
3. Los terminales `LV/LV1/LV2` y `HV/HV1/HV2` deben leerse sin solaparse.
4. El diagrama debe caber tanto en móvil como en escritorio y conservar controles de zoom.
5. La resistencia entre `GPIO4` y base `B` debe existir físicamente en el dibujo.
6. Diodo y capacitores necesitan dos conexiones visibles, no solo una etiqueta.
7. Faltaba mostrar la arquitectura final de cinco relés y diferenciar
   `IN/VCC/GND` de los contactos `COM/NO/NC`.
8. Faltaba una prueba simultánea con criterio medible de tensión, corriente,
   temperatura y reinicios.

Diagrama interactivo: [abrir cableado paso a paso](../../visualizaciones/diagrama-cableado-interactivo/index.html).

PDF imprimible actualizado: [manual de reunión](../../output/pdf/DOMUS_Ronda_B01-B05_sin_compras.pdf).

## Arquitectura final: cinco relés, cuatro de compra futura

| GPIO | Interfaz física | Destino | Polaridad prevista |
|---:|---|---|---|
| 4 | 1 kΩ + S8050 + relé desnudo + 1N4007 en bobina | bomba 3-6 V | `HIGH` energiza bobina |
| 5 | `IN1` del módulo 4 relés | luz sala | medir; típico `LOW` |
| 6 | `IN2` del módulo 4 relés | luz dormitorio | medir; típico `LOW` |
| 7 | `IN3` del módulo 4 relés | ventilador | medir; típico `LOW` |
| 8 | `IN4` del módulo 4 relés | luz invernadero | medir; típico `LOW` |

El relé desnudo se prueba hoy solo si se identifican por continuidad sus dos
patas de bobina y sus contactos `COM/NO/NC`. El S8050 no conmuta directamente la
bomba: conmuta la bobina. El 1N4007 va sobre la bobina, raya al lado +5 V.

### Cómo identificar el relé desnudo sin adivinar posiciones

1. Con todo desconectado, medir resistencia entre pares. Las dos patas que dan
   una resistencia finita estable son la bobina. Si marca casi 0 Ω, detenerse:
   puede ser corto o se están midiendo contactos, no energizar.
2. Entre las tres patas restantes, buscar el par con continuidad sin energía:
   son `COM-NC`. La tercera es `NO`; `COM-NO` debe estar abierto.
3. Alimentar la bobina a su tensión rotulada mediante S8050 y D1, durante una
   prueba breve. Debe oírse clic: ahora `COM-NO` cierra y `COM-NC` abre.
4. Etiquetar físicamente cada pata. La posición “del centro” no es evidencia:
   el encapsulado y fabricante pueden cambiar la distribución.

Medir la resistencia de bobina permite estimar `I = 5 V / R`. Registrar también
la caída colector-emisor del S8050 mientras la bobina está activa. Si el relé no
cierra firme o el transistor calienta, la resistencia de base de 1 kΩ y/o el
driver no quedan aprobados; no conectar todavía la bomba.

La palabra “típico” no autoriza el cableado. Antes de activar una salida hay que
fotografiar el módulo y anotar modelo, tensión de bobina, nivel de disparo y si
tiene `JD-VCC`. Un módulo de 5 V no es automáticamente compatible con lógica de
3.3 V. Debe conmutar de forma fiable con el ESP32 y quedar apagado durante reset.

### Lado lógico del módulo

| Módulo | ESP32 / fuente |
|---|---|
| `IN1` | `GPIO5` |
| `IN2` | `GPIO6` |
| `IN3` | `GPIO7` |
| `IN4` | `GPIO8` |
| `GND` | GND común de control |
| `VCC` | según serigrafía/hoja del módulo, normalmente 5 V |
| `JD-VCC` si existe | alimentación de bobinas según manual; no retirar/poner jumper por intuición |

### Lado de contactos de cada canal

Para una carga DC normalmente apagada:

```text
positivo de la fuente de la carga -> COM
NO -> positivo de la carga
negativo de la carga -> negativo de su fuente
NC -> aislado
```

`COM`, `NO` y `NC` nunca se conectan a un GPIO. Para motores DC, el relé separa
la señal pero no elimina el pico en el circuito de la carga: colocar el diodo
flyback sobre el motor, raya/cátodo al positivo.

## Alimentación: decisión que evita la mayoría de fallas

El MB102 o módulo similar sirve para sensores y pruebas ligeras. No hay evidencia
de que entregue 3 A continuos y no se diseñará alrededor de esa suposición.

La fuente final será una fuente regulada de 5 V cuya corriente se elige después
de medir. Punto de partida de compra: 5 V / 3 A de fabricante fiable, pero solo
si el consumo medido, los picos y el margen caben. Si la bomba o el motor tienen
picos grandes, subir capacidad o separar el ramal de potencia; nunca obtener
esa corriente del pin `3V3`, de un GPIO ni de un jumper fino.

```text
FUENTE 5 V -> fusible -> interruptor -> 5V_BUS
5V_BUS -> ramal ESP32
        -> ramal módulo de relés
        -> ramal bomba
        -> ramal ventilador/luces
GND común de control; retornos de motores separados hasta el punto estrella
```

### Medidas que hay que tomar

| Prueba | Registrar | Aceptación provisional |
|---|---|---|
| fuente sin carga | voltaje | 4.8-5.2 V |
| ESP32 + sensores + LCD | V mínimo y corriente | sin reset; señales ≤3.3 V |
| cuatro bobinas | corriente y temperatura | bus estable, módulo sin calentamiento anormal |
| bomba directa | arranque y régimen | gira; tensión no colapsa |
| motor/ventilador | arranque y régimen | probar separado primero |
| todo simultáneo 10 min | V mínimo, corriente, temperatura | bus ≥4.75 V y cero resets |

El fusible se dimensiona para proteger el calibre de cable y la instalación.
No se elige “3 A” únicamente porque la fuente diga 3 A.

## Orden de la reunión

1. Fotografiar ambas caras del ESP32, LCD/backpack, módulo de fuente, S8050 y
   cualquier relé. Anotar toda serigrafía.
2. Confirmar `GPIO2`, `GPIO9`, `GPIO13`, `GPIO21`, `3V3`, `5V/VIN` y `GND`.
3. Ejecutar cinco arranques con ESP32 solo; `DIAGNOSTICO` debe mostrar `FIS=00000`.
4. Conectar DHT, suelo, nivel, LDR, PIR y botones uno por uno, con energía apagada.
5. Con todos los sensores presentes, observar 20 ciclos; cada estímulo debe
   cambiar solo la variable esperada.
6. Conectar LCD por Ruta A o Ruta B, nunca las dos. Probar `0x27` y `0x3F`.
7. Calibrar y guardar NVS; reiniciar y confirmar `CAL=1`.
8. Con ESP32 desconectado, medir la fuente y probar la bomba directamente un segundo.
9. Identificar bobina/COM/NO/NC del relé desnudo y E/B/C del S8050; montar
   GPIO4 -> 1 kΩ -> base, transistor sobre la bobina y 1N4007 sobre la bobina.
   Probar primero clic/continuidad sin bomba; después conmutar la bomba.
10. Cuando existan los cuatro relés comprados: probar IN1-IN4 sin cargas, luego una
    carga por canal y por último combinación completa.

> [!IMPORTANT]
> “Todo al mismo tiempo” es la prueba final, no el primer encendido. Una pieza
> por vez permite localizar fallas; después se deja todo conectado y se hace la
> prueba simultánea.

## Rumbo del firmware

### 1. Una fuente de verdad por etapa

`firmware/domus_esqueleto` es el firmware activo de banco. No es desechable:
se convierte en el núcleo probado. `firmware/casa_inteligente_v4` queda como
referencia de funciones grandes hasta que el banco complete B01-B10.

No se corregirán los mismos fallos en dos sketches en paralelo. Cuando el banco
sea estable, se migran o extraen módulos comunes y se retira la duplicación.

### 2. Perfiles físicos explícitos

El siguiente cambio de código debe sustituir las banderas dispersas por un perfil:

```text
BANCO_SENSORES       GPIO4-8 sin salida
BANCO_BOMBA          GPIO4 HIGH; GPIO5-8 sin salida
FINAL_5_RELES        GPIO4 controla relé desnudo; GPIO5-8 controlan cuatro relés comprados
```

El perfil debe aparecer en `DIAGNOSTICO`, rechazar combinaciones imposibles en
compilación y arrancar todas las cargas físicamente apagadas. No se activa
`FINAL_ECO_4RELES` hasta conocer el módulo real.

### 3. Separación interna prevista

- `board_config`: pines, polaridades, perfiles y capacidades físicas.
- `drivers`: LCD, DHT, ADC, PIR, relés y driver de bomba.
- `safety`: PARO, timeout, nivel mínimo, watchdog y brownout observado.
- `control`: propiedad manual/automática e histéresis.
- `protocol`: comandos, ACK/NACK y diagnóstico.
- `storage`: calibración NVS versionada.
- `app`: coordina tareas sin conocer detalles eléctricos.

### 4. Pruebas que bloquean la promoción

- Parser y decisiones puras en host.
- Compilación de los tres perfiles.
- Cinco reinicios sin pulso.
- PARO durante cada actuador y durante todos simultáneos.
- Bomba: nivel inválido, timeout, rearme y orden repetida.
- I2C ausente o colgado sin congelar el control.
- Sensor desconectado produce fallo seguro, no automatización falsa.
- 1,000 ciclos o 24 h sin reset ni crecimiento sostenido de memoria.

Jarvis se integra al final como productor de órdenes hacia el mismo controlador;
nunca escribe GPIO directamente. Primero casa fiable, después voz.

## Cosas que pueden salir mal después si no se cierran hoy

- La salida del sensor de nivel puede subir o bajar con el agua; el firmware
  actual asume un mínimo crudo. Confirmar dirección antes de autorizar bomba.
- Un ADC desconectado puede devolver un valor aparentemente válido. Las pruebas
  de plausibilidad no sustituyen detección física de cable roto.
- El sensor resistivo de suelo se corroe si queda energizado continuamente.
  Para uso permanente, conmutar su alimentación o cambiarlo por uno capacitivo.
- El PIR necesita estabilización y puede dispararse por alimentación ruidosa.
- El LCD a 5 V puede elevar SDA/SCL a 5 V mediante pull-ups.
- El orden E/B/C del S8050 depende del fabricante; la cara plana no basta.
- La corriente de arranque de bomba/motor puede ser varias veces la corriente
  estable y reiniciar el ESP32 aunque un multímetro muestre 5 V en reposo.
- Los módulos de relés activos en LOW pueden hacer clic durante boot si los GPIO
  flotan. La etapa debe tener polarización segura además del software.
- Protoboard y jumpers no son montaje final cerca de agua: después de validar,
  usar conectores firmes, aislamiento, alivio de tensión y separación física.

## Salida esperada de esta reunión

- Tabla B01-B05 completa y calibraciones reales.
- Pinout/fotos de cada módulo guardados.
- Medidas reales del MB102 y de la bomba.
- Decisión fundada sobre la fuente final.
- Lista exacta de compra del módulo de cuatro relés compatible con 3.3 V.
- Ninguna salida habilitada por intuición.

## Relaciones

- [[01 - Inventario confirmado]]
- [[18 - Manual maestro de conexiones pin por pin]]
- [[33 - Base modular funcional y plan de banco]]
- [[36 - Configuracion final 1 mas 4 reles y planos v4]]
- [[37 - Ronda de pruebas sin compras]]
