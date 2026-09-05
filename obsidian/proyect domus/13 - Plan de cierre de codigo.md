---
proyecto: PROJECT DOMUS
tipo: plan-cierre
actualizado: 2026-09-04
estado_codigo: nucleo_compilado_voz_y_banco_pendientes
---

# Plan de cierre de código

> [!IMPORTANT] ESTADO ACTUAL
> El núcleo doméstico compila y tiene pruebas automatizadas, pero la validación
> física está pendiente. Jarvis requiere datos, entrenamiento e integración de
> software: no es solo un bloqueo de hardware. Véase
> [[23 - Cierre de robustez y entrenamiento pendiente]] para el estado vigente.

## Definición de terminado

El software base se considera terminado cuando las cinco cargas pueden operar
sin red, todas las fuentes de órdenes atraviesan el mismo despachador, una
lectura inválida conduce a un estado seguro, la bomba tiene bloqueos
independientes, el sistema sobrevive a entradas abusivas y las pruebas se
ejecutan antes de compilar.

“Terminado en software” no significa “validado físicamente”. Los pines,
umbrales ADC, consumo, caudal, ruido y precisión solo pueden cerrarse con el
hardware real.

## Estado por frente

| Frente | Estado | Evidencia / salida |
|---|---|---|
| Cinco relés y arranque apagado | TERMINADO | Firmware y contratos automatizados. |
| Riego seguro | TERMINADO | Nivel bajo, sensor inválido, histéresis 35/45 % y límite de 120 s. |
| Ventilación | TERMINADO | DHT, modo manual y histéresis 28/26 °C. |
| Iluminación | TERMINADO | LDR 25/40 %, PIR con retención y modo manual persistente. |
| Emergencia y MIC OFF | TERMINADO | Paro prioritario, rearme explícito y respaldo físico/Serial. |
| Resiliencia | TERMINADO | Watchdog, modo seguro, memoria, reinicios y límite de órdenes. |
| Simulador | TERMINADO | Replica estados, límites, fallos, emergencia y recuperación. |
| Pruebas/CI | AMPLIADAS | 20 pruebas de comportamiento + 22 contratos y pruebas C++ integradas. |
| INMP441 y audio I2S | PREPARADO | PoC separados; requieren módulos físicos. |
| Jarvis español | PENDIENTE | Dataset; entrenamiento; frontend e intérprete en ESP32; captura y salida integrada. |
| Pinout y calibración | BLOQUEADO POR HARDWARE | Requiere inspección y mediciones de la placa. |
| Solar/batería | FASE POSTERIOR | Requiere medir consumo del montaje completo. |

## Secuencia restante con hardware

1. Confirmar la serigrafía y sustituir únicamente los GPIO provisionales que
   no estén expuestos.
2. Cargar el firmware con voz y microSD deshabilitadas.
3. Ejecutar cinco arranques, probar cada relé y verificar que no hay pulsos.
4. Calibrar suelo, nivel de agua, LDR, DHT y PIR; guardar resultados medidos.
5. Probar bomba con bandeja antifugas y confirmar los dos cortes independientes.
6. Ejecutar tres demostraciones de 30 minutos y revisar `DIAGNOSTICO`.
7. Validar INMP441 y MAX98357A por separado.
8. Grabar dataset, entrenar, cuantizar y medir Jarvis antes de habilitarlo.
9. Medir consumo y dimensionar batería/solar al final.

## Criterio para aceptar Jarvis

- El modelo tiene checksum y versión conocidos.
- Confianza mínima 0.75 y clase desconocida explícita.
- Cero falsas activaciones durante una hora.
- La inferencia no escribe GPIO; solo crea una orden para el despachador.
- MIC OFF, emergencia y modo seguro prevalecen siempre.
- Al fallar la voz, botones, automatización, LCD y Serial siguen operativos.

## Fuera de alcance

BLE, aplicación Kotlin, MQTT, nube, conversación libre y reproducción directa
de Spotify no forman parte del producto offline decidido. No se cuentan como
código faltante.

## Relaciones

- [[09 - Plan de montaje y pruebas]]
- [[12 - Bitacora de implementacion]]
- [[14 - Protocolo anti-colapso IA y ESP32]]
- [[15 - Plan de optimizacion de codigo]]
- [[16 - Plan de testeo antes de construccion]]
- [[17 - Diagramas generales de conexiones]]
- [[18 - Manual maestro de conexiones pin por pin]]
- [[19 - Plan de testeo despues de construccion]]
- [[06 - Jarvis audio pantalla y microSD]]
