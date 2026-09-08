---
proyecto: PROJECT DOMUS
tipo: decision-vigente
actualizado: 2026-09-07
estado: elegido_pendiente_banco
---

# Configuración final: 1 + 4 relés y planos v4

Esta nota fija la configuración física elegida por Isaac y tiene prioridad
sobre propuestas económicas anteriores.

## Salidas elegidas

| GPIO | Etapa | Carga | Polaridad prevista |
|---:|---|---|---|
| 4 | Relé individual existente | Bomba | Activo LOW |
| 5 | Módulo de 4 relés, canal 1 | Luz sala | Activo LOW |
| 6 | Módulo de 4 relés, canal 2 | Luz dormitorio | Activo LOW |
| 7 | Módulo de 4 relés, canal 3 | Ventilador | Activo LOW |
| 8 | Módulo de 4 relés, canal 4 | Luz invernadero | Activo LOW |

El módulo debe aceptar control de 3.3 V. Bobinas y cargas se alimentan desde la
barra de 5 V, nunca desde GPIO. Usar contactos NO para que las cargas queden
apagadas al perder energía. Bomba y ventilador conservan diodo flyback según
su conexión y módulo físico.

`SALIDAS_HABILITADAS=false` permanece hasta confirmar nivel activo, arranque
sin pulsos, tensión de bus y una carga por vez. No mezclar este mazo con el
perfil LED/S8050 de [[21 - Simplificacion y reduccion de costos]].

## Geometría elegida

La única geometría para cortar es `planos/new`: base 800 × 520 mm, casa
344 × 260 mm, invernadero 200 × 280 mm, porche 200 × 156 mm, torre Jarvis
84 × 94.4 mm de huella y gabinete 88 × 120 mm de huella.

Las dimensiones 1000 × 650 mm y los planos v3 se conservan como historia y no
se usan para fabricar. Ante diferencias visuales mandan el PDF Ultimate y sus
CSV, después de medir espesor y componentes reales.

## Límites de la decisión

- La base de banco corta la bomba a 10 s para pruebas iniciales.
- El firmware principal conserva 120 s como máximo de operación; solo se usa
  después de validar depósito, caudal, fugas y calentamiento.
- Jarvis, microSD, WS2812, batería y solar no bloquean el núcleo.
- Batería y panel continúan desconectados y rotulados como representación.

## Puerta de aceptación

Completar B01-B09 de [[33 - Base modular funcional y plan de banco]], registrar
mediciones y después ejecutar [[19 - Plan de testeo despues de construccion]].
La elección del perfil no certifica el módulo ni autoriza habilitar salidas.

La ausencia actual del módulo de cuatro relés no bloquea B01-B05. Esa ronda se
ejecuta con GPIO4-8 libres siguiendo [[37 - Ronda de pruebas sin compras]].
