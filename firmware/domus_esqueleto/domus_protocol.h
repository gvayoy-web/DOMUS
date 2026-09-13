#pragma once
#include <stddef.h>
#include <stdint.h>
#include <string.h>

enum Salida : uint8_t { BOMBA, SALA, CUARTO, VENTILADOR, INVERNADERO, TOTAL };
enum class TipoComando : uint8_t { INVALIDO, SALIDA, AUTO, PARO, REARMAR, RECUPERAR, ESTADO, DIAGNOSTICO, PRUEBA, CAL_VER,
  MODO_AUTO, MODO_MANUAL, VOL_MAS, VOL_MENOS, MUTE, VOZ, PAGINA, IR_LEER, IR_LISTA, IR_BORRAR };
struct Comando { TipoComando tipo; Salida salida; bool activar; int valor; };

constexpr bool iguales(const char* a, const char* b) {
  while (*a && *a == *b) { ++a; ++b; }
  return *a == *b;
}
constexpr Comando interpretar(const char* texto) {
  if (iguales(texto, "PARO")) return {TipoComando::PARO, BOMBA, false, 0};
  if (iguales(texto, "REARMAR")) return {TipoComando::REARMAR, BOMBA, false, 0};
  if (iguales(texto, "RECUPERAR")) return {TipoComando::RECUPERAR, BOMBA, false, 0};
  if (iguales(texto, "ESTADO")) return {TipoComando::ESTADO, BOMBA, false, 0};
  if (iguales(texto, "DIAGNOSTICO")) return {TipoComando::DIAGNOSTICO, BOMBA, false, 0};
  if (iguales(texto, "PRUEBA")) return {TipoComando::PRUEBA, BOMBA, false, 0};
  if (iguales(texto, "CAL VER")) return {TipoComando::CAL_VER, BOMBA, false, 0};
  if (iguales(texto, "MODO AUTO")) return {TipoComando::MODO_AUTO, BOMBA, false, 0};
  if (iguales(texto, "MODO MANUAL")) return {TipoComando::MODO_MANUAL, BOMBA, false, 0};
  if (iguales(texto, "VOL+")) return {TipoComando::VOL_MAS, BOMBA, false, 0};
  if (iguales(texto, "VOL-")) return {TipoComando::VOL_MENOS, BOMBA, false, 0};
  if (iguales(texto, "MUTE ON")) return {TipoComando::MUTE, BOMBA, true, 0};
  if (iguales(texto, "MUTE OFF")) return {TipoComando::MUTE, BOMBA, false, 0};
  if (iguales(texto, "VOZ ON")) return {TipoComando::VOZ, BOMBA, true, 0};
  if (iguales(texto, "VOZ OFF")) return {TipoComando::VOZ, BOMBA, false, 0};
  if (iguales(texto, "PAGINA")) return {TipoComando::PAGINA, BOMBA, false, -1};
  if (iguales(texto, "PAGINA 0")) return {TipoComando::PAGINA, BOMBA, false, 0};
  if (iguales(texto, "PAGINA 1")) return {TipoComando::PAGINA, BOMBA, false, 1};
  if (iguales(texto, "PAGINA 2")) return {TipoComando::PAGINA, BOMBA, false, 2};
  if (iguales(texto, "PAGINA 3")) return {TipoComando::PAGINA, BOMBA, false, 3};
  if (iguales(texto, "IR LEER")) return {TipoComando::IR_LEER, BOMBA, false, 0};
  if (iguales(texto, "IR LISTA")) return {TipoComando::IR_LISTA, BOMBA, false, 0};
  if (iguales(texto, "IR BORRAR")) return {TipoComando::IR_BORRAR, BOMBA, false, 0};
  const char* const on[] = {"BOMBA ON","SALA ON","CUARTO ON","VENTILADOR ON","INVERNADERO ON"};
  const char* const off[] = {"BOMBA OFF","SALA OFF","CUARTO OFF","VENTILADOR OFF","INVERNADERO OFF"};
  const char* const automatico[] = {"BOMBA AUTO","SALA AUTO","CUARTO AUTO","VENTILADOR AUTO","INVERNADERO AUTO"};
  for (uint8_t i = 0; i < TOTAL; ++i) {
    if (iguales(texto, on[i])) return {TipoComando::SALIDA, static_cast<Salida>(i), true, 0};
    if (iguales(texto, off[i])) return {TipoComando::SALIDA, static_cast<Salida>(i), false, 0};
    if (iguales(texto, automatico[i])) return {TipoComando::AUTO, static_cast<Salida>(i), false, 0};
  }
  return {TipoComando::INVALIDO, BOMBA, false, 0};
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
