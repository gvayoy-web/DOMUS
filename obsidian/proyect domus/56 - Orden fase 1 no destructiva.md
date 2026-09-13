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
| `hardware/GUIA_MONTAJE.md` (6) | Artefactos canónicos en `hardware/` y `hardware/planos/`; generador en `tools/generate_design.py` | Ejecutado |
| `docs/ENTREGA_FINAL.md` (2) | Artefactos canónicos en `hardware/planos/` | Ejecutado |
| Nota `33` (frontmatter) | `../../docs/ESTADO_ACTUAL.md` | Ejecutado |
| `tools/build_project_domus_docs.py` | `assets/*opcion_*.png`, `arquitectura_*.png` | No toca raíz; sin efecto |
| `tools/validate_project.py` | `hardware/planos/GUIA_MONTAJE_ULTIMATE.md` | Ruta actualizada en el movimiento canónico |
| `README.md` (nuevo) | `docs/INDICE.md` | Creado en esta fase, existe |

Validadores tras la fase: `validate_markdown.py` y `validate_project.py` en
verde antes de cualquier movimiento (reporte de cierre).

## Prohibiciones respetadas

Árbol sucio del propietario intacto (~40 md, deleciones `planos/`, scripts
nuevos, `.rar`, `tmp/`). La copia `planos/planos/` fue consolidada después en
`hardware/planos/`. Sin
`filter-repo`, sin FINAL (F1–F7).

## Relaciones

- [[54 - Plan de orden del repositorio]]
- [[53 - Definicion formal de firmware final y puertas]]
