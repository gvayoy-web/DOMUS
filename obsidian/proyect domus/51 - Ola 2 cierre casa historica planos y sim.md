---
proyecto: PROJECT DOMUS
tipo: ola-cierre
actualizado: 2026-09-12
estado: aplicado_ola_2
---

# Ola 2 — cierre: casa histórica, planos canónicos y sim del esqueleto

Autoridad: [[46 - Plan maestro de consolidacion un costado]].
Ola previa: [[50 - Ola 1 buffers Jarvis GPIO12 y validacion por perfil]].

## 1. casa_inteligente_v4, referencia migrada candidata (ver nota 53)

`firmware/casa_inteligente_v4/casa_inteligente_v4.ino` lleva banner de
migración Fase E paso 1 (ver nota 52): conserva todas sus reglas, ya sin
abstracción de relés. Estado formal: `CANDIDATO`, no `FINAL` ni histórico
inerte (definición y puertas en
[[53 - Definicion formal de firmware final y puertas]]). El banco vigente es
`firmware/domus_esqueleto` (perfil `ALFA_UN_COSTADO_SIN_IR`).
`firmware/PLAN_CODIGO.md` y `firmware/domus_esqueleto/README.md` anteriores
quedan como historia donde contradigan a esta nota.
`00 - Inicio.md` apunta a las olas 50/51/52 y deja de llamar “vigente” a 43/44.

## 2. Planos canónicos (dualidad resuelta)

* **Canónico:** `planos/new/` (trackeado, probado por `planos/tests/`,
  verde en checkout limpio). Base 800 × 520 y familia Ultimate mandan.
* **No canónico:** `planos/planos/` (sin seguimiento, duplicado sin autoridad).
  Ningún script, workflow o nota vigente puede referenciarlo (verificado por
  búsqueda: cero referencias). Pendiente: borrarlo del disco cuando Isaac lo
  autorice; no se commitea ni se restaura nada desde ahí.
* **CSV/HTML sueltos borrados en el árbol de trabajo** (`lista_corte.csv`,
  `modelo_3d_interactivo.html`, etc.): superados por los Ultimate de
  `planos/new`. Son limpieza sin commitear del autor; no se restauran ni se
  commitean en esta ola. El validador omite la Guía Ultimate si falta en el
  árbol, pero `planos/tests` la exige donde existe.

## 3. Sim específica del esqueleto

`firmware/tests/test_esqueleto_sim.py` (8 tests): espeja
`decidirRiego/Ventilador/LuzSala/Invernadero`, `porcentajeCalibrado` con
polaridad invertida y la máquina bomba (calibración → nivel → timeout 10 s →
bloqueo → rearme). Los umbrales se afirman primero como literales de
`domus_control.h`; si el firmware cambia un umbral, el contrato falla antes
de que la sim mienta.

## 4. HIL: SKIP con puerta explícita

Sin placa en este entorno (`pyserial` ausente): `test_hil_esqueleto.py` se
omite. Puerta de ejecución real: placa N16R8 en COMx + `ALFA_UN_COSTADO_SIN_IR`
cargado + ronda B01-B05 (nota 37). No se declara validación física sin ella.

## 5. Verificación de la ola

Ver reporte final de la sesión (commit de cierre): pytest global,
`validate_project.py`, matriz 3+3, compilaciones casa 5/5 + selftest +
esqueleto, cero restos de abstracción de relés.

## Relaciones

- [[46 - Plan maestro de consolidacion un costado]]
- [[50 - Ola 1 buffers Jarvis GPIO12 y validacion por perfil]]
- [[52 - Ola 3 migracion SalidaDomus y diagrama final]]
