---
proyecto: PROJECT DOMUS
tipo: bitacora
actualizado: 2026-09-03
estado: historico_bitacora
---

# Bitácora de implementación

## 2026-09-01 — inicio de la migración

### DECIDIDO

- El firmware usa cinco salidas lógicas: bomba, sala, dormitorio, ventilador e invernadero.
- GPIO2 deja de representar un sensor de viento inexistente y pasa a la entrada analógica provisional del nivel de agua.
- GPIO9 queda reservado provisionalmente para el PIR.
- GPIO13 sustituye al GPIO22 inexistente como SCL provisional. Debe confirmarse que GPIO13 está expuesto en la placa física antes de cablear.
- `MANUAL_OFF` bloquea la reactivación automática hasta recibir el comando `*_AUTO` o reiniciar de forma controlada.

### IMPLEMENTADO EN SOFTWARE

- Simulador ampliado de 13 a 17 pruebas; todas pasan.
- Casos añadidos para las cinco cargas, MIC OFF, contrato de microSD y respuestas de Jarvis.
- Firmware reducido de ocho relés lógicos a cinco.
- Eliminada la lectura del supuesto sensor de viento.
- Añadida lectura de nivel de agua con bloqueo de la bomba.
- Añadida automatización de sala por PIR + LDR con retención de 30 segundos.
- Añadida histéresis para iluminación de sala e invernadero.
- Añadidos comandos `RIEGO_AUTO`, `LUZ1_AUTO`, `LUZ2_AUTO`, `VENT_AUTO` e `INVER_AUTO`.
- Corregidas las medidas resumidas de la maqueta para coincidir con `01_FINAL_V2/design/lista_corte.csv`: base de 100 × 65 cm y vivienda de 43 × 32.5 cm.
- Arduino CLI 1.5.1 verificado por SHA-256 e instalado de forma portátil dentro del entorno ignorado del proyecto.
- Firmware recompilado correctamente para ESP32-S3 N16R8 con Arduino-ESP32 3.3.10: 652,663 bytes de programa y 35,208 bytes de memoria global.
- Eliminada la única advertencia originada en el archivo principal; permanece únicamente el aviso de compatibilidad declarado por LiquidCrystal I2C 1.1.2.

### PENDIENTE DE MEDIR

- Confirmar GPIO13, GPIO9 y GPIO2 en la serigrafía exacta del ESP32-S3 N16R8.
- Calibrar `NIVEL_AGUA_MINIMO_CRUDO`; el valor 600 es únicamente un punto de partida seguro.
- Confirmar si el DHT físico es DHT11 o DHT22.
- Calibrar extremos del sensor resistivo de suelo y del LDR.
- Confirmar nivel activo del PIR y del módulo de relés.

### PENDIENTE DE VALIDAR

- Bloque BLE legado retirado; comandos de diagnóstico migrados a USB Serial local.
- Cargar en placa y ejecutar cinco arranques sin pulsos.
- Verificar el corte de bomba por nivel bajo y por 120 segundos con carga real.
- Comprobar que cada orden produce como máximo una conmutación.

> [!WARNING]
> No cablear todavía usando los pines provisionales. La corrección elimina GPIO22 del software, pero la fotografía/serigrafía de la placa sigue siendo el criterio final.

## 2026-09-02 — cierre de la fase verificable por software

### IMPLEMENTADO Y VALIDADO

- BLE y sus dependencias fueron retirados; diagnóstico y control migrados a USB Serial local.
- OLED y sus dependencias fueron retirados; LCD1602 es la única pantalla.
- Añadidos paro físico en GPIO10, MIC OFF en GPIO11 y botón de demostración en GPIO12, todos provisionales hasta confirmar la placa.
- El paro bloquea todo encendido y exige `REARMAR`; el rearme no enciende cargas ni borra `MANUAL_OFF`.
- Añadido soporte microSD SPI provisional en GPIO38/39/47/48, registro local y prueba real de escritura/lectura. `MICROSD_HABILITADA=false` permanece hasta montar el lector.
- Ejecutadas 18 pruebas de comportamiento y 9 pruebas de contrato: 27/27 correctas.
- Compilación ESP32-S3 N16R8 correcta: 399,078 bytes de programa, 24,948 bytes globales y binario de 399,232 bytes.
- SHA-256 del binario principal: `FBF52C10664BBF1400045FF52B11EC98F894AFFCC543D5DACAF2EF280D5F3D10`.

### ÚNICAMENTE PENDIENTE DE HARDWARE O DATOS REALES

- Confirmar todos los pines provisionales en la serigrafía de la placa.
- Calibrar DHT, humedad de suelo, LDR, nivel de agua, PIR y lógica de relés.
- Conectar la placa y ejecutar los ciclos físicos de arranque, bomba, ventilador y luces.
- Montar lector/tarjeta microSD y cambiar `MICROSD_HABILITADA` a `true` solo después de confirmar el cableado.
- Comprar/probar INMP441, MAX98357A y altavoz; grabar el dataset y entrenar los modelos TinyML antes de habilitar Jarvis.

## 2026-09-02 — gemelo digital y planos v3

### IMPLEMENTADO Y VALIDADO

- Rediseñado el modelo de exposición como gemelo digital offline con 203 piezas identificables.
- Añadidas ocho vistas: presentación, frontal, superior, interior, radiografía de sistemas, agua/riego, electricidad y explotada.
- Añadidos búsqueda, selección, aislamiento, 20 capas, etiquetas configurables, inspector dimensional y controles accesibles.
- El modo Radiografía distingue estructura, elementos removibles, agua, energía, señal y sensores sin ocultar su recorrido.
- El visor funciona como un único HTML local, sin recursos HTTP ni dependencias de red.
- Generados OBJ/MTL, inventario geométrico, render general, corte interior y vista explotada desde una única fuente regenerable.
- Creado un juego de planos técnicos A3 de seis páginas: portada, planta, elevaciones/sección, electricidad, riego y montaje/corte.
- Verificación real en Chromium a 1440×900 y 390×844: sin desbordamientos ni errores JavaScript.
- Objetivos táctiles móviles de 44 px e inspector técnico colapsable; la selección se limpia al ocultar su pieza.
- Las 203 piezas tienen una nota técnica; no se inventaron GPIO ni especificaciones de hardware.
- Evaluación visual independiente final: `PASS`.

### FUENTE DE VERDAD Y SALIDAS

- Generador: `assets/new/deliverables/execute/01_FINAL_V2/design/generate_design.py`.
- Visor: `assets/new/deliverables/execute/01_FINAL_V2/design/modelo_3d_interactivo.html`.
- Plano final: `output/pdf/planos_tecnicos_project_domus.pdf`.
- Regeneración: ejecutar el generador con el Python del proyecto; produce 203 elementos y todas las salidas visuales.

> [!NOTE]
> El plano eléctrico v3 es funcional y evita fijar GPIO no verificados. La tabla de cableado y la serigrafía de la placa siguen teniendo autoridad antes del montaje físico.

## 2026-09-03 — cierre lógico y protección anti-colapso

### IMPLEMENTADO Y VALIDADO

- Añadida histéresis de riego 35/45 % y ventilación 28/26 °C; simulador y firmware comparten límites.
- Añadido modo seguro que apaga cargas y bloquea encendidos sin reiniciar el ESP32.
- El supervisor entra en modo seguro con menos de 32 KiB libres o después de tres reinicios críticos consecutivos.
- `RECUPERAR` solo libera el modo seguro con al menos 64 KiB libres y sin emergencia; las cargas permanecen apagadas.
- Limitadas las entradas a 12 comandos por segundo, excepto `PARO`, que siempre tiene prioridad.
- Fallos de humedad, DHT o LDR apagan inmediatamente las salidas que fueron encendidas automáticamente.
- El búfer Serial reserva memoria una vez y tanto registros como eventos permanecen acotados.
- El simulador incorpora modo seguro, recuperación, límite de órdenes e indicadores de emergencia.
- Ejecutadas 20 pruebas de comportamiento y 18 contratos: 38/38 correctas.
- Añadido contrato de compilación para impedir GPIO duplicados y umbrales de
  histéresis/recuperación invertidos.
- Añadida visualización central interactiva de energía, módulos y pines.
- CI ejecuta ambas suites antes de compilar el firmware.

### BLOQUEADO EXTERNAMENTE, NO POR CÓDIGO

- Pinout final, calibraciones y cargas requieren la placa y mediciones físicas.
- La voz requiere INMP441, MAX98357A, altavoz, dataset y modelos int8 validados.
- `JARVIS_LOCAL_HABILITADO=false` y `MICROSD_HABILITADA=false` siguen siendo estados correctos hasta disponer de esos artefactos.

## 2026-09-07 — entorno semirreal, energía y documentación

- Campaña determinista de 10,000 pasos: 40,027 invariantes, 40 PARO, 22 modos
  seguros, 28 reinicios y 134 fallos de sensor; resultado PASS.
- Total local consolidado: 50 PASS y 5 SKIP nativos dependientes de CI; IA 16 PASS.
- Alimentación cerrada a fuente común regulada de 5 V. Batería y panel solar
  quedan como estética eléctricamente desconectada.
- Aclarado que 16 MB flash + 8 MB PSRAM corresponde al código oficial `N16R8`;
  “N8R16” se conserva como descripción comercial memoria/RAM del propietario.
- Diagnosticado `DHT.h: No such file or directory` como dependencia ausente del
  sketchbook de Arduino IDE. Se documentaron bibliotecas y versiones.
- Revisados 70 archivos Markdown; se actualizaron fuentes operativas y se
  preservaron reportes antiguos como evidencia histórica.

## 2026-09-07 — primera carga real del esqueleto

- Detectado ESP32-S3 mediante CH343 en COM9; `esptool` confirmó revisión 0.2 y
  PSRAM embebida de 8 MB.
- Compilado y cargado `domus_esqueleto` N16R8: 373,694 bytes de programa y
  24,388 bytes globales; todos los bloques fueron verificados por hash.
- Arranque real sin sensores ni módulos: LCD no detectado, DHT inválido y ADC
  flotante, resultados esperados para pines desconectados.
- `DIAGNOSTICO` confirmó `BANCO_SIN_ACTUADORES`, `SALIDAS=0`, `OUT=00000`,
  `PARO=0` y `SEGURO=0`.
- Corregido el orden del diagnóstico para que la primera línea sea
  autocontenida aunque el búfer serie omita telemetría secundaria.
