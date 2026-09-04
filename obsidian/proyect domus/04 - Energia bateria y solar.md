---
proyecto: PROJECT DOMUS
tipo: energia
actualizado: 2026-09-04
---

# Energía, batería y solar

## Por qué parecía haber demasiada protección

La lista anterior mezclaba tres diseños distintos. **No se montan todos a la vez.** Una batería de litio necesita:

1. Un método de carga adecuado.
2. Una sola etapa de protección contra sobrecarga, sobredescarga y cortocircuito.
3. Regulación a 5 V para la casa.
4. Fusible general como protección del cableado ante un corto grave.

El fusible y la protección electrónica no hacen lo mismo: el BMS protege la celda; el fusible protege principalmente cables y montaje.

## Arquitectura 1 — presentación con pared, recomendada primero

```text
Fuente 5 V/3 A con switch
          ↓
      fusible 3 A
          ↓
 barra 5 V / GND en estrella
   ├─ ESP32 + sensores
   ├─ relés
   ├─ bomba/ventilador
   └─ MAX98357A + LEDs
```

No usa batería, TP4056, BMS, CN3065 ni elevador. Es la forma correcta de probar todo antes de añadir solar.

## Arquitectura 2 — batería USB usando lo que ya tienes

```text
USB 5 V → un TP4056 protegido → una celda/pack 1S compatible → elevador 5 V → fusible → casa
```

- Solo **un TP4056** por pack.
- No conectar las dos placas TP4056 en paralelo.
- No usar esta ruta al mismo tiempo que CN3065.
- No ofrece un power-path garantizado; cargar con la casa apagada.
- Una sola 18650 de 2,500–2,800 mAh no garantiza dos horas.
- Para varias celdas paralelas se necesita comprobar corriente de protección, igualdad de celdas y temperatura. Para la versión final es más claro usar un BMS 1S explícito.

## Arquitectura 3 — solar final

```text
Panel 5–6 V verificado
    ↓
cargador solar 1S CN3065 o equivalente verificado
    ↓
batería/pack 1S diseñado y protegido
    ↓
elevador estable a 5.0 V
    ↓
fusible → switch → casa
```

Aquí los TP4056 **no se conectan**. El cargador solar carga; la protección de
la batería limita condiciones peligrosas; el elevador entrega 5 V. Los bornes
exactos entre cargador, batería, protección y carga dependen de las placas
compradas y deben copiarse de sus hojas técnicas. No ensamblar un pack 1S2P o
1S3P con celdas sueltas solo para alcanzar una cifra de capacidad.

> [!WARNING]
> Ninguna de estas rutas ofrece por sí sola cambio automático entre pared,
> batería y solar. Para usar dos fuentes sin apagar hace falta un módulo de
> power-path/selector verificado. Nunca unir sus positivos directamente.

## Capacidad para dos horas

Fórmula conservadora:

```text
C[mAh] = (5 V × corriente media × 2 h ÷ 3.7 V ÷ 0.85) × 1.25
```

| Corriente media de la casa | Capacidad calculada | Decisión |
|---:|---:|---|
| 0.40 A a 5 V | ≈3,180 mAh | Usar al menos 4,000 mAh. |
| 0.70 A a 5 V | ≈5,560 mAh | Usar mínimo 6,000 mAh. |
| 1.00 A a 5 V | ≈7,950 mAh | Objetivo 7,500–8,000 mAh. |

Los picos pueden superar el promedio: ESP32 con radio, cinco bobinas de relé, amplificador, bomba y ventilador pueden acercarse temporalmente a 1.5–2.5 A a 5 V. Por eso la fuente de feria debe ser 3 A y el elevador debe probarse bajo carga.

## Limitación solar que debe decirse con honestidad

El módulo CN3065 vendido localmente se anuncia alrededor de 500 mA. Un pack de 7,500 mAh tardaría como mínimo unas 15 horas ideales y aproximadamente 18–20 horas equivalentes de buen sol al considerar pérdidas y reducción de corriente. El panel puede demostrar generación y recarga lenta, pero no debe prometer recuperar toda la energía cada día sin mediciones.

## Panel de la captura

El panel de 3 V/110 mA produce solo 0.33 W nominales. No llega al mínimo de 4.4 V del CN3065. La variante local de 5 V/1,100 mA es más apropiada, pero su página mezcla 1,100 mA con 4.5 W; confirmar etiqueta y medir antes de conectar.

## Capacitores

- Los diez cerámicos “104” que ya tienes son de **100 nF** y deben colocarse cerca de módulos sensibles.
- Los electrolíticos de 10 µF ayudan localmente, pero no absorben los picos grandes.
- Comprar 1000 µF/25 V para cada rama crítica es útil.
- 4,700–6,800 µF en la barra principal ayuda durante milisegundos, no sustituye batería ni convertidor.
- A 1 A, 4,700 µF cae aproximadamente 0.21 V en 1 ms y 1.06 V en 5 ms.

## Reglas de litio

- No mezclar celdas recicladas diferentes.
- No usar celdas golpeadas, oxidadas, calientes o deformadas.
- No soldar con cautín directamente sobre una 18650 desnuda.
- No conectar panel directamente a batería.
- No recargar pilas alcalinas AA o 9 V.
- Medir 5.0 V en la salida antes de conectar el ESP32.

El cableado pin por pin de las tres rutas está en
[[18 - Manual maestro de conexiones pin por pin]].
