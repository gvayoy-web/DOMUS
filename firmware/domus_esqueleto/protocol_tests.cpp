// Regresiones evaluadas por el compilador: un fallo impide generar firmware.
// No consumen RAM/tiempo en la placa y no sustituyen pruebas de hardware.
#include "domus_protocol.h"
using Evento = ReceptorLineas::Evento;

constexpr bool lineaCompleta() {
  ReceptorLineas r;
  for (char c : "SALA ON") {
    if (!c) break;
    if (r.recibir(c) != Evento::NINGUNO) return false;
  }
  return r.recibir('\r') == Evento::LINEA && iguales(r.texto(), "SALA ON") &&
         r.recibir('\n') == Evento::NINGUNO;
}
constexpr bool descartaExceso() {
  ReceptorLineas r;
  for (unsigned i=0; i<60; ++i) r.recibir('x');
  for (char c : "SALA ON") if (c) r.recibir(c);
  return r.recibir('\n') == Evento::RECHAZADA && r.recibir('\n') == Evento::NINGUNO;
}
constexpr bool paroPrioritario() {
  ReceptorLineas r;
  for (unsigned i=0; i<60; ++i) r.recibir('x');
  if (r.recibir('!') != Evento::PARO) return false;
  for (char c : "REARMAR") if (c) r.recibir(c);
  return r.recibir('\n') == Evento::RECHAZADA;
}
constexpr bool byteInvalido() {
  ReceptorLineas r;
  r.recibir('S'); r.recibir('\0');
  return r.recibir('\n') == Evento::RECHAZADA;
}
constexpr bool recuperaLinea() {
  ReceptorLineas r;
  r.recibir('\0'); r.recibir('\n');
  for (char c : "ESTADO") if (c) r.recibir(c);
  return r.recibir('\n') == Evento::LINEA && interpretar(r.texto()).tipo == TipoComando::ESTADO;
}
static_assert(lineaCompleta(), "No ejecutar fragmentos ni duplicar CRLF");
static_assert(descartaExceso(), "No ejecutar sufijo tras desbordamiento");
static_assert(paroPrioritario(), "PARO debe interrumpir incluso descarte");
static_assert(byteInvalido(), "NUL no debe truncar una orden valida");
static_assert(recuperaLinea(), "Recuperacion tras linea invalida");
static_assert(interpretar("s").tipo == TipoComando::INVALIDO, "Retirar comandos de una letra");
static_assert(interpretar("hola SALA ON").tipo == TipoComando::INVALIDO, "No buscar subcadenas");
static_assert(interpretar("SALA ON extra").tipo == TipoComando::INVALIDO, "Sin sufijos");
static_assert(interpretar("BOMBA ON").salida == BOMBA && interpretar("BOMBA ON").activar, "Bomba ON");
static_assert(interpretar("VENTILADOR OFF").salida == VENTILADOR && !interpretar("VENTILADOR OFF").activar, "Ventilador OFF");
static_assert(interpretar("PARO").tipo == TipoComando::PARO, "Paro");
static_assert(interpretar("REARMAR").tipo == TipoComando::REARMAR, "Rearme");
static_assert(interpretar("RECUPERAR").tipo == TipoComando::RECUPERAR, "Recuperacion");
static_assert(interpretar("SALA AUTO").tipo == TipoComando::AUTO, "Modo automatico");
static_assert(interpretar("DIAGNOSTICO").tipo == TipoComando::DIAGNOSTICO, "Diagnostico");
static_assert(interpretar("CAL VER").tipo == TipoComando::CAL_VER, "Calibracion");
