---
fecha: 2026-09-06
estado: software_compilado_banco_pendiente
fuente_estado: ../../ESTADO_ACTUAL.md
---

# Base modular funcional y plan de banco

> Dependencias de Arduino IDE y solución de `DHT.h` en
> [[35 - Preparacion Arduino IDE y revision documental]].

La ruta recomendada para probar las piezas confirmadas es
`firmware/domus_esqueleto`. Usa un S8050 para la bomba de 3-6 V; el rele queda
reservado y GPIO5-8 no tienen etapa fisica. Esta nota sustituye la descripcion limitada de las
notas 31 y 32, pero no declara validacion fisica.

La ronda inmediata B01-B05 se realiza con
`HABILITAR_BOMBA=false`, GPIO4-8 sin actuadores y solo las piezas ya
compradas. La hoja operativa es [[37 - Ronda de pruebas sin compras]]. B06-B10
se difieren hasta disponer de la etapa correspondiente.

## Capacidades integradas

- Sensores ADC de suelo, nivel y luz con promedio y deteccion de rieles.
- PIR con retencion de presencia; DHT11/22 seleccionable.
- LCD1602 detectado en 0x27 o 0x3F con bus acotado.
- Bomba, sala, cuarto, ventilador e invernadero con propiedad AUTO/manual.
- Riego, ventilacion y luces automaticas con histeresis.
- Calibracion persistente en NVS con version, rangos y checksum.
- PARO prioritario, timeout y bloqueo de bomba, watchdog, heap y modo seguro.
- Protocolo por lineas, limite de ON, diagnostico y recuperacion sin encendido.

Compilacion local N16R8/OPI con advertencias: PASS. Programa 373694 bytes;
globales 24388 bytes.
Las salidas siguen en `false`; compilar no prueba electricidad.

Carga física inicial del 7 de septiembre: PASS en COM9 mediante CH343.
`esptool` confirmó ESP32-S3 revisión 0.2 y PSRAM de 8 MB; el hash escrito fue
verificado. El diagnóstico devolvió `SALIDAS=0`, `OUT=00000`, `PARO=0` y
`SEGURO=0`. Esto aprueba carga y arranque individual, no los cinco reinicios de
B02 ni ningún sensor desconectado.

## Secuencia obligatoria

| ID | Prueba | Aceptacion | Estado |
|---|---|---|---|
| B01 | Inspeccion de placa y GPIO | N16R8 confirmado; 2, 9, 13 y alimentaciones identificados | PARCIAL: chip/PSRAM/USB confirmados |
| B02 | Arranque sin cargas | Cinco reinicios, ningun GPIO pulsa activo | PARCIAL: 1 arranque y OUT=00000 |
| B03 | LCD y DHT | Direccion/modelo confirmados, 20 lecturas validas | PENDIENTE |
| B04 | ADC y PIR | Lecturas responden al estimulo y no quedan en rieles | PENDIENTE |
| B05 | Calibracion | Valores reales guardados, reinicio conserva checksum | PENDIENTE |
| B06 | Fuente y bomba directa, sin ESP32 | Rail medido; bomba gira a 3-5 V | PENDIENTE |
| B07 | Driver S8050 + bomba | Corriente, temperatura, diodo y FIS=10000 aprobados | PENDIENTE |
| B08 | Automatizacion de bomba | Nivel bajo y 10 s cortan; rearme no enciende | PENDIENTE |
| B09 | PARO y fallos | PARO durante cada carga; sensores retirados fallan seguro | PENDIENTE |
| B10 | Duracion | 24 h o 1000 ciclos sin reset ni crecimiento sostenido | PENDIENTE |

## Regla de habilitacion

`HABILITAR_BOMBA=true` se permite unicamente despues de identificar patas,
medir el driver y completar B06 con la bomba directa. B07-B08 se hacen una carga a la vez y con fuente
regulada. Si un resultado falla, volver a `false`, registrar medicion y corregir
la etapa; no bajar protecciones para lograr una demostracion.

Completar B01 y B02 no obliga a habilitar la bomba. El cambio exacto esta en
`domus_config.h`: `constexpr bool HABILITAR_BOMBA = false;` pasa a `true`.
GPIO5-8 continuan en `false` dentro de `SALIDA_FISICA_HABILITADA[]`.

## Relacion con Jarvis

La voz futura debe entregar comandos al mismo despachador. No controla GPIO de
forma directa. Se mantiene deshabilitada hasta completar datos, audio e
inferencia de [[25 - Plan ejecutable Jarvis offline fiable y entrenado]].
