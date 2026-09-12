/* PROJECT DOMUS v2: controlador local modular ESP32-S3.
 * Banco alfa por un solo costado, sin IR ni controlador doble supuesto.
 * 120 V solo en extensión externa -> cargador USB + fuente 5 V/5 A.
 * El 120 V NUNCA entra a la maqueta.
 */
#include <Arduino.h>
#include <DHT.h>
#include <LiquidCrystal_I2C.h>
#include <Preferences.h>
#include <Wire.h>
#include <esp_heap_caps.h>
#include <esp_task_wdt.h>
#include "domus_config.h"
#include "domus_control.h"
#include "domus_protocol.h"
#include "domus_ir.h"
#include "domus_lcd.h"
#include "domus_voice.h"
using namespace Config;

bool encendida[TOTAL] = {};
Propietario propietario[TOTAL] = {};
bool paro = false, modoSeguro = false, bloqueoBomba = false;
bool watchdogActivo = false, lcdDisponible = false, calibracionGuardada = false;
bool modoAuto = true, muteSW = false;
const char *motivoRechazo = "ninguno", *motivoSeguro = "ninguno";
uint32_t mensajesOmitidos = 0, inicioBomba = 0, ultimaLectura = 0;
uint32_t ultimaDht = 0, ultimaPresencia = 0;
int8_t irPendiente = -1;
uint16_t ultimoIR = 0;
Sensores sensores;
Calibracion calibracion, calibracionPendiente;
DHT dht(PIN_DHT, DHT_TIPO);
LiquidCrystal_I2C lcd27(0x27, 16, 2), lcd3f(0x3F, 16, 2);
LiquidCrystal_I2C *lcd = nullptr;
PantallaBonita pantalla;
IRDOMUS::GestorIR ir;
VozJarvis voz;

void notificar(const char *texto) {
  const size_t longitud = strlen(texto);
  if (Serial.availableForWrite() >= static_cast<int>(longitud + 1)) {
    Serial.write(reinterpret_cast<const uint8_t*>(texto), longitud); Serial.write('\n');
  } else if (mensajesOmitidos != UINT32_MAX) ++mensajesOmitidos;
}

void notificarFormato(const char *formato, ...) {
  char linea[220]; va_list args; va_start(args, formato);
  const int n = vsnprintf(linea, sizeof(linea), formato, args); va_end(args);
  if (n > 0 && n < static_cast<int>(sizeof(linea))) notificar(linea);
  else if (mensajesOmitidos != UINT32_MAX) ++mensajesOmitidos;
}

void escribirSalida(Salida salida, bool activar) {
  if (SALIDA_FISICA_HABILITADA[salida])
    digitalWrite(PINES[salida], (activar != ACTIVA_LOW[salida]) ? HIGH : LOW);
  encendida[salida] = activar;
}
void apagarTodo() { for (uint8_t i=0; i<TOTAL; ++i) escribirSalida(static_cast<Salida>(i), false); }

void entrarModoSeguro(const char *motivo) {
  if (modoSeguro) return;
  motivoSeguro = motivo;
  modoSeguro = true; apagarTodo();
  notificarFormato("EVENTO;MODO_SEGURO;%s", motivoSeguro);
}

bool pedirSalida(Salida salida, bool activar, Propietario origen) {
  motivoRechazo = "ninguno";
  if (salida >= TOTAL) { motivoRechazo = "salida_invalida"; return false; }
  if (!activar) { escribirSalida(salida, false); propietario[salida] = origen; return true; }
  if (!SALIDA_FISICA_HABILITADA[salida]) { motivoRechazo = "salida_sin_etapa_habilitada"; return false; }
  if (paro || digitalRead(PIN_PARO) == LOW) { motivoRechazo = "paro"; return false; }
  if (modoSeguro) { motivoRechazo = "modo_seguro"; return false; }
  if (salida == BOMBA) {
    if (bloqueoBomba) { motivoRechazo = "bomba_requiere_rearme"; return false; }
    if (!calibracionGuardada) { motivoRechazo = "calibracion_requerida"; return false; }
    const int nivel = analogRead(PIN_NIVEL);
    if (!adcValido(nivel) || nivel < calibracion.nivelMinimo) { motivoRechazo = "nivel_no_aprobado"; return false; }
    if (!encendida[BOMBA]) inicioBomba = millis();
  }
  escribirSalida(salida, true); propietario[salida] = origen; return true;
}

void setModoAuto(bool v) {
  modoAuto = v;
  for (uint8_t i = 0; i < TOTAL; ++i) propietario[i] = Propietario::AUTO;
}

int leerPromedio(uint8_t pin) {
  uint32_t suma=0; for (uint8_t i=0; i<8; ++i) { suma += analogRead(pin); delayMicroseconds(150); }
  return static_cast<int>(suma/8);
}

void leerSensores() {
  const uint32_t ahora=millis();
  if (uint32_t(ahora-ultimaLectura) < SENSOR_INTERVALO_MS) return;
  ultimaLectura=ahora;
  sensores.suelo=leerPromedio(PIN_SUELO); sensores.nivel=leerPromedio(PIN_NIVEL); sensores.luz=leerPromedio(PIN_LUZ);
  sensores.sueloValido=adcValido(sensores.suelo); sensores.nivelValido=adcValido(sensores.nivel); sensores.luzValida=adcValido(sensores.luz);
  if (calibracionGuardada && sensores.sueloValido) sensores.sueloPct=porcentajeCalibrado(sensores.suelo,calibracion.sueloSeco,calibracion.sueloHumedo);
  if (calibracionGuardada && sensores.luzValida) sensores.luzPct=porcentajeCalibrado(sensores.luz,calibracion.luzOscura,calibracion.luzClara);
  if (digitalRead(PIN_PIR)==HIGH) ultimaPresencia=ahora;
  sensores.presencia=ultimaPresencia!=0 && uint32_t(ahora-ultimaPresencia)<=PIR_RETENCION_MS;
  if (DHT_HABILITADO && uint32_t(ahora-ultimaDht)>=DHT_INTERVALO_MS) {
    ultimaDht=ahora; const float t=dht.readTemperature(), h=dht.readHumidity();
    sensores.ambienteValido=!isnan(t)&&!isnan(h)&&t>=-10&&t<=60&&h>=0&&h<=100;
    if (sensores.ambienteValido) { sensores.temperatura=t; sensores.humedadAire=h; }
  }
  notificarFormato("SENSORES;SUELO=%d;VS=%d;NIVEL=%d;VN=%d;LUZ=%d;VL=%d;PIR=%d;TEMP=%.1f;HA=%.1f;VA=%d;CAL=%d",
    sensores.suelo,sensores.sueloValido,sensores.nivel,sensores.nivelValido,
    sensores.luz,sensores.luzValida,sensores.presencia,sensores.temperatura,
    sensores.humedadAire,sensores.ambienteValido,calibracionGuardada);
}

void aplicarDecision(Salida salida, DecisionAuto decision) {
  if (propietario[salida]!=Propietario::AUTO || decision==DecisionAuto::NADA) return;
  pedirSalida(salida,decision==DecisionAuto::ENCENDER,Propietario::AUTO);
}

void revisarAutomatizacion() {
  if (!modoAuto) return;
  if (!calibracionGuardada || paro || modoSeguro) return;
  if (!sensores.nivelValido || sensores.nivel<calibracion.nivelMinimo || !sensores.sueloValido) {
    if (encendida[BOMBA] && propietario[BOMBA]==Propietario::AUTO) escribirSalida(BOMBA,false);
  } else aplicarDecision(BOMBA,decidirRiego(sensores.sueloPct,encendida[BOMBA]));
  if (!sensores.ambienteValido) {
    if (encendida[VENTILADOR] && propietario[VENTILADOR]==Propietario::AUTO) escribirSalida(VENTILADOR,false);
  } else aplicarDecision(VENTILADOR,decidirVentilador(sensores.temperatura,encendida[VENTILADOR]));
  if (!sensores.luzValida) {
    if (encendida[SALA] && propietario[SALA]==Propietario::AUTO) escribirSalida(SALA,false);
    if (encendida[INVERNADERO] && propietario[INVERNADERO]==Propietario::AUTO) escribirSalida(INVERNADERO,false);
  } else {
    aplicarDecision(SALA,decidirLuzSala(sensores.luzPct,sensores.presencia,encendida[SALA]));
    aplicarDecision(INVERNADERO,decidirInvernadero(sensores.luzPct,encendida[INVERNADERO]));
  }
}

void revisarSeguridad() {
  if (digitalRead(PIN_PARO)==LOW) { paro=true; apagarTodo(); }
  if (!encendida[BOMBA]) return;
  const int nivel=analogRead(PIN_NIVEL);
  if (!calibracionGuardada || !adcValido(nivel) || nivel<calibracion.nivelMinimo || uint32_t(millis()-inicioBomba)>=BOMBA_MAX_MS) {
    escribirSalida(BOMBA,false); bloqueoBomba=true; notificar("EVENTO;BOMBA_BLOQUEADA;REARMAR_REQUERIDO");
    voz.dice("Riego detenido por seguridad.", 0, notificar);
  }
}
void revisarSalud() { if (esp_get_free_heap_size()<HEAP_CRITICO_BYTES) entrarModoSeguro("heap_critico"); }

// Botón MODO temporal del perfil alfa (GPIO18). El gesto largo solo arma
// aprendizaje cuando el perfil IR está habilitado.
void revisarBoton() {
  static bool crudoAnterior=HIGH,estable=HIGH;
  static uint32_t cambio=0, pressIni=0;
  const bool crudo=digitalRead(PIN_BOTON);
  if (crudo!=crudoAnterior) { crudoAnterior=crudo; cambio=millis(); if (crudo==LOW) pressIni=millis(); }
  if (crudo!=estable && uint32_t(millis()-cambio)>=40) {
    estable=crudo;
    if (estable==HIGH) {
      const uint32_t dur = millis()-pressIni;
      if (dur >= 3000 && IR_HABILITADO) {
        ir.setAprender(!ir.modoAprender());
        notificarFormato("IR;APRENDER=%d", ir.modoAprender());
        pantalla.feedback(ir.modoAprender() ? "IR APRENDER ON" : "IR APRENDER OFF", "Pulsa 21 teclas");
      } else {
        const bool on = !encendida[SALA];
        const Propietario o = on ? Propietario::MANUAL_ON : Propietario::MANUAL_OFF;
        if (pedirSalida(SALA, on, o)) {
          pantalla.feedback(on ? "SALA ON" : "SALA OFF", "Boton fisico");
          voz.dice(on ? "He encendido la luz de la sala." : "He apagado la luz de la sala.", on ? 1 : 2, notificar);
          notificar("ACK;BOTON;SALA");
        } else {
          pantalla.feedback("SALA BLOQUEADA", motivoRechazo);
          voz.error();
          notificarFormato("NACK;BOTON;%s", motivoRechazo);
        }
      }
    }
  }
}

bool detectarI2C(uint8_t direccion) { Wire.beginTransmission(direccion); return Wire.endTransmission()==0; }
void inicializarPantalla() {
  if (!LCD_HABILITADO) return;
  Wire.begin(PIN_LCD_SDA,PIN_LCD_SCL); Wire.setTimeOut(20);
  uint8_t halladas = 0;
  for (uint8_t direccion = 0x08; direccion <= 0x77; ++direccion) {
    if (!detectarI2C(direccion)) continue;
    ++halladas;
    notificarFormato("I2C;ENCONTRADO=0x%02X", direccion);
    if (direccion == 0x27) lcd = &lcd27;
    else if (direccion == 0x3F) lcd = &lcd3f;
  }
  if (!halladas) { notificar("EVENTO;I2C_SIN_DISPOSITIVOS"); return; }
  if (!lcd) { notificar("EVENTO;LCD_DIRECCION_NO_COMPATIBLE"); return; }
  lcd->init(); lcd->backlight();
  pantalla.begin(lcd);
  lcdDisponible=true;
}
void actualizarPantalla() {
  if (!lcdDisponible) return;
  pantalla.actualizar(sensores, encendida, modoAuto, voz.volumen(),
    voz.pausa(), voz.mute(), paro, modoSeguro, voz.ultimaFrase(), ultimoIR,
    calibracionGuardada);
}

void cargarCalibracion() {
  Preferences prefs;
  if (prefs.begin("domus-base",true)) {
    Calibracion leida={};
    if (prefs.getBytesLength("cal")==sizeof(leida) && prefs.getBytes("cal",&leida,sizeof(leida))==sizeof(leida) &&
        calibracionValida(leida) && checksumCalibracion(leida)==leida.checksum) { calibracion=leida; calibracionGuardada=true; }
    prefs.end();
  }
  calibracionPendiente=calibracion;
}
bool parsearValor(const char *texto,const char *prefijo,uint16_t &destino) {
  const size_t n=strlen(prefijo); if (strncmp(texto,prefijo,n)!=0) return false;
  char *fin=nullptr; const long valor=strtol(texto+n,&fin,10);
  if (!fin || *fin || valor<0 || valor>4095) { notificar("NACK;CAL;VALOR"); return true; }
  destino=static_cast<uint16_t>(valor); notificar("ACK;CAL;PENDIENTE"); return true;
}
bool procesarCalibracion(const char *texto) {
  if (iguales(texto,"CAL VER")) {
    notificarFormato("CAL;SECO=%u;HUMEDO=%u;OSCURO=%u;CLARO=%u;NIVEL=%u;GUARDADA=%d",
      calibracionPendiente.sueloSeco,calibracionPendiente.sueloHumedo,calibracionPendiente.luzOscura,
      calibracionPendiente.luzClara,calibracionPendiente.nivelMinimo,calibracionGuardada); return true;
  }
  if (strncmp(texto,"CAL ",4)!=0) return false;
  bool apagadas=true; for (bool estado:encendida) apagadas=apagadas&&!estado;
  if (!paro || !apagadas) { notificar("NACK;CAL;REQUIERE_PARO"); return true; }
  if (iguales(texto,"CAL CANCELAR")) { calibracionPendiente=calibracion; notificar("ACK;CAL;CANCELADA"); return true; }
  if (iguales(texto,"CAL GUARDAR")) {
    if (!calibracionValida(calibracionPendiente)) { notificar("NACK;CAL;RANGOS"); return true; }
    calibracionPendiente.checksum=checksumCalibracion(calibracionPendiente);
    Preferences prefs; bool guardada=false;
    if (prefs.begin("domus-base",false)) { guardada=prefs.putBytes("cal",&calibracionPendiente,sizeof(calibracionPendiente))==sizeof(calibracionPendiente); prefs.end(); }
    if (guardada) { calibracion=calibracionPendiente; calibracionGuardada=true; }
    notificar(guardada?"ACK;CAL;GUARDADA":"NACK;CAL;NVS"); return true;
  }
  if (parsearValor(texto,"CAL SECO=",calibracionPendiente.sueloSeco) ||
      parsearValor(texto,"CAL HUMEDO=",calibracionPendiente.sueloHumedo) ||
      parsearValor(texto,"CAL OSCURO=",calibracionPendiente.luzOscura) ||
      parsearValor(texto,"CAL CLARO=",calibracionPendiente.luzClara) ||
      parsearValor(texto,"CAL NIVEL=",calibracionPendiente.nivelMinimo)) return true;
  notificar("NACK;CAL;CLAVE"); return true;
}

void informarEstado(bool diagnostico) {
  // Ráfagas por UART 115200 (FIFO 128 B vía CH343): pausar tras cada línea
  // para no perderlas. ~10 ms por línea; solo en diagnósticos puntuales.
  if (diagnostico) notificarFormato("DIAGNOSTICO;PLACA=%s;PERFIL=%s;DRIVER=%d;DF=%d;IR=%d;FIS=%d%d%d%d%d;OUT=%d%d%d%d%d;PARO=%d;SEGURO=%d",
    PERFIL_PLACA,PERFIL_PRUEBA,CONTROLADOR_DOBLE_IDENTIFICADO,DFPLAYER_HABILITADO,IR_HABILITADO,
    SALIDA_FISICA_HABILITADA[0],SALIDA_FISICA_HABILITADA[1],SALIDA_FISICA_HABILITADA[2],
    SALIDA_FISICA_HABILITADA[3],SALIDA_FISICA_HABILITADA[4],
    encendida[0],encendida[1],encendida[2],encendida[3],encendida[4],paro,modoSeguro);
    Serial.flush();
  notificarFormato("ESTADO;PARO=%d;SEGURO=%d;BLOQUEO_BOMBA=%d;MODO=%s;VOL=%u;MUTE=%d;PAUSA=%d;OUT=%d%d%d%d%d;CAL=%d;TX_OMITIDOS=%lu",
    paro,modoSeguro,bloqueoBomba,modoAuto?"AUTO":"MANUAL",voz.volumen(),voz.mute(),voz.pausa(),
    encendida[0],encendida[1],encendida[2],encendida[3],encendida[4],calibracionGuardada,
    static_cast<unsigned long>(mensajesOmitidos));
  Serial.flush();
  if (diagnostico) notificarFormato("SALUD;HEAP=%lu;LCD=%d;DHT=%d;IR=%04X;MOTIVO=%s",
    static_cast<unsigned long>(esp_get_free_heap_size()),lcdDisponible,sensores.ambienteValido,ultimoIR,motivoSeguro);
  if (diagnostico) Serial.flush();
  if (diagnostico) notificarFormato("BANCO;PLACA=%s;PERFIL=%s;ADC=15,16,3;PIR=9;IR=OFF;BTN=18;I2C=17,13;MOTORES=%d%d",
    PERFIL_PLACA,PERFIL_PRUEBA,HABILITAR_MOTOR_BOMBA,HABILITAR_MOTOR_VENTILADOR);
  if (diagnostico) Serial.flush();
}

// Alterna una salida por IR/botón con feedback. NO emite Jarvis aquí:
// el llamador emite UNA sola frase humana y UN solo ACK/NACK (ola 1).
bool alternarIR(Salida s, const char* nomOn, const char* nomOff) {
  const bool on = !encendida[s];
  const Propietario o = on ? Propietario::MANUAL_ON : Propietario::MANUAL_OFF;
  if (pedirSalida(s, on, o)) {
    pantalla.feedback(on ? nomOn : nomOff, "Control IR");
    return true;
  }
  pantalla.feedback("BLOQUEADO", motivoRechazo);
  voz.error();
  notificarFormato("NACK;IR;%s", motivoRechazo);
  return false;
}

void ejecutarTeclaIR(IRDOMUS::Tecla t) {
  using namespace IRDOMUS;
  char buf[17];
  switch (t) {
    case T_CH_MENOS:
      setModoAuto(false);
      pantalla.feedback("MODO MANUAL", "Auto no contradice");
      voz.dice("Modo manual activado.", 30, notificar);
      notificar("ACK;IR;MANUAL"); break;
    case T_CH:
      pantalla.siguientePagina();
      snprintf(buf, sizeof(buf), "PAGINA %u/4", pantalla.pagina() + 1);
      pantalla.feedback(buf, "CH cambia pag.");
      notificarFormato("ACK;IR;PAGINA=%u", pantalla.pagina()); break;
    case T_CH_MAS:
      setModoAuto(true);
      pantalla.feedback("MODO AUTO", "Automatico activo");
      voz.dice("Modo automático activado.", 31, notificar);
      notificar("ACK;IR;AUTO"); break;
    case T_ANTERIOR: case T_1: {
      const bool on = !encendida[SALA];
      if (alternarIR(SALA, "SALA ON", "SALA OFF")) {
        voz.dice(on ? "He encendido la luz de la sala." : "He apagado la luz de la sala.", on ? 1 : 2, notificar);
        notificar("ACK;IR;SALA");
      }
      break;
    }
    case T_PLAY:
      voz.setPausa(!voz.pausa());
      pantalla.feedback(voz.pausa() ? "VOZ PAUSADA" : "VOZ ACTIVA", "Play pausa Jarvis");
      if (!voz.pausa()) voz.dice("Voz reanudada.", 32, notificar);
      else notificar("JARVIS;Voz pausada.");
      notificarFormato("ACK;IR;PAUSA=%d", voz.pausa()); break;
    case T_SIGUIENTE: case T_2: {
      const bool on = !encendida[CUARTO];
      if (alternarIR(CUARTO, "DORM ON", "DORM OFF")) {
        voz.dice(on ? "He encendido la luz del dormitorio." : "He apagado la luz del dormitorio.", on ? 3 : 4, notificar);
        notificar("ACK;IR;CUARTO");
      }
      break;
    }
    case T_VOL_MENOS:
      voz.bajar();
      snprintf(buf, sizeof(buf), "VOL %u", voz.volumen());
      pantalla.feedback(buf, "VOL-");
      notificarFormato("ACK;IR;VOL=%u", voz.volumen()); break;
    case T_VOL_MAS:
      voz.subir();
      snprintf(buf, sizeof(buf), "VOL %u", voz.volumen());
      pantalla.feedback(buf, "VOL+");
      notificarFormato("ACK;IR;VOL=%u", voz.volumen()); break;
    case T_EQ:
      informarEstado(true);
      pantalla.feedback("DIAGNOSTICO", "Todo revisado");
      voz.dice("Diagnóstico completado. El sistema funciona correctamente.", 33, notificar);
      notificar("ACK;IR;EQ"); break;
    case T_0:
      apagarTodo();
      for (uint8_t i = 0; i < TOTAL; ++i) propietario[i] = Propietario::MANUAL_OFF;
      pantalla.feedback("TODO APAGADO", "Tecla 0");
      voz.dice("Todas las cargas han sido apagadas.", 10, notificar);
      notificar("ACK;IR;TODO_OFF"); break;
    case T_100MAS:
      muteSW = !muteSW;
      voz.setMute(muteSW || digitalRead(PIN_SILENCIO) == LOW);
      pantalla.feedback(muteSW ? "JARVIS MUTE" : "JARVIS SONIDO", "100+ silencia");
      if (muteSW) notificar("JARVIS;Jarvis silenciado.");
      else voz.dice("Sonido activado.", 34, notificar);
      notificarFormato("ACK;IR;MUTE=%d", muteSW); break;
    case T_200MAS:
      apagarTodo();
      if (digitalRead(PIN_PARO) == LOW) {
        pantalla.feedback("PARO FISICO", "Libera GPIO10");
        notificar("NACK;IR;PARO_FISICO");
      } else {
        paro = false; bloqueoBomba = false;
        pantalla.feedback("REARME OK", "Salidas en OFF");
        voz.dice("Sistema rearmado.", 35, notificar);
        notificar("ACK;IR;REARMAR");
      }
      break;
    case T_3: {
      const bool on = !encendida[INVERNADERO];
      if (alternarIR(INVERNADERO, "CULTIVO ON", "CULTIVO OFF")) {
        voz.dice(on ? "Iluminación suplementaria de cultivo activada." : "Iluminación de cultivo apagada.", on ? 5 : 6, notificar);
        notificar("ACK;IR;CULTIVO");
      }
      break;
    }
    case T_4: {
      const bool on = !encendida[VENTILADOR];
      if (alternarIR(VENTILADOR, "VENT ON", "VENT OFF")) {
        voz.dice(on ? "He encendido la ventilación." : "He apagado la ventilación.", on ? 7 : 8, notificar);
        notificar("ACK;IR;VENT");
      }
      break;
    }
    case T_5: { // riego: pulsación nueva, nivel y timeout mandan.
      if (pedirSalida(BOMBA, true, Propietario::MANUAL_ON)) {
        pantalla.feedback("REGANDO", "Bomba ON");
        if (sensores.sueloValido)
          voz.dice("El suelo está seco y existe agua suficiente. Iniciando riego.", 9, notificar);
        else
          voz.dice("Iniciando riego.", 9, notificar);
        notificar("ACK;IR;RIEGO");
      } else {
        pantalla.feedback("RIEGO NO", motivoRechazo);
        if (strcmp(motivoRechazo, "nivel_no_aprobado") == 0)
          voz.dice("No puedo regar porque el depósito tiene poca agua.", 0, notificar);
        else if (strcmp(motivoRechazo, "calibracion_requerida") == 0)
          voz.dice("Calibración pendiente. No puedo regar.", 0, notificar);
        else voz.error();
        notificarFormato("NACK;IR;RIEGO;%s", motivoRechazo);
      }
      break;
    }
    case T_6:
      if (sensores.ambienteValido) {
        snprintf(buf, sizeof(buf), "T:%4.1fC", sensores.temperatura);
        pantalla.feedback(buf, "Temperatura");
        voz.dice("Temperatura consultada. El valor aparece en pantalla.", 11, notificar);
      } else { pantalla.feedback("SIN DHT", "No hay dato"); voz.error(); }
      notificarFormato("ACK;IR;TEMP=%.1f", sensores.temperatura); break;
    case T_7:
      if (sensores.ambienteValido) {
        snprintf(buf, sizeof(buf), "H:%2.0f%%", sensores.humedadAire);
        pantalla.feedback(buf, "Humedad aire");
        voz.dice("Humedad consultada. El valor aparece en pantalla.", 12, notificar);
      } else { pantalla.feedback("SIN DHT", "No hay dato"); voz.error(); }
      notificarFormato("ACK;IR;HUM=%.1f", sensores.humedadAire); break;
    case T_8:
      snprintf(buf, sizeof(buf), "S:%d%% N:%d", sensores.sueloPct, sensores.nivel);
      pantalla.feedback(buf, "Suelo y nivel");
      voz.dice("Suelo y nivel en pantalla.", 13, notificar);
      notificar("ACK;IR;SUELO_NIVEL"); break;
    case T_9:
      informarEstado(false);
      pantalla.feedback("ESTADO TOTAL", "Revisa Serial");
      voz.dice("Estado completo en pantalla y puerto serial.", 14, notificar);
      notificar("ACK;IR;ESTADO"); break;
    default: break;
  }
}

void revisarIR() {
  IRDOMUS::EventoIR ev = ir.actualizar();
  if (!ev.hay) return;
  ultimoIR = ev.codigo;
  notificarFormato("IR;CMD=0x%02X;PROTO=%u;TECLA=%s;REP=%d",
    ev.codigo, ev.protocolo,
    ev.tecla == IRDOMUS::T_NINGUNA ? "?" : IRDOMUS::GestorIR::nombre(ev.tecla),
    ev.repeticion);
  if (ir.modoAprender()) {
    if (irPendiente >= 0 && ev.tecla == IRDOMUS::T_NINGUNA) {
      // Solo se aprenden códigos nuevos, no se pisan solos.
    }
    if (irPendiente >= 0) {
      ir.grabar(irPendiente, ev.codigo);
      notificarFormato("IR;GRABADA;TECLA=%s;CMD=0x%02X", IRDOMUS::GestorIR::nombre(irPendiente), ev.codigo);
      pantalla.feedback("IR GRABADA", IRDOMUS::GestorIR::nombre(irPendiente));
      irPendiente = -1;
    } else {
      pantalla.feedback("IR CODIGO", "IR GRABAR <n>");
    }
    return;
  }
  if (ev.tecla == IRDOMUS::T_NINGUNA) {
    pantalla.feedback("TECLA NUEVA", "IR LEER p/ mapa");
    return; // desconocida: no ejecuta ninguna carga.
  }
  ejecutarTeclaIR(ev.tecla);
}

bool procesarIRGrabar(const char* texto) {
  const char* p = "IR GRABAR ";
  if (strncmp(texto, p, strlen(p)) != 0) return false;
  if (!IR_HABILITADO) { notificar("NACK;IR;DESHABILITADO_EN_PERFIL"); return true; }
  const long n = strtol(texto + strlen(p), nullptr, 10);
  if (n < 0 || n > 20) { notificar("NACK;IR;TECLA 0-20"); return true; }
  irPendiente = static_cast<int8_t>(n);
  ir.setAprender(true);
  notificarFormato("ACK;IR;ARMANDO_TECLA=%s;PULSA_CONTROL", IRDOMUS::GestorIR::nombre(n));
  pantalla.feedback("PULSA TECLA", IRDOMUS::GestorIR::nombre(n));
  return true;
}

void procesarLinea(const char *texto) {
  if (procesarCalibracion(texto)) return;
  if (procesarIRGrabar(texto)) return;
  const Comando comando=interpretar(texto);
  if (comando.tipo==TipoComando::PARO) { paro=true; apagarTodo(); notificar("ACK;PARO"); }
  else if (comando.tipo==TipoComando::REARMAR) {
    apagarTodo(); if (digitalRead(PIN_PARO)==LOW) notificar("NACK;PARO_FISICO");
    else { paro=false; bloqueoBomba=false; notificar("ACK;REARMAR;SALIDAS_OFF"); }
  } else if (comando.tipo==TipoComando::RECUPERAR) {
    apagarTodo();
    if (paro || digitalRead(PIN_PARO)==LOW) notificar("NACK;RECUPERAR;PARO");
    else if (!watchdogActivo || esp_get_free_heap_size()<HEAP_CRITICO_BYTES+8000) notificar("NACK;RECUPERAR;SALUD");
    else { modoSeguro=false; motivoSeguro="ninguno"; notificar("ACK;RECUPERAR;SALIDAS_OFF"); }
  } else if (comando.tipo==TipoComando::ESTADO) informarEstado(false);
  else if (comando.tipo==TipoComando::DIAGNOSTICO) informarEstado(true);
  else if (comando.tipo==TipoComando::MODO_AUTO) { setModoAuto(true); notificar("ACK;MODO;AUTO"); }
  else if (comando.tipo==TipoComando::MODO_MANUAL) { setModoAuto(false); notificar("ACK;MODO;MANUAL"); }
  else if (comando.tipo==TipoComando::VOL_MAS) { voz.subir(); notificarFormato("ACK;VOL=%u", voz.volumen()); }
  else if (comando.tipo==TipoComando::VOL_MENOS) { voz.bajar(); notificarFormato("ACK;VOL=%u", voz.volumen()); }
  else if (comando.tipo==TipoComando::MUTE) { muteSW=comando.activar; voz.setMute(muteSW); notificarFormato("ACK;MUTE=%d", muteSW); }
  else if (comando.tipo==TipoComando::VOZ) {
    voz.setPausa(!comando.activar); notificarFormato("ACK;VOZ=%d", comando.activar);
  }
  else if (comando.tipo==TipoComando::PAGINA) {
    if (comando.valor < 0) pantalla.siguientePagina();
    else pantalla.setPagina(comando.valor);
    notificarFormato("ACK;PAGINA=%u", pantalla.pagina());
  }
  else if (comando.tipo==TipoComando::IR_LEER && IR_HABILITADO) {
    ir.setAprender(!ir.modoAprender());
    notificarFormato("ACK;IR;APRENDER=%d", ir.modoAprender());
  }
  else if (comando.tipo==TipoComando::IR_LISTA && IR_HABILITADO) {
    for (uint8_t i = 0; i < 21; ++i) {
      notificarFormato("IR;TECLA=%s;CMD=0x%02X", IRDOMUS::GestorIR::nombre(i), ir.codigoDe(i));
      Serial.flush(); // ráfaga 21 líneas por UART 115200: no saturar FIFO.
    }
  }
  else if (comando.tipo==TipoComando::IR_BORRAR && IR_HABILITADO) { ir.borrar(); notificar("ACK;IR;DEFECTO"); }
  else if (comando.tipo==TipoComando::AUTO) { escribirSalida(comando.salida,false); propietario[comando.salida]=Propietario::AUTO; notificar("ACK;AUTO;SALIDA_OFF"); }
  else if (comando.tipo==TipoComando::SALIDA) {
    const Propietario origen=comando.activar?Propietario::MANUAL_ON:Propietario::MANUAL_OFF;
    if (pedirSalida(comando.salida,comando.activar,origen)) notificar("ACK;SALIDA"); else notificarFormato("NACK;SALIDA;%s",motivoRechazo);
  } else notificar("NACK;COMANDO_DESCONOCIDO");
}
void revisarComandos() {
  static ReceptorLineas receptor; static uint32_t ultimaOrdenOn=0; static bool huboOn=false;
  for (uint8_t i=0; i<16 && Serial.available(); ++i) {
    revisarSeguridad(); const auto evento=receptor.recibir(static_cast<char>(Serial.read()));
    if (evento==ReceptorLineas::Evento::PARO) { paro=true; apagarTodo(); notificar("ACK;PARO"); continue; }
    if (evento==ReceptorLineas::Evento::RECHAZADA) { notificar("NACK;LINEA_INVALIDA"); continue; }
    if (evento!=ReceptorLineas::Evento::LINEA) continue;
    const Comando comando=interpretar(receptor.texto());
    if (comando.tipo==TipoComando::SALIDA && comando.activar && huboOn && uint32_t(millis()-ultimaOrdenOn)<250) { notificar("NACK;LIMITE_FRECUENCIA"); continue; }
    if (comando.tipo==TipoComando::SALIDA && comando.activar) { ultimaOrdenOn=millis(); huboOn=true; }
    procesarLinea(receptor.texto());
  }
}

bool inicializarWatchdog() {
  esp_task_wdt_config_t config={.timeout_ms=WATCHDOG_TIMEOUT_MS,.idle_core_mask=0,.trigger_panic=true};
  esp_err_t resultado=esp_task_wdt_init(&config);
  if (resultado==ESP_ERR_INVALID_STATE) resultado=esp_task_wdt_reconfigure(&config);
  return resultado==ESP_OK && (esp_task_wdt_status(nullptr)==ESP_OK || esp_task_wdt_add(nullptr)==ESP_OK);
}
void setup() {
  Serial.begin(115200); delay(200);
  pinMode(PIN_PARO,INPUT_PULLUP); pinMode(PIN_SILENCIO,INPUT_PULLUP); pinMode(PIN_BOTON,INPUT_PULLUP); pinMode(PIN_PIR,INPUT);
  analogReadResolution(12); analogSetAttenuation(ADC_11db);
  for (uint8_t i=0; i<TOTAL; ++i) {
    digitalWrite(PINES[i],ACTIVA_LOW[i]?HIGH:LOW);
    pinMode(PINES[i],SALIDA_FISICA_HABILITADA[i]?OUTPUT:INPUT);
    propietario[i]=Propietario::AUTO;
  }
  paro=digitalRead(PIN_PARO)==LOW; apagarTodo(); cargarCalibracion(); inicializarPantalla();
  if (IR_HABILITADO) ir.begin();
  voz.begin();
  voz.setMute(muteSW || digitalRead(PIN_SILENCIO)==LOW);
  if (DHT_HABILITADO) dht.begin(); watchdogActivo=inicializarWatchdog();
  if (!watchdogActivo) entrarModoSeguro("watchdog");
  notificarFormato("DOMUS_LISTO;PLACA=%s;PERFIL=%s;DRIVER=%d;BOMBA=%d;VENT=%d;IR=%d;BUZZER=%d;BTN=%u;USE_DIAGNOSTICO",
    PERFIL_PLACA,PERFIL_PRUEBA,CONTROLADOR_DOBLE_IDENTIFICADO,HABILITAR_MOTOR_BOMBA,
    HABILITAR_MOTOR_VENTILADOR,IR_HABILITADO,BUZZER_HABILITADO,PIN_BOTON);
  notificar("USA: DIAGNOSTICO para revisar I2C, sensores y salidas bloqueadas");
}
void loop() {
  if (watchdogActivo && esp_task_wdt_reset()!=ESP_OK) { watchdogActivo=false; entrarModoSeguro("watchdog_reset"); }
  revisarSeguridad();
  // Mute por hardware (PIN_SILENCIO a GND) + software (100+).
  voz.setMute(muteSW || digitalRead(PIN_SILENCIO)==LOW);
  revisarBoton(); if (IR_HABILITADO) revisarIR(); revisarComandos(); leerSensores(); revisarAutomatizacion(); revisarSalud(); actualizarPantalla(); voz.actualizar(); delay(1);
}
