---
fecha: 2026-09-06
estado: software_verificado_hardware_pendiente
---

# Cierre de software y matriz de verificación

Esta nota es la evidencia vigente del cierre ejecutable. Sustituye conteos y
tamaños publicados en notas históricas; no convierte una compilación en una
prueba eléctrica.

Placa declarada como “N8R16”: se interpreta como 8 MB RAM y 16 MB de flash.
El código oficial de Espressif para esa capacidad es `N16R8`; por eso la
configuración permanece en 16 MB con PSRAM OPI.

## Resultado local

| Objetivo | Programa | Globales | Resultado |
|---|---:|---:|---|
| Firmware principal N16R8 original | 415,250 B | 25,092 B | PASS |
| Firmware principal N16R8 económico | 415,250 B | 25,092 B | PASS |
| Firmware principal N16R8 con microSD | 456,182 B | 25,228 B | PASS |
| Firmware principal 4 MB sin PSRAM | 410,056 B | 24,616 B | PASS |
| Firmware principal 8 MB QSPI | 412,942 B | 24,692 B | PASS |
| `domus_esqueleto` N16R8 | 373,286 B | 24,388 B | PASS |
| `domus_selftest` N16R8 | 417,913 B | 24,556 B | PASS |
| `domus_anim` N16R8 | 382,598 B | 24,340 B | PASS |

Herramientas: Arduino CLI 1.5.1, Arduino-ESP32 3.3.10 y advertencias completas.
Las advertencias residuales pertenecen a LiquidCrystal I2C y al core ESP32.

El validador consolidado reporta 50 PASS y 5 SKIP: los SKIP son las ejecuciones
nativas C++ que requieren un compilador de escritorio y se ejecutan en CI.
La suite de IA reporta 16 PASS. El workflow compila los cinco perfiles del
principal y los tres sketches auxiliares para impedir regresiones.

## Campaña semirreal

El gemelo digital ejecutó 10,000 pasos deterministas y 40,027 comprobaciones de
invariantes. Inyectó 40 PARO, 22 entradas en modo seguro, 28 reinicios y 134
fallos de sensor. Resultado: PASS, con registro de eventos limitado a 250.

Esta campaña aproxima cambios ambientales y fallos lógicos, pero no reproduce
ruido ADC, rebote eléctrico, consumo, caídas de 5 V, calor ni comportamiento
real del relé/motor. Se reproduce con `python scripts/run_semireal_campaign.py`.

## Qué quedó funcional en el esqueleto

- Lectura DHT, PIR y ADC de suelo, nivel y luz.
- LCD I2C, botón manual, PARO enclavado y cinco salidas lógicas.
- Automatizaciones con histéresis y propiedad manual de cada salida.
- Calibración persistente con versión y checksum; datos inválidos bloquean la
  automatización afectada.
- Timeout y bloqueo de bomba, vigilancia de heap/watchdog y modo seguro.
- Protocolo serie acotado con ACK/NACK, recuperación y pruebas de contrato.
- `SALIDAS_HABILITADAS=false` por defecto para que una carga no se active antes
  de comprobar el montaje.

## Frontera que exige hardware

El software está cerrado hasta el banco. Falta identificar físicamente la placa,
confirmar GPIO 2/9/13, polaridades y tensión de cada etapa; calibrar los tres ADC;
medir fuente, bomba y motor; probar PARO/rearme; ejecutar cinco arranques y el
ensayo prolongado. Jarvis hablado requiere micrófono/corpus/modelo y la ruta de
audio elegida. Batería y solar quedan fuera del circuito y sólo serán estética.
La fuente operativa será una fuente común regulada de 5 V; todavía deben medirse
su corriente disponible y caída de tensión con cargas reales.

## Dependencia DHT detectada el 7 de septiembre

Una compilación desde Arduino IDE informó `DHT.h: No such file or directory`.
El firmware conserva el DHT real y no fabrica datos: se deben instalar `DHT
sensor library` de Adafruit y `Adafruit Unified Sensor` en el sketchbook activo.
La guía completa está en [[35 - Preparacion Arduino IDE y revision documental]].

La secuencia segura está en [[33 - Base modular funcional y plan de banco]].
No habilitar salidas ni declarar terminado el sistema físico sin completar esa
matriz con mediciones reales.
