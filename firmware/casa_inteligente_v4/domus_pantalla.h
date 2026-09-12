#pragma once
// PROJECT DOMUS - Pantalla final LCD1602 I2C (16x2).
// Interfaz de producto: saludo breve no bloqueante con PROJECT DOMUS,
// cinco pantallas fijas de 16x2, campos de ancho fijo con relleno y
// truncado, escritura diferencial con memoria sombra y rotacion manual
// sin pausas bloqueantes. Solo depende de Arduino.h y LiquidCrystal_I2C.h.
//
// Reglas de dibujo:
// - El borrado total solo ocurre en begin y al cambiar de vista; jamas
//   en cada ciclo. Entre ciclos solo se reescriben los caracteres que
//   difieren de la sombra char[2][17] mediante setCursor.
// - Cada linea se normaliza a 16 caracteres exactos con snprintf y el
//   formato "%-16.16s": lo corto se rellena con espacios y lo largo se
//   trunca, asi nunca quedan restos de la vista anterior.
// - Sensor invalido muestra ERR y jamas un porcentaje inventado.
// - La vista 4 (emergencia / error) tiene prioridad absoluta: mientras
//   haya paro, modo seguro o mensaje de error se impone sobre el indice
//   manual. El puntero al LCD puede ser nulo (modo sin pantalla): en ese
//   caso la logica avanza igual y el resto del sistema no se detiene.
// - Iconos CGRAM sencillos (gota, sol, termometro, nivel, voz) creados
//   una sola vez en begin; ocupan un caracter cada uno.
#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

// Estado resumido de una salida para la vista 3.
enum EstadoSalidaFinal : uint8_t {
  SAL_OFF = 0,
  SAL_ON = 1,
  SAL_AUTO = 2,
  SAL_BLOQ = 3,
  SAL_ERR = 4
};

// Instantanea de lo que la pantalla puede mostrar. La construye el .ino
// con las lecturas ya validadas; esta clase solo formatea y dibuja.
struct DatosPantallaFinal {
  float tempC;
  bool tempValida;
  float humAire;
  bool humAireValida;
  int sueloPct;
  bool sueloValido;
  int nivelRaw;
  bool nivelValido;
  int nivelMin;
  int luzPct;
  bool luzValida;
  bool presencia;
  EstadoSalidaFinal salidas[5];
  bool emergencia;
  bool modoSeguro;
  const char* error;   // nullptr o "" significa sin error visible
  bool escuchando;     // ventana de voz activa: mensaje estatico breve
  bool micOn;
};

class PantallaFinal {
 public:
  static const uint8_t NUM_PANTALLAS = 5;
  static const uint8_t P_EMERGENCIA = 4;

  PantallaFinal()
      : lcd_(nullptr),
        indice_(0),
        ultimaDibujada_(ID_SPLASH),
        splashHecho_(false),
        inicioMs_(0) {
    for (uint8_t f = 0; f < 2; ++f) {
      for (uint8_t c = 0; c < 17; ++c) sombra_[f][c] = 0;
    }
  }

  // Guarda el objeto LCD (puede ser nulo), crea los iconos, deja el
  // saludo listo y hace el unico borrado total del arranque.
  void begin(LiquidCrystal_I2C* lcd) {
    lcd_ = lcd;
    indice_ = 0;
    ultimaDibujada_ = ID_SPLASH;
    splashHecho_ = false;
    inicioMs_ = millis();
    for (uint8_t f = 0; f < 2; ++f) {
      for (uint8_t c = 0; c < 17; ++c) sombra_[f][c] = 0;
    }
    if (lcd_ != nullptr) {
      crearIconos();
      lcd_->clear();
    }
  }

  // Rotacion manual (boton demo / MODO). Solo cambia el indice.
  void siguiente() {
    indice_ = (uint8_t)((indice_ + 1) % NUM_PANTALLAS);
  }

  void anterior() {
    indice_ = (uint8_t)((indice_ + NUM_PANTALLAS - 1) % NUM_PANTALLAS);
  }

  void irA(uint8_t i) {
    if (i < NUM_PANTALLAS) indice_ = i;
  }

  uint8_t indice() const { return indice_; }

  // Vista que realmente se dibuja: la 4 se impone ante paro, modo
  // seguro o mensaje de error; si no, manda el indice manual.
  uint8_t efectiva(const DatosPantallaFinal& d) const {
    if (d.emergencia || d.modoSeguro) return P_EMERGENCIA;
    if (d.error != nullptr && d.error[0] != '\0') return P_EMERGENCIA;
    return indice_;
  }

  // Formateo puro de una vista a dos lineas de 16 caracteres exactos.
  // No toca el hardware: sirve para pruebas en PC y para el dibujo.
  void formatear(uint8_t pantalla, const DatosPantallaFinal& d,
                 char l0[17], char l1[17]) const {
    if (pantalla >= NUM_PANTALLAS) pantalla = 0;
    char a[24];
    char b[24];
    switch (pantalla) {
      case 0:  // Temperatura + humedad ambiental (aire, DHT11).
        if (d.tempValida) {
          snprintf(a, sizeof(a), "\x03 T aire %dC", (int)d.tempC);
        } else {
          snprintf(a, sizeof(a), "\x03 T aire ERR");
        }
        if (d.humAireValida) {
          snprintf(b, sizeof(b), "H aire %d%%", (int)d.humAire);
        } else {
          snprintf(b, sizeof(b), "H aire ERR");
        }
        break;
      case 1:  // Humedad de suelo + nivel del deposito.
        if (d.sueloValido) {
          snprintf(a, sizeof(a), "\x01 Suelo %d%%", d.sueloPct);
        } else {
          snprintf(a, sizeof(a), "\x01 Suelo ERR");
        }
        if (!d.nivelValido) {
          snprintf(b, sizeof(b), "Nivel ERR");
        } else if (d.nivelRaw < d.nivelMin) {
          snprintf(b, sizeof(b), "Nivel BAJO");
        } else {
          snprintf(b, sizeof(b), "Nivel %d", d.nivelRaw);
        }
        break;
      case 2:  // Luz ambiental + presencia.
        if (d.luzValida) {
          snprintf(a, sizeof(a), "\x02 Luz %d%%", d.luzPct);
        } else {
          snprintf(a, sizeof(a), "\x02 Luz ERR");
        }
        snprintf(b, sizeof(b), "Presencia %s", d.presencia ? "SI" : "NO");
        break;
      case 3: {  // Estado de las 5 salidas.
        snprintf(a, sizeof(a), "B:%s S:%s C:%s", etiq(d.salidas[0]),
                 etiq(d.salidas[1]), etiq(d.salidas[2]));
        snprintf(b, sizeof(b), "V:%s I:%s", etiq(d.salidas[3]),
                 etiq(d.salidas[4]));
        break;
      }
      case 4: {  // Emergencia / error, prioridad absoluta.
        const char* msg = (d.error != nullptr) ? d.error : "";
        if (d.emergencia) {
          snprintf(a, sizeof(a), "!! EMERGENCIA !!");
          if (msg[0] != '\0') {
            snprintf(b, sizeof(b), "%s", msg);
          } else {
            snprintf(b, sizeof(b), "PARO ACTIVO");
          }
        } else if (d.modoSeguro) {
          snprintf(a, sizeof(a), "!! MODO SEGURO !");
          if (msg[0] != '\0') {
            snprintf(b, sizeof(b), "%s", msg);
          } else {
            snprintf(b, sizeof(b), "MODO SEGURO");
          }
        } else if (msg[0] != '\0') {
          snprintf(a, sizeof(a), "ERROR:");
          snprintf(b, sizeof(b), "%s", msg);
        } else {
          snprintf(a, sizeof(a), "Sistema OK");
          snprintf(b, sizeof(b), "Sin errores");
        }
        break;
      }
      default:
        snprintf(a, sizeof(a), "PROJECT DOMUS");
        snprintf(b, sizeof(b), "Iniciando...");
        break;
    }
    snprintf(l0, 17, "%-16.16s", a);
    snprintf(l1, 17, "%-16.16s", b);
  }

  // Refresco principal: decide saludo, emergencia, escucha o vista
  // manual y dibuja solo lo que cambio. Nunca bloquea.
  void tick(const DatosPantallaFinal& d) {
    char l0[17];
    char l1[17];
    uint8_t id;
    if (!splashHecho_) {
      if (millis() - inicioMs_ < SPLASH_MS) {
        id = ID_SPLASH;
        lineasSplash(l0, l1);
        dibujar(l0, l1, ultimaDibujada_ != id);
        ultimaDibujada_ = id;
        return;
      }
      splashHecho_ = true;
    }
    if (d.emergencia || d.modoSeguro ||
        (d.error != nullptr && d.error[0] != '\0')) {
      id = P_EMERGENCIA;
      formatear(P_EMERGENCIA, d, l0, l1);
    } else if (d.escuchando) {
      id = ID_ESCUCHA;
      lineasEscucha(d.micOn, l0, l1);
    } else {
      id = indice_;
      formatear(indice_, d, l0, l1);
    }
    dibujar(l0, l1, ultimaDibujada_ != id);
    ultimaDibujada_ = id;
  }

  // Ultima linea dibujada (sombra), para diagnostico y pruebas.
  const char* linea(uint8_t f) const {
    return (f < 2) ? sombra_[f] : "";
  }

 private:
  static const uint8_t ID_ESCUCHA = 98;
  static const uint8_t ID_SPLASH = 99;
  static const unsigned long SPLASH_MS = 2000;

  static const char* etiq(EstadoSalidaFinal e) {
    switch (e) {
      case SAL_ON: return "ON";
      case SAL_AUTO: return "AUTO";
      case SAL_BLOQ: return "BLOQ";
      case SAL_ERR: return "ERR";
      case SAL_OFF:
      default: return "OFF";
    }
  }

  void lineasSplash(char l0[17], char l1[17]) const {
    snprintf(l0, 17, "%-16.16s", "PROJECT DOMUS");
    snprintf(l1, 17, "%-16.16s", "Iniciando...");
  }

  void lineasEscucha(bool micOn, char l0[17], char l1[17]) const {
    snprintf(l0, 17, "%-16.16s", "\x05 Escuchando...");
    if (micOn) {
      snprintf(l1, 17, "%-16.16s", "Di una orden");
    } else {
      snprintf(l1, 17, "%-16.16s", "MIC OFF");
    }
  }

  // Iconos de 5x8 en las posiciones 1 a 5 de la CGRAM.
  void crearIconos() {
    if (lcd_ == nullptr) return;
    uint8_t gota[8] = {0x04, 0x04, 0x0A, 0x0A, 0x11, 0x11, 0x0E, 0x00};
    uint8_t sol[8] = {0x00, 0x15, 0x0E, 0x1F, 0x0E, 0x15, 0x00, 0x00};
    uint8_t termo[8] = {0x04, 0x0A, 0x0A, 0x0E, 0x0E, 0x1F, 0x1F, 0x0E};
    uint8_t nivel[8] = {0x0E, 0x11, 0x11, 0x13, 0x1D, 0x1F, 0x1F, 0x00};
    uint8_t voz[8] = {0x04, 0x0E, 0x15, 0x15, 0x0E, 0x04, 0x00, 0x00};
    lcd_->createChar(1, gota);
    lcd_->createChar(2, sol);
    lcd_->createChar(3, termo);
    lcd_->createChar(4, nivel);
    lcd_->createChar(5, voz);
  }

  // Dibuja con la sombra: borrado total solo al cambiar de vista;
  // si no, reescribe caracter por caracter lo que difiere.
  void dibujar(const char l0[17], const char l1[17], bool cambio) {
    if (lcd_ == nullptr) {
      for (uint8_t c = 0; c < 17; ++c) {
        sombra_[0][c] = l0[c];
        sombra_[1][c] = l1[c];
      }
      return;
    }
    if (cambio) {
      lcd_->clear();
      for (uint8_t f = 0; f < 2; ++f) {
        const char* n = (f == 0) ? l0 : l1;
        lcd_->setCursor(0, f);
        for (uint8_t c = 0; c < 16; ++c) lcd_->print(n[c]);
      }
    } else {
      for (uint8_t f = 0; f < 2; ++f) {
        const char* n = (f == 0) ? l0 : l1;
        for (uint8_t c = 0; c < 16; ++c) {
          if (n[c] != sombra_[f][c]) {
            lcd_->setCursor(c, f);
            lcd_->print(n[c]);
          }
        }
      }
    }
    for (uint8_t c = 0; c < 17; ++c) {
      sombra_[0][c] = l0[c];
      sombra_[1][c] = l1[c];
    }
  }

  LiquidCrystal_I2C* lcd_;
  uint8_t indice_;
  uint8_t ultimaDibujada_;
  bool splashHecho_;
  unsigned long inicioMs_;
  char sombra_[2][17];
};
