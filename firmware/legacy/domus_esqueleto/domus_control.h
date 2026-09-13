#pragma once
#include <stdint.h>
#include "domus_protocol.h"

enum class Propietario : uint8_t { AUTO, MANUAL_ON, MANUAL_OFF };

struct Calibracion {
  uint16_t version = 1;
  uint16_t sueloSeco = 0;
  uint16_t sueloHumedo = 0;
  uint16_t luzOscura = 0;
  uint16_t luzClara = 0;
  uint16_t nivelMinimo = 0;
  uint32_t checksum = 0;
};

struct Sensores {
  int suelo = 0, nivel = 0, luz = 0;
  int sueloPct = 0, luzPct = 0;
  float temperatura = 0, humedadAire = 0;
  bool sueloValido = false, nivelValido = false, luzValida = false;
  bool ambienteValido = false, presencia = false;
};

constexpr bool adcValido(int valor) { return valor > 20 && valor < 4075; }
constexpr int distancia(int a, int b) { return a > b ? a - b : b - a; }
constexpr int porcentajeCalibrado(int valor, int cero, int cien) {
  if (cero == cien) return 0;
  const long calculado = (long(valor) - cero) * 100L / (long(cien) - cero);
  return calculado < 0 ? 0 : (calculado > 100 ? 100 : int(calculado));
}
constexpr bool calibracionValida(const Calibracion &c) {
  return c.version == 1 && adcValido(c.sueloSeco) && adcValido(c.sueloHumedo) &&
         adcValido(c.luzOscura) && adcValido(c.luzClara) && adcValido(c.nivelMinimo) &&
         distancia(c.sueloSeco, c.sueloHumedo) >= 100 &&
         distancia(c.luzOscura, c.luzClara) >= 100;
}
inline uint32_t checksumCalibracion(const Calibracion &c) {
  const uint8_t *bytes = reinterpret_cast<const uint8_t*>(&c);
  uint32_t hash = 2166136261u;
  for (size_t i = 0; i < sizeof(Calibracion) - sizeof(c.checksum); ++i) {
    hash ^= bytes[i]; hash *= 16777619u;
  }
  return hash;
}

enum class DecisionAuto : int8_t { APAGAR = -1, NADA = 0, ENCENDER = 1 };
constexpr DecisionAuto decidirRiego(int humedadPct, bool bombaEncendida) {
  return !bombaEncendida && humedadPct <= 35 ? DecisionAuto::ENCENDER :
         bombaEncendida && humedadPct >= 45 ? DecisionAuto::APAGAR : DecisionAuto::NADA;
}
constexpr DecisionAuto decidirVentilador(float temp, bool encendido) {
  return !encendido && temp >= 28.0f ? DecisionAuto::ENCENDER :
         encendido && temp <= 26.0f ? DecisionAuto::APAGAR : DecisionAuto::NADA;
}
constexpr DecisionAuto decidirLuzSala(int luzPct, bool presencia, bool encendida) {
  return !encendida && presencia && luzPct <= 30 ? DecisionAuto::ENCENDER :
         encendida && (!presencia || luzPct >= 45) ? DecisionAuto::APAGAR : DecisionAuto::NADA;
}
constexpr DecisionAuto decidirInvernadero(int luzPct, bool encendida) {
  return !encendida && luzPct <= 25 ? DecisionAuto::ENCENDER :
         encendida && luzPct >= 40 ? DecisionAuto::APAGAR : DecisionAuto::NADA;
}

static_assert(porcentajeCalibrado(2000, 3000, 1000) == 50, "Calibracion invertida");
static_assert(decidirRiego(35, false) == DecisionAuto::ENCENDER, "Riego seco");
static_assert(decidirRiego(45, true) == DecisionAuto::APAGAR, "Riego humedo");
static_assert(decidirVentilador(28, false) == DecisionAuto::ENCENDER, "Ventilacion");
static_assert(decidirLuzSala(20, true, false) == DecisionAuto::ENCENDER, "Luz sala");
