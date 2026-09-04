---
proyecto: PROJECT DOMUS
tipo: firmware-hardware
actualizado: 2026-09-04
---

# Auditoría de pines y cableado

## Mapa que declara hoy el firmware

| Función | GPIO actual | Auditoría |
|---|---:|---|
| Humedad suelo | 1 | Disponible; el sensor real es resistivo, no capacitivo. |
| Nivel de agua | 2 | Reasignado en software; entrada analógica provisional y umbral pendiente de calibrar. |
| LDR | 3 | Disponible; usar divisor con 10 kΩ. |
| Relés | 4–8 | Cinco cargas lógicas: bomba, sala, dormitorio, ventilador e invernadero. |
| PIR | 9 | Entrada digital provisional; confirmar nivel activo y pin expuesto. |
| DHT11 | 14 | Disponible. |
| INMP441 WS/SD/SCK | 15/16/17 | Provisional; falta hardware. |
| DFPlayer RX/TX | 18/19 | DFPlayer está deshabilitado. GPIO19 puede interferir con USB nativo en algunos montajes S3. |
| I2C SDA | 21 | GPIO válido. |
| I2C SCL | 13 | Sustituye a GPIO22 en software; confirmar que está expuesto antes de cablear. |

## Problemas que deben resolverse antes de cablear

1. Confirmar físicamente que GPIO13 está expuesto y usarlo como I2C SCL, o reasignarlo.
2. Confirmar la serigrafía/pinout exacto del DevKitC N16R8; no asumir que todos los GPIO del chip están disponibles.
3. Verificar las cinco salidas de relé ya reducidas en software.
4. Validar GPIO9 para PIR y GPIO2 para nivel de agua con los módulos reales.
5. El “sensor de viento” ya fue eliminado del firmware; no reintroducirlo sin hardware real.
6. Reservar tres GPIO para salida MAX98357A. El PoC propone 40/41/42 como valores iniciales, no definitivos.
7. Asignar WS2812 sin usar un pin de arranque o un pin ocupado por USB/flash/PSRAM.
8. Mantener tierra común entre ESP32, relés, sensores, MAX98357A y fuente.

> [!DANGER]
> No construir el mazo final hasta confirmar GPIO13, GPIO9 y GPIO2 en la serigrafía de la placa. El error de GPIO22 ya fue retirado del software.

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

## Relaciones

- [[16 - Plan de testeo antes de construccion]]
- [[17 - Diagramas generales de conexiones]]
- [[18 - Manual maestro de conexiones pin por pin]]
