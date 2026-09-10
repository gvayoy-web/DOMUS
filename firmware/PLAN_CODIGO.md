# Plan del código: esqueleto v2 → firmware FINAL

Fuente vigente de pines: `firmware/domus_esqueleto/domus_config.h`.
Guía física: `visualizaciones/diagrama-final.html`. Estado real medido abajo.

## v2 actual (verificado 2026-09-10)

- Compila N16R8: 405749 programa / 25652 globales (`build/esqueleto_v2`).
- Subido por COM9 y verificado en serie real: `DIAGNOSTICO` 4/4 líneas,
  `IR LISTA` 21/21, `TX_OMITIDOS` estable (solo ráfaga de arranque).
- Medido en placa: `FIS=01101 OUT=00000 PARO=0 SEGURO=0`, sensores ADC vivos,
  `LCD=0 DHT=0` = aún sin cablear (pendiente banco, pasos 2 y 7 del diagrama).
- Contratos: `firmware/tests/test_domus_esqueleto_contract.py` (36 tests,
  35 pass + fostering: 5 nativos solo en CI Ubuntu por falta de g++ local).
- Cuello real encontrado y parchado: ráfagas UART 115200 perdían líneas
  (FIFO 128 B del CH343) → `Serial.flush()` tras cada línea de
  `informarEstado()` (`domus_esqueleto.ino:241`) y de `IR LISTA`.
  Regla: una línea TX por vez; lo periódico (SENSORES 1/s) no necesita flush.

## Archivos (no duplicar lógica entre firmwares)

| Archivo | Dueño de |
|---|---|
| `domus_config.h` | Pines, flags `HABILITAR_BOMBA/USAR_DRV8833/DFPLAYER_HABILITADO`, tiempos |
| `domus_control.h` | Calibración, decisiones auto con histéresis |
| `domus_protocol.h` | Comandos serie (PARO > todo; `!` = paro inmediato) |
| `domus_ir.h` | Mapa CAR MP3 + aprender NVS + filtro repeat |
| `domus_lcd.h` | 4 páginas, feedback+animación, nunca % sin `CAL` |
| `domus_voice.h` | Frases fijas: Serial+LCD siempre; DFPlayer si hay; si no, buzzer |
| `domus_esqueleto.ino` | Orquestación: seguridad → botón → IR → serie → sensores → auto → LCD |
| `protocol_tests.cpp` | Regresiones constexpr (rompen la compilación si mienten) |

Toda función nueva entra primero aquí con prueba o contrato. No copiar
lógica al firmware principal y a la base a la vez.

## Camino a FINAL (en orden, cada paso con su PASS físico)

1. **Banco completo sin motores** (hoy): cablear pasos 0–15 del diagrama,
   `CAL … GUARDAR`, `IR LEER` + 21 teclas. PASS: LCD sin `SIN DATOS`,
   `VA=1`, riego manual con agua.
2. **Fuente final**: medir 5.0 V centro positivo → fusible 4 A → switch →
   bus. PASS: 5 V bajo carga, sin reinicios. `USAR_DRV8833` sigue false.
3. **DRV8833 sin motores**: VM/GND/nSLEEP/AIN1=4/AIN2=GND/BIN1=7/BIN2=GND.
   PASS: no calienta. Luego `USAR_DRV8833=true`, `HABILITAR_BOMBA=true`,
   recompilar, re-subir, probar bomba en agua (10 s) y ventilador por separado.
4. **Audio**: opción A DFPlayer (`DFPLAYER_HABILITADO=true`, SD con
   `0001.mp3…` según tabla del README esqueleto) u opción B MAX98357A
   (16/17/18, **exclusivo** con DF). PASS: tecla 1 suena limpio.
5. **Cierre**: `BOMBA_MAX_MS` 10000 → 120000 solo tras medir consumo y
   timeout real; campaña semireal + `validate_project.py` en verde.

## Fuera del núcleo (no prometen demo)

TinyML/PicoTTS/INMP441/microSD-SPI/relés de potencia/solar funcional:
experimentales, no bloquean feria. Jarvis = IR + frases fijas.

## Chuleta serie (115200)

`ESTADO · DIAGNOSTICO · IR LEER · IR LISTA · IR GRABAR <0-20> · IR BORRAR ·`
`MODO AUTO/MANUAL · VOL+/- · MUTE ON/OFF · VOZ ON/OFF · PAGINA [0-3] ·`
`SALA/CUARTO/VENTILADOR/INVERNADERO/BOMBA ON|OFF|AUTO · PARO · REARMAR`
