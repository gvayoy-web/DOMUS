---
proyecto: PROJECT DOMUS
tipo: correccion-auditoria
actualizado: 2026-09-12
estado: aplicado_correccion_5
---

# Corrección auditoría 5: mapa autorizado, fuente real, driver primero

Esqueleto congelado: no se tocó `firmware/domus_esqueleto/` (verificado con
`git status` vacío en esa carpeta). Solo `test_esqueleto_control_native.py`
sigue existiendo y pasando, sin modificaciones.

## 1. Mapa autorizado 15/16/17/18 (nota 46/47)

`MAPA_CASA` usa suelo 15, nivel 16, SDA 17, demo/modo 18. Se eliminaron los
`#define` de pines del candidato (`PIN_HUMEDAD`, `PIN_NIVEL_AGUA`, `PIN_LDR`,
`PIN_PIR`, `PIN_PARO_EMERGENCIA`, `PIN_MIC_OFF`, `PIN_BOTON_DEMO`, `PIN_DHT11`,
`I2C_SDA_PIN`, `I2C_SCL_PIN`, `PIN_SALIDA_*`, `PINES_SALIDAS`): 35 sitios
migrados a `MAPA_CASA.*`. MIC (15/16/17) y MP3 (18/19) quedan en `-1`
(FINAL-ONLY, puertas F4/F5) y fuera del registro de unicidad.

## 2. Fuente real

`Wire.begin`, `digitalWrite/Read`, sensores, botones, DHT y `setup()` leen
`MAPA_CASA`; el registro `PINES_RESERVADOS_DOMUS` deriva de él. Prueba
`test_map_is_the_single_pin_source` + contrato de cableado del validador
contra la guía 47.

## 3. Driver antes que etapa

Motores: primero `driver_no_listo`, después `salida_no_instalada`.
Prueba de ejecución `test_despacho_distinque_driver_de_etapa` compila el
despachador real con dos fakes y exige ambos motivos (+ `SALA_OK` intacta).

## 4. Harness nativos al día

`native_integration.cpp` y `test_native_firmware.py` incluyen fake de
`MAPA_CASA` con los valores de producción; la máscara fake es total para
probar despacho (el rechazo real lo cubren candidato + matriz).

## Relaciones

- [[46 - Plan maestro de consolidacion un costado]]
- [[53 - Definicion formal de firmware final y puertas]]
- [[54 - Plan de orden del repositorio]]
