---
fecha: 2026-09-06
estado: software_compilado_banco_pendiente
fuente_estado: ../../ESTADO_ACTUAL.md
---

# Base modular funcional y plan de banco

> Dependencias de Arduino IDE y solución de `DHT.h` en
> [[35 - Preparacion Arduino IDE y revision documental]].

La ruta recomendada para probar las piezas confirmadas es
`firmware/domus_esqueleto`. Esta nota sustituye la descripcion limitada de las
notas 31 y 32, pero no declara validacion fisica.

## Capacidades integradas

- Sensores ADC de suelo, nivel y luz con promedio y deteccion de rieles.
- PIR con retencion de presencia; DHT11/22 seleccionable.
- LCD1602 detectado en 0x27 o 0x3F con bus acotado.
- Bomba, sala, cuarto, ventilador e invernadero con propiedad AUTO/manual.
- Riego, ventilacion y luces automaticas con histeresis.
- Calibracion persistente en NVS con version, rangos y checksum.
- PARO prioritario, timeout y bloqueo de bomba, watchdog, heap y modo seguro.
- Protocolo por lineas, limite de ON, diagnostico y recuperacion sin encendido.

Compilacion local N16R8/OPI con advertencias: PASS. Programa 373286 bytes;
globales 24388 bytes.
Las salidas siguen en `false`; compilar no prueba electricidad.

## Secuencia obligatoria

| ID | Prueba | Aceptacion | Estado |
|---|---|---|---|
| B01 | Inspeccion de placa y GPIO | 2, 9, 13 y alimentaciones identificados | PENDIENTE |
| B02 | Arranque sin cargas | Cinco reinicios, ningun GPIO pulsa activo | PENDIENTE |
| B03 | LCD y DHT | Direccion/modelo confirmados, 20 lecturas validas | PENDIENTE |
| B04 | ADC y PIR | Lecturas responden al estimulo y no quedan en rieles | PENDIENTE |
| B05 | Calibracion | Valores reales guardados, reinicio conserva checksum | PENDIENTE |
| B06 | LED uno por uno | ON/OFF/AUTO y boton sin inversion | PENDIENTE |
| B07 | Driver ventilador | Corriente, temperatura y flyback aprobados | PENDIENTE |
| B08 | Rele y bomba | Nivel bajo y 10 s cortan; rearme no enciende | PENDIENTE |
| B09 | PARO y fallos | PARO durante cada carga; sensores retirados fallan seguro | PENDIENTE |
| B10 | Duracion | 24 h o 1000 ciclos sin reset ni crecimiento sostenido | PENDIENTE |

## Regla de habilitacion

`SALIDAS_HABILITADAS=true` se permite unicamente despues de B01 y B02, primero
sin bomba/motor conectados. B06-B08 se hacen una carga a la vez y con fuente
regulada. Si un resultado falla, volver a `false`, registrar medicion y corregir
la etapa; no bajar protecciones para lograr una demostracion.

## Relacion con Jarvis

La voz futura debe entregar comandos al mismo despachador. No controla GPIO de
forma directa. Se mantiene deshabilitada hasta completar datos, audio e
inferencia de [[25 - Plan ejecutable Jarvis offline fiable y entrenado]].
