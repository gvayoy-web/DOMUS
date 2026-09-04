---
proyecto: PROJECT DOMUS
tipo: indice
actualizado: 2026-09-04
---

# PROJECT DOMUS — bóveda técnica

Esta bóveda usa como inventario oficial **únicamente la lista confirmada por Isaac el 1 de septiembre de 2026**. Si una pieza aparece en un documento antiguo pero no en [[01 - Inventario confirmado]], se considera no disponible.

## Respuesta rápida

- **Pantalla:** ya existe LCD1602 con interfaz I2C. No comprar OLED.
- **Relés:** hay 1 canal disponible. Para las cinco cargas previstas falta **un módulo de 4 canales**, no uno de 8.
- **microSD:** comprar un lector SPI dedicado y una tarjeta FAT32 para archivos accesibles por el ESP32. La ranura del DFPlayer solo sirve para sus pistas; si se usa como respaldo, necesita una segunda tarjeta.
- **Voz Jarvis:** faltan INMP441, MAX98357A, altavoz 4 Ω/3 W y los modelos de voz entrenados.
- **Energía de feria:** falta una fuente real de 5 V/3 A y distribución segura. El módulo de alimentación de protoboard no debe alimentar bomba, cinco relés y audio.
- **Batería:** no se necesitan TP4056 + CN3065 + otro BMS todos juntos. Se elige una arquitectura; véase [[04 - Energia bateria y solar]].
- **Software:** el núcleo offline, las cinco cargas, sensores, seguridad y
  simulación están integrados. Quedan calibración física y modelos de voz;
  véanse [[13 - Plan de cierre de codigo]] y
  [[14 - Protocolo anti-colapso IA y ESP32]].

## Navegación

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

## Estado real del proyecto

| Entregable | Estado |
|---|---|
| Firmware doméstico y anti-colapso | TERMINADO y compilado |
| Simulador y contratos automáticos | TERMINADOS; 38/38 en PASS |
| Planes de optimización, montaje y pruebas | DOCUMENTOS TERMINADOS |
| Diagramas y manual de conexiones | TERMINADOS para banco; pines provisionales señalados |
| Calibración y validación eléctrica | PENDIENTE DE HARDWARE |
| Jarvis hablado, batería y solar | FASES BLOQUEADAS por módulos/mediciones faltantes |

## Visualización central

Abrir [PROJECT DOMUS — sistema completo](../../visualizaciones/sistema-domus.html)
para cambiar entre fuente, batería y solar y consultar los pines de cada módulo.

## Regla de control

Cada componente se etiqueta así:

- **YA TIENES:** está en la lista confirmada.
- **FALTA:** necesario para una función prometida.
- **OPCIONAL:** mejora o respaldo, pero la demostración puede funcionar sin él.
- **NO USAR / NO COMPRAR:** duplicado, incompatible o ajeno al alcance.
