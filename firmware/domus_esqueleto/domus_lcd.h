#pragma once
// PROJECT DOMUS — LCD1602 I2C bonito: páginas, letras grandes, animación.
// 16x2. Cuando se presiona un botón (físico o IR) muestra el texto de la
// acción y después una animación corta. Páginas con CH. Todo no bloqueante.
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>
#include "domus_control.h"

class PantallaBonita {
 public:
  void begin(LiquidCrystal_I2C* lcd) {
    lcd_ = lcd;
    crearIconos();
    splash();
  }
  void splash() {
    if (!lcd_) return;
    // No bloqueante: muestra título y arma feedback corto, sin delay().
    lcd_->clear();
    lcd_->setCursor(0, 0); lcd_->print("PROJECT DOMUS");
    lcd_->setCursor(0, 1); lcd_->print("JARVIS LISTO");
    modo_ = 0; feedbackHasta_ = millis() + 1400;
    snprintf(feedbackTitulo_, sizeof(feedbackTitulo_), "JARVIS LISTO");
    snprintf(feedbackSub_, sizeof(feedbackSub_), "CH cambia pag.");
  }
  // Muestra letras de la acción + animación posterior (1200 ms).
  void feedback(const char* titulo, const char* sub = "") {
    // Copia a buffers propios: el llamador puede pasar char buf[] local.
    snprintf(feedbackTitulo_, sizeof(feedbackTitulo_), "%-16.16s", titulo ? titulo : "");
    snprintf(feedbackSub_, sizeof(feedbackSub_), "%-16.16s", sub ? sub : "");
    feedbackHasta_ = millis() + 1400; animPaso_ = 0; ultimoAnim_ = 0;
  }
  void setPagina(uint8_t p) { pagina_ = p % 4; }
  uint8_t pagina() const { return pagina_; }
  void siguientePagina() { pagina_ = (pagina_ + 1) % 4; }

  // Llamar cada loop. Si hay feedback activo lo muestra con animación,
  // si no la página correspondiente. `jarvisScroll` es la frase larga actual.
  // `cal` = calibración guardada: sin ella jamás se presentan % de sensores.
  void actualizar(const Sensores& s, const bool* enc, bool modoAuto,
                  uint8_t volumen, bool vozOff, bool mute, bool paro,
                  bool seguro, const char* jarvisScroll, uint16_t ultimoIR,
                  bool cal) {
    if (!lcd_) return;
    const uint32_t ahora = millis();
    if (ahora < feedbackHasta_) { dibujarFeedback(ahora); return; }
    // Repintado limitado: 300 ms para animar iconos sin parpadeo agresivo.
    if (ahora - ultimoPag_ < 300) return;
    ultimoPag_ = ahora;
    char f0[17], f1[17];
    const char* spin = "|/-\\";
    char sp = spin[(ahora / 300) % 4];
    switch (pagina_) {
      case 0: // HOME: temperatura / humedad + estado
        if (paro) snprintf(f0, 17, "%c PARO ACTIVO   ", sp);
        else if (seguro) snprintf(f0, 17, "%c MODO SEGURO   ", sp);
        else if (s.ambienteValido) snprintf(f0, 17, "\x02%4.1fC \x01%2.0f%% %c", s.temperatura, s.humedadAire, sp);
        else snprintf(f0, 17, "DHT SIN DATOS %c", sp);
        if (modoAuto) snprintf(f1, 17, "AUTO V%02u %c%c%c%c%c", volumen,
                 enc[1] ? 'S' : '-', enc[2] ? 'C' : '-', enc[4] ? 'I' : '-',
                 enc[3] ? 'V' : '-', enc[0] ? 'R' : '-');
        else snprintf(f1, 17, "MANU V%02u %c%c%c%c%c", volumen,
                 enc[1] ? 'S' : '-', enc[2] ? 'C' : '-', enc[4] ? 'I' : '-',
                 enc[3] ? 'V' : '-', enc[0] ? 'R' : '-');
        break;
      case 1: // Sensores: suelo / nivel / luz + PIR (nunca % sin calibrar)
        if (!cal) {
          snprintf(f0, 17, "CAL PENDIENTE   ");
          snprintf(f1, 17, "PARO y CAL serie");
        } else {
          if (s.sueloValido) snprintf(f0, 17, "\x00S:%3d%% \x03N:%4d", s.sueloPct, s.nivel);
          else snprintf(f0, 17, "\x00S:---  \x03N:%4d", s.nivel);
          if (s.luzValida) snprintf(f1, 17, "\x01L:%3d%% PIR:%c %c", s.luzPct, s.presencia ? '*' : '-', sp);
          else snprintf(f1, 17, "\x01L:---  PIR:%c %c", s.presencia ? '*' : '-', sp);
        }
        break;
      case 2: // Salidas 5 cargas bien dibujadas
        snprintf(f0, 17, "R%c S%c C%c V%c I%c",
                 enc[0] ? '\xFF' : '-', enc[1] ? '\xFF' : '-',
                 enc[2] ? '\xFF' : '-', enc[3] ? '\xFF' : '-',
                 enc[4] ? '\xFF' : '-');
        snprintf(f1, 17, "Rie Sal Dor Ven Inv");
        break;
      default: // Jarvis / IR
        if (mute) snprintf(f0, 17, "\x04 MUTE  V%02u %c", volumen, sp);
        else if (vozOff) snprintf(f0, 17, "\x04 PAUSA V%02u %c", volumen, sp);
        else snprintf(f0, 17, "\x04 JARVIS V%02u %c", volumen, sp);
        if (jarvisScroll && jarvisScroll[0]) {
          // scroll 16 ventanas, 350 ms por paso.
          size_t n = strlen(jarvisScroll);
          uint32_t paso = (ahora / 350) % (n + 1);
          for (uint8_t i = 0; i < 16; ++i) {
            size_t k = paso + i;
            f1[i] = (k < n) ? jarvisScroll[k] : ' ';
          }
          f1[16] = 0;
        } else snprintf(f1, 17, "IR:%04X PAG CH %c", ultimoIR, sp);
        break;
    }
    pintar(f0, f1);
  }

 private:
  void pintar(const char* f0, const char* f1) {
    lcd_->setCursor(0, 0); lcd_->print("                ");
    lcd_->setCursor(0, 0); lcd_->print(f0);
    lcd_->setCursor(0, 1); lcd_->print("                ");
    lcd_->setCursor(0, 1); lcd_->print(f1);
  }
  void dibujarFeedback(uint32_t ahora) {
    // Letras de la acción arriba, animación abajo (barra + spinner).
    if (ahora - ultimoAnim_ < 150) return;
    ultimoAnim_ = ahora; animPaso_++;
    char f0[17], f1[17];
    snprintf(f0, 17, "%-16.16s", feedbackTitulo_);
    const char* spin = "|/-\\";
    char sp = spin[animPaso_ % 4];
    uint8_t n = animPaso_ % 17;
    for (uint8_t i = 0; i < 16; ++i) f1[i] = (i < n) ? (char)255 : '-';
    f1[16] = 0;
    if (feedbackSub_[0]) {
      // alterna sub y barra cada 4 pasos para que se lean las letras.
      if ((animPaso_ / 4) % 2 == 0) snprintf(f1, 17, "%-15.15s%c", feedbackSub_, sp);
    }
    pintar(f0, f1);
  }
  void crearIconos() {
    if (!lcd_) return;
    // 0 gota, 1 sol, 2 termómetro, 3 nivel, 4 voz, 5 candado, 6 flecha, 7 bloque.
    const uint8_t gota[8] = {0x04,0x0A,0x0A,0x11,0x11,0x11,0x0E,0x00};
    const uint8_t sol[8] = {0x15,0x0E,0x1F,0x0E,0x15,0x00,0x00,0x00};
    const uint8_t term[8] = {0x04,0x0A,0x0A,0x0A,0x0E,0x1F,0x1F,0x0E};
    const uint8_t nivel[8] = {0x00,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F,0x00};
    const uint8_t voz[8] = {0x01,0x03,0x07,0xFF,0xFF,0x07,0x03,0x01};
    const uint8_t cand[8] = {0x0E,0x11,0x11,0x1F,0x1B,0x1B,0x1F,0x00};
    lcd_->createChar(0, (uint8_t*)gota); lcd_->createChar(1, (uint8_t*)sol);
    lcd_->createChar(2, (uint8_t*)term); lcd_->createChar(3, (uint8_t*)nivel);
    lcd_->createChar(4, (uint8_t*)voz); lcd_->createChar(5, (uint8_t*)cand);
  }
  LiquidCrystal_I2C* lcd_ = nullptr;
  uint8_t pagina_ = 0, animPaso_ = 0, modo_ = 0;
  uint32_t feedbackHasta_ = 0, ultimoAnim_ = 0, ultimoPag_ = 0;
  // Buffers propios: nunca se conserva el puntero del llamador (podía ser buf[] local).
  char feedbackTitulo_[17] = "";
  char feedbackSub_[17] = "";
};
