#pragma once
// PROJECT DOMUS — voz Jarvis: Serial + LCD + DFPlayer (opcional) + buzzer.
// Frases fijas en español (sin IA/entrenamiento). Si DFPlayer no está
// habilitado o no hay SD, cae a buzzer + Serial + LCD sin bloquear.
#include <Arduino.h>
#include "domus_config.h"

class VozJarvis {
 public:
  void begin() {
    if (Config::BUZZER_HABILITADO) {
      pinMode(Config::PIN_BUZZER, OUTPUT);
      digitalWrite(Config::PIN_BUZZER, LOW);
    }
    if (Config::DFPLAYER_HABILITADO) {
      Serial1.begin(Config::DF_BAUDIOS, SERIAL_8N1, Config::PIN_DF_RX, Config::PIN_DF_TX);
      delay(300);
      dfEnviar(0x3F, 0, 0);  // init
      dfVolumen(volumen_);
    }
  }
  void setVolumen(uint8_t v) {
    volumen_ = constrain(v, Config::JARVIS_VOL_MIN, Config::JARVIS_VOL_MAX);
    if (Config::DFPLAYER_HABILITADO) dfVolumen(volumen_);
  }
  uint8_t volumen() const { return volumen_; }
  void subir() { setVolumen(volumen_ + 2); }
  void bajar() { setVolumen(volumen_ > 2 ? volumen_ - 2 : 0); }
  void setPausa(bool v) { pausa_ = v; }
  bool pausa() const { return pausa_; }
  void setMute(bool v) { mute_ = v; }
  bool mute() const { return mute_; }
  const char* ultimaFrase() const { return ultima_; }

  // Dice una frase: Serial JARVIS; + LCD scroll + DFPlayer track (si hay) + beep.
  // `track`: 0 = sin pista (solo Serial/LCD/beep), 1..99 = 0001.mp3.. en DFPlayer.
  // Copia la frase a buffer propio: el llamador puede pasar buf[] local.
  void dice(const char* frase, uint8_t track = 0, void (*notificar)(const char*) = nullptr) {
    snprintf(ultima_, sizeof(ultima_), "%s", frase ? frase : "");
    if (notificar) {
      char linea[160];
      snprintf(linea, sizeof(linea), "JARVIS;%s", ultima_);
      notificar(linea);
    }
    if (mute_ || pausa_) { beep(1, 60); return; }
    if (Config::DFPLAYER_HABILITADO && track > 0) dfPlay(track);
    else beep(1, 90);
  }

  // Programa pulsos sin bloquear: actualizar() los ejecuta desde el loop.
  // Si el buzzer está deshabilitado en el perfil, no toca GPIO ni demora.
  void beep(uint8_t n = 1, uint16_t ms = 90) {
    if (!Config::BUZZER_HABILITADO || mute_) return;
    if (n == 0) return;
    // Si ya hay una secuencia en curso, la nueva la sustituye (última orden manda).
    pulsosPendientes_ = n;
    pulsoMs_ = ms;
    nivelActual_ = true;
    digitalWrite(Config::PIN_BUZZER, HIGH);
    proximoCambio_ = millis() + ms;
    secuenciaActiva_ = true;
  }
  void error() { beep(2, 160); }

  // Llamar cada loop. Apaga/en alterna el pin sin delay().
  void actualizar() {
    if (!secuenciaActiva_ || !Config::BUZZER_HABILITADO) return;
    const uint32_t ahora = millis();
    if ((int32_t)(ahora - proximoCambio_) < 0) return;
    if (nivelActual_) {
      // Terminó el HIGH de un pulso.
      digitalWrite(Config::PIN_BUZZER, LOW);
      if (pulsosPendientes_ > 0) --pulsosPendientes_;
      if (pulsosPendientes_ == 0) { secuenciaActiva_ = false; return; }
      nivelActual_ = false;
      proximoCambio_ = ahora + 70;  // pausa entre pulsos.
    } else {
      digitalWrite(Config::PIN_BUZZER, HIGH);
      nivelActual_ = true;
      proximoCambio_ = ahora + pulsoMs_;
    }
  }

 private:
  void dfEnviar(uint8_t cmd, uint8_t p1, uint8_t p2) {
    uint8_t t[10] = {0x7E, 0xFF, 0x06, cmd, 0x00, p1, p2, 0x00, 0x00, 0xEF};
    uint16_t sum = 0;
    for (uint8_t i = 1; i < 7; ++i) sum += t[i];
    sum = 0xFFFF - sum + 1;
    t[7] = sum >> 8; t[8] = sum & 0xFF;
    Serial1.write(t, 10);
  }
  void dfPlay(uint8_t track) { dfEnviar(0x03, 0, track); }
  void dfVolumen(uint8_t v) { dfEnviar(0x06, 0, v); }
  uint8_t volumen_ = Config::JARVIS_VOL_DEF;
  bool pausa_ = false, mute_ = false;
  // Buffer propio: nunca se conserva el puntero del llamador.
  char ultima_[160] = "";
  // Estado del beep no bloqueante.
  bool secuenciaActiva_ = false, nivelActual_ = false;
  uint8_t pulsosPendientes_ = 0;
  uint16_t pulsoMs_ = 90;
  uint32_t proximoCambio_ = 0;
};
