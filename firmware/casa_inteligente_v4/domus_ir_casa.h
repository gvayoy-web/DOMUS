#pragma once
// Receptor IR del firmware de producto. Aprende las 21 teclas CAR MP3 y
// conserva el mapa en NVS. El pin se entrega en begin() para que MAPA_CASA
// siga siendo la unica fuente de GPIO.
#include <Arduino.h>
#include <Preferences.h>
#include <IRremote.hpp>

namespace IRCasa {
enum Tecla : uint8_t {
  CH_MENOS = 0, CH = 1, CH_MAS = 2, ANTERIOR = 3, PLAY = 4,
  SIGUIENTE = 5, VOL_MENOS = 6, VOL_MAS = 7, EQ = 8, N_0 = 9,
  N_100_MAS = 10, N_200_MAS = 11, N_1 = 12, N_2 = 13, N_3 = 14,
  N_4 = 15, N_5 = 16, N_6 = 17, N_7 = 18, N_8 = 19, N_9 = 20,
  TOTAL = 21, NINGUNA = 255
};

constexpr uint16_t CODIGOS_INICIALES[TOTAL] = {
  0x45, 0x46, 0x47, 0x44, 0x40, 0x43, 0x07, 0x15, 0x09,
  0x16, 0x19, 0x0D, 0x0C, 0x18, 0x5E, 0x08, 0x1C,
  0x5A, 0x42, 0x52, 0x4A
};
constexpr const char* NOMBRES[TOTAL] = {
  "CH-", "CH", "CH+", "ANTERIOR", "PLAY", "SIGUIENTE",
  "VOL-", "VOL+", "EQ", "0", "100+", "200+",
  "1", "2", "3", "4", "5", "6", "7", "8", "9"
};

struct Evento {
  bool hay = false;
  Tecla tecla = NINGUNA;
  bool repeticion = false;
  uint16_t codigo = 0;
  uint8_t protocolo = 0;
};

class Receptor {
 public:
  void begin(uint8_t pin) {
    preferencias_.begin("domus-ir", false);
    for (uint8_t i = 0; i < TOTAL; ++i) {
      uint16_t valor = preferencias_.getUShort(clave(i), 0xFFFF);
      tabla_[i] = valor == 0xFFFF ? CODIGOS_INICIALES[i] : valor;
    }
    IrReceiver.begin(pin, DISABLE_LED_FEEDBACK);
  }

  Evento actualizar() {
    Evento evento;
    if (!IrReceiver.decode()) return evento;
    evento.codigo = IrReceiver.decodedIRData.command;
    evento.protocolo = IrReceiver.decodedIRData.protocol;
    evento.repeticion =
      (IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT) != 0;
    ultimoCodigo_ = evento.codigo;
    evento.tecla = buscar(evento.codigo);
    IrReceiver.resume();

    // Una pulsacion sostenida no repite acciones. Solo volumen admite repeat
    // limitado, aunque audio permanezca deshabilitado en el banco.
    if (evento.repeticion && evento.tecla != VOL_MENOS && evento.tecla != VOL_MAS)
      return Evento{};
    if (evento.repeticion) {
      if (millis() - ultimoVolumenMs_ < 150) return Evento{};
      ultimoVolumenMs_ = millis();
    }
    evento.hay = true;
    return evento;
  }

  bool grabar(uint8_t indice, uint16_t codigo) {
    if (indice >= TOTAL) return false;
    tabla_[indice] = codigo;
    return preferencias_.putUShort(clave(indice), codigo) == sizeof(uint16_t);
  }
  void borrar() {
    for (uint8_t i = 0; i < TOTAL; ++i) {
      tabla_[i] = CODIGOS_INICIALES[i];
      preferencias_.remove(clave(i));
    }
  }
  uint16_t codigo(uint8_t indice) const { return indice < TOTAL ? tabla_[indice] : 0; }
  uint16_t ultimoCodigo() const { return ultimoCodigo_; }
  static const char* nombre(uint8_t indice) { return indice < TOTAL ? NOMBRES[indice] : "?"; }

 private:
  Tecla buscar(uint16_t codigo) const {
    for (uint8_t i = 0; i < TOTAL; ++i)
      if (tabla_[i] == codigo) return static_cast<Tecla>(i);
    return NINGUNA;
  }
  const char* clave(uint8_t indice) {
    static char buffer[8];
    snprintf(buffer, sizeof(buffer), "k%02u", indice);
    return buffer;
  }
  Preferences preferencias_;
  uint16_t tabla_[TOTAL] = {};
  uint16_t ultimoCodigo_ = 0;
  uint32_t ultimoVolumenMs_ = 0;
};
}  // namespace IRCasa
