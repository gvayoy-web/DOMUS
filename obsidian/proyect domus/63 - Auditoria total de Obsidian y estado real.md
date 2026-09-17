---
estado: autoridad_documental
fecha: 2026-09-16
alcance: toda_la_boveda
---

# Auditoría total de Obsidian y estado real

Esta nota clasifica las notas Markdown históricas que existían antes de esta
auditoría y enlaza la evidencia creada después.
Si otra nota contradice esta clasificación, gana esta nota. El código es la
autoridad del comportamiento y el SVG vigente es la autoridad del cableado.
La evidencia física más nueva está en
[[64 - Sesion fisica COM9 LCD IR sensores y bomba]] y prevalece sobre estados
anteriores que digan “no ejecutado”.
La autoridad del audio futuro es
[[65 - Arquitectura de audios Jarvis con DFPlayer]].

## Hecho

- `casa_inteligente_v4` concentra sensores, LCD, automatización, IR, seguridad
  y actuadores.
- `domus_esqueleto` compila literalmente ese producto con el perfil del banco:
  sensores, LCD, IR, luces y una bomba mediante el único S8050.
- El diagnóstico independiente permite escaneo I2C, lecturas crudas, códigos IR
  y captura de calibración sin activar salidas.
- DHT11, suelo, nivel, LDR y PIR tienen lectura, validación y presentación.
- Riego, ventilación y luces tienen automatización, histéresis y prioridad
  manual; PARO, nivel bajo, timeout, rearme y modo seguro protegen las cargas.
- El LCD tiene vistas de resumen, clima, cultivo, salidas y sistema, errores
  prioritarios y actualización diferencial.
- IR exige aprendizaje real: 21 teclas persistentes, sin duplicados y sin
  ejecutar valores de ejemplo no aprendidos.
- IA, TinyML, INMP441, ESP-SR y PicoTTS fueron retirados del producto. Jarvis es
  la interacción por IR y sus respuestas fijas de texto.
- Las pruebas automatizadas cubren contratos, simulación, lógica nativa,
  perfiles y compilación. Lo que necesita hardware se informa como `SKIP`.

## Falta porque requiere hardware

| Pendiente físico | Evidencia que debe anotarse |
|---|---|
| LCD1602 | PASS físico en `0x27`: estable, legible y sin parpadeos a 50 kHz |
| DHT11 | NaN; protección de tres fallos cargada y 56 s sin reinicios; reparar cableado |
| Suelo, nivel y LDR | seco/húmedo, vacío/lleno, oscuro/claro y polaridad |
| PIR | alimentación usada, OUT seguro y retención real |
| Mando IR | 21 códigos capturados, protocolo 7/dirección 0; falta aprendizaje supervisado |
| S8050 + bomba | un pulso GPIO4 no movió la bomba; revisar etapa y luego hacer diez pulsos |
| DRV8833 | llegada, rotulado/pinout y prueba de bomba y ventilador |
| Fuente, fusible y capacitores | llegada y montaje; mediciones siguen `SKIP por decisión del dueño` |
| Baquelita | distribución definitiva después de aprobar el banco |
| DFPlayer + microSD + parlante | validar tarjeta, UART, BUSY, volumen y cuatro pistas |
| MAX98306 | ampliación analógica opcional; no decodifica MP3 por sí solo |
| HIL | ejecución vigilada del firmware en la placa real |

No son defectos ocultos del código y no se convierten en PASS por simulación.

## Ideas descartadas o fuera de alcance

- Reconocimiento de voz, IA/TinyML, entrenamiento, INMP441 y PicoTTS.
- Nube obligatoria, Wi-Fi como dependencia, batería de 9 V y solar funcional.
- Relés múltiples y el mapa antiguo GPIO1/GPIO2/GPIO21.
- Dos motores simultáneos con dos S8050 en el banco actual.
- S8550 como reemplazo directo del S8050.
- MAX98357A/I2S: la compra informada es MAX98306 analógico.
- Declarar calibraciones, códigos IR, dirección LCD o HIL aprobados sin hardware.

## Clasificación completa

| Grupo | Notas | Uso permitido |
|---|---|---|
| Entrada y autoridad | `Bienvenido`, `00`, `63`, `64`, `65` | Estado y arquitectura actual |
| Operación vigente | `49`, `59`, `60`, `61`, `62` | Banco, S8050, software y evidencia |
| Bitácora aplicada | `50–57` | Saber qué cambió; no cablear desde ellas |
| Historia fundacional | `01–13` | Inventario, ideas y planes originales |
| Historia IA/voz | `14`, `23–26`, `30`; secciones de `06`, `20`, `40` | Explicar la idea retirada; no implementar |
| Planes/pruebas antiguos | `15–22`, `27–39`, `46–48` | Trazabilidad; mapas y perfiles superados |
| Compras antiguas | `03–10`, `36`, `40–45` | Comparar historia; no comprar ni cablear |
| Corte anterior | `58` | Estado previo, superado por esta auditoría |

Una nota puede aparecer en dos grupos porque contiene decisiones de distintas
clases. Una cita explícita desde una nota vigente rescata sólo el dato citado,
no vuelve vigente toda la nota antigua.

## Orden de lectura

1. [[00 - Inicio]].
2. [[64 - Sesion fisica COM9 LCD IR sensores y bomba]].
3. [[65 - Arquitectura de audios Jarvis con DFPlayer]].
4. Esta auditoría.
5. [[61 - Esqueleto literal y diagnostico IR calibracion]].
6. [[59 - Firmware unico y perfil banco S8050 IR]].
7. `visualizaciones/domus-banco-final-s8050-ir.svg`.
8. [[60 - Orden Git y pruebas multientorno]].
9. [[62 - Cierre total de software no fisico]].

## Regla de mantenimiento

Toda nota nueva debe declarar estado, fecha y rol: autoridad, operación,
bitácora, prueba o historia. Una nota nueva no revive una arquitectura antigua;
para cambiar autoridad debe actualizar `00` y esta matriz explícitamente.
