---
proyecto: PROJECT DOMUS
tipo: diagramas-conexion
actualizado: 2026-09-04
estado: terminado_usar_despues_de_testeo
---

# Diagramas generales de conexiones

> [!DANGER]
> Usar estos diagramas solo después de aprobar
> [[16 - Plan de testeo antes de construccion]]. Los GPIO marcados como
> provisionales deben confirmarse en la serigrafía. Todo el montaje es baja
> tensión DC; no conectar red eléctrica dentro de la maqueta.

## 1. Distribución de energía

```mermaid
flowchart LR
    PSU[Fuente regulada 5 V / 3 A] --> F[Fusible 3 A]
    F --> SW[Interruptor general]
    SW --> BUS5[Barra 5 V en estrella]
    PSU --> GND[Barra GND común]

    BUS5 --> ESP[ESP32-S3 por 5V/VIN]
    BUS5 --> RC[Bobinas de relés]
    BUS5 --> LOADS[Cargas 5 V]
    BUS5 --> AUDIO[MAX98357A]
    BUS5 --> LED[WS2812]
    BUS5 --> LCD5[LCD1602 backpack]

    ESP --> V33[Salida 3.3 V]
    V33 --> SENS[Sensores y lógica 3.3 V]
    V33 --> MIC[INMP441]
    V33 --> SD[microSD 3.3 V compatible]

    GND --> ESP
    GND --> RC
    GND --> LOADS
    GND --> AUDIO
    GND --> LED
    GND --> SENS
    GND --> MIC
    GND --> SD
```

La bomba, ventilador, relés, audio y WS2812 no se alimentan desde 3.3 V. Usar
ramales separados desde la barra y capacitores cerca de las cargas ruidosas.

## 2. Mapa general de señales del ESP32

```mermaid
flowchart TB
    ESP[ESP32-S3 N16R8]

    SOIL[Humedad suelo AO] -->|GPIO1 ADC · provisional calibración| ESP
    WATER[Nivel de agua AO] -->|GPIO2 ADC · provisional| ESP
    LDR[LDR + divisor 10 kΩ] -->|GPIO3 ADC| ESP
    PIR[PIR OUT] -->|GPIO9 · provisional| ESP
    STOP[Paro a GND] -->|GPIO10 INPUT_PULLUP| ESP
    MICOFF[MIC OFF a GND] -->|GPIO11 INPUT_PULLUP| ESP
    DEMO[Botón demo a GND] -->|GPIO12 INPUT_PULLUP| ESP
    DHT[DHT DATA + pull-up 3.3 V] -->|GPIO14| ESP

    ESP -->|GPIO4| R1[Relé bomba]
    ESP -->|GPIO5| R2[Relé luz sala]
    ESP -->|GPIO6| R3[Relé luz dormitorio]
    ESP -->|GPIO7| R4[Relé ventilador]
    ESP -->|GPIO8| R5[Relé luz invernadero]

    ESP <-->|GPIO21 SDA + GPIO13 SCL provisional| SHIFT[Conversor I2C bidireccional]
    SHIFT <--> LCD[LCD1602 I2C a 5 V]

    MIC[INMP441 3.3 V] -->|SD GPIO16| ESP
    ESP -->|WS GPIO15 + SCK GPIO17| MIC
    ESP <-->|USB Serial diagnóstico| PC[Computadora]
```

Si el backpack LCD ya trabaja a 3.3 V y sus pull-ups están a 3.3 V, el
conversor puede no ser necesario; verificarlo eléctricamente, no asumirlo.

## 3. Relés y cargas

```mermaid
flowchart LR
    GPIO[GPIO4–GPIO8] --> IN[IN1–IN5 de relés]
    BUS5[5 V lógica] --> VCC[VCC/JD-VCC según módulo]
    GND[GND común] --> RGND[GND relés]

    PWR[5 V con fusible] --> COM[COM de cada canal]
    COM --> NO[Contacto NO]
    NO --> POS[Positivo de la carga]
    POS --> LOAD[Bomba / luces / ventilador]
    LOAD --> GND

    DIODE[Diodo flyback en bomba/motor<br/>cátodo a +, ánodo a GND] -.-> LOAD
```

Confirmar si el módulo es activo en LOW y si separa JD-VCC/VCC. No puentear ni
aislar tierras sin seguir el esquema específico del módulo comprado.

## 4. Audio, Jarvis, microSD y aro

```mermaid
flowchart TB
    ESP[ESP32-S3]
    INMP[INMP441<br/>VDD 3.3 V]
    AMP[MAX98357A<br/>VIN 5 V]
    SPK[Altavoz 4 Ω / 3 W]
    SD[microSD SPI]
    RING[WS2812 5 V]
    LEVEL[74AHCT125 recomendado]

    ESP -->|GPIO15 WS + GPIO17 SCK| INMP
    INMP -->|GPIO16 SD| ESP

    ESP -.->|BCLK / LRC / DOUT<br/>40/41/42 solo propuesta| AMP
    AMP -->|SPK+ y SPK−| SPK

    ESP <-->|SCK38 MISO39 MOSI47 CS48<br/>provisionales| SD
    ESP -.->|GPIO aún sin asignar| LEVEL
    LEVEL -->|330 Ω en datos| RING
```

Todos comparten referencia GND cuando el módulo lo exige. Añadir capacitor de
reserva cerca del aro. El altavoz se conecta únicamente entre SPK+ y SPK−.

## 5. Agua y seguridad física

```mermaid
flowchart LR
    TANK[Depósito cerrado] --> PUMP[Bomba 5 V]
    PUMP --> TUBE[Tubo de riego]
    TUBE --> POT[Maceta / invernadero]
    POT --> TRAY[Bandeja antifugas]

    LEVEL[Sensor de nivel] -->|GPIO2 ADC| ESP[ESP32]
    SOIL[Sensor de suelo] -->|GPIO1 ADC| ESP
    ESP -->|GPIO4| RELAY[Relé de bomba]
    RELAY --> PUMP

    LOW[Nivel bajo] --> BLOCK[Bloqueo]
    BAD[Sensor inválido] --> BLOCK
    TIME[120 s máximos] --> BLOCK
    BLOCK --> RELAY
```

El depósito y los tubos quedan al lado opuesto del gabinete. Usar bucles
antigoteo y situar la electrónica al menos 25 cm por encima del agua.

## Tabla final de conexiones

| Grupo | Señal | GPIO | Estado |
|---|---|---:|---|
| ADC | Humedad suelo | 1 | Calibrar físicamente. |
| ADC | Nivel de agua | 2 | Provisional. |
| ADC | LDR | 3 | Divisor a 3.3 V. |
| Relés | Bomba/sala/dormitorio/ventilador/invernadero | 4/5/6/7/8 | Confirmar activo LOW. |
| Entrada | PIR | 9 | Provisional. |
| Entrada | Paro/MIC OFF/demo | 10/11/12 | A GND, `INPUT_PULLUP`. |
| I2C | SCL/SDA LCD | 13/21 | SCL provisional; revisar niveles. |
| Sensor | DHT | 14 | Pull-up a 3.3 V. |
| I2S RX | INMP441 WS/SD/SCK | 15/16/17 | Provisional. |
| UART opcional | DFPlayer RX/TX | 18/19 | Deshabilitado; revisar USB nativo. |
| SPI opcional | SD SCK/MISO/MOSI/CS | 38/39/47/48 | Provisional. |
| I2S TX | MAX98357A BCLK/LRC/DOUT | 40/41/42 propuestos | No definitivo. |
| LED | WS2812 DATA | Sin asignar | Elegir después del pinout. |

## Relaciones

- [[05 - Auditoria de pines y cableado]]
- [[14 - Protocolo anti-colapso IA y ESP32]]
- [[16 - Plan de testeo antes de construccion]]
- [[18 - Manual maestro de conexiones pin por pin]]
- [[19 - Plan de testeo despues de construccion]]
