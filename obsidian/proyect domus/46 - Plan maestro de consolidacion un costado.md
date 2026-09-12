---
proyecto: PROJECT DOMUS
tipo: plan-maestro
actualizado: 2026-09-10
estado: plan vigente para ejecutar
autoridad: sustituira 43-45 al terminar la consolidacion
---

# Plan maestro de consolidación: montaje por un solo costado

## 0. Resultado buscado

Construir una base alfa completa, comprobable y fácil de cablear con el ESP32-S3
N16R8 colocado atravesando la ranura central de la protoboard. La placa cabe,
pero su ancho tapa las hileras libres de uno de los costados; por eso **todas las
señales del banco deben salir por el único costado que queda accesible**.

El proyecto tendrá tres perfiles físicos documentados, no un único dibujo que
mezcle piezas presentes, compras futuras y pruebas:

1. `ALFA_UN_COSTADO`: lo disponible hoy, sin control IR y sin piezas pedidas.
2. `DRIVER_IDENTIFICADO`: después de recibir e identificar el controlador.
3. `FERIA_FINAL`: fuente, controlador, audio y montaje permanente aprobados.

## 1. Fuente de verdad y clasificación documental

### Documentos vigentes durante la consolidación

| Nota | Papel |
|---|---|
| [[01 - Inventario confirmado]] | autoridad de qué piezas existen |
| [[39 - Inventario fotografiado y pines visibles]] | evidencia visual, no pinout universal |
| [[45 - Diagrama ASCII alfa sin control IR]] | borrador físico anterior; debe migrarse al nuevo costado |
| [[46 - Plan maestro de consolidacion un costado]] | plan actual y registro de descubrimientos |

### Documentos que deben ser reemplazados o rebajados

| Nota/archivo | Estado que debe recibir | Motivo |
|---|---|---|
| [[43 - Manual final completo PROJECT DOMUS]] | `SUPERADO_EN_CONSOLIDACION` | supone GPIO1/2/21 accesibles, DRV8833 confirmado y no refleja la protoboard real |
| [[44 - Arquitectura y ciclo de vida del firmware]] | `SUPERADO_EN_CONSOLIDACION` | todavía define banco IR y DRV8833; conservar reglas de seguridad |
| [[45 - Diagrama ASCII alfa sin control IR]] | `BORRADOR_SUPERADO` al publicar el nuevo diagrama | usa GPIO1/2/21 del lado tapado |
| `firmware/PLAN_CODIGO.md` | `HISTORICO_V2_IR` | describe `BANCO_IR_LCD`, no el banco de hoy |
| `visualizaciones/diagrama-final.html` | `NO_CABLEAR` hasta regenerarlo | duplica GPIO16 y dibuja un DRV8833 distinto al producto pedido |
| `output/pdf/DOMUS_Ronda_B01-B05_sin_compras.pdf` | `HISTORICO` | no contempla el costado único ni el fallo real de LCD |

### Archivo histórico

Las notas 02-42 conservan el razonamiento y evolución, pero no autorizan
cableado, compras ni cambios de firmware. Al ejecutar este plan se añadirá un
banner uniforme en cada nota histórica y se actualizarán `00 - Inicio.md` y
`Bienvenido.md` para apuntar únicamente al manual consolidado nuevo.

No se borrará historia. Se marcará claramente qué fue descartado:

- batería y solar funcional;
- cinco relés y módulo de cuatro relés;
- reconocimiento de voz/INMP441 como requisito;
- TA6586, que no está en el kit modificado;
- suposición de que la placa pedida es definitivamente DRV8833;
- mapa antiguo con GPIO1, GPIO2 y GPIO21 atravesando la placa.

## 2. Descubrimientos y decisiones acumuladas

### Placa y protoboard

- Placa confirmada: ESP32-S3 N16R8.
- La placa ocupa ambos lados de la ranura central.
- Solo queda una hilera lateral utilizable para jumpers rígidos y componentes.
- Costado accesible observado, en orden aproximado:
  `3V3, 3V3, RST, 4, 5, 6, 7, 15, 16, 17, 18, 3, 46, 9, 10, 11, 12, 13, 14, 5V, GND`.
- Costado tapado incluye GPIO1, GPIO2 y GPIO21, por lo que no se usarán en el
  banco alfa.
- GPIO46 se tratará como entrada solamente y no será salida de actuador.
- GPIO19/20 continúan reservados para USB nativo; GPIO0/45/46 se evitan para
  funciones que puedan afectar el arranque.

### Alimentación

- El módulo de alimentación de protoboard está averiado.
- El TP4056 USB-C hizo funcionar la bomba durante una prueba, incluso con
  `B+`/`OUT+` y negativos unidos, pero esa experiencia no lo convierte en una
  fuente de distribución final: es un cargador/protector para una celda 1S.
- El ESP32 se alimenta por USB durante el banco.
- Bomba y ventilador no se alimentan desde GPIO, 3V3 ni el pin 5V del ESP32.
- Hasta recibir la fuente regulada, las etapas de motor pueden montarse sin
  conectar `+5V_MOTORES`; cualquier prueba usa una fuente externa 5 V medida.
- Todas las señales de control comparten GND con la fuente de motores.
- La fuente final pedida es cerrada, 5 V/5 A, con fusible lento 4 A y switch
  maestro DC.

### Pantalla y sensores

- LCD1602 con backpack I2C: físicamente solo `GND, VCC, SDA, SCL`.
- La unidad se ha usado a 3.3 V; no se sube a 5 V sin revisar pull-ups I2C.
- Al conectar el montaje reciente, el LCD no dibujó nada.
- El firmware actual solo busca `0x27` y `0x3F`; el plan exige escaneo completo
  y diagnóstico serial antes de culpar la pantalla.
- Sensores disponibles: DHT11 suelto, suelo resistivo con comparador, nivel de
  agua, LDR, PIR; opcionales HC-SR04, MPU6050, reed, termistor y tilt.
- El HC-SR04 no entra en el banco común sin divisor de ECHO.
- Los sensores analógicos deben recalibrarse después del cambio de GPIO.

### Actuadores

- Bomba 3-6 V y motor con aspa disponibles.
- Dos S8050 y dos S8550 disponibles; los S8050 sirven como interruptores de
  lado bajo para pruebas cortas, solo tras identificar E/B/C.
- Cada motor con S8050 requiere su propio 1N4007 en paralelo, raya al positivo,
  resistencia de base y GND común.
- El relé desnudo queda fuera del núcleo; no comprar relés.
- Tres LED (dos azules y uno rojo) representan iluminación suplementaria, no UV
  real ni crecimiento agrícola comprobado.
- Buzzer TMB12A05 es activo de 5 V; buzzer pasivo es alternativa. No poner una
  carga de 5 V desconocida directamente en un GPIO.
- L293D existente queda como alternativa de banco si las corrientes superan lo
  razonable para los S8050.

### Control y Jarvis

- Hoy no se usa el control CAR MP3 ni el HX1838.
- La idea final de Jarvis sigue siendo control IR determinista y respuestas
  españolas, sin entrenamiento de IA.
- INMP441 no se compra; voz libre y wake word no son requisitos.
- MAX98357A y parlante siguen pendientes.
- DFPlayer está disponible, pero requiere microSD y no es obligatorio.

### Controlador pedido

- El anuncio lo llama DRV8833.
- La fotografía muestra `VCC, GND, IN1-IN4, OUT1-OUT4`, distribución más cercana
  a MX1508 que a un breakout DRV8833 típico.
- No existe `nSLEEP` visible en la foto.
- Hasta fotografiar ambas caras y leer el integrado, el software lo denominará
  `CONTROLADOR_DOBLE_PENDIENTE`, nunca `DRV8833` como hecho confirmado.
- No se define el pinout final del controlador antes de recibirlo.

### Software y pruebas

- `casa_inteligente_v4.ino` está desactualizado: usa `CANTIDAD_RELES`,
  `PINES_RELES`, `estadoReles` y retardos de relé.
- No se arregla renombrando variables: se sustituirá la abstracción por
  `SalidaDomus` y drivers físicos por perfil.
- El esqueleto v2 compila y responde por Serial, pero corresponde a
  `BANCO_IR_LCD`, no al montaje de hoy.
- El mapa actual duplica GPIO16 entre botón físico y BCLK futuro del MAX98357A.
- Las pruebas HIL existentes validan principalmente el protocolo serie; todavía
  no prueban físicamente LCD, IR, motores ni sensores.
- `validate_project.py` falla en el árbol actual porque faltan entregables bajo
  `planos/new`; antes de cerrar se decidirá si se restauran o se retiran también
  sus pruebas y referencias.

## 3. Mapa candidato `ALFA_UN_COSTADO`

Este mapa es el objetivo del rediseño, sujeto a comprobar que cada etiqueta de
la placa real corresponde al GPIO esperado. No se cablea por memoria: se sigue
la serigrafía visible.

```text
COSTADO ACCESIBLE DE ARRIBA HACIA ABAJO

3V3  -> riel de sensores y LCD
3V3  -> reserva/distribución corta
RST  -> libre

G4   -> bomba por S8050 #1 (solo perfil ALFA_BOMBA_1; bloqueado en normal)
G5   -> LED sala + resistor
G6   -> LED dormitorio + resistor
G7   -> ventilador por S8050 #2 (solo perfil ALFA_VENTILADOR_1; bloqueado en normal)
G8   -> tres LED cultivo, cada uno con 1 kOhm en alfa (corrige asignación previa a G11)

G15  -> humedad de suelo AO
G16  -> nivel de agua S/AO
G17  -> LCD SDA
G18  -> botón MODO temporal a GND

G3   -> nodo LDR + 10 kOhm
G46  -> NO USAR COMO SALIDA; libre
G9   -> PIR OUT
G10  -> botón STOP a GND
G11  -> SILENCIO Jarvis a GND (botón, INPUT_PULLUP; NO es salida de cultivo)
G12  -> RESERVADO, SIN CONECTAR (buzzer deshabilitado en alfa; IR fuera del perfil)
G13  -> LCD SCL
G14  -> DHT11 DATA + pull-up 10 kOhm

5V   -> no alimentar motores; solo se usa si una carga ligera fue medida
GND  -> riel común
```

### Límites del mapa candidato

> [!NOTE] Actualización 2026-09-12 (ola 1): cultivo queda en GPIO8 (corrige mención
> previa a G11, que es SILENCIO-botón). GPIO12 pasa a RESERVADO, SIN CONECTAR:
> `BUZZER_HABILITADO=false`, IR fuera del perfil. Ver nota 50.

- El buzzer no se conecta en alfa (`BUZZER_HABILITADO=false`); GPIO12 reservado,
  sin conectar. El firmware ya no configura ni escribe GPIO12 en este perfil.

- El buzzer activo no se conecta mientras los dos S8050 estén ocupados por
  bomba y ventilador.
- Los tres LED de cultivo usan 1 kOhm individual en alfa para reducir corriente
  total del GPIO; la etapa final se rediseña.
- GPIO12 deja de ser IR solo en este perfil. El firmware debe expresarlo como
  perfil, no como edición manual escondida.
- GPIO16 deja de ser botón y queda como nivel analógico en alfa; esto elimina
  el conflicto inmediato con la asignación anterior, pero el mapa final de
  audio se decidirá por separado.
- No se conecta simultáneamente todo el inventario opcional: “todo” significa
  todo el núcleo funcional. Extras se prueban con sketches aislados.

## 4. Arquitectura objetivo del firmware

### Un solo núcleo y drivers intercambiables

```text
Sensores -> EstadoDomus -> Seguridad -> Reglas automáticas
Botones  -> OrdenDomus  -> Seguridad -> SalidaDomus
Serial   -> OrdenDomus  -> Seguridad -> SalidaDomus

SalidaDomus -> DriverAlphaS8050
             DriverDobleConfirmado
             DriverSimulado

Eventos -> LCD
           Buzzer
           Audio futuro
```

### Perfiles de compilación

| Perfil | Uso | Salidas permitidas |
|---|---|---|
| `SELFTEST` | ESP32 solo | ninguna |
| `ALFA_UN_COSTADO_SIN_IR` | banco actual | LED; motores bloqueados por defecto y habilitación individual de prueba |
| `ALFA_MOTOR_1` | prueba vigilada | únicamente bomba o únicamente ventilador |
| `DRIVER_DOBLE_TEST` | módulo recibido e identificado | un canal cada vez |
| `FERIA_FINAL` | hardware aprobado | todas, con interlocks |

Cada perfil posee su propia tabla `PinMap`; una comprobación de compilación debe
detectar duplicados por **función**, no solo comprobar que un número aparece en
una lista deduplicada.

### Nombres que se retiran

```text
CANTIDAD_RELES        -> TOTAL_SALIDAS
PINES_RELES           -> pinMap.salidas
estadoReles           -> estadoSalidas
propietarioReles      -> propietarioSalidas
encenderRele()        -> solicitarSalida()
apagarRele()          -> desactivarSalida()
verificar...Rele()    -> verificarNivelLogicoSalida()
USAR_DRV8833          -> DRIVER_MOTORES_SELECCIONADO
```

Las funciones de seguridad, calibración, propiedad manual/automática, timeout,
paro y rearme se conservan. Se retiran únicamente las suposiciones físicas de
relés.

## 5. Plan de implementación

### Fase A — congelar evidencia física

1. Fotografiar el ESP32 montado en la protoboard mostrando el costado libre.
2. Fotografiar serigrafía completa y corregir etiquetas ilegibles (`41/42`,
   `19/20`, TX/RX) sin adivinarlas.
3. Medir continuidad de rieles; comprobar si están cortados a mitad.
4. Registrar si LCD tiene retroiluminación, cuadros o pantalla totalmente negra.
5. Ejecutar un escáner I2C completo `0x08-0x77` y registrar dirección/respuesta.

**PASS:** mapa físico confirmado y dirección LCD conocida.

### Fase B — reparar el esqueleto

1. Añadir `PinMap` y perfil `ALFA_UN_COSTADO_SIN_IR`.
2. Mover suelo `1 -> 15`, nivel `2 -> 16`, LCD SDA `21 -> 17`.
3. Deshabilitar inicialización IR en este perfil; GPIO12 queda disponible.
4. Sustituir búsqueda fija del LCD por escaneo completo con reporte Serial.
5. Mostrar por Serial dirección detectada y causa de modo sin pantalla.
6. Mantener motores deshabilitados y todas las salidas LOW al arranque.
7. Añadir pruebas de contrato para el mapa y para ausencia de duplicados.

**PASS:** LCD muestra bienvenida; sensores cambian; ninguna carga se activa.

### Fase C — firmware alfa de actuadores

1. Implementar `DriverAlphaS8050` sin duplicar reglas de seguridad.
2. Habilitación por compilación de una sola carga motriz.
3. Pulso inicial máximo 500 ms; bomba siempre sumergida.
4. Nivel inválido o bajo impide bomba.
5. STOP corta todas las salidas independientemente del modo.
6. Medir caída de fuente, temperatura de S8050 y corriente de arranque.
7. Si un S8050 calienta o no satura, detener y probar L293D; no paralelar BJT.

**PASS:** diez pulsos individuales sin reinicio, calentamiento ni bloqueo.

### Fase D — identificar e integrar el módulo pedido

1. Fotografiar ambas caras al recibirlo.
2. Leer referencia del chip; comparar pinout de fuente primaria.
3. Crear exactamente un driver: `Mx1508Driver` o `Drv8833Driver`.
4. Si es MX1508, asignar cuatro entradas y retirar toda referencia a `nSLEEP`.
5. Si es DRV8833 real, documentar nombres exactos del breakout recibido.
6. Probar placa sin motores, bomba sola, ventilador solo y ambos.

**PASS:** módulo identificado, tabla de verdad medida y sin caída de 5 V.

### Fase E — migrar `CASA FINAL`

1. Extraer reglas válidas del firmware antiguo.
2. Reemplazar toda abstracción `Rele` por salidas y drivers.
3. Eliminar polaridad global basada en relés y delays de conmutación mecánica.
4. Usar el mismo `PinMap` aprobado, sin copiar constantes.
5. Integrar LCD y sensores validados.
6. Mantener IR fuera hasta terminar el banco; luego añadirlo como entrada, no
   como escritor directo de GPIO.
7. Resolver el mapa MAX98357A sin compartir GPIO16 con botón/sensor.

**PASS:** búsquedas por `CANTIDAD_RELES`, `PINES_RELES`, `estadoReles` y
`encenderRele` devuelven cero en el firmware vigente.

### Fase F — Jarvis y audio

1. Reintroducir HX1838 solo después de congelar mapa final.
2. Aprender los 21 códigos del control real; ignorar repeticiones peligrosas.
3. Elegir una ruta de audio: MAX98357A desde flash o DFPlayer con microSD.
4. Reservar pines exclusivos y añadir verificación de duplicados.
5. Las acciones funcionan sin audio; MUTE nunca bloquea seguridad.

**PASS:** órdenes deterministas, cero falsos accionamientos y respuesta española.

### Fase G — documentación y entregables

1. Crear un manual maestro nuevo que sustituya notas 43-45.
2. Marcar todas las notas antiguas con banner histórico uniforme.
3. Regenerar PDF desde la misma tabla de pines del manual.
4. Reparar o retirar referencias a `planos/new` y dejar validación verde.
5. Registrar mediciones reales, no estimaciones, en la hoja de feria.

## 6. Diseño requerido del nuevo diagrama

El nuevo diagrama tendrá cuatro vistas claramente separadas.

### Vista 1 — colocación física

```text
          COSTADO TAPADO                  COSTADO ACCESIBLE

      x x x x x x x x x          ||     o-- señal/componente
   +------------------------+     ||     o-- señal/componente
   | ESP32-S3 N16R8         |=====||=====o-- señal/componente
   +------------------------+     ||     o-- GND/3V3
      sin espacio útil             ranura  hileras libres
```

Debe dibujar la protoboard, ranura, orientación USB y los nombres en el mismo
orden físico visto por Isaac. Nada de un ESP32 genérico flotando sin orientación.

### Vista 2 — alfa disponible hoy

- Una línea por cable, numerada y con origen/destino textual.
- LCD representado con solo cuatro pines.
- Sensores agrupados en 3V3.
- Motores con S8050, resistencia de base, pull-down, diodo y fuente separada.
- Control IR ausente y señalado como `NO MONTAR HOY`.
- Buzzer activo marcado `SIN TRANSISTOR DISPONIBLE`; pasivo como alternativa.
- Colores: rojo potencia, negro GND, naranja 3V3, azul señal analógica, amarillo
  señal digital, verde motor.

### Vista 3 — módulo pedido

Dos tarjetas comparativas:

```text
FOTO RECIBIDA / POSIBLE MX1508       DRV8833 TÍPICO, NO CONFIRMADO
IN1 IN2 IN3 IN4                      AIN1 AIN2 BIN1 BIN2
VCC GND                              VM GND nSLEEP
OUT1 OUT2 OUT3 OUT4                  AOUT1/2 BOUT1/2
```

No mostrar una conexión final hasta seleccionar una identidad.

### Vista 4 — final de feria

- Fuente 5 V/5 A -> fusible -> switch -> distribución estrella.
- Controlador confirmado -> bomba/ventilador.
- ESP32 por una sola ruta positiva y GND común.
- Audio con pines no duplicados.
- Tabla de estados: `YA TIENES`, `MONTAR HOY`, `PRUEBA SEPARADA`, `EN CAMINO`,
  `NO USAR`.

### Formatos

1. HTML interactivo imprimible, responsive y sin dependencias externas.
2. Diagrama ASCII dentro del manual de Obsidian.
3. PDF derivado de la misma fuente, inspeccionado página por página.
4. Tabla CSV/Markdown de cables con número, color, origen, destino y prueba.

## 7. Verificación completa

### Software

- Compilar cada perfil para ESP32-S3 N16R8.
- Pruebas unitarias de reglas, seguridad y parser.
- Pruebas de mapas de pines y exclusión mutua de perfiles.
- HIL debe distinguir `SKIP` de `PASS` y guardar evidencia de puerto/firmware.
- `validate_project.py` debe terminar con código 0.

### Hardware

- Escaneo I2C y bienvenida LCD.
- Lecturas crudas y calibradas de cada sensor.
- Cinco reinicios con salidas apagadas.
- Diez pulsos de cada motor por separado.
- Diez bloqueos de bomba por nivel bajo.
- Diez cortes de bomba por timeout.
- Prueba conjunta de 15 minutos; después una hora vigilada con fuente final.

### Documentación

- Un único mapa de pines por perfil.
- Cero instrucciones vigentes de cinco relés.
- Cero afirmaciones de DRV8833 antes de identificar el módulo.
- Cero GPIO duplicados dentro del mismo perfil.
- Cada pieza del diagrama coincide con inventario o aparece como pendiente.

## 8. Orden recomendado de ejecución

```text
EVIDENCIA FÍSICA
      |
      v
LCD + MAPA UN COSTADO
      |
      v
SENSORES SIN ACTUADORES
      |
      v
UN MOTOR POR VEZ CON S8050
      |
      v
IDENTIFICAR DRIVER PEDIDO
      |
      v
MIGRAR CASA FINAL SIN RELES
      |
      v
JARVIS IR + AUDIO
      |
      v
DIAGRAMA/PDF FINAL + PRUEBA 1 HORA
```

## 9. Decisiones que quedan abiertas

Solo quedan abiertas porque requieren evidencia física:

1. Dirección I2C real y causa del LCD vacío.
2. Serigrafía exacta de los pines ilegibles del ESP32.
3. Corriente de arranque real de bomba y ventilador.
4. E/B/C real de cada S8050.
5. Identidad y tabla de verdad del módulo pedido.
6. Pines definitivos de audio después de liberar el conflicto GPIO16.
7. Restaurar o retirar definitivamente los planos eliminados.

Ninguna de estas dudas autoriza improvisar un cableado. Cada una tiene una fase
de medición antes de convertirse en decisión final.

## 10. Dirección completa del producto

### Concepto de la demostración

PROJECT DOMUS será una maqueta de casa inteligente local que observa el ambiente,
protege sus actuadores y permite control manual mediante un mando infrarrojo. El
nombre de la interfaz es **Jarvis**. Jarvis no es una IA conversacional ni usa
Internet: recibe órdenes cerradas y confiables, ejecuta reglas deterministas y
responde con frases españolas pregrabadas o almacenadas en la flash.

La experiencia final será:

```text
PERSONA pulsa el control
          |
          v
HX1838 recibe el código IR
          |
          v
Dispatcher identifica una de 21 teclas
          |
          v
Seguridad acepta o rechaza la acción
          |
          +---- rechaza ---> LCD explica + Jarvis explica + carga queda OFF
          |
          `---- acepta ----> actuador cambia + LCD confirma + Jarvis responde
```

El mando no se monta durante `ALFA_UN_COSTADO_SIN_IR`; se incorpora en
`FERIA_FINAL`. Esta separación evita que el trabajo de hoy dependa del control,
pero conserva el control como interfaz oficial de la presentación.

### Funciones automáticas

| Situación | Decisión DOMUS | Respuesta visible/audible |
|---|---|---|
| Suelo seco y depósito con agua | riego por tiempo limitado | LCD `REGANDO`; Jarvis confirma inicio |
| Depósito bajo, sensor inválido o timeout | bomba apagada y bloqueada | LCD muestra causa; Jarvis explica que el riego fue detenido |
| Temperatura sobre umbral alto | ventilador encendido | LCD indica ventilación; Jarvis solo habla si la acción fue solicitada o cambió de modo |
| Temperatura bajo umbral bajo | ventilador apagado | estado actualizado sin anuncios repetitivos |
| Oscuridad + horario permitido | LED de cultivo encendidos | LCD indica iluminación suplementaria |
| Luz suficiente o fin del horario | LED de cultivo apagados | estado actualizado |
| Oscuridad + presencia | luz de sala encendida | LCD muestra sala activa |
| Falta de presencia después de retención | luz de sala apagada | transición silenciosa |
| STOP físico | todas las salidas apagadas | LCD `PARO ACTIVO`; ninguna orden puede reactivar |

Las decisiones automáticas usan histéresis para evitar parpadeo o encendidos y
apagados rápidos. Los valores se obtienen por calibración física, nunca se copian
de otra maqueta.

### Modos del sistema

| Modo | Comportamiento |
|---|---|
| `AUTO` | sensores y reglas controlan las cargas |
| `MANUAL` | el control decide; las reglas de seguridad siguen activas |
| `PARO` | todo apagado; requiere liberación física y rearme explícito |
| `SEGURO` | fallo crítico; salidas apagadas hasta diagnóstico y recuperación |
| `SILENCIO` | las órdenes funcionan, pero Jarvis no reproduce audio |
| `DIAGNOSTICO` | LCD/Serial presentan sensores, salidas, calibración y fallos |

### Mapa final de las 21 teclas CAR MP3

Los códigos HEX se aprenderán del mando real. La siguiente tabla define la
**acción**, no el código infrarrojo. Las tramas de repetición se ignoran para
riego, rearme, cambio de modo y apagado general.

| Tecla | Acción final | Respuesta Jarvis propuesta |
|---|---|---|
| `CH-` | activar modo manual | «Modo manual activado.» |
| `CH` | cambiar página del LCD | sin voz; confirmación corta en pantalla |
| `CH+` | activar modo automático | «Modo automático activado.» |
| `Anterior` | alternar luz de sala | «He encendido/apagado la luz de la sala.» |
| `Siguiente` | alternar luz de dormitorio | «He encendido/apagado la luz del dormitorio.» |
| `Play/Pause` | pausar o reanudar respuestas de Jarvis | «Voz reanudada.» al reactivar |
| `VOL-` | bajar volumen | LCD muestra nivel; sin frase larga |
| `VOL+` | subir volumen | LCD muestra nivel; sin frase larga |
| `EQ` | ejecutar diagnóstico | «Diagnóstico completado.» o anunciar el fallo encontrado |
| `0` | apagar todas las cargas | «Todas las cargas han sido apagadas.» |
| `100+` | alternar silencio | «Sonido activado.» al salir de silencio |
| `200+` | solicitar rearme seguro | «Sistema rearmado.» o explicar por qué sigue bloqueado |
| `1` | alternar luz de sala | misma respuesta que `Anterior` |
| `2` | alternar luz de dormitorio | misma respuesta que `Siguiente` |
| `3` | alternar iluminación de cultivo | «Iluminación suplementaria activada/apagada.» |
| `4` | alternar ventilador | «He encendido/apagado la ventilación.» |
| `5` | solicitar riego | «Iniciando riego.» o rechazo con causa concreta |
| `6` | consultar temperatura | «La temperatura aparece en pantalla.» |
| `7` | consultar humedad ambiental | «La humedad aparece en pantalla.» |
| `8` | consultar suelo y depósito | «El estado del suelo y del depósito aparece en pantalla.» |
| `9` | consultar estado completo | «El sistema está funcionando.» o enumerar el fallo prioritario |

### Respuestas seguras de Jarvis

Jarvis nunca afirma que una acción ocurrió antes de recibir confirmación del
núcleo. Las respuestas se generan a partir del resultado real:

```text
Orden: tecla 5 / RIEGO

si STOP activo          -> "No puedo regar: el paro está activo."
si falta calibración    -> "No puedo regar: falta calibrar el sistema."
si nivel insuficiente   -> "No puedo regar: el depósito tiene poca agua."
si bomba bloqueada      -> "El riego necesita un rearme seguro."
si salida no instalada  -> "La bomba todavía no está disponible."
si todo está correcto   -> activar bomba y decir "Iniciando riego."
```

El audio es una salida secundaria. STOP, nivel, timeout y control de motores
siguen funcionando aunque MAX98357A, parlante o reproducción fallen.

### Dirección de la pantalla LCD

El LCD1602 tendrá cuatro páginas rotativas:

1. `INICIO`: temperatura, humedad, AUTO/MANUAL y resumen de salidas.
2. `SENSORES`: suelo, nivel, luz y presencia; sin porcentajes antes de calibrar.
3. `SALIDAS`: riego, sala, dormitorio, ventilación y cultivo.
4. `JARVIS`: última orden, volumen, silencio y último código IR.

Toda acción manual presenta primero una confirmación breve y vuelve después a
la página anterior. El LCD no debe limpiarse continuamente si eso provoca
parpadeo; se actualizan solo los caracteres que cambian o se usa un buffer de
dos filas.

### Dirección de la iluminación de cultivo

Dos LED azules y uno rojo representan una lámpara suplementaria. El discurso
correcto es:

> Cuando la luz natural no es suficiente y estamos dentro del horario
> configurado, DOMUS activa una representación de iluminación suplementaria.

No se llamará luz ultravioleta y no se afirmará que tres LED mantienen una
planta trabajando todo el día. Para una aplicación biológica real se necesitaría
medir PAR/PPFD, fotoperiodo y potencia de una luminaria adecuada.

### Dirección de alimentación final

```text
TOMACORRIENTE
   |
   `-> adaptador cerrado 5 V/5 A
          |
          `-> fusible lento 4 A
                 |
                 `-> switch maestro DC
                        |
                        `-> distribución estrella +5 V/GND
                               |-> controlador de motores
                               |-> ESP32 por una única ruta positiva
                               |-> MAX98357A
                               `-> LED/cargas auxiliares
```

El 120 V permanece fuera de la maqueta. El botón STOP es lógico y el switch
maestro corta físicamente la alimentación de baja tensión.

### Alcance final comprometido

Debe funcionar en la feria:

- LCD y cinco mediciones: temperatura, humedad ambiental, suelo, nivel y luz;
- presencia mediante PIR;
- luces de sala y dormitorio;
- representación de luz de cultivo;
- bomba con nivel mínimo, timeout y rearme;
- ventilador automático y manual;
- STOP físico y switch maestro;
- control IR de 21 teclas;
- Jarvis con confirmaciones españolas;
- funcionamiento local sin nube.

Extras que no pueden bloquear la entrega: RFID, servo, WS2812, keypad, joystick,
matriz, displays, HC-SR04, MPU6050, reconocimiento de voz, batería y solar.

### Guion operativo de la demo

```text
1. Encender: todas las cargas permanecen OFF.
2. LCD muestra PROJECT DOMUS y luego sensores.
3. Mostrar LDR: cubrirlo y explicar el horario de cultivo.
4. Pulsar 1: Jarvis enciende y confirma la luz de sala.
5. Pulsar 4: activa y confirma ventilación.
6. Con depósito lleno, pulsar 5: riego corto y confirmación.
7. Simular nivel bajo: repetir 5 y demostrar rechazo seguro.
8. Pulsar 9: mostrar estado completo.
9. Activar STOP: comprobar que ninguna tecla enciende cargas.
10. Liberar STOP, pulsar 200+ y demostrar rearme con salidas todavía OFF.
```

La demostración debe durar entre dos y cuatro minutos y conservar una variante
manual sin audio si el ambiente impide escuchar el parlante.
