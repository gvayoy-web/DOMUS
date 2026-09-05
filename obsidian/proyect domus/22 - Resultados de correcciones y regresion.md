---
fecha: 2026-09-04
estado: software_validado_banco_pendiente
codigo: f811065
matriz: 1f6b6a4
---

# Resultados de correcciones y regresión

## Resultado

Se resolvió el fallo de compilación de la nota 20. El firmware actual compila
en Windows y Ubuntu. Se incorporó una alternativa de salidas económicas,
conservando el cableado original como configuración predeterminada.

Código y configuración subidos a `gvayoy-web/domusv1`, rama `main`.
[CI completa en verde](https://github.com/gvayoy-web/domusv1/actions/runs/33941659044).
La ejecución precedente `33941570903` detectó un identificador QSPI inválido
en la matriz; se corrigió de `qspi` a `enabled` y se ejecutaron de nuevo los
cuatro perfiles. No se oculta ese intento fallido.

## Correcciones aplicadas

| Hallazgo | Cambio y evidencia |
|---|---|
| Arduino desconocía los tipos de órdenes al generar prototipos | Tipos trasladados a `domus_types.h`; siete compilaciones finales correctas |
| ADC aceptaba lecturas saturadas | Márgenes interiores al rango 0–4095; nivel requiere tres lecturas válidas consecutivas tras arranque/fallo |
| Una línea larga podía ejecutar su sufijo | Descarte persistente hasta salto de línea; prueba C++ con `RIEGO_ON` tras desbordamiento |
| Recepción Serial podía acaparar el lazo | Máximo 128 bytes por llamada; prueba con flujo de 1,000 bytes comprueba retorno tras 128 |
| Un único nivel activo para todas las cargas | Tabla por salida y perfil económico explícito; ON/OFF probados en ambos perfiles |
| Compra innecesaria para núcleo funcional | Audio/SD/solar marcados opcionales; alternativa al relé adicional documentada |
| BOM no coincidía con firmware/inventario | Sensor resistivo, LCD1602, dos botones y MIC OFF opcional; alternativas de potencia separadas |
| Documentación daba por compilada una versión rota | `COMPILACION_VALIDADA.md` reemplazado con métricas y hash del binario actual |

## Pruebas efectivamente ejecutadas

| Entorno | Alcance | Resultado |
|---|---|---|
| Windows / Python 3.12 | 20 casos de simulador + 22 contratos de firmware | 42 PASS |
| Windows / Python 3.12 | Geometría y paquete de planos | 4 PASS |
| Windows / C++ de escritorio | Prueba nativa | 1 SKIP explícito: no hay compilador host |
| Ubuntu / Python 3.12 + g++ | 20 casos + 22 contratos + prueba nativa de funciones reales en perfiles 0 y 1 | 43 PASS, sin omisiones |
| Windows / Arduino CLI 1.5.1 | N16R8, OPI, 240 MHz, Core 1 | PASS; programa 402,374 B; globales 25,020 B |
| Windows / Arduino CLI 1.5.1 | 4 MB, sin PSRAM, 160 MHz, Core 0 | PASS; programa 397,180 B; globales 24,544 B |
| Windows / Arduino CLI 1.5.1 | 8 MB, QSPI, 80 MHz, Core 1 | PASS; programa 400,066 B; globales 24,620 B |
| Ubuntu / Arduino | N16R8 original | PASS, artefacto generado |
| Ubuntu / Arduino | N16R8 económico | PASS, artefacto generado |
| Ubuntu / Arduino | 4 MB sin PSRAM | PASS, artefacto generado |
| Ubuntu / Arduino | 8 MB QSPI | PASS, artefacto generado |
| Chromium, Firefox, WebKit | 1440×900, 768×1024, 390×844; 9 combinaciones | Controles comprobados correctos, avisos menores abajo |
| Bóveda y mapa de pines | Wikilinks, notas, mapa y visualización | PASS |
| Placa, sensores y cargas reales | Corrientes, temperatura, arranque y cableado | PENDIENTE; hardware no ejercitado |

Todas las compilaciones usan Arduino-ESP32 3.3.10. El perfil reducido sirve
para comprobar portabilidad y margen de tamaño: no demuestra que sustituir la
N16R8 sea conveniente, ni valida ejecución física a esas frecuencias.

La prueba C++ extrae las funciones de producción, usa dispositivos Serial y
ADC simulados y ejecuta aserciones sobre líneas de 40/41 caracteres, entrada
fragmentada, descarte hasta nueva línea, recuperación, límite por ciclo,
valores ADC 0/15/4080/4095 y las cinco salidas en ambas polaridades.
No equivale a ejecutar el sketch entero sobre un ESP32.

## Visualizador

Se revisó [el despliegue público](https://domus-visualizadores-publicos.vercel.app):
rutas principal, `/3d` y `/circuito`, cambio de tema, vista superior, contador
de 111 piezas y selector de siete módulos. Sin desbordamiento horizontal en
los nueve escenarios. Las respuestas principales fueron HTTP 200 o 304.

Queda un aviso menor de favicon: 404 en Chromium y bloqueo de imagen por CSP
en Firefox. También se registraron cancelaciones de peticiones de iframe al
navegar inmediatamente desde el test; los contenidos cargaron en sus rutas
directas y no hubo `pageerror`. No se atribuyen esas cancelaciones a fallos
del firmware. Esta sesión no cambió ni volvió a desplegar el visualizador.
Representa el perfil original; la alternativa económica tiene su diagrama
y tabla pin por pin en [[21 - Simplificacion y reduccion de costos]].

## Límites y mejoras pendientes

- Los nuevos márgenes ADC rechazan saturación, pero no garantizan detectar una
  señal flotante dentro de rango. Calibrar extremos físicos y evaluar polarización
  de entrada o realimentación si se exige detectar desconexión con certeza.
- El S8050 requiere comprobar fabricante/pinout, corriente de arranque,
  saturación y temperatura. Mantener relé si no supera la prueba; ahorro de
  L250 condicionado a esa aceptación y disponibilidad del resto de materiales.
- Medir consumo simultáneo y arranques. El tamaño de memoria global no mide
  pico de heap, fragmentación, estabilidad de alimentación ni temperatura.
- Advertencias de LCD/TinyUSB siguen presentes en dependencias; las compilaciones
  pasan y no se maquillaron esas bibliotecas.
- Voz española, audio y autonomía solar siguen siendo fases opcionales pendientes.
- Antes de cargar, seleccionar perfil y seguir [[19 - Plan de testeo despues de construccion]].

## Revisión de cambios

Veredicto de revisión de software: APPROVE para continuar al banco, confianza
media. No se detectaron nuevos P0/P1 en los cambios revisados. Evidencia: pruebas
nativas de Serial/ADC/polaridad, contratos, compilaciones completas y revisión
de llamadores de salida e interlocks. Esto no es aprobación eléctrica de montaje.

Se preservan cinco funciones domésticas y la compatibilidad de salidas existente.
No se marca todo el proyecto terminado mientras falten pruebas de hardware y voz.
