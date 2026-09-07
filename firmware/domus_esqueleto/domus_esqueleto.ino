/* PROJECT DOMUS: controlador local modular ESP32-S3.
 * Hardware confirmado: LCD1602/I2C, DHT, suelo, nivel, LDR, PIR, un rele,
 * tres LED y driver de ventilador. Voz, red y solar quedan fuera.
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
using namespace Config;

bool encendida[TOTAL] = {};
Propietario propietario[TOTAL] = {};
bool paro = false, modoSeguro = false, bloqueoBomba = false;
bool watchdogActivo = false, lcdDisponible = false, calibracionGuardada = false;
const char *motivoRechazo = "ninguno", *motivoSeguro = "ninguno";
uint32_t mensajesOmitidos = 0, inicioBomba = 0, ultimaLectura = 0;
uint32_t ultimaDht = 0, ultimaPantalla = 0, ultimaPresencia = 0;
Sensores sensores;
Calibracion calibracion, calibracionPendiente;
DHT dht(PIN_DHT, DHT_TIPO);
LiquidCrystal_I2C lcd27(0x27, 16, 2), lcd3f(0x3F, 16, 2);
LiquidCrystal_I2C *lcd = nullptr;

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
  if (SALIDAS_HABILITADAS)
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
  if (!SALIDAS_HABILITADAS) { motivoRechazo = "salidas_deshabilitadas"; return false; }
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
  notificarFormato("SENSORES;SUELO=%d;NIVEL=%d;LUZ=%d;PIR=%d;TEMP=%.1f;HA=%.1f;CAL=%d",
    sensores.suelo,sensores.nivel,sensores.luz,sensores.presencia,sensores.temperatura,sensores.humedadAire,calibracionGuardada);
}

void aplicarDecision(Salida salida, DecisionAuto decision) {
  if (propietario[salida]!=Propietario::AUTO || decision==DecisionAuto::NADA) return;
  pedirSalida(salida,decision==DecisionAuto::ENCENDER,Propietario::AUTO);
}

void revisarAutomatizacion() {
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
  }
}
void revisarSalud() { if (esp_get_free_heap_size()<HEAP_CRITICO_BYTES) entrarModoSeguro("heap_critico"); }

void revisarBoton() {
  static bool crudoAnterior=HIGH,estable=HIGH; static uint32_t cambio=0;
  const bool crudo=digitalRead(PIN_BOTON);
  if (crudo!=crudoAnterior) { crudoAnterior=crudo; cambio=millis(); }
  if (crudo!=estable && uint32_t(millis()-cambio)>=40) {
    estable=crudo;
    if (estable==LOW) pedirSalida(SALA,!encendida[SALA],!encendida[SALA]?Propietario::MANUAL_ON:Propietario::MANUAL_OFF);
  }
}

bool detectarI2C(uint8_t direccion) { Wire.beginTransmission(direccion); return Wire.endTransmission()==0; }
void inicializarPantalla() {
  if (!LCD_HABILITADO) return;
  Wire.begin(PIN_LCD_SDA,PIN_LCD_SCL); Wire.setTimeOut(20);
  if (detectarI2C(0x27)) lcd=&lcd27; else if (detectarI2C(0x3F)) lcd=&lcd3f;
  if (!lcd) { notificar("EVENTO;LCD_NO_DETECTADO"); return; }
  lcd->init(); lcd->backlight(); lcd->clear(); lcd->print("PROJECT DOMUS");
  lcd->setCursor(0,1); lcd->print("Base modular"); lcdDisponible=true;
}
void actualizarPantalla() {
  if (!lcdDisponible || uint32_t(millis()-ultimaPantalla)<LCD_INTERVALO_MS) return;
  ultimaPantalla=millis(); char fila[17]; lcd->setCursor(0,0);
  if (modoSeguro) snprintf(fila,sizeof(fila),"MODO SEGURO     ");
  else if (paro) snprintf(fila,sizeof(fila),"PARO ACTIVO     ");
  else if (sensores.ambienteValido) snprintf(fila,sizeof(fila),"T:%4.1fC H:%2.0f%% ",sensores.temperatura,sensores.humedadAire);
  else snprintf(fila,sizeof(fila),"DHT SIN DATOS   ");
  lcd->print("                "); lcd->setCursor(0,0); lcd->print(fila); lcd->setCursor(0,1);
  if (calibracionGuardada) snprintf(fila,sizeof(fila),"S:%3d%% L:%3d%%   ",sensores.sueloPct,sensores.luzPct);
  else snprintf(fila,sizeof(fila),"CAL PENDIENTE   ");
  lcd->print("                "); lcd->setCursor(0,1); lcd->print(fila);
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
  notificarFormato("ESTADO;PARO=%d;SEGURO=%d;BLOQUEO_BOMBA=%d;OUT=%d%d%d%d%d;CAL=%d;TX_OMITIDOS=%lu",
    paro,modoSeguro,bloqueoBomba,encendida[0],encendida[1],encendida[2],encendida[3],encendida[4],calibracionGuardada,
    static_cast<unsigned long>(mensajesOmitidos));
  if (diagnostico) notificarFormato("DIAGNOSTICO;HEAP=%lu;LCD=%d;DHT=%d;SALIDAS=%d;MOTIVO=%s",
    static_cast<unsigned long>(esp_get_free_heap_size()),lcdDisponible,sensores.ambienteValido,SALIDAS_HABILITADAS,motivoSeguro);
}
void procesarLinea(const char *texto) {
  if (procesarCalibracion(texto)) return;
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
  pinMode(PIN_PARO,INPUT_PULLUP); pinMode(PIN_MIC_OFF,INPUT_PULLUP); pinMode(PIN_BOTON,INPUT_PULLUP); pinMode(PIN_PIR,INPUT);
  analogReadResolution(12); analogSetAttenuation(ADC_11db);
  for (uint8_t i=0; i<TOTAL; ++i) {
    digitalWrite(PINES[i],ACTIVA_LOW[i]?HIGH:LOW); pinMode(PINES[i],SALIDAS_HABILITADAS?OUTPUT:INPUT); propietario[i]=Propietario::AUTO;
  }
  paro=digitalRead(PIN_PARO)==LOW; apagarTodo(); cargarCalibracion(); inicializarPantalla();
  if (DHT_HABILITADO) dht.begin(); watchdogActivo=inicializarWatchdog();
  if (!watchdogActivo) entrarModoSeguro("watchdog"); notificar("DOMUS_LISTO;USE_DIAGNOSTICO");
}
void loop() {
  if (watchdogActivo && esp_task_wdt_reset()!=ESP_OK) { watchdogActivo=false; entrarModoSeguro("watchdog_reset"); }
  revisarSeguridad(); revisarBoton(); revisarComandos(); leerSensores(); revisarAutomatizacion(); revisarSalud(); actualizarPantalla(); delay(1);
}
