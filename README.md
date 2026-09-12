# PROJECT DOMUS — casa inteligente local (ESP32-S3 N16R8)

Maqueta de feria sin nube: sensores, automatización con histéresis, seguridad
(PARO, nivel, timeout, rearme) y Jarvis por control IR con frases fijas.
Estados del producto en [`obsidian/proyect domus/53`](obsidian/proyect%20domus/53%20-%20Definicion%20formal%20de%20firmware%20final%20y%20puertas.md):
`BANCO` (vigente) → `CANDIDATO` → `FINAL` (puertas F1–F7, ninguna superada aún).

## Qué abrir primero

- Índice canónico: [`docs/INDICE.md`](docs/INDICE.md)
- Bóveda técnica: [`obsidian/proyect domus/00 - Inicio.md`](obsidian/proyect%20domus/00%20-%20Inicio.md) (autoridad: nota 46)
- Plan de orden del repo: nota `54`

## Qué firmware cargar

| Necesidad | Firmware | Perfil |
|---|---|---|
| Banco: sensores, LCD, botones, LED | `firmware/domus_esqueleto` | `ALFA_UN_COSTADO_SIN_IR` (motores bloqueados; `ALFA_BOMBA_1`/`ALFA_VENTILADOR_1` solo vigilados) |
| Candidato a producto | `firmware/casa_inteligente_v4` | `CANDIDATO_BANCO_SIN_ACTUADORES` por defecto (`-DDOMUS_PERFIL_CASA=1` LED, `=2` motor pendiente) |
| Solo diagnóstico de placa | `firmware/domus_selftest` | — |

`domus_esqueleto` está congelado (solo regresiones P0/P1). `JARVIS_LOCAL_HABILITADO=false`
y `MICROSD_HABILITADA=false` hasta superar sus puertas. No hay app móvil, BLE
ni dependencia de internet en funciones críticas.

## Documentos vigentes

- Mapa y banco por un costado: notas `46`, `47` (guía), `49` (una carga)
- Olas y correcciones: notas `50`, `51`, `52`, `53`, `54`, `55`
- Ronda B01-B05: nota `37` · IDE: nota `35` · Cierre SW: nota `34`
- Históricos (no cablear/comprar): notas `43`, `44`, `45`, `18`, `PLAN_PROYECTO.md`

## Diagramas vigentes

- Guía final pin por pin: `visualizaciones/domus-final-guia-principiantes.svg`
- Arquitectura general: `visualizaciones/domus-arquitectura-feria.svg`
- Banco alfa: `domus-alfa-guia-principiantes.svg` · potencia: `domus-alfa-una-carga-s8050.svg`
- Interactivo (revisar vigencia por nota): `visualizaciones/diagrama-cableado-interactivo/index.html`

## Jarvis (sin micrófono)

Órdenes por control IR CAR MP3 (21 teclas, códigos del mando real) y respuestas
fijas en español. Sin reconocimiento de voz, sin entrenamiento, sin INMP441.
`GPIO12` reservado; audio solo tras puerta F5.

## Compilación

CI (`firmware-ci.yml`) compila el candidato en 7 configuraciones, el esqueleto
en 3 perfiles (+3 rechazos) y la base modular, con Arduino-ESP32 3.3.10:

```powershell
arduino-cli compile --fqbn "esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB" firmware/casa_inteligente_v4
python scripts/check_perfil_matrix.py   # 3 perfiles alfa OK + 3 prohibidos rechazados
```

La compilación comprueba software; sensores, etapas y fuente se validan en
físico (notas 33/37). Batería y solar son estética desconectada.

## Comandos locales por USB

Monitor Serial a 115200 baudios, una orden por línea: `RIEGO_ON/OFF`,
`LUZ1/2_ON/OFF`, `VENT_ON/OFF`, `INVER_ON/OFF`, `*_AUTO`, `ESTADO`,
`DIAGNOSTICO` (incluye `PERFIL_CANDIDATO=`), `PARO`, `REARMAR`, `RECUPERAR`,
`MIC_ESTADO`, `SD_PRUEBA`, `CAL_*`.

## Protección contra bloqueos

Watchdog + supervisor (memoria, reinicios, sensores, ráfagas). Ante riesgo:
apaga cargas, suspende automatización/voz y deja Serial. `DIAGNOSTICO` da la
causa; `RECUPERAR` libera el modo seguro con memoria suficiente; las cargas
quedan apagadas hasta orden explícita. Detalle: nota `14`.

## Límites honestos

- Sin driver identificado no hay bomba/ventilador en banco (F1).
- Sin mapa IR/audio no hay Jarvis hablado (F4/F5).
- Los modelos de cientos de MB no caben en esta placa; PicoTTS/TinyML siguen en puertas.
- Riego y ventilación funcionan sin Wi-Fi. Spotify requeriría gateway local con internet.
