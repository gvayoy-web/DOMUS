---
fecha: 2026-09-07
estado: vigente
tipo: entorno_y_auditoria
---

# Preparación Arduino IDE y revisión documental

Esta nota explica cómo abrir y compilar la base modular sin errores de
bibliotecas y resume la revisión integral de los Markdown. La fuente operativa
sigue siendo [[00 - Inicio]]; la evidencia de pruebas está en
[[34 - Cierre de software y matriz de verificacion]].

## Placa y opciones

La capacidad declarada es 16 MB flash + 8 MB PSRAM. En la nomenclatura oficial
de Espressif corresponde a `N16R8`, aunque el propietario la describa como
“N8R16” por mencionar primero RAM y después memoria.

En Arduino IDE seleccionar:

- Placa: `ESP32S3 Dev Module`.
- Flash Size: `16MB`.
- PSRAM: `OPI PSRAM`.
- Partition Scheme: `3M APP/9M FATFS` o equivalente `app3M_fat9M_16MB`.
- CPU Frequency: `240MHz`.
- Upload Speed: comenzar con `460800`; bajar a `115200` si la carga falla.
- Monitor serie: `115200` baudios y fin de línea habilitado.

## Bibliotecas obligatorias

Abrir **Programa > Incluir librería > Administrar bibliotecas** e instalar:

| Biblioteca | Autor | Versión validada |
|---|---|---:|
| DHT sensor library | Adafruit | 1.4.7 |
| Adafruit Unified Sensor | Adafruit | 1.1.15 |
| LiquidCrystal I2C | Frank de Brabander o compatible | 1.1.2 |

Después, cerrar y volver a abrir Arduino IDE. Si continúa `DHT.h: No such file
or directory`, revisar **Archivo > Preferencias > Ubicación del sketchbook** y
confirmar que la biblioteca fue instalada en ese mismo sketchbook. No descargar
un archivo `DHT.h` suelto ni eliminar el sensor del código.

## Orden seguro de prueba

1. Abrir `firmware/domus_esqueleto/domus_esqueleto.ino`.
2. Compilar con las salidas todavía deshabilitadas.
3. Conectar placa, LCD, botones y sensores; mantener bomba y motor desconectados.
4. Cargar y ejecutar `DIAGNOSTICO` por Serial.
5. Completar calibración y la matriz de [[33 - Base modular funcional y plan de banco]].
6. Verificar la fuente común de 5 V antes de habilitar una carga.

## Decisiones documentales vigentes

- Controlador: ESP32-S3 con 16 MB flash y 8 MB PSRAM.
- Salidas económicas: relé de bomba, tres LED y driver S8050 de ventilador.
- Alimentación: una fuente común regulada de 5 V; 3 A o más hasta medir consumo.
- Batería y solar: estética, terminales aislados y sin conexión al circuito.
- Jarvis: fase separada; no bloquea el núcleo doméstico.
- microSD: opcional, no requerida para las pruebas de banco actuales.

## Resultado de la revisión Markdown

Se inventariaron 70 archivos `.md`, incluida esta nota. Las fuentes vigentes fueron alineadas con
las decisiones anteriores. Los informes con conteos o diseños antiguos se
conservan como snapshots históricos y remiten a las notas 34 y 35; no deben
interpretarse como instrucciones actuales. El validador automático comprueba
Wikilinks, planes requeridos, mapa de pines y contratos del firmware.

La revisión global se reproduce con `python scripts/validate_markdown.py`; exige
título H1, contenido no vacío y destinos existentes para enlaces locales y
Wikilinks de todos los Markdown fuera de carpetas de herramientas/compilación.

## Lo único que esta revisión no demuestra

La documentación y la compilación no miden voltaje, corriente, ruido ADC,
polaridad del relé, temperatura del transistor, fugas de agua ni estabilidad de
la placa real. Esas pruebas permanecen abiertas en las notas 16, 19 y 33.
