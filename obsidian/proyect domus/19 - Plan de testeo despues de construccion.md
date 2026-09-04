---
proyecto: PROJECT DOMUS
tipo: plan-pruebas-postconstruccion
actualizado: 2026-09-04
estado: plan_terminado_pendiente_hardware
---

# Plan de testeo después de construcción

> [!IMPORTANT]
> El plan está terminado; su ejecución queda pendiente hasta que exista el
> montaje físico. No se declara la casa validada solo porque el código compila.

## Registro obligatorio

| ID | Fecha | Firmware/SHA | Tensión 5 V mín./máx. | Corriente pico | Resultado | Evidencia/corrección |
|---|---|---|---:|---:|---|---|
| P00–P09 |  |  |  |  | PENDIENTE |  |

## P00 — inspección del montaje apagado

- [ ] Comparar cada cable con [[18 - Manual maestro de conexiones pin por pin]].
- [ ] Confirmar fusible, polaridades, diodos, capacitores y conectores.
- [ ] Buscar cobre expuesto, tornillos flojos y cables pellizcados.
- [ ] Confirmar separación física entre agua y electrónica.

**PASS:** dos revisiones visuales sin discrepancias y sin corto 5 V–GND.

## P01 — energización por etapas

1. Energizar barra sin ESP32 ni cargas.
2. Energizar ESP32 solo.
3. Añadir sensores/LCD.
4. Añadir relés sin cargas.
5. Añadir una carga por vez.

En cada etapa medir 5 V, 3.3 V, corriente y temperatura táctil/medida de cables
y módulos. Si cae la tensión, aparece olor, calor o reset, cortar y volver al
último estado seguro.

**PASS:** ninguna etapa produce corto, calentamiento o reset.

## P02 — arranque y recuperación

- [ ] Ejecutar diez arranques desde frío.
- [ ] Confirmar que las cinco cargas permanecen apagadas durante el arranque.
- [ ] Probar `ESTADO`, `DIAGNOSTICO`, `PARO`, `REARMAR` y `RECUPERAR`.
- [ ] Desconectar y restaurar un sensor para observar fallo seguro.

**PASS:** 10/10 arranques, cero pulsos peligrosos y recuperación explícita.

## P03 — sensores instalados

| Sensor | Prueba mínima | PASS |
|---|---|---|
| DHT | comparar con referencia en dos condiciones | lectura plausible y estable |
| suelo | seco, húmedo y desconectado | calibración monotónica y fallo seguro |
| nivel | vacío, medio, lleno y desconectado | bloqueo correcto de bomba |
| LDR | oscuridad y luz intensa | histéresis sin oscilación |
| PIR | presencia, ausencia y retención | no parpadea la luz por ruido |

## P04 — cargas instaladas

Activar por separado bomba, sala, dormitorio, ventilador e invernadero; luego
la combinación de mayor consumo. Registrar caída de `5V_BUS`, corriente y
ruido/reset. La bomba nunca funciona en seco.

**PASS:** cinco canales correctos, sin reset y sin cables/módulos calientes.

## P05 — pruebas destructivas simuladas de forma segura

- Nivel bajo mientras la bomba está encendida: debe apagarse.
- Sensor de suelo inválido en AUTO: no debe iniciar riego.
- 120 s de bomba: debe cortar y exigir rearme.
- Ráfaga de comandos: `PARO` mantiene prioridad.
- MIC OFF: voz rechazada, botones/Serial siguen disponibles.
- microSD/Jarvis ausentes: el núcleo continúa operativo.

**PASS:** toda falla lleva a apagado o degradación, nunca a activación insegura.

## P06 — demostración completa

Ejecutar tres ciclos consecutivos: entrada de persona, cambio de luz,
ventilación, riego bloqueado/permitido, control manual y paro. Una persona que
no construyó el sistema debe poder seguir el guion sin abrir el gabinete.

**PASS:** 3/3 demostraciones sin reinicio, atasco ni intervención técnica.

## P07 — estabilidad prolongada

- Ejecutar 60 minutos con registro detallado.
- Después ejecutar ocho horas con la carga real y eventos periódicos.
- Registrar `MEM_LIBRE`, `MEM_MIN`, errores, watchdog y reinicios.

**PASS:** cero resets, sin caída sostenida de memoria y sin calentamiento.

## P08 — agua, vibración y transporte

- Comprobar bandeja, depósito cerrado y bucles antigoteo.
- Mover la maqueta apagada como se transportará a la feria.
- Repetir P00, P01 y cinco arranques después del transporte.

**PASS:** ningún conector se afloja, no hay fuga y 5/5 arranques correctos.

## P09 — aceptación final

La construcción queda **ACEPTADA** solo si P00–P08 están en PASS, el firmware y
su SHA están registrados, los GPIO provisionales fueron confirmados y no queda
ningún empalme temporal en potencia, agua o PARO.

Si una prueba falla, anotar causa, corrección y repetición. No ocultar el fallo
marcándolo como “no aplica” sin justificarlo.

## Relaciones

- [[13 - Plan de cierre de codigo]]
- [[16 - Plan de testeo antes de construccion]]
- [[17 - Diagramas generales de conexiones]]
- [[18 - Manual maestro de conexiones pin por pin]]
