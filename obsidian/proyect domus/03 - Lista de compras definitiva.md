---
proyecto: PROJECT DOMUS
tipo: compras
moneda: HNL
actualizado: 2026-09-07
---

# Lista de compras definitiva

> Actualización 06-09-2026: consultar [[27 - Comparador de planes costo y versatilidad]]
> antes de comprar. La sección B histórica agrupa voz y almacenamiento: lector
> SPI y microSD NO son obligatorios para arrancar la ruta PicoTTS del plan 25.
> DFPlayer sí requiere su almacenamiento de pistas. No comprar ambos motores
> de audio por defecto. Las cifras siguientes no constituyen cotización actual.
> Decisión vigente: usar S8050, resistencia de 1 kOhm y 1N4007 directamente
> con la bomba de 3-6 V; el relé desnudo queda reservado. No comprar ahora el módulo de cuatro
> canales; GPIO5-GPIO8 quedan como expansión futura y bloqueados por software.
> Batería y solar son decoración, no compras eléctricas.

Los precios son referencias web consultadas el 1 de septiembre de 2026. No incluyen envío a Choluteca y deben reconfirmarse antes de pagar.

## A. Comprar primero — casa funcional sin Jarvis ni solar

**Perfil actual:** véanse [[29 - Plan B DOMUS ampliable y reutilizable]] y
[[36 - Configuracion final 1 mas 4 reles y planos v4]]. La tabla siguiente es
la ruta activa. La ampliación de cuatro relés queda diferida.

| Compra | Cant. | Precio visto | Subtotal | Motivo |
|---|---:|---:|---:|---|
| Fuente 5 V/3 A USB-C con interruptor | 1 | C&D L350 | L350 | Alimentación estable de feria. |
| Relé 4 canales, 5 V/10 A, entrada 3.3 V/5 V | 0 ahora | C&D L250 | L0 | Expansión futura; no es necesario para la ronda actual. |
| Portafusible aéreo 5×20 mm | 1 | C&D L15 | L15 | Protección de la entrada de 5 V. |
| Fusible cerámico 3 A, 5×20 mm | 3 | C&D L15 | L45 | Uno instalado y dos repuestos. |
| Capacitores 1000 µF/25 V, paquete de 5 | 1 | C&D L35 | L35 | Uno en barra principal y otros cerca de audio/actuadores. |
| Conectores PCT, 4 unidades | 1 | C&D L40 | L40 | Distribución desmontable. |
| Cable 22 AWG | 1 lote | C&D desde L35 | L35+ | Alimentación; no pasar bomba/relés por jumpers finos largos. |
| Jumpers H/H | 1 faja | Confirmar variante; set completo C&D L250 | hasta L250 | Tus módulos y el ESP32 tienen pines macho. Comprar solo H/H si la tienda separa variantes. |

**Subtotal mínimo de esta lista sin el relé diferido:** L485 sin cable nuevo ni H/H.
**Subtotal conservador:** hasta L770 incluyendo cable desde L35 y el set completo de jumpers.

> [!WARNING]
> La fuente USB-C alimenta bien el ESP32, pero hace falta derivar los 5 V hacia una barra de distribución. No obligar a que toda la corriente de bomba, relés y audio atraviese el regulador de 3.3 V ni pistas pequeñas del ESP32.

## B. Comprar para Jarvis local

| Compra | Cant. | Precio visto | Prioridad | Nota |
|---|---:|---:|---|---|
| INMP441 I2S | 1 | Sin oferta hondureña verificada | Obligatorio | Importar o consultar directamente a C&D; no sustituir por KY-037. |
| MAX98357A | 1 | C&D L130 | Obligatorio | Amplificador/DAC I2S. |
| Altavoz 4 Ω/3 W | 1 | C&D L90 | Obligatorio | Conectar solo a SPK+ y SPK−. |
| 74AHCT125 o 74HCT14 | 1 | Sin oferta hondureña verificada | Recomendado | Nivel lógico estable para WS2812 a 5 V; 74HC595 no es sustituto. |
| Lector/escritor microSD SPI | 1 | C&D L149 | Obligatorio | Almacenamiento que el ESP32 sí puede montar y leer/escribir. |
| microSD 4 GB FAT32 | 1 | Sin oferta local verificada; usar 32 GB Steren L159 | Obligatorio | Archivos, configuraciones y registros del ESP32. |
| Segunda microSD FAT32 | 1 | Steren L159 | Opcional | Solo si se activa el DFPlayer como respaldo de audio. |

**Subtotal local de voz y almacenamiento:** L528 + precio/importación del INMP441. Con segunda microSD para DFPlayer: L687 + INMP441.  
El lector SPI y el DFPlayer no comparten tarjeta: cada ranura tiene una función distinta.

## C. Solar y batería — referencia histórica, no comprar

### Estimación de una opción de 7,500 mAh, no orden de compra inmediata

| Compra | Cant. | Precio visto | Subtotal |
|---|---:|---:|---:|
| Panel 5 V/1,100 mA | 1 | C&D L280 | L280 |
| Solución de batería 1S protegida equivalente a 7,500 mAh | 1 | estimación basada en 3 × L180 | L540 |
| Portabatería/conjunto adecuado para el pack | 1 | estimación previa 3 × L55 | L165 |
| Protección BMS 1S | 1 | C&D L85 | L85 |
| CN3065 solar | 1 | C&D L135 | L135 |
| MT3608 elevador a 5 V | 1 | C&D L90 | L90 |
| Interruptor KCD1 ON/OFF | 1 | C&D L25 | L25 |
| Capacitor 6800 µF/25 V | 1 | C&D L35 | L35 |

**Subtotal histórico solar:** L1,355, excluido del presupuesto vigente.

No uses los TP4056 a la vez que CN3065/protección. Los TP4056 quedan para una
arquitectura USB separada o para pruebas de una sola celda. Esta tabla solo
reserva presupuesto: no comprar ni montar celdas en paralelo hasta medir el
consumo y definir un pack protegido con conectores, corriente y cargador
compatibles. Véase [[18 - Manual maestro de conexiones pin por pin]].

## D. Materiales todavía no confirmados

- Plywood 6–9 mm o cartón corrugado doble para base y casa.
- Acrílico transparente para invernadero y bahía electrónica.
- Pintura negra, azul cobalto, madera y sellador.
- Silicón caliente, pegamento para madera, cinta doble cara y bridas.
- Depósito de agua cerrado, bandeja antifugas y tubo adicional si hace falta.
- Separadores M3, tornillos, tuercas y tapa transparente.
- Cautín, estaño, termorretráctil, pelacables y destornilladores si no están disponibles en el equipo.

Véase [[10 - Materiales de maqueta y exposicion]].
