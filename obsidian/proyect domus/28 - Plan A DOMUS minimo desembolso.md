---
estado: historico_alternativa_no_elegida
fecha: 2026-09-14
---

# Plan A: DOMUS con mínimo desembolso

> [!WARNING]
> Alternativa no elegida. Se conserva para comparar costos; la ejecución
> vigente está en [[29 - Plan B DOMUS ampliable y reutilizable]] y
> [[36 - Configuracion final 1 mas 4 reles y planos v4]].

**Objetivo:** casa funcional con cinco controles y el máximo material existente.
**Arquitectura/tecnología:** ESP32-S3 Arduino, perfil económico existente,
relé de bomba, LEDs individuales y driver ventilador validado.
**Base:** [[27 - Comparador de planes costo y versatilidad]], [[21 - Simplificacion y reduccion de costos]].
**Compatibilidad:** sensores, LCD, controles y protecciones no se eliminan.
**TDD:** no se prescribe ciclo TDD; regresiones antes de aceptar cualquier cambio.
**Verificación:** pruebas del proyecto, compilación del perfil y banco físico.
**Estado:** propuesta, no montaje aprobado. No es Jarvis hablado.

## Material y gasto pendiente

Reutilizar ESP32, LCD/backpack, DHT, suelo, nivel, PIR, LDR + 10 kΩ, bomba/tubo,
relé individual, motor, tres LEDs + tres resistencias 1 kΩ, S8050 + resistencias
de base/pull-down y diodos según nota 21, botones y cables aptos.

Comprar solo lo ausente: fuente apta si la existente no sirve, fusible/soporte,
interruptor dimensionado, distribución, aislamiento, desacoplo y adaptación
I2C si el backpack eleva señales a 5 V. Instrumento de medida prestado o propio.
El presupuesto anterior L520 no incluye todas las incógnitas; no es total cerrado.
No comprar panel/batería/elevador, relé cuádruple, lector SPI ni audio para esta fase.

La etapa S8050 no se aprueba por su nombre. Si no conmuta el motor con margen,
el ahorro del relé queda sin aprobar: cotizar etapa MOSFET apta para lógica
3.3 V o relé compatible. No alimentar el motor desde un GPIO.

## Pasos y archivos responsables

1. En `obsidian/proyect domus/01 - Inventario confirmado.md`, confirmar variante
   DHT, voltaje de motores y marcado del S8050; registrar faltantes reales.
2. En `obsidian/proyect domus/21 - Simplificacion y reduccion de costos.md`,
   usar la tabla GPIO4/5/6/7/8, sin inventar otro mazo. Mantener nota 18 para sensores.
3. Con alimentación desconectada, preparar conectores etiquetados y revisar
   E/B/C, polaridad LED/diodos y niveles I2C. No usar MB102 como fuente general.
4. Compilar el perfil ya existente; no duplicar el sketch ni cambiar el
   valor predeterminado para usuarios del cableado original:

```powershell
.local-tools/arduino-cli/bin/arduino-cli.exe compile --config-file .arduino-local/arduino-cli.yaml --fqbn esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB,CPUFreq=240,LoopCore=1 --build-property build.extra_flags=-DDOMUS_SALIDAS_ECONOMICAS=1 --output-dir build/plan_a firmware/casa_inteligente_v4
.venv-ia/Scripts/python.exe tools/validate_project.py
```

5. Comprobar arranque/reset sin pulsos de carga, cinco ON/OFF, PARO y rearme,
   bloqueo por nivel inválido, timeout y ausencia de anulación del OFF manual.
6. Medir voltaje de bus y corriente/temperatura del motor en arranque y régimen.
   Detener si aparece reinicio, calentamiento anormal o falta de margen.
7. Guardar resultados en nota 19, con binario/perfil y mediciones; solo entonces
   trasladar de protoboard a montaje aislado y protegido de agua.

## Qué conserva y qué limita

Conserva automatización doméstica, no intensidad de tiras ni múltiples LEDs por
GPIO. No ofrece voz, registro SD o autonomía. Se amplía cambiando la etapa de
salida validada, no borrando las cinco funciones del firmware.

No se retira código opcional en esta fase. Si falla el driver, no rebajar el
criterio de prueba: mantener la carga desconectada hasta escoger etapa apta.
