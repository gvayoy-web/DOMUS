---
proyecto: PROJECT DOMUS
tipo: decision-vigente
actualizado: 2026-09-07
estado: corregido_inventario_real
---

# Configuración corregida: un único relé y planos v4

El nombre histórico del archivo conserva “1 mas 4”, pero esa configuración fue
retirada al confirmar el inventario real. Hay un solo relé azul desnudo de 5 V.

## Salidas elegidas

| GPIO | Etapa disponible | Carga | Estado físico |
|---:|---|---|---|
| 4 | S8050 + 1 kOhm + relé 5 V + 1N4007 | Bomba | Disponible; bloqueado hasta B06 |
| 5 | Ninguna | Luz sala | Bloqueado; LED futuro |
| 6 | Ninguna | Luz dormitorio | Bloqueado; LED futuro |
| 7 | Ninguna | Ventilador | Bloqueado; driver futuro |
| 8 | Ninguna | Luz invernadero | Bloqueado; LED futuro |

El relé desnudo no se conecta al GPIO. GPIO4 controla la base del S8050 mediante
1 kOhm; el transistor conmuta la bobina de 5 V y el 1N4007 absorbe el retorno.
La bomba usa COM y NO para permanecer apagada cuando la bobina no tiene energía.

La línea `constexpr bool HABILITAR_RELE_BOMBA = false;` permanece en `false`
hasta confirmar patas, driver, 5 V y arranque sin pulsos. Después se cambia solo
a `true`; GPIO5-8 continúan bloqueados por `SALIDA_FISICA_HABILITADA[]`.

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
La elección del perfil no certifica el relé ni autoriza habilitar la bomba.

B01-B05 se ejecutan con GPIO4-8 libres siguiendo
[[37 - Ronda de pruebas sin compras]]. B06 prueba solo GPIO4 y el relé sin bomba.
