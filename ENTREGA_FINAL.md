# PROJECT DOMUS — entrega técnica consolidada

Actualizado: 7 de septiembre de 2026.

Estado: software doméstico compilado y sometido a campaña semirreal; pruebas
físicas y Jarvis integrado pendientes. Ver las notas 34 y 35 de Obsidian.
La preparación del entrenamiento no equivale a tener una IA entrenada.

## Código terminado

- Firmware principal: `firmware/casa_inteligente_v4/casa_inteligente_v4.ino`.
- Cinco cargas, automatización, modos manuales, sensores y LCD.
- Paro de emergencia, MIC OFF, límite de bomba y fallos seguros.
- Supervisor anti-colapso, watchdog, límite de comandos y recuperación explícita.
- Contrato microSD y ramas opcionales de voz aisladas por banderas.
- Contratos de compilación para GPIO únicos y umbrales coherentes.

Jarvis hablado permanece deshabilitado porque no existen todavía el micrófono,
amplificador, dataset ni modelos `int8` validados. El núcleo doméstico no depende
de esa fase.

## Validación terminada

- 20 pruebas de comportamiento del gemelo digital.
- 50 pruebas locales PASS y 5 pruebas C++ nativas omitidas localmente, ejecutables en CI.
- Campaña semirreal: 10,000 pasos y 40,027 invariantes PASS.
- 16 pruebas de IA PASS; el modelo generado sigue siendo candidato, no validado en ESP32.
- El conteo vigente se obtiene con `scripts/validate_project.py`; no conservar
  un total historico como criterio de aprobacion.
- Compilación Arduino completa corregida; evidencia vigente en `firmware/COMPILACION_VALIDADA.md`.
- Validación de planes, Wikilinks, mapa de pines y visualización central.
- Revisión de sintaxis Python/JavaScript y diferencias sin errores.

Comando único:

```powershell
python scripts/validate_project.py
```

## Planes terminados

La bóveda `obsidian/proyect domus` incluye auditoría y simplificación económica. Las salidas
principales son:

- `13 - Plan de cierre de codigo.md`.
- `14 - Protocolo anti-colapso IA y ESP32.md`.
- `15 - Plan de optimizacion de codigo.md`.
- `16 - Plan de testeo antes de construccion.md`.
- `17 - Diagramas generales de conexiones.md`.
- `18 - Manual maestro de conexiones pin por pin.md`.
- `19 - Plan de testeo despues de construccion.md`.
- `21 - Simplificacion y reduccion de costos.md`.
- `22 - Resultados de correcciones y regresion.md`.

## Visualizaciones terminadas

- `visualizaciones/sistema-domus.html`: energía, módulos y conexiones.
- `modelo_3d_interactivo.html`: maqueta interactiva existente.
- `plano_tecnico_domus.svg` y `plano_tecnico_domus.pdf`: planos técnicos.
- Imágenes renderizadas y vistas explotadas en el proyecto.

## Lo que requiere el mundo físico

No puede cerrarse honestamente desde software:

1. Confirmación del pinout serigrafiado de la placa exacta.
2. Calibración de suelo, nivel, LDR, PIR y DHT.
3. Prueba de relés, bomba, ventilador y caída de la fuente.
4. Validación opcional futura de INMP441, MAX98357A, altavoz y microSD; no comprar para el núcleo.
5. Entrenamiento del modelo de voz español.
6. Medición de consumo y caída de la fuente común de 5 V. Batería y solar son decoración desconectada.

Las pruebas físicas están completamente especificadas en los planes 16 y 19;
no se marcan como PASS hasta ejecutarlas sobre el montaje real.
