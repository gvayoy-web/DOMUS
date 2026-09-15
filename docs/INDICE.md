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
| Cargar firmware de banco | `firmware/casa_inteligente_v4` (`BANCO_COMPLETO_S8050_IR`) |
| Cargar candidato | `firmware/casa_inteligente_v4` (`CANDIDATO_*`, nota 53) |
| Ordenar el repo | Nota `54` (plan) + nota `56` (fase 1) |

## Firmware (único producto: `casa_inteligente_v4`)

| Pieza | Ruta |
|---|---|
| Candidato | `firmware/casa_inteligente_v4/casa_inteligente_v4.ino` |
| Interfaces futuras (driver/IR/audio) | `firmware/casa_inteligente_v4/domus_drivers.h` |
| Esqueleto actual (misma fuente del producto, perfil 3) | `firmware/domus_esqueleto/` |
| Esqueleto v2 archivado para regresión | `firmware/legacy/domus_esqueleto/` |
| Lector seguro IR + calibración | `firmware/diagnosticos/domus_banco_integracion/` |
| Diagnóstico de placa | `firmware/domus_selftest/` |
| Pruebas firmware | `firmware/tests/` (contratos, sim, nativas, HIL) |

## Hardware y planos

| Pieza | Ruta |
|---|---|
| Planos canónicos | `hardware/planos/` (base 800 × 520, familia Ultimate) |
| Guías y SVG fuente | `visualizaciones/` |
| Manuales impresos generados | `output/pdf/` (se regeneran; futuro: `artefactos/`) |

## Documentos vigentes (bóveda)

`00` (índice) · `46` (autoridad) · `47` (guía) · `49` (una carga) ·
`50`–`56` (olas y correcciones) · `34` (cierre SW) · `35` (IDE) · `37` (B01-B05).
Históricos, no cablear/comprar: `43`, `44`, `45`, `18`, `docs/PLAN_PROYECTO.md`.

## Validar antes de commitear

```powershell
python -m unittest discover -s firmware/tests -v
python tools/validate_project.py
python tools/validate_markdown.py
python tools/check_perfil_matrix.py
```
