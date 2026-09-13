---
proyecto: PROJECT DOMUS
tipo: indice
actualizado: 2026-09-10
---

# PROJECT DOMUS — bóveda técnica

> [!IMPORTANT]
> Estado operativo: [[58 - Estado vigente firmware sensores control y documentos]]. La decisión más reciente de firmware y cableado de banco es [[59 - Firmware unico y perfil banco S8050 IR]] y prevalece en bomba, IR y fuente de código.

> [!IMPORTANT]
> La autoridad durante la consolidación es [[46 - Plan maestro de consolidacion un costado]].
> El manual 43 y los diagramas 44-45 quedan superados hasta publicar el manual
> consolidado. Las notas 02-45 conservan historia, pero no autorizan cableado.

Esta bóveda usa como inventario oficial **únicamente la lista confirmada por Isaac el 1 de septiembre de 2026**. Si una pieza aparece en un documento antiguo pero no en [[01 - Inventario confirmado]], se considera no disponible.

## Respuesta rápida

- **Firmware y banco actuales:** `casa_inteligente_v4` es la única base. Usar
  `BANCO_COMPLETO_S8050_IR`: bomba S8050 en GPIO4, IR en GPIO12, LEDs en
  GPIO5/6/8 y ventilador GPIO7 bloqueado. Ver [[59 - Firmware unico y perfil banco S8050 IR]].

- **Pantalla:** ya existe LCD1602 con interfaz I2C. No comprar OLED.
- **Motores:** probar uno por vez con S8050; no asumir DRV8833 hasta identificar el módulo pedido.
- **microSD:** no obligatoria para el núcleo. DFPlayer necesita una tarjeta para sus pistas; lector SPI y otra tarjeta solo si se requiere almacenamiento independiente del ESP32.
- **Jarvis:** control confiable con control remoto CAR MP3 + receptor HX1838. El
  MAX98357A y parlante reproduciran respuestas fijas en español; no comprar
  INMP441 ni entrenar reconocimiento de voz.
- **Energía de feria:** fuente cerrada regulada de 5 V/5 A, fusible principal de 4 A y distribución común. El módulo de protoboard y el TP4056 no forman parte de la alimentación final.
- **Batería y solar:** quedan como estética, eléctricamente desconectados. La casa funciona con una fuente común regulada de 5 V.
- **Software:** `firmware/casa_inteligente_v4` es la única base. El perfil
  `BANCO_COMPLETO_S8050_IR` habilita sensores, LCD, LED, una bomba S8050 e IR;
  audio, ventilador y driver doble permanecen fuera.
- **Ronda inmediata:** cablear desde [[59 - Firmware unico y perfil banco S8050 IR]],
  abrir Serial a 115200 y enviar `PRUEBA`. La bomba comienza bloqueada en OFF.

## Navegación

Resumen actualizado de decisiones y ejemplo inicial: [[31 - Esqueleto y decisiones consolidadas]].
Metas y criterios vigentes de la base modular: [[32 - Metas y madurez de la base DOMUS]].
Implementacion vigente y secuencia de banco: [[33 - Base modular funcional y plan de banco]].
Cierre local de software y evidencia vigente: [[34 - Cierre de software y matriz de verificacion]].
Preparacion del IDE y auditoria Markdown: [[35 - Preparacion Arduino IDE y revision documental]].
Arquitectura histórica descartada de relés: [[36 - Configuracion final 1 mas 4 reles y planos v4]].
Guía histórica de la primera ronda: [[37 - Ronda de pruebas sin compras]].
Acta histórica previa al DRV8833: [[38 - Reunion integracion final y rumbo del firmware]].
Inventario fotografiado y pines visibles: [[39 - Inventario fotografiado y pines visibles]].
Presupuesto mínimo, diagramas antes/después y migración: [[40 - Presupuesto minimo Jarvis diagramas y migracion de firmware]].
Compra hondureña vigente y banco de soldadura: [[41 - Compra nacional minima y banco de soldadura]].
Texto definitivo para cotizar en C&D: [[42 - Solicitud final de cotizacion C&D]].
Manual histórico superado (solo historia, nota 50): [[43 - Manual final completo PROJECT DOMUS]].
Arquitectura histórica superada (conservar reglas de seguridad): [[44 - Arquitectura y ciclo de vida del firmware]].
Ola 1 (buffers, Jarvis único, GPIO12, validación por perfil): [[50 - Ola 1 buffers Jarvis GPIO12 y validacion por perfil]].
Ola 2 (cierre: casa candidata, planos canónicos, sim del esqueleto): [[51 - Ola 2 cierre casa historica planos y sim]].
Ola 3 (migración SalidaDomus + diagrama final con TBD): [[52 - Ola 3 migracion SalidaDomus y diagrama final]].
Definición formal de firmware final y puertas F1-F7: [[53 - Definicion formal de firmware final y puertas]].
Plan de orden del repositorio (inventario + antes→después): [[54 - Plan de orden del repositorio]].
Corrección auditoría 5 (mapa 15/16/17/18, fuente real, driver primero): [[55 - Correccion auditoria 5 mapa fuente driver]].
Orden fase 1 no destructiva (índice, README, ignores): [[56 - Orden fase 1 no destructiva]].
Integración LCD final + backends + movimiento 1: [[57 - Integracion LCD backends movimiento 1]].
Estado vigente consolidado de firmware, sensores y control: [[58 - Estado vigente firmware sensores control y documentos]].
Decisión vigente de firmware único y perfil de banco S8050 + IR: [[59 - Firmware unico y perfil banco S8050 IR]].
Ordenamiento Git y pruebas multientorno vigentes: [[60 - Orden Git y pruebas multientorno]].
Plano alfa anterior sin IR, conservado solo como historia: [[45 - Diagrama ASCII alfa sin control IR]].
Plan maestro vigente por un solo costado: [[46 - Plan maestro de consolidacion un costado]].

1. [[01 - Inventario confirmado]]
2. [[02 - Matriz funciones y componentes]]
3. [[03 - Lista de compras definitiva]]
4. [[04 - Energia bateria y solar]]
5. [[05 - Auditoria de pines y cableado]]
6. [[06 - Jarvis audio pantalla y microSD]]
7. [[07 - Precios y fuentes Honduras]]
8. [[08 - Errores y contradicciones encontradas]]
9. [[09 - Plan de montaje y pruebas]]
10. [[10 - Materiales de maqueta y exposicion]]
11. [[11 - Migracion de deliverables y chat]]
12. [[12 - Bitacora de implementacion]]
13. [[13 - Plan de cierre de codigo]]
14. [[14 - Protocolo anti-colapso IA y ESP32]]
15. [[15 - Plan de optimizacion de codigo]]
16. [[16 - Plan de testeo antes de construccion]]
17. [[17 - Diagramas generales de conexiones]]
18. [[18 - Manual maestro de conexiones pin por pin]]
19. [[19 - Plan de testeo despues de construccion]]
20. [[33 - Base modular funcional y plan de banco]]
21. [[34 - Cierre de software y matriz de verificacion]]
22. [[35 - Preparacion Arduino IDE y revision documental]]
23. [[36 - Configuracion final 1 mas 4 reles y planos v4]]
24. [[37 - Ronda de pruebas sin compras]]
25. [[38 - Reunion integracion final y rumbo del firmware]]
26. [[39 - Inventario fotografiado y pines visibles]]
27. [[40 - Presupuesto minimo Jarvis diagramas y migracion de firmware]]
28. [[41 - Compra nacional minima y banco de soldadura]]
29. [[42 - Solicitud final de cotizacion C&D]]

## Estado real del proyecto

Plan vigente de Jarvis: [[25 - Plan ejecutable Jarvis offline fiable y entrenado]].
Prioriza reconocimiento de intenciones; la alternativa económica usa DFPlayer
para frases grabadas según nota 30, sin sustituir silenciosamente PicoTTS. Conversación libre
con Barista queda experimental. Entrenamiento e integración siguen pendientes.

Actualización: ver [[34 - Cierre de software y matriz de verificacion]] para
la evidencia vigente y [[24 - Viabilidad Barista DOMUS memoria voz y entrenamiento]]
para el prototipo generativo propuesto. Barista todavía no está integrado ni
entrenado para DOMUS; la tabla histórica siguiente no certifica voz ni hardware.

| Entregable | Estado |
|---|---|
| Firmware doméstico y anti-colapso | Implementado y compilado; validación física pendiente |
| Simulador y contratos automáticos | 50 PASS locales; 5 pruebas C++ omitidas por falta de compilador; además 16 pruebas de IA PASS y campaña semirreal de 10,000 pasos; ver nota 34 |
| Planes de optimización, montaje y pruebas | DOCUMENTOS TERMINADOS |
| Diagramas y manual de conexiones | TERMINADOS para banco; pines provisionales señalados |
| Calibración y validación eléctrica | PENDIENTE DE HARDWARE |
| Jarvis hablado | PENDIENTE de micrófono, modelo real e integración física |
| Batería y solar | Sólo estética; desconectados del circuito por decisión |

## Alternativas de costo y ampliación

[[27 - Comparador de planes costo y versatilidad]] reúne
[[28 - Plan A DOMUS minimo desembolso]], [[29 - Plan B DOMUS ampliable y reutilizable]]
y [[30 - Plan C Jarvis offline por etapas]]. Son propuestas, no pruebas de montaje aprobadas.

## Visualización central

Avance Jarvis: [[26 - Avance Jarvis contrato entrenamiento y pruebas]]. Voz integrada y
entrenamiento útil siguen pendientes; los resultados antiguos no aprueban esos cambios.

Abrir [PROJECT DOMUS — sistema completo](../../visualizaciones/sistema-domus.html)
para consultar los pines y las rutas históricas de energía. La ruta operativa
vigente usa únicamente la fuente común de 5 V.

## Regla de control

Cada componente se etiqueta así:

- **YA TIENES:** está en la lista confirmada.
- **FALTA:** necesario para una función prometida.
- **OPCIONAL:** mejora o respaldo, pero la demostración puede funcionar sin él.
- **NO USAR / NO COMPRAR:** duplicado, incompatible o ajeno al alcance.
