---
proyecto: PROJECT DOMUS
tipo: orden-fase-1
actualizado: 2026-09-12
estado: aplicado_fase_1_no_destructiva
---

# Orden fase 1 (no destructiva): índice, README, ignores, P2

Cero movimientos y cero borrados. Esqueleto congelado intacto. Plan: [[54 - Plan de orden del repositorio]].

## Cambios de esta fase

1. `.gitignore`: `tmp/`, `*.rar`, `artefactos/` (binarios sueltos y
   generados van a Releases/LFS, no al código).
2. `docs/INDICE.md` (nuevo): índice canónico por rol, sin duplicar la bóveda.
3. `README.md` reescrito: qué abrir, qué firmware cargar, documentos/diagramas
   vigentes, Jarvis sin micrófono, compilación, comandos, límites honestos.
4. P2 auditoría: `static_assert` une campos y arreglo de salidas en
   `MAPA_CASA` (`bomba/sala/cuarto/vent/inv` == `salidas[0..4]`).

## Inventario de enlaces antes de mover (fase 2)

Referencias a los 20 sueltos de raíz que condicionan los movimientos:

| Origen | Destino referenciado | Efecto al mover |
|---|---|---|
| `GUIA_MONTAJE.md` (6) | `plano_tecnico_domus.pdf`, `lista_corte.csv`, `modelo_3d_interactivo.html`, `project_domus.obj/mtl`, `verificacion_geometria_v4.json`, `generate_design.py` | Mover el bloque junto a `docs/` o reescribir 6 líneas |
| `ENTREGA_FINAL.md` (2) | `modelo_3d_interactivo.html`, `plano_tecnico_domus.svg` | Ídem |
| Nota `33` (frontmatter) | `../../ESTADO_ACTUAL.md` | Actualizar a nueva ruta de `ESTADO_ACTUAL.md` |
| `scripts/build_project_domus_docs.py` | `assets/*opcion_*.png`, `arquitectura_*.png` | No toca raíz; sin efecto |
| `scripts/validate_project.py` | `planos/new/GUIA_MONTAJE_ULTIMATE.md` | No mover `planos/new` sin actualizar |
| `README.md` (nuevo) | `docs/INDICE.md` | Creado en esta fase, existe |

Validadores tras la fase: `validate_markdown.py` y `validate_project.py` en
verde antes de cualquier movimiento (reporte de cierre).

## Prohibiciones respetadas

Árbol sucio del propietario intacto (~40 md, deleciones `planos/`, scripts
nuevos, `.rar`, `tmp/`). `planos/planos/` ni se toca ni se ignora. Sin
`filter-repo`, sin FINAL (F1–F7).

## Relaciones

- [[54 - Plan de orden del repositorio]]
- [[53 - Definicion formal de firmware final y puertas]]
