---
proyecto: PROJECT DOMUS
tipo: indice
actualizado: 2026-09-07
---

# PROJECT DOMUS — bóveda técnica

Esta bóveda usa como inventario oficial **únicamente la lista confirmada por Isaac el 1 de septiembre de 2026**. Si una pieza aparece en un documento antiguo pero no en [[01 - Inventario confirmado]], se considera no disponible.

## Respuesta rápida

- **Pantalla:** ya existe LCD1602 con interfaz I2C. No comprar OLED.
- **Relés:** decisión vigente: reutilizar el relé individual para la minibomba y usar un módulo de cuatro canales para sala, dormitorio, ventilador e invernadero. Total: cinco cargas, perfil activo LOW sujeto a prueba física.
- **microSD:** no obligatoria para el núcleo. DFPlayer necesita una tarjeta para sus pistas; lector SPI y otra tarjeta solo si se requiere almacenamiento independiente del ESP32.
- **Voz Jarvis:** objetivo de comandos locales; falta micrófono y reconocimiento integrado/validado. Para respuestas grabadas reutilizar DFPlayer con altavoz y tarjeta; MAX98357A solo para la alternativa PicoTTS.
- **Energía de feria:** falta una fuente real de 5 V/3 A y distribución segura. El módulo de alimentación de protoboard no debe alimentar bomba, cinco relés y audio.
- **Batería y solar:** quedan como estética, eléctricamente desconectados. La casa funciona con una fuente común regulada de 5 V.
- **Software:** el núcleo offline, las cinco cargas, sensores, seguridad y
  simulación están integrados. Quedan calibración física y modelos de voz;
  véanse [[13 - Plan de cierre de codigo]] y
  [[14 - Protocolo anti-colapso IA y ESP32]].
- **Ronda inmediata:** B01-B05 se ejecutan con el N16R8 y las piezas ya
  compradas, sin relés ni cargas; usar [[37 - Ronda de pruebas sin compras]].

## Navegación

Resumen actualizado de decisiones y ejemplo inicial: [[31 - Esqueleto y decisiones consolidadas]].
Metas y criterios vigentes de la base modular: [[32 - Metas y madurez de la base DOMUS]].
Implementacion vigente y secuencia de banco: [[33 - Base modular funcional y plan de banco]].
Cierre local de software y evidencia vigente: [[34 - Cierre de software y matriz de verificacion]].
Preparacion del IDE y auditoria Markdown: [[35 - Preparacion Arduino IDE y revision documental]].
Decisión física consolidada 1+4 y geometría v4: [[36 - Configuracion final 1 mas 4 reles y planos v4]].
Guía y hoja imprimible para la ronda sin compras: [[37 - Ronda de pruebas sin compras]].

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
