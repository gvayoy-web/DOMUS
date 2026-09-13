#pragma once
// PROJECT DOMUS — receptor IR CAR MP3 21 teclas (HX1838 / VS1838B / TSOP1838).
// Protocolo NEC. Los códigos pueden variar entre controles: hay modo aprender
// que guarda la tabla en NVS y valores Keyes por defecto.
//
// Medidas contra fallos (pedidas por Isaac):
// - Cada pulsación se acepta una sola vez; se ignoran tramas repeat,
//   salvo VOL+ / VOL- con repetición controlada (150 ms).
// - Riego (tecla 5) exige pulsación nueva; mantener no extiende.
// - El remoto nunca sustituye el PARO físico GPIO10.
// - Orden desconocida no ejecuta ninguna carga.
// - Último código siempre por Serial para diagnosticar el control.
#include <Arduino.h>
#include <Preferences.h>
#include <IRremote.hpp>
#include "domus_config.h"

namespace IRDOMUS {
// Orden de teclas físicas del CAR MP3.
enum Tecla : uint8_t {
  T_CH_MENOS = 0, T_CH = 1, T_CH_MAS = 2,
  T_ANTERIOR = 3, T_PLAY = 4, T_SIGUIENTE = 5,
  T_VOL_MENOS = 6, T_VOL_MAS = 7, T_EQ = 8,
  T_0 = 9, T_100MAS = 10, T_200MAS = 11,
  T_1 = 12, T_2 = 13, T_3 = 14, T_4 = 15, T_5 = 16,
  T_6 = 17, T_7 = 18, T_8 = 19, T_9 = 20,
  T_TOTAL = 21, T_NINGUNA = 255
};
// Códigos Keyes por defecto (command NEC, address 0x00). Se sobrescriben al aprender.
constexpr uint16_t CODIGOS_DEF[21] = {
  0x45, 0x46, 0x47, 0x44, 0x40, 0x43, 0x07, 0x15, 0x09,
  0x16, 0x19, 0x0D, 0x0C, 0x18, 0x5E, 0x08, 0x1C,
  0x5A, 0x42, 0x52, 0x4A
};
constexpr const char* NOMBRES[21] = {
  "CH-", "CH", "CH+", "ANTERIOR", "PLAY", "SIGUIENTE",
  "VOL-", "VOL+", "EQ", "0", "100+", "200+",
  "1", "2", "3", "4", "5", "6", "7", "8", "9"
};

struct EventoIR {
  bool hay = false;
  Tecla tecla = T_NINGUNA;
  bool repeticion = false;
  uint16_t codigo = 0;
  uint8_t protocolo = 0;
};

class GestorIR {
 public:
  void begin() {
    prefs_.begin("domus-ir", false);
    for (uint8_t i = 0; i < 21; ++i) {
      uint16_t v = prefs_.getUShort(nombreClave(i), 0xFFFF);
      tabla_[i] = (v == 0xFFFF) ? CODIGOS_DEF[i] : v;
    }
    aprender_ = prefs_.getBool("aprender", false);
    IrReceiver.begin(Config::PIN_IR, DISABLE_LED_FEEDBACK);
  }
  // Llamar cada loop. Devuelve evento aceptado (repeat ya filtrado salvo VOL).
  EventoIR actualizar() {
    EventoIR ev;
    if (!IrReceiver.decode()) return ev;
    const uint16_t cmd = IrReceiver.decodedIRData.command;
    const uint8_t proto = IrReceiver.decodedIRData.protocol;
    const bool rep = (IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT) != 0;
    ultimoCodigo_ = cmd; ultimoProto_ = proto; huboCodigo_ = true;
    IrReceiver.resume();
    Tecla t = buscar(cmd);
    ev.codigo = cmd; ev.protocolo = proto; ev.repeticion = rep; ev.tecla = t;
    // Antirrebote repeat: solo VOL acepta repeat, con throttle.
    if (rep && t != T_VOL_MENOS && t != T_VOL_MAS) return EventoIR{};
    if (rep && (t == T_VOL_MENOS || t == T_VOL_MAS)) {
      if (millis() - ultimoVol_ < 150) return EventoIR{};
      ultimoVol_ = millis();
    }
    // Riego exige pulsación nueva.
    if (t == T_5 && rep) return EventoIR{};
    if (t == T_NINGUNA) { ev.hay = true; return ev; } // desconocida: avisar, no actuar.
    ev.hay = true;
    return ev;
  }
  Tecla buscar(uint16_t cmd) const {
    for (uint8_t i = 0; i < 21; ++i) if (tabla_[i] == cmd) return static_cast<Tecla>(i);
    return T_NINGUNA;
  }
  bool modoAprender() const { return aprender_; }
  void setAprender(bool v) { aprender_ = v; prefs_.putBool("aprender", v); }
  // Graba la próxima tecla indicada con el último código recibido.
  bool grabar(uint8_t tecla, uint16_t codigo) {
    if (tecla >= 21) return false;
    tabla_[tecla] = codigo;
    prefs_.putUShort(nombreClave(tecla), codigo);
    return true;
  }
  void borrar() {
    for (uint8_t i = 0; i < 21; ++i) { tabla_[i] = CODIGOS_DEF[i]; prefs_.remove(nombreClave(i)); }
  }
  uint16_t codigoDe(uint8_t tecla) const { return tecla < 21 ? tabla_[tecla] : 0; }
  uint16_t ultimoCodigo() const { return ultimoCodigo_; }
  uint8_t ultimoProto() const { return ultimoProto_; }
  bool huboCodigo() const { return huboCodigo_; }
  void limpiarFlag() { huboCodigo_ = false; }
  static const char* nombre(uint8_t t) { return t < 21 ? NOMBRES[t] : "?"; }

 private:
  const char* nombreClave(uint8_t i) {
    // claves cortas: k00..k20 (buffer estático rotativo).
    static char buf[4][8]; static uint8_t idx = 0;
    char* b = buf[idx++ & 3];
    snprintf(b, 8, "k%02u", i);
    return b;
  }
  Preferences prefs_;
  uint16_t tabla_[21] = {};
  bool aprender_ = false;
  uint16_t ultimoCodigo_ = 0;
  uint8_t ultimoProto_ = 0;
  bool huboCodigo_ = false;
  uint32_t ultimoVol_ = 0;
};
} // namespace IRDOMUS
