#pragma once
#include <stddef.h>
#include <stdint.h>
#include <string.h>

enum Salida : uint8_t { BOMBA, SALA, CUARTO, VENTILADOR, INVERNADERO, TOTAL };
enum class TipoComando : uint8_t { INVALIDO, SALIDA, AUTO, PARO, REARMAR, RECUPERAR, ESTADO, DIAGNOSTICO, CAL_VER };
struct Comando { TipoComando tipo; Salida salida; bool activar; };

constexpr bool iguales(const char* a, const char* b) {
  while (*a && *a == *b) { ++a; ++b; }
  return *a == *b;
}
constexpr Comando interpretar(const char* texto) {
  if (iguales(texto, "PARO")) return {TipoComando::PARO, BOMBA, false};
  if (iguales(texto, "REARMAR")) return {TipoComando::REARMAR, BOMBA, false};
  if (iguales(texto, "RECUPERAR")) return {TipoComando::RECUPERAR, BOMBA, false};
  if (iguales(texto, "ESTADO")) return {TipoComando::ESTADO, BOMBA, false};
  if (iguales(texto, "DIAGNOSTICO")) return {TipoComando::DIAGNOSTICO, BOMBA, false};
  if (iguales(texto, "CAL VER")) return {TipoComando::CAL_VER, BOMBA, false};
  const char* const on[] = {"BOMBA ON","SALA ON","CUARTO ON","VENTILADOR ON","INVERNADERO ON"};
  const char* const off[] = {"BOMBA OFF","SALA OFF","CUARTO OFF","VENTILADOR OFF","INVERNADERO OFF"};
  const char* const automatico[] = {"BOMBA AUTO","SALA AUTO","CUARTO AUTO","VENTILADOR AUTO","INVERNADERO AUTO"};
  for (uint8_t i = 0; i < TOTAL; ++i) {
    if (iguales(texto, on[i])) return {TipoComando::SALIDA, static_cast<Salida>(i), true};
    if (iguales(texto, off[i])) return {TipoComando::SALIDA, static_cast<Salida>(i), false};
    if (iguales(texto, automatico[i])) return {TipoComando::AUTO, static_cast<Salida>(i), false};
  }
  return {TipoComando::INVALIDO, BOMBA, false};
}

// Una linea completa; desbordamiento o byte no textual invalida toda la linea.
// '!' tiene prioridad incluso durante descarte; no permite ejecutar el sufijo.
class ReceptorLineas {
 public:
  enum class Evento { NINGUNO, LINEA, RECHAZADA, PARO };
  constexpr Evento recibir(char c) {
    if (c == '!') { usado_ = 0; descarte_ = true; return Evento::PARO; }
    if (c == '\r' || c == '\n') {
      if (descarte_) { reiniciar(); return Evento::RECHAZADA; }
      if (!usado_) return Evento::NINGUNO;
      texto_[usado_] = '\0'; usado_ = 0; return Evento::LINEA;
    }
    if (descarte_) return Evento::NINGUNO;
    if (c < 32 || c > 126 || usado_ >= sizeof(texto_) - 1) {
      descarte_ = true; usado_ = 0; return Evento::NINGUNO;
    }
    texto_[usado_++] = c;
    return Evento::NINGUNO;
  }
  constexpr const char* texto() const { return texto_; }
 private:
  constexpr void reiniciar() { usado_ = 0; descarte_ = false; }
  char texto_[48] = {};
  size_t usado_ = 0;
  bool descarte_ = false;
};
