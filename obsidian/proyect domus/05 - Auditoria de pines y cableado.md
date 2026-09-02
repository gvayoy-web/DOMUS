---
proyecto: PROJECT DOMUS
tipo: firmware-hardware
actualizado: 2026-09-01
---

# Auditoría de pines y cableado

## Mapa que declara hoy el firmware

| Función | GPIO actual | Auditoría |
|---|---:|---|
| Humedad suelo | 1 | Disponible; el sensor real es resistivo, no capacitivo. |
| “Viento” | 2 | No hay sensor de viento confirmado. Debe deshabilitarse o reasignarse al nivel de agua. |
| LDR | 3 | Disponible; usar divisor con 10 kΩ. |
| Relés | 4–11 | El código reserva ocho, pero físicamente solo se necesitan cinco. |
| DHT11 | 14 | Disponible. |
| INMP441 WS/SD/SCK | 15/16/17 | Provisional; falta hardware. |
| DFPlayer RX/TX | 18/19 | DFPlayer está deshabilitado. GPIO19 puede interferir con USB nativo en algunos montajes S3. |
| I2C SDA | 21 | GPIO válido. |
| I2C SCL | 22 | **ERROR CRÍTICO: GPIO22 no existe en ESP32-S3.** |

## Problemas que deben resolverse antes de cablear

1. Cambiar I2C SCL a un GPIO realmente expuesto en tu placa.
2. Confirmar la serigrafía/pinout exacto del DevKitC N16R8; no asumir que todos los GPIO del chip están disponibles.
3. Reducir los relés físicos a cinco y liberar tres GPIO.
4. Asignar pines a PIR y nivel de agua; hoy no existen en el firmware.
5. Decidir si se elimina por completo el “sensor de viento”. El motor con aspa no es automáticamente un anemómetro calibrado.
6. Reservar tres GPIO para salida MAX98357A. El PoC propone 40/41/42 como valores iniciales, no definitivos.
7. Asignar WS2812 sin usar un pin de arranque o un pin ocupado por USB/flash/PSRAM.
8. Mantener tierra común entre ESP32, relés, sensores, MAX98357A y fuente.

> [!DANGER]
> No construir el mazo final usando el mapa actual: GPIO22 hace imposible el I2C tal como está escrito.

## Reglas eléctricas

- INMP441: solo 3.3 V.
- MAX98357A: 5 V, GND común; altavoz entre SPK+ y SPK−, nunca SPK− a tierra.
- HC-SR04 opcional: reducir ECHO de 5 V a 3.3 V con divisor.
- Relés: alimentar bobinas a 5 V y comprobar activación con lógica 3.3 V. El modelo C&D declara entrada 3.3/5 V y activación en LOW.
- Bomba y motor: usar diodo flyback cuando corresponda y ramal separado.
- WS2812: resistencia de 330 Ω en datos, capacitor de reserva en 5 V y adaptación 74AHCT recomendada si hay inestabilidad.
- Agua: sensores y cables con bucle antigoteo; electrónica al menos 25 cm por encima del depósito.

## Distribución sugerida de relés

El relé de un canal existente controla la bomba. El nuevo módulo de cuatro canales controla sala, dormitorio, ventilador e invernadero. No controlar tensión de red en la exposición; todas las cargas serán de baja tensión.

