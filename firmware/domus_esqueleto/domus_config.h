#pragma once
#include <stdint.h>

namespace Config {
// No habilitar antes de validar alimentacion, etapas y polaridades fisicas.
constexpr bool SALIDAS_HABILITADAS = false;
constexpr bool LCD_HABILITADO = true;
constexpr bool DHT_HABILITADO = true;
constexpr uint8_t DHT_TIPO = 11; // Cambiar a 22 solo tras identificar el modulo.
constexpr uint32_t BOMBA_MAX_MS = 10000;
constexpr uint32_t SENSOR_INTERVALO_MS = 1000;
constexpr uint32_t DHT_INTERVALO_MS = 2200;
constexpr uint32_t LCD_INTERVALO_MS = 1000;
constexpr uint32_t PIR_RETENCION_MS = 30000;
constexpr uint32_t WATCHDOG_TIMEOUT_MS = 5000;
constexpr uint32_t HEAP_CRITICO_BYTES = 24000;
constexpr uint8_t PIN_SUELO = 1, PIN_NIVEL = 2, PIN_LUZ = 3;
constexpr uint8_t PIN_PIR = 9, PIN_PARO = 10, PIN_MIC_OFF = 11, PIN_BOTON = 12;
constexpr uint8_t PIN_DHT = 14, PIN_LCD_SDA = 21, PIN_LCD_SCL = 13;
constexpr uint8_t PINES[] = {4, 5, 6, 7, 8};
constexpr bool ACTIVA_LOW[] = {true, false, false, false, false};
constexpr uint8_t LCD_DIRECCIONES[] = {0x27, 0x3F};
// Reservas de voz: microfono15/16/17 y DFPlayer18/19.
constexpr uint8_t RESERVADOS[] = {1,2,3,4,5,6,7,8,9,10,11,12,14,21,13,15,16,17,18,19};
constexpr bool pinesUnicos() {
  for (unsigned i = 0; i < sizeof(RESERVADOS); ++i)
    for (unsigned j = i + 1; j < sizeof(RESERVADOS); ++j)
      if (RESERVADOS[i] == RESERVADOS[j]) return false;
  return true;
}
static_assert(pinesUnicos(), "GPIO duplicado");
static_assert(BOMBA_MAX_MS > 0 && BOMBA_MAX_MS <= 120000, "Tiempo bomba invalido");
static_assert(DHT_TIPO == 11 || DHT_TIPO == 22, "DHT_TIPO debe ser 11 o 22");
static_assert(sizeof(PINES) == sizeof(ACTIVA_LOW), "Tabla de salidas inconsistente");
}
