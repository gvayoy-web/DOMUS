---
estado: vigente
fecha: 2026-09-12
autoridad: pruebas_y_repositorio
---

# Orden Git y pruebas multientorno

## Repositorio

- Rama de trabajo: `proyecdomus`.
- Destino publicado: `origin/main`.
- `hardware/planos/` es la ubicación canónica de planos.
- `tools/` es la ubicación canónica de validadores y generadores.
- `docs/` contiene los documentos generales que antes estaban sueltos en raíz.
- `firmware/casa_inteligente_v4/` es el producto.
- `firmware/domus_esqueleto/` es banco heredado.
- `firmware/diagnosticos/domus_banco_integracion/` es una utilidad temporal para
  LCD + IR + DRV8833; no sustituye al producto.

## Evidencia local del 2026-09-12

| Entorno | Resultado | Alcance |
|---|---:|---|
| Validador integral Python | PASS | 20 pruebas núcleo, 83 firmware (9 SKIP), 7 planos |
| Gemelo semirreal | PASS | 10,000 pasos, 40,027 invariantes, fallos y reinicios inyectados |
| Arduino ESP32-S3 N16R8, perfiles CASA 0/1/2 | PASS | 422,310 B programa; 26,172 B RAM global |
| Arduino ESP32-S3 N16R8, perfil CASA 3 | PASS | 444,901 B programa; 26,388 B RAM global |
| Matriz esqueleto | PASS | 3 perfiles permitidos compilan; 3 configuraciones peligrosas se rechazan |
| Diagnóstico LCD+IR+DRV8833 | PASS de compilación | 369,361 B programa; 25,140 B RAM global |
| HIL físico | NO EJECUTADO | COM3/COM4 aparecen como puertos desconocidos; falta identificar placa, `pyserial` y banco conectado |

Ubuntu CI reveló dos desajustes de harness y una dependencia de planos no
declarada. Se sincronizaron `DOMUS_PERFIL_CASA`, `BOMBA_DIRECTA_S8050` y el
conteo del escaneo I2C de 112 direcciones; además se añadió el requirements
canónico de Pillow/ReportLab al job remoto. El resultado verde se registra
únicamente cuando termine la ejecución del commit corregido.

La segunda pasada remota confirmó los tests nativos, pero descubrió que los
jobs Arduino instalaban LCD y DHT sin declarar `IRremote`, aunque el producto
ya incluye `domus_ir_casa.h`. CI instala ahora `IRremote@4.7.1` en todas las
familias de compilación.

El sketch auxiliar histórico `domus_anim` requería además GFX, SSD1306 y
ST7789. Esas dependencias quedaron fijadas únicamente en su familia de CI;
no se añadieron al firmware de producto.

La campaña semirreal no certifica voltajes, corriente, polaridad ni temperatura.
Las mediciones eléctricas se mantienen marcadas como `SKIP por decisión del dueño`;
no deben presentarse como PASS. Tampoco se cargó firmware ni se accionó una bomba
sin supervisión física.

## Avisos que no bloquean

`LiquidCrystal I2C 1.1.2` declara arquitectura AVR en sus metadatos, por eso
Arduino emite un warning. Aun así, todas las compilaciones ESP32 terminaron con
código 0. Debe confirmarse el comportamiento del LCD en el banco real.

El shell normal no tiene `python` en `PATH`; las pruebas se ejecutaron con el
runtime Python empaquetado de Codex. Las pruebas C++ nativas reservadas para
Ubuntu CI se omiten localmente porque no hay compilador host.
