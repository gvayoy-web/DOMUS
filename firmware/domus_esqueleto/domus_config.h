#pragma once
#include <stdint.h>

// PROJECT DOMUS v2 — banco IR + LCD + Jarvis + DRV8833 listo.
// Placa: ESP32-S3 N16R8. Alimentación banco: USB / fuente regulada.
// Alimentación final (cuando llegue): extensión 120 V AC -> cargador USB ESP32
// + fuente cerrada 5 V/5 A -> portafusible 4 A lento -> switch 5 A DC -> bus 5 V.
// El 120 V NUNCA entra a la maqueta ni a la protoboard.
//
// Cambios v2:
// - IR HX1838/VS1838B S/OUT -> GPIO12 (VCC->3V3, GND->GND, leer serigrafía S/+/-).
// - BOTON sala se mueve GPIO12 -> GPIO16 (el 12 lo ocupa el IR).
// - Buzzer activo 5 V via S8050 -> GPIO15.
// - DFPlayer (opcional, ya tienes) Serial1 RX=18 TX=17, 9600. No usar GPIO19/20 (USB).
// - DRV8833 (compra): AIN1=GPIO4 bomba, BIN1=GPIO7 ventilador, AIN2/BIN2=GND,
//   nSLEEP=3V3, VM=5 V bus, GND común. Sin diodos externos.
// - Sala/cuarto/invernadero son LED (ya tienes), bomba/vent se habilitan con DRV.
namespace Config {
constexpr bool HABILITAR_BOMBA = false;   // banco: false. Con DRV medido: true.
constexpr bool USAR_DRV8833 = false;      // true solo cuando el DRV esté medido.
constexpr bool DFPLAYER_HABILITADO = false; // true solo con DFPlayer + microSD cableados.
constexpr const char PERFIL_PLACA[] = "ESP32-S3-N16R8";
constexpr const char PERFIL_PRUEBA[] = "BANCO_IR_LCD";
constexpr bool LCD_HABILITADO = true;
constexpr bool DHT_HABILITADO = true;
constexpr uint8_t DHT_TIPO = 11; // Cambiar a 22 solo tras identificar el modulo.
constexpr uint32_t BOMBA_MAX_MS = 10000; // banco 10 s. Final 120000.
constexpr uint32_t SENSOR_INTERVALO_MS = 1000;
constexpr uint32_t DHT_INTERVALO_MS = 2200;
constexpr uint32_t LCD_INTERVALO_MS = 250; // UI fluida; el repintado real se limita.
constexpr uint32_t PIR_RETENCION_MS = 30000;
constexpr uint32_t WATCHDOG_TIMEOUT_MS = 5000;
constexpr uint32_t HEAP_CRITICO_BYTES = 24000;
// Sensores / entradas
constexpr uint8_t PIN_SUELO = 1, PIN_NIVEL = 2, PIN_LUZ = 3;
constexpr uint8_t PIN_PIR = 9, PIN_PARO = 10, PIN_SILENCIO = 11, PIN_BOTON = 16;
constexpr uint8_t PIN_DHT = 14, PIN_LCD_SDA = 21, PIN_LCD_SCL = 13;
// Salidas lógicas 5 cargas: 0 bomba, 1 sala, 2 cuarto, 3 ventilador, 4 invernadero.
constexpr uint8_t PINES[] = {4, 5, 6, 7, 8};
// Buzzer activo 5 V via S8050 (segundo transistor). HIGH = suena.
constexpr uint8_t PIN_BUZZER = 15;
// IR receptor (VS1838B/TSOP1838/HX1838 en placa): S/OUT a este pin.
constexpr uint8_t PIN_IR = 12;
// DFPlayer Mini Serial1 (opcional). ESP_RX <- DF_TX, ESP_TX -> DF_RX (con 1 k).
constexpr uint8_t PIN_DF_RX = 18, PIN_DF_TX = 17;
constexpr uint32_t DF_BAUDIOS = 9600;
// I2S MAX98357A futuro (EXCLUSIVO con DFPlayer en 17/18): BCLK=16 LRC=17 DIN=18.
constexpr uint8_t PIN_I2S_BCLK = 16, PIN_I2S_LRC = 17, PIN_I2S_DIN = 18;
// Habilitación física: LEDs ya (sala/cuarto/invernadero), motores solo con DRV.
constexpr bool SALIDA_FISICA_HABILITADA[] = {
  HABILITAR_BOMBA && USAR_DRV8833, true, true, HABILITAR_BOMBA && USAR_DRV8833, true
};
// DRV8833 es HIGH activo. Relé desnudo queda fuera del núcleo (demo separada).
constexpr bool ACTIVA_LOW[] = {false, false, false, false, false};
constexpr uint8_t LCD_DIRECCIONES[] = {0x27, 0x3F};
// Jarvis voz (runtime, no flash): volumen DFPlayer 0-30.
constexpr uint8_t JARVIS_VOL_DEF = 20, JARVIS_VOL_MIN = 0, JARVIS_VOL_MAX = 30;
// Reservas: no cablear 19/20 (USB nativo S3).
constexpr uint8_t RESERVADOS[] = {1,2,3,4,5,6,7,8,9,10,11,12,14,21,13,15,16,17,18};
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
static_assert(sizeof(PINES) == sizeof(SALIDA_FISICA_HABILITADA), "Mascara fisica inconsistente");
} // namespace Config
