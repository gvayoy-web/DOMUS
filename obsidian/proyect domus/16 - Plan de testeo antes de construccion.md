---
proyecto: PROJECT DOMUS
tipo: plan-pruebas-preconstruccion
actualizado: 2026-09-04
estado: plan_terminado_pendiente_hardware
---

# Plan de testeo antes de construcción

> [!IMPORTANT]
> El plan de pruebas está terminado. Los casilleros siguen pendientes porque
> requieren módulos, instrumentos y montaje físicos; no son código faltante.

## Regla de aprobación

No cortar, pegar ni montar permanentemente hasta que las pruebas T00–T10 estén
en **PASS**. Una prueba fallida detiene la secuencia; se corrige y se repite
desde la última etapa segura.

## Seguridad del banco

- Trabajar únicamente con 5 V/3.3 V DC; nunca tensión de red en la maqueta.
- Usar fuente regulada con límite de corriente, fusible y switch general.
- Mantener bomba/depósito en bandeja separada y electrónica elevada.
- No hacer cambios de cableado con la fuente conectada.
- No alimentar motores, relés, WS2812 o audio desde el pin 3.3 V del ESP32.
- Verificar polaridad y continuidad antes de insertar el ESP32.

## Registro mínimo por prueba

Anotar: ID, fecha, firmware/hash, conexión usada, tensión sin carga/con carga,
corriente, resultado, evidencia y corrección aplicada.

## Secuencia T00–T10

### T00 — documentación y pinout

- [ ] Fotografiar ambas caras del ESP32-S3 N16R8.
- [ ] Confirmar que GPIO1–21, 38, 39, 47 y 48 estén realmente expuestos.
- [ ] Marcar como provisionales GPIO2, 9, 13, audio 40/41/42 y WS2812.
- [ ] Comparar el mapa físico con [[05 - Auditoria de pines y cableado]].

**PASS:** no existe pin asignado que esté ausente, reservado o duplicado.

### T01 — continuidad sin energía

- [ ] Confirmar que 5 V y GND no estén en corto.
- [ ] Confirmar GND común en ramas que lo requieren.
- [ ] Revisar orientación de diodos, capacitores y conectores.
- [ ] Verificar que SPK− del MAX98357A no vaya a GND.

**PASS:** continuidad correcta y resistencia entre 5 V/GND no indica corto.

### T02 — fuente y distribución

- [ ] Probar fuente, fusible, switch y barra en estrella sin ESP32.
- [ ] Medir 5 V sin carga y con cargas de prueba.
- [ ] Confirmar que ningún cable/conector se caliente.

**PASS:** tensión estable dentro de la tolerancia de los módulos y sin calor.

### T03 — ESP32 solo

- [ ] Cargar el binario validado con todas las cargas desconectadas.
- [ ] Ejecutar cinco arranques.
- [ ] Consultar `ESTADO` y `DIAGNOSTICO`.
- [ ] Probar `PARO`, `REARMAR` y `RECUPERAR`.

**PASS:** cinco arranques, cero bucles de reset y diagnóstico coherente.

### T04 — entradas y sensores, uno por uno

- [ ] LCD I2C con adaptación de nivel si el backpack usa pull-ups a 5 V.
- [ ] DHT, LDR, PIR, humedad de suelo y nivel de agua por separado.
- [ ] Paro, MIC OFF y botón demo conectados a GND con `INPUT_PULLUP`.
- [ ] Calibrar extremos ADC y documentar valores reales.
- [ ] Desconectar cada sensor para verificar el estado seguro.

**PASS:** valores plausibles, sin superar 3.3 V en GPIO y fallo seguro.

### T05 — relés sin cargas reales

- [ ] Alimentar bobinas desde 5 V, no desde 3.3 V.
- [ ] Confirmar si la entrada es activa en LOW.
- [ ] Probar GPIO4–GPIO8 usando LEDs/carga ficticia en los contactos.
- [ ] Ejecutar ON/OFF/AUTO y comprobar una sola conmutación por orden.

**PASS:** arranque sin pulsos, cinco canales correctos y lógica confirmada.

### T06 — cargas reales, una por una

- [ ] Luz sala, luz dormitorio y luz invernadero.
- [ ] Ventilador con supresión de transitorios.
- [ ] Bomba en bandeja con agua; nunca en seco.
- [ ] Medir corriente y caída de 5 V de cada carga.

**PASS:** cada carga funciona sin reset, caída excesiva ni calentamiento.

### T07 — seguridad de bomba y agua

- [ ] Nivel bajo bloquea encendido manual y automático.
- [ ] Humedad inválida corta riego automático.
- [ ] Timeout de 120 s corta incluso con sensor defectuoso.
- [ ] Revisar fugas, bucles antigoteo y bandeja.

**PASS:** los tres bloqueos son independientes y no hay agua cerca de electrónica.

### T08 — concurrencia y fallos

- [ ] Encender la combinación de mayor consumo prevista.
- [ ] Inyectar ráfaga de más de 12 comandos/s y verificar que `PARO` responde.
- [ ] Simular sensor desconectado, microSD ausente y Jarvis deshabilitado.
- [ ] Confirmar que el núcleo permanece operativo.

**PASS:** sin reset; las cargas críticas pasan a estado seguro.

### T09 — audio y Jarvis, fase opcional

- [ ] Probar INMP441 aislado a 3.3 V.
- [ ] Probar MAX98357A/altavoz aislados a 5 V.
- [ ] Confirmar pines de audio sin conflicto antes de integrarlos.
- [ ] No activar `JARVIS_LOCAL_HABILITADO` sin modelo versionado y métricas.

**PASS:** cada PoC funciona solo y su fallo no afecta el firmware doméstico.

### T10 — prueba prolongada y decisión de construcción

- [ ] Ejecutar primero 60 minutos y después ocho horas.
- [ ] Registrar `MEM_LIBRE`, `MEM_MIN`, errores y reinicios.
- [ ] Realizar tres ciclos completos de demostración.
- [ ] Repetir cinco arranques al terminar.

**PASS:** cero resets, memoria estable, cero activaciones peligrosas y tres demos.

## Puerta GO / NO-GO

**GO:** T00–T10 aplicables en PASS, pinout firmado, consumos anotados y ningún
cable provisional en funciones críticas.

**NO-GO:** cualquier pin dudoso, GPIO por encima de 3.3 V, reset con cargas,
relé que pulsa al arrancar, fuga, calentamiento o protección de bomba fallida.

Después de aprobar, cablear siguiendo
[[17 - Diagramas generales de conexiones]] y la tabla exacta de
[[18 - Manual maestro de conexiones pin por pin]].
