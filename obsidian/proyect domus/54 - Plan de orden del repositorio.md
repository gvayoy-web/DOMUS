---
proyecto: PROJECT DOMUS
tipo: plan-orden-repositorio
actualizado: 2026-09-12
estado: plan_para_ejecutar
---

# Plan de orden del repositorio (inventario 2026-09-12)

Jefatura: esqueleto congelado; `casa_inteligente_v4` es el candidato;
no mover ni borrar archivos del árbol sucio del propietario. Este plan se
ejecuta desde checkout limpio; los cambios del propietario se reportan aparte.

## 1. Inventario (solo lectura, commit `3c5e704` + candidato)

| Zona | Trackeados | Contenido |
|---|---|---|
| Raíz suelta | 20 | 5 md + `README.md` + 6 renders/obj + 4 csv/html/pdf + `generate_design.py` + gitconfigs |
| `assets/` | 64 | Incluye `execute.zip` 51 MB + duplicado 49 MB + historial V1/V2 |
| `obsidian/` | 60 | Bóveda 00-53 + `.obsidian/` (¡`graph.json`/`workspace.json` trackeados!) |
| `planos/` | 50 | `new/` canónico + raíz/zip históricos |
| `firmware/` | 43+4 | 5 firmwares + headers + 9 tests + PoCs + docs |
| `ai/` | 9 | Entrenador + evaluador + 3 tests |
| `visualizaciones/` | 12 | 6 SVG/HTML fuente + interactivos |
| `scripts/` | 10 | Validadores + generadores PDF + matriz |
| `documentos/` | 6 | 6 `.docx` (3 pares actual/original duplicados) |
| `docs/` | 4 | Bitácora aegis 2026-09-06 |
| `output/` | 4 | 2 PDF generados + 1 md + 1 png |
| `.github/` | 3 | CI firmware/ai/audio |

Ignorados grandes (bien): `build/`, `firmware/**/build/`, toolchains,
`.venv-ia/`, `__pycache__/`, `deploy/`, `ai/data|runs`. Sin ignorar:
`*.rar` (`firmware/domus_esqueleto.rar` suelto), `tmp/`, `.boss/`,
`.codex-remote-attachments/`, `planos/planos/`.

Árbol sucio del propietario (NO TOCAR aquí, solo reportar): ~40 md de
obsidian modificados, `planos/*` + raíz suelta borrados sin commitear,
`scripts/build_ronda_banco_pdf.py` modificado, `build_domus_final_pdf.py` +
`domus_esqueleto.rar` + `tmp/` + PDFs nuevos sin seguimiento.

## 2. Estructura canónica propuesta

```text
firmware/casa_inteligente_v4/   candidato (único producto)
firmware/domus_esqueleto/       banco congelado (P0/P1)
firmware/domus_selftest|anim|*_poc/  diagnóstico y experimentos
firmware/tests/                 pruebas de firmware (incl. sim + nativas)
docs/                           bóveda publicada: inicio, manuales, olas, actas
hardware/                       planos/new canónico + guías + SVG fuente
visualizaciones/                solo fuente web/SVG (ya está bien)
tests/  → NO crear: cada suite vive con su código (firmware/ai/planos)
tools/ (renombrar scripts/)     validadores + matriz + generadores
artefactos/ (ignorada)          PDF/ZIP/renders generados (hoy en output/, raíz, assets)
```

## 3. Tabla antes → después (EJECUTAR en siguiente entrega, no aquí)

| Antes | Después | Notas |
|---|---|---|
| 20 sueltos de raíz | `docs/` (md), `hardware/` (csv/obj/png/pdf/html), `tools/` (`generate_design.py`) | Raíz queda con README + gitconfigs |
| `planos/new/*` | `hardware/planos/` | Única ruta canónica; `planos/` raíz se retira |
| `planos/planos/` (untracked) | eliminar del disco (autorización) | No commitear |
| `assets/*.zip` 100 MB + 6 docx + renders | Releases/LFS o `artefactos/` ignorada | `.git` hoy 199 MB |
| `output/*.pdf` generados | `artefactos/` o Releases | Se regeneran desde fuente |
| `obsidian/proyect domus/` | se queda (fuente); `docs/` publica índice | `.obsidian/*.json` fuera del repo |
| `scripts/` | `tools/` (+ `.gitignore`: `*.rar`, `tmp/`, artefactos) | Corregir imports/links |

## 4. Reglas de ejecución

1. Un commit por fila de la tabla, con `antes → después` en el mensaje.
2. Tras cada movimiento: `validate_markdown.py` + `validate_project.py` en verde
   y cero enlaces rotos antes del siguiente.
3. README raíz final: qué abrir (docs), qué firmware cargar (banco vs
   candidato + perfiles), qué documentos son vigentes (00/46/47/49/50-54).
4. Prohibido: borrar historia (`git filter-repo` solo con orden explícita),
   tocar el árbol sucio, declarar FINAL (F1–F7).

## Relaciones

- [[46 - Plan maestro de consolidacion un costado]]
- [[53 - Definicion formal de firmware final y puertas]]
