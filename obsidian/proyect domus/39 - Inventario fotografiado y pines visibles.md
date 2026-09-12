---
proyecto: PROJECT DOMUS
tipo: evidencia-fotografica
actualizado: 2026-09-09
estado: foto_revisada
---

# Inventario fotografiado y pines visibles

> [!IMPORTANT]
> Prueba posterior confirmada por Isaac: el LCD con backpack trabaja a 3.3 V y
> no requiere conversor de nivel. No alimentarlo a 5 V en este montaje.

Fuente: fotografía conjunta recibida el 9 de septiembre. La foto confirma tipo
y presencia aparente; no certifica que una pieza funcione ni su corriente real.

## Confirmado visualmente

| Pieza | Lo que demuestra la foto | Cómo se conecta |
|---|---|---|
| ESP32-S3 | placa física con GPIO serigrafiados | usar el texto `GPIOx`; no contar posiciones |
| LCD1602 + backpack I²C | el adaptador ya está unido al LCD | solo cuatro cables externos: `GND`, `VCC`, `SDA`, `SCL` |
| DHT11 suelto | encapsulado azul de cuatro patas | frente perforado: 1 VCC, 2 DATA, 3 NC, 4 GND |
| Sensor de suelo | sonda de dos puntas + módulo comparador | sonda al conector de dos pines; `AO` al ESP32; `DO` libre |
| Sensor de nivel | placa roja analógica de tres pines | seguir `S/+/-` impresos; no adivinar orden |
| PIR | módulo con domo tipo HC-SR501 | seguir `VCC/OUT/GND`; la foto no prueba izquierda/derecha |
| Relé desnudo | relé azul de cinco patas, aparentemente bobina 5 V | identificar bobina y `COM/NO/NC` por diagrama/continuidad |
| Potencia | minibomba, motor/aspa, MB102 y adaptador | medir voltaje, polaridad y corriente antes de integrar |
| Discretos | botones, LDR, resistencias, diodos y transistores | identificar valor/marca antes de energizar |

## LCD real: una sola pieza de cuatro pines

El backpack I²C que se ve detrás del LCD ya realiza la expansión. No se conecta
otro módulo I²C entre ambos y no se cablean los 16 pines paralelos.

```text
LCD/backpack GND -> ESP32 GND
LCD/backpack VCC -> ESP32 3V3  (primera prueba segura)
LCD/backpack SDA -> ESP32 GPIO21
LCD/backpack SCL -> ESP32 GPIO13
```

Usar las letras impresas en el backpack, no copiar un orden izquierda-derecha.
Si a 3.3 V no funciona o la retroiluminación queda débil, no cambiar simplemente
VCC a 5 V: las resistencias del backpack podrían subir SDA/SCL a 5 V. En ese
caso se detiene la prueba y se añade/verifica conversión bidireccional después.

## Orden físico que sí puede afirmarse

Para el DHT11 suelto, mirándolo de frente (rejilla hacia la persona) y con patas
hacia abajo:

```text
pata 1 VCC -> 3V3
pata 2 DATA -> GPIO14
pata 3 NC -> sin cable
pata 4 GND -> GND
10 kΩ entre pata 1 y pata 2
```

En nivel, suelo, PIR, S8050 y relé no se fija orden físico solamente desde esta
foto. La serigrafía, marca exacta, hoja de datos y multímetro mandan.

## Adaptador y MB102

La etiqueta del adaptador no se lee completa con suficiente certeza. No conectar
su barril al MB102 hasta leer y anotar voltaje de salida, corriente, polaridad del
centro y comprobar que coinciden con la entrada del módulo. El MB102 no se usa
como fuente final ni se asume capaz de 3 A.

## Relaciones

- [[01 - Inventario confirmado]]
- [[18 - Manual maestro de conexiones pin por pin]]
- [[38 - Reunion integracion final y rumbo del firmware]]
