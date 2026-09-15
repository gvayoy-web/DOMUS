---
proyecto: PROJECT DOMUS
tipo: seguridad-operativa
actualizado: 2026-09-03
estado: historico_idea_ia_retirada
---

# Protocolo anti-colapso de IA y ESP32

> [!DANGER]
> HISTÓRICO. DOMUS ya no usa IA, TinyML, micrófono ni reconocimiento de voz.
> Sólo siguen vigentes las reglas generales presentes en el firmware actual.

## Objetivo

Una función opcional nunca debe detener las funciones domésticas. Si memoria,
sensores, entrada Serial o voz se comportan mal, el ESP32 degrada servicios,
apaga cargas y conserva diagnóstico en vez de reiniciarse indefinidamente.

## Estados

| Estado | Entradas permitidas | Salidas |
|---|---|---|
| NORMAL | Física, Serial, automatización y voz validada | Según AUTO/MANUAL. |
| EMERGENCIA | `ESTADO`, `DIAGNOSTICO`, `REARMAR` | Todas apagadas; encendidos bloqueados. |
| MODO SEGURO | `ESTADO`, `DIAGNOSTICO`, `PARO`, `RECUPERAR` | Todas apagadas; automatización y voz suspendidas. |
| VOZ DESHABILITADA | Física, Serial y automatización | Casa completa sin reconocimiento ni audio. |

## Barreras implementadas

1. Arranque con todos los relés apagados.
2. Watchdog de ocho segundos para un bloqueo duro del ciclo principal.
3. Entrada a modo seguro con menos de 32 KiB de heap libre.
4. Entrada a modo seguro después de tres reinicios por panic/watchdog.
5. Limpieza del contador tras 60 segundos estables, usando RTC RAM sin
   escribir repetidamente en flash.
6. Máximo de 12 comandos por segundo. `PARO` no se limita.
7. Búfer Serial acotado y reservado una sola vez.
8. Registro circular de errores; no crece sin límite.
9. Riego automático se corta si falla humedad o nivel de agua.
10. Ventilación automática se corta si falla DHT.
11. Luces automáticas se apagan si falla LDR.
12. Bomba se corta a los 120 segundos aunque falle el sensor.
13. Voz y microSD permanecen compiladas como opcionales y deshabilitadas hasta
    validar hardware/modelos.

## Recuperación operativa

1. Enviar `DIAGNOSTICO` y anotar `MOTIVO_SEGURO`, `MEM_LIBRE`, `MEM_MIN` y
   `REINICIOS_CRITICOS`.
2. Corregir alimentación, cableado, sensor o fuente de órdenes.
3. Soltar físicamente el paro y enviar `REARMAR` si había emergencia.
4. Enviar `RECUPERAR`. Se rechaza si quedan menos de 64 KiB libres.
5. Confirmar `ESTADO;...;MODO_SEGURO=OFF`.
6. Devolver cada carga a `*_AUTO` o encenderla manualmente. La recuperación no
   reactiva nada por sí sola.

## Contrato obligatorio para la IA de voz

- Modelo int8 pequeño, versionado y con checksum.
- Vocabulario cerrado; desconocido/ruido/silencio son resultados válidos.
- Confianza inferior a 0.75 no cambia ningún estado.
- Una detección produce como máximo una orden.
- Ventana de escucha de cinco segundos y anti-rebote de dos segundos.
- Half-duplex: micrófono detenido mientras habla el altavoz.
- Tres fallos o tiempos excesivos consecutivos deben suspender únicamente la
  voz; nunca el control físico, sensores o seguridad.
- La IA no accede directamente a GPIO, archivos ni credenciales. Entrega una
  intención al despachador común.
- No hay descarga de modelos ni dependencia de Internet durante la demo.

## Pruebas antes de habilitar voz

- 90 % de wake word a 50 cm en silencio.
- 80 % de intenciones a un metro con ruido moderado.
- Cero falsas activaciones durante una hora.
- Prueba de eco con altavoz y MIC OFF.
- Prueba de modelo ausente/corrupto: la casa debe iniciar con voz deshabilitada.
- Tres demostraciones completas consecutivas sin reset, bloqueo ni crecimiento
  sostenido de `MEM_MIN`.

## Regla final

No se activa `JARVIS_LOCAL_HABILITADO` por fecha o para una demostración. Solo
se activa después de adjuntar resultados medidos a [[12 - Bitacora de implementacion]].

