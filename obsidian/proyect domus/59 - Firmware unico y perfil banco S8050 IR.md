---
proyecto: PROJECT DOMUS
tipo: decision_arquitectura
actualizado: 2026-09-16
estado: vigente
autoridad: firmware_y_banco_actual
---

# Firmware único y perfil de banco S8050 + IR

> [!IMPORTANT]
> Decisión vigente: `firmware/casa_inteligente_v4/` es la única base funcional
> de DOMUS. El banco no desarrolla otra lógica: ejecuta esa misma base mediante
> el perfil `BANCO_COMPLETO_S8050_IR` (`DOMUS_PERFIL_CASA=3`).

## Motivo

El banco debe probar las mismas reglas que llegarán a la feria: sensores, LCD,
automatización, control manual, propiedad de salidas, PARO, modo seguro,
histéresis, nivel mínimo y timeout. Mantener un segundo firmware completo
permitiría que banco y producto se separaran silenciosamente.

`firmware/domus_esqueleto/` es el envoltorio vigente que selecciona perfil 3 e
incluye literalmente el producto. La implementación antigua y sus pruebas
heredadas viven en `firmware/legacy/domus_esqueleto/`; no autorizan otro mapa.

## Perfil físico vigente

| Función | GPIO | Estado en el banco |
|---|---:|---|
| LDR | 3 | Activo |
| Bomba | 4 | Activa mediante el único S8050 NPN |
| LED sala | 5 | Activo, salida HIGH |
| LED dormitorio | 6 | Activo, salida HIGH |
| Ventilador | 7 | Bloqueado y configurado como entrada |
| LED cultivo | 8 | Activo, salida HIGH |
| PIR | 9 | Activo |
| PARO | 10 | Activo, botón a GND con `INPUT_PULLUP` |
| SILENCIO | 11 | Activo, botón a GND con `INPUT_PULLUP` |
| Receptor IR | 12 | Activo; `OUT/S` a GPIO12 |
| LCD SCL | 13 | Activo |
| DHT11 DATA | 14 | Activo |
| Suelo AO | 15 | Activo |
| Nivel S | 16 | Activo |
| LCD SDA | 17 | Activo |
| MODO LCD | 18 | Activo, botón a GND con `INPUT_PULLUP` |

El diagrama cableable de este perfil es
`visualizaciones/domus-banco-final-s8050-ir.svg`.

## Bomba con un solo transistor

- GPIO4 → resistencia 1 kΩ → base del S8050.
- Base → resistencia pull-down 10 kΩ → GND.
- Emisor → GND común.
- Colector → negativo de la minibomba.
- TP4056 `OUT+` → positivo de la minibomba.
- TP4056 `OUT-` → GND común y GND del ESP32.
- 1N4007 en paralelo: raya plateada hacia `OUT+`; lado sin raya hacia colector.
- El ventilador permanece desconectado. El S8550 continúa en reserva.

El TP4056 se usa únicamente para esta prueba aceptada por el propietario; no
se redefine como fuente final regulada del proyecto.

## Infrarrojo

El receptor IR se conserva y usa GPIO12. La tabla CAR MP3 tiene 21 posiciones,
se aprende desde Serial y se guarda en NVS:

```text
IR_GRABAR_0
IR_GRABAR_1
...
IR_GRABAR_20
IR_LISTA
IR_LEER
IR_BORRAR
```

Las repeticiones sostenidas no vuelven a disparar acciones críticas. Una tecla
desconocida o todavía no aprendida solo genera `NACK` y no modifica salidas.
El firmware conserva una máscara NVS de posiciones aprendidas, rechaza códigos
duplicados y muestra `APRENDIDAS=n/21`. `IR_BORRAR` deja todo el mando sin
autoridad hasta volver a grabarlo. PARO físico conserva prioridad sobre IR.

Desde el commit `9bb9684`, cada pulsación recibida se muestra cinco segundos en
el LCD como protocolo/dirección y comando (`IR P7 A00FF` / `CMD 0x0019`). Los
errores ordinarios de sensores no tapan esta vista; PARO y modo seguro sí.

## Funciones disponibles para probar

- Lectura de DHT11, suelo, nivel, LDR y PIR.
- Cinco vistas del LCD, lector temporal de códigos IR y navegación con MODO/IR.
- Luces manuales y automáticas.
- Bomba manual o automática con nivel, histéresis y timeout.
- PARO, rearme, modo seguro, diagnósticos y comandos Serial.
- Aprendizaje y acciones del mando IR.

La bomba comienza en `MANUAL_OFF`: no arranca por una lectura provisional al
energizar. `RIEGO_ON` permite la prueba manual con la bomba sumergida y
`RIEGO_AUTO` entrega después el control a humedad+nivel. El comando `PRUEBA`
genera un bloque copiable con sensores, LCD, dirección I2C, IR, salidas y
diagnóstico.

La vista de cultivo muestra suelo y agua en porcentaje. Agua usa provisionalmente
600 ADC = 0% y 2500 ADC = 100%; esos extremos no son calibración física aprobada.

## Hardware expresamente deshabilitado

- Driver doble DRV8833/MX1508 mientras no haya llegado.
- Ventilador físico.
- Micrófono y reconocimiento de voz.
- microSD.
- Audio y bocinas.

Las bocinas disponibles de 1–2 Ω no se conectan directamente a GPIO, 3V3,
TP4056 ni al S8050 de la bomba. Solo podrán probarse con un amplificador cuya
impedancia mínima admita explícitamente esa carga.

## Evidencia de software

Validación fresca posterior al registro anticolisiones, al comando `PRUEBA` y
al bloqueo de arranque de la bomba:

- compilación ESP32-S3 N16R8: PASS;
- programa: 444885 bytes;
- RAM global: 26388 bytes;
- firmware: 83 PASS, 0 FAIL, 9 SKIP;
- planos: 7 PASS;
- `validate_project.py`: `VALIDACION_OK`.

> [!WARNING]
> La compilación y simulación están verificadas, pero todavía no existe prueba
> HIL en la placa. Ningún PASS de software certifica el cableado físico.

## Relación con documentos anteriores

- [[58 - Estado vigente firmware sensores control y documentos]] queda
  actualizado por esta decisión en firmware, bomba e IR.
- [[47 - Guia visual principiante conexiones alfa]] conserva utilidad para los
  sensores, pero su indicación “GPIO12 reservado” pertenece al perfil antiguo.
- [[49 - Prueba de una carga con un S8050 y TP4056]] continúa vigente para la
  etapa eléctrica de una sola carga.
- [[53 - Definicion formal de firmware final y puertas]] sigue definiendo la
  evidencia necesaria antes de afirmar validación física o estado FINAL.

## Regla de estado

`BANCO_COMPLETO_S8050_IR` significa firmware de producto adaptado al hardware
disponible. No significa que el montaje físico ya fue probado ni que las
compras futuras estén integradas.
