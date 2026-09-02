---
proyecto: PROJECT DOMUS
tipo: indice
actualizado: 2026-09-01
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
- **Software:** hay errores de pinout y funciones todavía no integradas; véase [[08 - Errores y contradicciones encontradas]].

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

## Regla de control

Cada componente se etiqueta así:

- **YA TIENES:** está en la lista confirmada.
- **FALTA:** necesario para una función prometida.
- **OPCIONAL:** mejora o respaldo, pero la demostración puede funcionar sin él.
- **NO USAR / NO COMPRAR:** duplicado, incompatible o ajeno al alcance.
