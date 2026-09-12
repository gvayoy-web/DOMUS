# Índice canónico del repositorio (nota 54)

> Fuente de navegación. La autoridad técnica vive en la bóveda (`obsidian`,
> nota 46). Este índice no duplica decisiones, solo rutas.

## Entrar por rol

| Quiero… | Abrir |
|---|---|
| Entender el proyecto en 5 min | `README.md` → nota `00` |
| Montar el banco alfa | Nota `47` + `visualizaciones/domus-final-guia-principiantes.svg` |
| Probar una carga | Nota `49` + `visualizaciones/domus-alfa-una-carga-s8050.svg` |
| Ver la arquitectura y el guion demo | `visualizaciones/domus-arquitectura-feria.svg` |
| Cargar firmware de banco | `firmware/domus_esqueleto` (`ALFA_UN_COSTADO_SIN_IR`) |
| Cargar candidato | `firmware/casa_inteligente_v4` (`CANDIDATO_*`, nota 53) |
| Ordenar el repo | Nota `54` (plan) + nota `56` (fase 1) |

## Firmware (único producto: `casa_inteligente_v4`)

| Pieza | Ruta |
|---|---|
| Candidato | `firmware/casa_inteligente_v4/casa_inteligente_v4.ino` |
| Interfaces futuras (driver/IR/audio) | `firmware/casa_inteligente_v4/domus_drivers.h` |
| Banco congelado (P0/P1) | `firmware/domus_esqueleto/` |
| Diagnóstico de placa | `firmware/domus_selftest/` |
| Pruebas firmware | `firmware/tests/` (contratos, sim, nativas, HIL) |
| PoCs de audio | `firmware/inmp441_poc/`, `firmware/picotts_poc/` |
| Voz/entrenamiento | `ai/` + `ai/tests/` |

## Hardware y planos

| Pieza | Ruta |
|---|---|
| Planos canónicos | `planos/new/` (base 800 × 520, familia Ultimate) |
| Guías y SVG fuente | `visualizaciones/` |
| Manuales impresos generados | `output/pdf/` (se regeneran; futuro: `artefactos/`) |

## Documentos vigentes (bóveda)

`00` (índice) · `46` (autoridad) · `47` (guía) · `49` (una carga) ·
`50`–`56` (olas y correcciones) · `34` (cierre SW) · `35` (IDE) · `37` (B01-B05).
Históricos, no cablear/comprar: `43`, `44`, `45`, `18`, `PLAN_PROYECTO.md`.

## Validar antes de commitear

```powershell
python -m pytest firmware/tests/ ai/tests/ -q
python scripts/validate_project.py
python scripts/validate_markdown.py
python scripts/check_perfil_matrix.py
```
