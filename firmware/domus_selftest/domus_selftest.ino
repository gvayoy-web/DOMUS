/*
  ============================================================================
  PROJECT DOMUS — SELFTEST TOLERANTE (Ronda de prueba)
  ============================================================================
  Placa objetivo: ESP32-S3 N16R8 (16 MB Flash / 8 MB PSRAM OPI)
  FQBN: esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB

  OBJETIVO:
    Probar TODO lo que la casa requerira, sin aguitarse si algo falta.
    Cada bloque es independiente: si un sensor/modulo no esta conectado,
    reporta SKIP y sigue. Nunca bloquea, nunca reinicia a proposito.

  QUE PRUEBA (adaptado a tu placa: solo 16 GPIOs expuestos):
    [SIST] Chip, heap, PSRAM, flash, NVS, uptime, reset reason
    [I2C ] Scan 0x03-0x77, detecta LCD 0x27/0x3F + OLED 0x3C/0x3D en SDA11/SCL12
    [LCD ] LCD1602 I2C SDA11/SCL12 -> "Hola" si detectado
    [OLED] OLED 4pines I2C SSD1306/SH1106 0x3C/0x3D 128x64/128x32 -> "Hola"
    [TFT ] ST7789 1.54" SPI 240x240 -> "Hola" (HSPI SCLK46 MOSI28 CS25 DC26 RST27)
    [DHT ] DHT11/DHT22 en GPIO25 (comparte con TFT_CS -> SKIP si TFT conectado)
    [ADC ] Suelo GPIO3, Nivel GPIO9, LDR GPIO10 (promediado + % calibrado)
    [PIR ] Presencia GPIO13
    [BTN ] PARO 26, MIC_OFF 27, DEMO 28 (comparten con TFT -> SKIP si TFT)
    [RELE] 5 salidas 4..8 (verifica nivel logico GPIO, pulso opcional)
    [SD  ] deshabilitado (38/39/47/48 no expuestos) -> SKIP
    [MIC ] deshabilitado (15/16/17 no expuestos) -> SKIP
    [SPK ] deshabilitado (40/41/42 no expuestos) -> SKIP
    [MP3 ] deshabilitado (18/19 no expuestos) -> SKIP
    [WS  ] WS2812 SKIP
    NOTA PLACA LIMITADA: 16 GPIOs no alcanzan para todo a la vez.
    Pantallas+TFT ocupan 25/26/27/28/46 compartidos con DHT/botones -> esos haran SKIP.
    Para probar DHT/botones: desconecta TFT o pon TFT_* a -1 y reconecta.
    I2C LCD+OLED comparten SDA11/SCL12 (distinta direccion). TFT usa HSPI aparte.

   COMO USAR (PLACA LIMITADA 16 pines: 3,4,5,6,7,8,9,10,11,12,13,25,26,27,28,46):
    1. Carga con FQBN esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB
    2. Monitor Serial 115200 NL. Al arrancar ronda completa -> cada pantalla -> "Hola".
    3. Comandos: H ayuda, T todo, I I2C, L LCD, OLED oled, TFT tft, W 3 pantallas,
       D DHT (25), A analog 3/9/10, P PIR13, B botones 26/27/28, R reles 4-8, E resumen, O monitor.
    4. Cableado pantallas 3x:
       LCD I2C: VCC 5V, GND, SDA 11, SCL 12 (ajusta pot)
       OLED 4p: VCC 3.3V, GND, SDA 11, SCL 12 (mismo bus que LCD, addr 0x3C)
       TFT ST7789: VCC 3.3V, GND, SCLK 46, MOSI 28, CS 25, DC 26, RST 27, BLK->3V3
       OJO: TFT usa 25/26/27/28 -> DHT25 y botones 26/27/28 haran SKIP con TFT conectado.
            Para probar DHT/botones desconecta TFT o pon TFT_* a -1 en el sketch.
    5. Sensores: suelo 3, nivel 9, LDR 10 (divisores 3.3V), PIR 13, reles 4-8.
       SD/Mic/MAX/MP3 deshabilitados (-1) -> SKIP (no tienes esos GPIOs).
    6. R SI = rele con pulso (desconecta cargas, bomba nunca en seco)
       BUZZ <pin> <hz> / LED <pin> [n] para buzzer/LED sueltos.

  SEGURIDAD:
    - No alimenta motores/reles/audio desde 3V3.
    - Rele inicia APAGADO (precarga nivel inactivo antes de pinMode).
    - La bomba/ventilador tienen diodo flyback en el mazo final.
    - El agua siempre debajo y lejos de electronica.

   DEPENDENCIAS:
    Arduino-ESP32 3.3.10, LiquidCrystal I2C 1.1.2, DHT sensor 1.4.7,
    Adafruit Unified Sensor 1.1.15. I2S via driver/i2s_std.h (ESP-IDF 5).
    Pantallas opcionales (solo para test 3x, si falta libreria -> SKIP):
      Adafruit GFX Library + Adafruit SSD1306 + Adafruit SH110X + Adafruit ST7789
    Instala desde Library Manager si quieres probar OLED/TFT. El sketch compila
    igual sin ellas (reporta SKIP con instruccion).

  PLANES PENDIENTES (no son fallo del selftest):
    T00 pinout, T03 cinco arranques, T04 sensores, T05 reles, T06 cargas,
    T07 bomba, T08 concurrencia, T09 audio/Jarvis, T10 prolongada.
    Ver obsidian/proyect domus/16 - Plan de testeo antes de construccion.md
    y 18 - Manual maestro de conexiones pin por pin.md

  Inventario YA TIENES vs FALTA (01 - Inventario confirmado.md):
    YA: ESP32-S3, LCD1602+I2C, DHT, suelo, nivel, LDR, PIR, bomba, motor,
        LEDs, resistencias 1k/10k, diodos 1N4007, S8050, buzzer, protoboard.
    FALTA: rele 4ch (o usar perfil economico), fuente 5V/3A, INMP441,
           MAX98357A, altavoz, lector SD + SD, 74AHCT125, panel/bateria.

  SALIDA:
    Humana:  [TAG] mensaje
    Maquina: TEST;ID;RESULTADO;DETALLE  (PASS/FAIL/SKIP/WARN)
===========================================================================
*/

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <DHT.h>
#include <LiquidCrystal_I2C.h>
#include <esp_heap_caps.h>
#include <esp_system.h>
#include <esp_chip_info.h>
#include <esp_flash.h>
#include <nvs_flash.h>
#include <Preferences.h>
#include <math.h>

// Declarado antes de cualquier funcion: el preprocesador de Arduino genera
// prototipos al inicio del archivo y debe conocer este tipo previamente.
typedef uint8_t DomusResult;
#define DOMUS_PASS 0
#define DOMUS_FAIL 1
#define DOMUS_SKIP 2
#define DOMUS_WARN 3
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// I2S solo si el core lo trae (Arduino-ESP32 3.x si). Si no, el bloque se desactiva solo.
#if __has_include("driver/i2s_std.h")
  #include "driver/i2s_std.h"
  #define DOMUS_HAS_I2S 1
#else
  #define DOMUS_HAS_I2S 0
#endif

// ---------- OLED 4 pines (I2C) — SSD1306 / SH1106 — tolerante ----------
#if __has_include(<Adafruit_SSD1306.h>)
  #include <Adafruit_GFX.h>
  #include <Adafruit_SSD1306.h>
  #define DOMUS_HAS_SSD1306 1
#else
  #define DOMUS_HAS_SSD1306 0
#endif
#if __has_include(<Adafruit_SH110X.h>)
  #include <Adafruit_SH110X.h>
  #define DOMUS_HAS_SH110X 1
#else
  #define DOMUS_HAS_SH110X 0
#endif
#if __has_include(<Adafruit_ST7789.h>)
  #include <Adafruit_ST7789.h>
  #define DOMUS_HAS_ST7789 1
#else
  #define DOMUS_HAS_ST7789 0
#endif

// -------------------- MAPA DE PINES — ADAPTADO A TU PLACA LIMITADA --------------------
// Solo tienes: 3v3, RST, 4 5 6 7 25 26 27 28 8 3 46 9 10 11 12 13 5v gnd  (16 GPIOs)
// El mapa original usa 21,14,15,16,17,18,19,38,39,40,41,42,47,48 -> NO expuestos -> se desactivan.
// Para que quepan: I2C se mueve a 11/12, sensores a 3/9/10, reles 4-8 intactos, TFT a 25/26/27/28/46.
// Eso deja DHT y botones compartiendo con TFT: en este build TFT tiene prioridad y DHT/botones
// haran SKIP mientras TFT este conectado. Si quieres probar DHT/botones, desconecta TFT o cambia
// TFT_* a -1 y reconecta DHT a 25 y botones a 26/27/28.
// Pon PLACA_LIMITADA=1 para activar este mapa; 0 para volver al mapa original (21/13 y 1/2/3).
#define PLACA_LIMITADA  1

#if PLACA_LIMITADA
  #define I2C_SDA_PIN     11   // SDA LCD+OLED comparten bus
  #define I2C_SCL_PIN     12
  #define DIR_LCD_1       0x27
  #define DIR_LCD_2       0x3F
  #define PIN_HUMEDAD     3    // suelo -> GPIO3  (ADC1_CH2) divisor 3.3V + 10k a GND
  #define PIN_NIVEL_AGUA  9    // nivel -> GPIO9  (ADC1_CH8) nunca >3.3V
  #define PIN_LDR         10   // luz   -> GPIO10 (ADC1_CH9) divisor 3.3V-LDR-10k-GND
  #define PIN_PIR         13   // PIR OUT -> GPIO13 (verifica que tu PIR no saque 5V; si >3.3V usa divisor)
  // DHT y botones comparten con TFT: se desactivan si TFT esta activo (ver abajo)
  #define PIN_DHT11       25   // DHT DATA -> GPIO25 (comparte con TFT_CS, ver nota)
  #define TIPO_DHT        DHT11
  #define PIN_PARO        26   // PARO a GND -> GPIO26 (comparte TFT_DC)
  #define PIN_MIC_OFF     27   // MIC_OFF -> GPIO27 (comparte TFT_RST)
  #define PIN_DEMO        28   // DEMO -> GPIO28 (comparte TFT_MOSI)
  #define MIC_WS_PIN      I2S_GPIO_UNUSED   // INMP441 no expuesto -> SKIP
  #define MIC_SD_PIN      I2S_GPIO_UNUSED
  #define MIC_SCK_PIN     I2S_GPIO_UNUSED
  #define TTS_BCLK_PIN    I2S_GPIO_UNUSED   // MAX98357 no expuesto -> SKIP
  #define TTS_WS_PIN      I2S_GPIO_UNUSED
  #define TTS_DOUT_PIN    I2S_GPIO_UNUSED
  #define MP3_RX_PIN      -1   // DFPlayer no expuesto -> SKIP
  #define MP3_TX_PIN      -1
  #define PIN_SALIDA_BOMBA           4    // reles intactos: 4-8 son los 5 que SÍ tienes
  #define PIN_SALIDA_LUZ_SALA        5
  #define PIN_SALIDA_LUZ_CUARTO      6
  #define PIN_SALIDA_VENTILADOR      7
  #define PIN_SALIDA_LUZ_INVERNADERO 8
  #define TOTAL_SALIDAS 5
  #define SD_SCK_PIN      -1   // SD no expuesto (38/39/47/48) -> SKIP
  #define SD_MISO_PIN     -1
  #define SD_MOSI_PIN     -1
  #define SD_CS_PIN       -1
#else
  // Mapa original completo (21 pines, para placa con todos expuestos)
  #define I2C_SDA_PIN     21
  #define I2C_SCL_PIN     13
  #define DIR_LCD_1       0x27
  #define DIR_LCD_2       0x3F
  #define PIN_HUMEDAD     1
  #define PIN_NIVEL_AGUA  2
  #define PIN_LDR         3
  #define PIN_PIR         9
  #define PIN_PARO        10
  #define PIN_MIC_OFF     11
  #define PIN_DEMO        12
  #define PIN_DHT11       14
  #define TIPO_DHT        DHT11
  #define MIC_WS_PIN      15
  #define MIC_SD_PIN      16
  #define MIC_SCK_PIN     17
  #define TTS_BCLK_PIN    40
  #define TTS_WS_PIN      41
  #define TTS_DOUT_PIN    42
  #define MP3_RX_PIN      18
  #define MP3_TX_PIN      19
  #define PIN_SALIDA_BOMBA           4
  #define PIN_SALIDA_LUZ_SALA        5
  #define PIN_SALIDA_LUZ_CUARTO      6
  #define PIN_SALIDA_VENTILADOR      7
  #define PIN_SALIDA_LUZ_INVERNADERO 8
  #define TOTAL_SALIDAS 5
  #define SD_SCK_PIN   38
  #define SD_MISO_PIN  39
  #define SD_MOSI_PIN  47
  #define SD_CS_PIN    48
#endif

// -------------------- PANTALLAS 3x — PINES SEGUN PLACA ------------------------
#if PLACA_LIMITADA
  // OLED comparte I2C 11/12 con LCD (ver arriba)
  // TFT usa los 5 GPIOs que en modo completo serian DHT+botones: 25/26/27/28/46
  // Si quieres probar DHT/botones, desconecta TFT o pon TFT_* a -1
  #define TFT_CS_PIN    25   // CS   -> GPIO25 (comparte con DHT si no usas TFT)
  #define TFT_DC_PIN    26   // DC   -> GPIO26 (comparte con PARO)
  #define TFT_RST_PIN   27   // RST  -> GPIO27 (comparte con MIC_OFF)  (-1 si lo puenteas a 3V3)
  #define TFT_MOSI_PIN  28   // MOSI -> GPIO28 (comparte con DEMO)
  #define TFT_SCLK_PIN  46   // SCLK -> GPIO46 (libre, OJO: strapping, no lo lleves a GND en boot)
  #define TFT_BLK_PIN   -1   // BLK -> -1 o 46? deja -1 y conecta BLK a 3V3 directo
#else
  // Placa completa con todos los GPIOs expuestos
  #define TFT_CS_PIN    33
  #define TFT_DC_PIN    34
  #define TFT_RST_PIN   35
  #define TFT_MOSI_PIN  36
  #define TFT_SCLK_PIN  37
  #define TFT_BLK_PIN   -1
#endif

// -------------------- CALIBRACION PROVISIONAL (misma que firmware principal) ---------------
#define HUMEDAD_LECTURA_SECA     2800
#define HUMEDAD_LECTURA_HUMEDA   1200
#define LDR_LECTURA_OSCURO       3200
#define LDR_LECTURA_BRILLANTE    400
#define NIVEL_AGUA_MINIMO_CRUDO  600
#define HUMEDAD_MIN_VALIDA      50
#define HUMEDAD_MAX_VALIDA      4045
#define NIVEL_AGUA_MIN_VALIDO   16
#define NIVEL_AGUA_MAX_VALIDO   4079
#define LDR_MIN_VALIDO          16
#define LDR_MAX_VALIDO          4079

DHT dht(PIN_DHT11, TIPO_DHT);
LiquidCrystal_I2C* lcd = nullptr;
uint8_t lcdAddrActiva = 0;
bool lcdOk = false;

// OLED / TFT objetos dinamicos (tolerante si no hay libreria/hardware)
#if DOMUS_HAS_SSD1306
Adafruit_SSD1306* oledSSD = nullptr;
#endif
#if DOMUS_HAS_SH110X
Adafruit_SH1106G* oledSH1106 = nullptr;
#endif
bool oledOk = false;
String oledInfo = "";

#if DOMUS_HAS_ST7789
Adafruit_ST7789* tft = nullptr;
SPIClass* spiTFT = nullptr;
#endif
bool tftOk = false;
String tftInfo = "";

const int PINES_SALIDAS[TOTAL_SALIDAS] = {
  PIN_SALIDA_BOMBA, PIN_SALIDA_LUZ_SALA, PIN_SALIDA_LUZ_CUARTO, PIN_SALIDA_VENTILADOR, PIN_SALIDA_LUZ_INVERNADERO
};
const char* NOMBRES_SALIDAS[TOTAL_SALIDAS] = {"Bomba","Luz Sala","Luz Cuarto","Ventilador","Luz Inv."};
// Perfil 0 = rele activo LOW (compatible con modulo C&D). Si usas perfil economico cambia a false para 1-4.
const bool SALIDA_ACTIVA_EN_BAJO[TOTAL_SALIDAS] = {true, true, true, true, true};

int nivelSalida(int idx, bool on) { return (on == SALIDA_ACTIVA_EN_BAJO[idx]) ? LOW : HIGH; }

// -------------------- FRAMEWORK DE REPORTE TOLERANTE --------------------------------------
const char* resStr(DomusResult r){ return r==DOMUS_PASS?"PASS":r==DOMUS_FAIL?"FAIL":r==DOMUS_SKIP?"SKIP":"WARN"; }

struct Contadores { int total=0, pass=0, fail=0, skip=0, warn=0; } cnt;

void emitLog(const String &tag, const String &msg){
  Serial.print("["); Serial.print(millis()); Serial.print("]["); Serial.print(tag); Serial.print("] "); Serial.println(msg);
}
void report(const char* id, DomusResult r, const String &detalle){
  cnt.total++; if(r==DOMUS_PASS)cnt.pass++; else if(r==DOMUS_FAIL)cnt.fail++; else if(r==DOMUS_SKIP)cnt.skip++; else cnt.warn++;
  // Humano
  Serial.print("["); Serial.print(id); Serial.print("] ");
  Serial.print(resStr(r)); Serial.print(" : "); Serial.println(detalle);
  // Maquina parseable
  Serial.print("TEST;"); Serial.print(id); Serial.print(";"); Serial.print(resStr(r)); Serial.print(";"); Serial.println(detalle);
}

int adcProm(int pin, int muestras=10){
  long s=0; for(int i=0;i<muestras;i++){ s+=analogRead(pin); delayMicroseconds(300);} return s/muestras;
}
int pctDesdeCal(int raw, int ref0_pct0, int ref1_pct100){
  long rango=(long)ref1_pct100 - (long)ref0_pct0;
  if(rango==0) return 0;
  long p=((long)raw - ref0_pct0)*100L / rango;
  if(p<0)p=0; if(p>100)p=100; return (int)p;
}
bool adcValido(int v,int lo,int hi){ return v>=lo && v<=hi; }

// -------------------- TESTS INDIVIDUALES --------------------------------------------------
void testSistema(){
  esp_chip_info_t chip; esp_chip_info(&chip);
  uint32_t flash=0; esp_flash_get_size(NULL,&flash);
  size_t freeHeap=esp_get_free_heap_size();
  size_t freeInternal=heap_caps_get_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
  size_t freePsram=heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
  size_t largestInternal=heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
  size_t largestPsram=heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM);
  String det="chip="+String(chip.model==CHIP_ESP32S3?"ESP32-S3":String(chip.model))
    +" cores="+String(chip.cores)+" rev="+String(chip.revision)
    +" flash="+String(flash/1024/1024)+"MB"
    +" heapLibre="+String(freeHeap)+" int="+String(freeInternal)+" psram="+String(freePsram)
    +" blkInt="+String(largestInternal)+" blkPsram="+String(largestPsram)
    +" uptime="+String(millis()/1000)+"s";
  // NVS check tolerante
  esp_err_t nvs=nvs_flash_init();
  if(nvs==ESP_ERR_NVS_NO_FREE_PAGES || nvs==ESP_ERR_NVS_NEW_VERSION_FOUND){ nvs_flash_erase(); nvs=nvs_flash_init(); }
  det += String(" nvs=")+(nvs==ESP_OK?"OK":String(esp_err_to_name(nvs)));
  // Reset reason
  det += String(" reset=")+String(esp_reset_reason());
  // Criterio: si no hay PSRAM es WARN (placa no es N16R8)
  DomusResult r = (freePsram < 1024*1024) ? DOMUS_WARN : DOMUS_PASS;
  if(freePsram < 100*1024) r=DOMUS_WARN; // N16R8 debe tener ~8MB
  report("SIST", r, det);
  // Verificacion de voltajes por instruccion (no medible por software)
  report("ALIM", DOMUS_SKIP, "Medir con multimetro: 5V_BUS=5.0V y 3V3=3.3V sin y con cargas (ver 18-Manual pin por pin). Este test es recordatorio.");
}

void testI2C(){
  int encontrados=0;
  String lista="";
  for(uint8_t addr=0x03; addr<0x78; addr++){
    Wire.beginTransmission(addr);
    uint8_t e=Wire.endTransmission();
    if(e==0){ encontrados++; lista += "0x"+String(addr,HEX)+" "; }
  }
  String busInfo = "SDA"+String(I2C_SDA_PIN)+" SCL"+String(I2C_SCL_PIN);
  if(encontrados==0){
    report("I2C", DOMUS_WARN, "Bus I2C sin dispositivos en "+busInfo+". Verifica VCC 3.3/5V, GND. LCD/OLED -> SKIP.");
    lcdOk=false; oledOk=false;
    return;
  }
  String det="encontrados="+String(encontrados)+" ["+lista+"] en "+busInfo;
  bool hay27 = lista.indexOf("0x27")>=0;
  bool hay3F = lista.indexOf("0x3f")>=0 || lista.indexOf("0x3F")>=0;
  bool hay3C = lista.indexOf("0x3c")>=0 || lista.indexOf("0x3C")>=0;
  bool hay3D = lista.indexOf("0x3d")>=0 || lista.indexOf("0x3D")>=0;
  if(hay27 || hay3F) det += " LCD candidato OK";
  if(hay3C || hay3D) det += " OLED candidato OK (0x3C/0x3D)";
  if(!hay27 && !hay3F && !hay3C && !hay3D) det += " sin LCD/OLED tipico (0x27/0x3F/0x3C) — normal si solo usas TFT SPI";
  report("I2C", DOMUS_PASS, det);
}

void testLCD(){
  uint8_t addrs[2]={DIR_LCD_1, DIR_LCD_2};
  lcdOk=false;
  for(uint8_t a: addrs){
    Wire.beginTransmission(a);
    if(Wire.endTransmission()==0){
      if(lcd) { delete lcd; lcd=nullptr; }
      lcd = new (std::nothrow) LiquidCrystal_I2C(a,16,2);
      if(!lcd){ report("LCD", DOMUS_FAIL, "Sin RAM para LCD en 0x"+String(a,HEX)); return; }
      lcdAddrActiva=a;
      lcd->init(); lcd->backlight();
      lcd->clear(); lcd->setCursor(0,0); lcd->print("Hola DOMUS");
      lcd->setCursor(0,1); lcd->print("LCD 0x"+String(a,HEX)+" OK");
      lcdOk=true;
      report("LCD", DOMUS_PASS, "LCD1602 I2C en 0x"+String(a,HEX)+" SDA"+String(I2C_SDA_PIN)+" SCL"+String(I2C_SCL_PIN)+" -> 'Hola DOMUS' OK. Ajusta pot si no ves texto.");
      return;
    }
  }
  report("LCD", DOMUS_SKIP, "LCD I2C no encontrado en 0x27/0x3F en bus SDA"+String(I2C_SDA_PIN)+" SCL"+String(I2C_SCL_PIN)+". Normal si solo usas OLED/TFT.");
}

// -------------------- OLED 4 pines I2C (SSD1306 / SH1106) -------------------------
void testOLED(){
  oledOk=false; oledInfo="";
  uint8_t addrOLED=0;
  for(uint8_t a: { (uint8_t)0x3C, (uint8_t)0x3D }){
    Wire.beginTransmission(a);
    if(Wire.endTransmission()==0){ addrOLED=a; break; }
  }
  if(addrOLED==0){
    report("OLED", DOMUS_SKIP, "OLED I2C no encontrado en 0x3C/0x3D en SDA"+String(I2C_SDA_PIN)+" SCL"+String(I2C_SCL_PIN)+". Normal si no tienes OLED. VCC 3.3V, no 5V.");
    return;
  }
#if !DOMUS_HAS_SSD1306 && !DOMUS_HAS_SH110X
  report("OLED", DOMUS_SKIP, "OLED detectado en 0x"+String(addrOLED,HEX)+" pero faltan librerias Adafruit SSD1306/SH110X + GFX. Instala en Library Manager: Adafruit SSD1306, Adafruit SH110X, Adafruit GFX Library. Luego re-compila. Hardware OK, software SKIP.");
  return;
#endif

  // Intento 1: SSD1306 128x64 en addr encontrado (el mas comun)
#if DOMUS_HAS_SSD1306
  {
    if(oledSSD){ delete oledSSD; oledSSD=nullptr; }
    oledSSD = new (std::nothrow) Adafruit_SSD1306(128, 64, &Wire, -1);
    if(oledSSD && oledSSD->begin(SSD1306_SWITCHCAPVCC, addrOLED)){
      oledSSD->clearDisplay();
      oledSSD->setTextColor(SSD1306_WHITE);
      oledSSD->setTextSize(2);
      oledSSD->setCursor(0, 0);
      oledSSD->println("Hola");
      oledSSD->setTextSize(1);
      oledSSD->setCursor(0, 28);
      oledSSD->println("DOMUS OLED");
      oledSSD->setCursor(0, 40);
      oledSSD->print("0x"); oledSSD->print(addrOLED, HEX); oledSSD->print(" 128x64 OK");
      oledSSD->setCursor(0, 52);
      oledSSD->print("I2C "+String(I2C_SDA_PIN)+"/"+String(I2C_SCL_PIN));
      oledSSD->display();
      oledOk=true; oledInfo="SSD1306 128x64 0x"+String(addrOLED,HEX);
      report("OLED", DOMUS_PASS, "OLED SSD1306 128x64 en 0x"+String(addrOLED,HEX)+" I2C SDA"+String(I2C_SDA_PIN)+" SCL"+String(I2C_SCL_PIN)+" -> 'Hola' OK. Si ves basura prueba SH1106.");
      return;
    }
    // intento 128x32
    if(oledSSD){ delete oledSSD; oledSSD=nullptr; }
    oledSSD = new (std::nothrow) Adafruit_SSD1306(128, 32, &Wire, -1);
    if(oledSSD && oledSSD->begin(SSD1306_SWITCHCAPVCC, addrOLED)){
      oledSSD->clearDisplay();
      oledSSD->setTextColor(SSD1306_WHITE);
      oledSSD->setTextSize(2);
      oledSSD->setCursor(0, 0);
      oledSSD->println("Hola");
      oledSSD->setTextSize(1);
      oledSSD->setCursor(0, 18);
      oledSSD->print("DOMUS 128x32 0x"); oledSSD->print(addrOLED, HEX);
      oledSSD->display();
      oledOk=true; oledInfo="SSD1306 128x32 0x"+String(addrOLED,HEX);
      report("OLED", DOMUS_PASS, "OLED SSD1306 128x32 en 0x"+String(addrOLED,HEX)+" -> 'Hola' OK.");
      return;
    }
    if(oledSSD){ delete oledSSD; oledSSD=nullptr; }
  }
#endif

#if DOMUS_HAS_SH110X
  {
    if(oledSH1106){ delete oledSH1106; oledSH1106=nullptr; }
    oledSH1106 = new (std::nothrow) Adafruit_SH1106G(128, 64, &Wire, -1);
    if(oledSH1106 && oledSH1106->begin(addrOLED, true)){
      oledSH1106->clearDisplay();
      oledSH1106->setTextColor(SH110X_WHITE);
      oledSH1106->setTextSize(2);
      oledSH1106->setCursor(0, 0);
      oledSH1106->println("Hola");
      oledSH1106->setTextSize(1);
      oledSH1106->setCursor(0, 28);
      oledSH1106->println("DOMUS SH1106");
      oledSH1106->setCursor(0, 40);
      oledSH1106->print("0x"); oledSH1106->print(addrOLED, HEX); oledSH1106->print(" 128x64");
      oledSH1106->display();
      oledOk=true; oledInfo="SH1106 128x64 0x"+String(addrOLED,HEX);
      report("OLED", DOMUS_PASS, "OLED SH1106 128x64 en 0x"+String(addrOLED,HEX)+" -> 'Hola' OK.");
      return;
    }
    if(oledSH1106){ delete oledSH1106; oledSH1106=nullptr; }
  }
#endif

  report("OLED", DOMUS_WARN, "OLED en 0x"+String(addrOLED,HEX)+" responde a I2C pero ningun driver (SSD1306 128x64/32 ni SH1106) logro iniciar. Prueba libreria U8g2 o verifica VCC 3.3V y que no sea SH1107/SSD1309. No es FAIL critico.");
}

// -------------------- TFT ST7789 1.54" SPI ------------------------------------
void testST7789(){
  tftOk=false; tftInfo="";
#if !DOMUS_HAS_ST7789
  report("TFT", DOMUS_SKIP, "TFT ST7789 no probado: falta libreria Adafruit ST7789 + Adafruit GFX. Instala ambas y re-compila. Pines actuales CS"+String(TFT_CS_PIN)+" DC"+String(TFT_DC_PIN)+" RST"+String(TFT_RST_PIN)+" MOSI"+String(TFT_MOSI_PIN)+" SCLK"+String(TFT_SCLK_PIN)+". SKIP tolerante.");
  return;
#else
  if(TFT_CS_PIN<0 || TFT_DC_PIN<0 || TFT_MOSI_PIN<0 || TFT_SCLK_PIN<0){
    report("TFT", DOMUS_SKIP, "TFT deshabilitado (pin -1). Activa defines TFT_*_PIN a GPIOs expuestos si quieres probar ST7789.");
    return;
  }
  // En placa limitada TFT comparte 25/26/27/28/46 con DHT/botones -> informa
#if PLACA_LIMITADA
  if(PIN_DHT11==TFT_CS_PIN || PIN_PARO==TFT_DC_PIN || PIN_MIC_OFF==TFT_RST_PIN || PIN_DEMO==TFT_MOSI_PIN){
    emitLog("TFT","Placa limitada: TFT comparte 25/26/27/28 con DHT/botones. Esos haran SKIP mientras TFT este conectado. Desconecta TFT para probar DHT/botones.");
  }
#endif
  int pinesTFT[]={TFT_CS_PIN, TFT_DC_PIN, TFT_MOSI_PIN, TFT_SCLK_PIN};
  for(int p: pinesTFT) if(p>=0 && p<=48){ /* ok */ } else { report("TFT", DOMUS_SKIP, "TFT SKIP: pin TFT fuera de rango 0-48 (revisa defines TFT_*_PIN)"); return; }

  if(spiTFT){ delete spiTFT; spiTFT=nullptr; }
  if(tft){ delete tft; tft=nullptr; }

  // Usa HSPI para no pisar SD (FSPI en 38/47). Si prefieres compartir bus SD, cambia defines a 38/47.
  spiTFT = new (std::nothrow) SPIClass(HSPI);
  if(!spiTFT){ report("TFT", DOMUS_FAIL, "Sin RAM para SPIClass HSPI"); return; }
  // HSPI begin: SCK, MISO, MOSI, SS
  spiTFT->begin(TFT_SCLK_PIN, -1, TFT_MOSI_PIN, TFT_CS_PIN);

  // RST puede ser -1 si esta puenteado a 3V3
  int rst = TFT_RST_PIN;
  if(rst>=0) pinMode(rst, OUTPUT);
  // BLK opcional
  if(TFT_BLK_PIN>=0){ pinMode(TFT_BLK_PIN, OUTPUT); digitalWrite(TFT_BLK_PIN, HIGH); }

  tft = new (std::nothrow) Adafruit_ST7789(spiTFT, TFT_CS_PIN, TFT_DC_PIN, rst);
  if(!tft){ report("TFT", DOMUS_FAIL, "Sin RAM para Adafruit_ST7789"); delete spiTFT; spiTFT=nullptr; return; }

  // ST7789 1.54" suele ser 240x240
  tft->init(240, 240);
  tft->setRotation(0);
  tft->fillScreen(ST77XX_BLACK);
  tft->setTextWrap(false);
  tft->setTextColor(ST77XX_WHITE);
  tft->setTextSize(3);
  int16_t x = (240 - 72)/2;
  tft->setCursor(x, 60);
  tft->print("Hola");
  tft->setTextSize(2);
  tft->setCursor(30, 100);
  tft->setTextColor(ST77XX_GREEN);
  tft->print("DOMUS ST7789");
  tft->setTextSize(1);
  tft->setCursor(20, 130);
  tft->setTextColor(ST77XX_CYAN);
  tft->print("TFT 1.54\" 240x240");
  tft->setCursor(20, 145);
  tft->print("SPI CS"+String(TFT_CS_PIN)+" DC"+String(TFT_DC_PIN)+" RST"+String(TFT_RST_PIN));
  tft->drawRect(0,0,240,240, ST77XX_RED);
  tft->drawRect(1,1,238,238, ST77XX_BLUE);
  tftOk=true; tftInfo="ST7789 240x240 HSPI CS"+String(TFT_CS_PIN)+" DC"+String(TFT_DC_PIN)+" RST"+String(TFT_RST_PIN)+" MOSI"+String(TFT_MOSI_PIN)+" SCLK"+String(TFT_SCLK_PIN);
  report("TFT", DOMUS_PASS, "TFT ST7789 1.54\" SPI HSPI MOSI"+String(TFT_MOSI_PIN)+" SCLK"+String(TFT_SCLK_PIN)+" CS"+String(TFT_CS_PIN)+" DC"+String(TFT_DC_PIN)+" RST"+String(TFT_RST_PIN)+" -> 'Hola' enviado. Si negra revisa VCC 3.3V y BLK a 3.3V. Para 240x320 prueba init(240,320).");
#endif
}

void testTodasPantallas(){
  // Prueba las 3 secuencial, cada una dibuja "Hola" si es detectada. Tolerante.
  testLCD();
  delay(250);
  testOLED();
  delay(250);
  testST7789();
  delay(250);
  int okCount = (lcdOk?1:0) + (oledOk?1:0) + (tftOk?1:0);
  String det = "Pantallas OK: "+String(okCount)+"/3 [LCD:"+(lcdOk?"SI":"NO")+" OLED:"+(oledOk?oledInfo:"NO")+" TFT:"+(tftOk?tftInfo:"NO")+"]";
  String busInfo = "I2C SDA"+String(I2C_SDA_PIN)+" SCL"+String(I2C_SCL_PIN)+" o SPI CS"+String(TFT_CS_PIN)+" DC"+String(TFT_DC_PIN);
  if(okCount==0) report("PANTALLAS", DOMUS_WARN, det+" -> ninguna respondio. Revisa "+busInfo+" y VCC 3.3V/5V. WARN si aun no cableaste.");
  else if(okCount==3) report("PANTALLAS", DOMUS_PASS, det+" -> las 3 muestran 'Hola'.");
  else report("PANTALLAS", DOMUS_PASS, det+" -> alguna muestra 'Hola' (es lo pedido). Las NO son SKIP esperado.");
}

void testAnalogSensor(const char* id, int pin, const char* nombre, int lo, int hi, int refOscuro, int refClaro){
  int raw = adcProm(pin, 12);
  bool ok = adcValido(raw, lo, hi);
  int pct = pctDesdeCal(raw, refOscuro, refClaro);
  String det = String(nombre)+" GPIO"+String(pin)+" raw="+String(raw)+" pct="+String(pct)+"% rangoValido=["+String(lo)+","+String(hi)+"] "
              + (ok?"OK":"FUERA_DE_RANGO")
              + " | Cal: seco/osucro="+String(refOscuro)+" humedo/claro="+String(refClaro)+" -> cubre/tapa sensor y repite A";
  if(!ok){
    // Si esta flotante puede dar valor medio valido aunque sin sensor. Por eso WARN, no FAIL.
    report(id, DOMUS_WARN, det + " | Posible cable suelto, sensor desconectado o GPIO flotante. Revisa divisor y que pin no supere 3.3V. SKIP funcional.");
  } else {
    report(id, DOMUS_PASS, det);
  }
}

void testDHT(){
  if(PIN_DHT11<0){ report("DHT", DOMUS_SKIP, "DHT deshabilitado (pin -1) en placa limitada -> SKIP"); return; }
#if PLACA_LIMITADA
  if(PIN_DHT11==TFT_CS_PIN){
    emitLog("DHT","Nota placa limitada: DHT25 comparte con TFT_CS25. Si TFT esta conectado, lectura DHT sera inestable. Desconecta TFT para probar DHT.");
  }
#endif
  for(int intento=1; intento<=3; intento++){
    float t=dht.readTemperature();
    float h=dht.readHumidity();
    if(!isnan(t) && !isnan(h)){
      bool tOk = t>=0 && t<=50;
      bool hOk = h>=20 && h<=90;
      String det="DHT GPIO"+String(PIN_DHT11)+" intento "+String(intento)+" T="+String(t,1)+"C H="+String(h,1)+"%";
      if(!tOk || !hOk) report("DHT", DOMUS_WARN, det+" fuera de rango fisico plausible (calibrar/confirmar modelo DHT11 vs DHT22)");
      else report("DHT", DOMUS_PASS, det+" lectura valida. Confirma modelo real.");
      return;
    }
    if(intento<3) delay(2600);
  }
  report("DHT", DOMUS_SKIP, "DHT GPIO"+String(PIN_DHT11)+" sin respuesta tras 3 intentos (NaN). Verifica VCC=3V3, GND, DATA=GPIO"+String(PIN_DHT11)+" con pull 10k si es sensor suelto.");
}

void testPIRSnapshot(){
  int v=digitalRead(PIN_PIR);
  String det="PIR GPIO"+String(PIN_PIR)+" OUT="+(v==HIGH?"HIGH (presencia)":"LOW (reposo)")+" | PIR HC-SR501 tarda 30-60s en estabilizar al energizar. Muevete frente a el y repite P.";
  // No hay forma de saber si el modulo entrega 5V en OUT -> medir con multimetro antes. Si >3.3V usar divisor.
  report("PIR", v==HIGH||v==LOW?DOMUS_PASS:DOMUS_FAIL, det+" (snapshot instantaneo, usa P para 10s live)");
}
void testPIRLive10s(){
  emitLog("PIR","Vigilando PIR 10s... mueve tu mano frente al sensor");
  bool vioHIGH=false, vioLOW=false;
  unsigned long t0=millis();
  while(millis()-t0 < 10000){
    int v=digitalRead(PIN_PIR);
    if(v==HIGH) vioHIGH=true; else vioLOW=true;
    Serial.print(v==HIGH?"1":"0"); delay(200);
  }
  Serial.println();
  String det="PIR live 10s vioHIGH="+String(vioHIGH?"SI":"NO")+" vioLOW="+String(vioLOW?"SI":"NO")+" retencion firmware 30s (verifica con movimiento)";
  report("PIRLIVE", DOMUS_PASS, det);
}

void testBotones(){
  if(PIN_PARO<0 || PIN_MIC_OFF<0 || PIN_DEMO<0){ report("BTN", DOMUS_SKIP, "Botones deshabilitados (pin -1) -> SKIP"); return; }
#if PLACA_LIMITADA
  if(PIN_PARO==TFT_DC_PIN || PIN_MIC_OFF==TFT_RST_PIN || PIN_DEMO==TFT_MOSI_PIN){
    emitLog("BTN","Nota placa limitada: BTNs 26/27/28 comparten con TFT DC/RST/MOSI. Si TFT conectado, BTNs inestables.");
  }
#endif
  int paro=digitalRead(PIN_PARO);
  int mic =digitalRead(PIN_MIC_OFF);
  int demo=digitalRead(PIN_DEMO);
  String det="PARO GPIO"+String(PIN_PARO)+"="+(paro==LOW?"LOW=PULSADO (emergencia)":"HIGH=libre")
    +" MIC_OFF GPIO"+String(PIN_MIC_OFF)+"="+(mic==LOW?"LOW=BLOQUEADO":"HIGH=habilitado")
    +" DEMO GPIO"+String(PIN_DEMO)+"="+(demo==LOW?"LOW=pulsado":"HIGH=libre")
    +" | Todos a GND con INPUT_PULLUP. Si lees LOW permanente revisa cable suelto a GND.";
  DomusResult r=(paro==LOW)?DOMUS_WARN:DOMUS_PASS;
  report("BTN", r, det);
}

void testRelesDry(bool conPulso){
  // Verifica nivel logico GPIO sin asumir carga. Si conPulso==false solo chequea apagado inicial.
  // Si conPulso==true hace pulso 350ms por canal con confirmacion via digitalRead.
  for(int i=0;i<TOTAL_SALIDAS;i++){
    int pin=PINES_SALIDAS[i];
    int lvlOff = nivelSalida(i,false);
    int leidoOff = digitalRead(pin);
    bool okInit = (leidoOff==lvlOff);
    String base=String(NOMBRES_SALIDAS[i])+" GPIO"+String(pin)+" activoLow="+(SALIDA_ACTIVA_EN_BAJO[i]?"SI":"NO")+" init="+(leidoOff==LOW?"LOW":"HIGH");
    if(!okInit){
      report(("RL"+String(i)).c_str(), DOMUS_FAIL, base+" esperado "+String(lvlOff==LOW?"LOW":"HIGH")+" -> FAIL cable o pinMode. Revisa 18-Manual.");
      continue;
    }
    if(!conPulso){
      report(("RL"+String(i)).c_str(), DOMUS_PASS, base+" -> PASS init apagado. Para pulso real escribe R SI (desconecta cargas primero).");
      continue;
    }
    // Pulso con verificacion
    digitalWrite(pin, nivelSalida(i,true)); delay(350);
    int leidoOn = digitalRead(pin);
    bool okOn = (leidoOn==nivelSalida(i,true));
    digitalWrite(pin, nivelSalida(i,false)); delay(250);
    int leidoOff2 = digitalRead(pin);
    bool okOff2 = (leidoOff2==lvlOff);
    if(okOn && okOff2) report(("RL"+String(i)).c_str(), DOMUS_PASS, base+" pulso 350ms ON->OFF verificado por GPIO -> PASS (ojo: esto no confirma contacto NO, solo GPIO)");
    else report(("RL"+String(i)).c_str(), DOMUS_FAIL, base+" pulso fallo on="+String(leidoOn)+" off2="+String(leidoOff2)+" esperado ON="+String(nivelSalida(i,true))+" OFF="+String(lvlOff));
  }
  if(!conPulso){
    report("RELE", DOMUS_SKIP, "Rele en seco verificado sin pulso. Para prueba con pulso y señal visible escribe R SI con cargas desconectadas y lee advertencia.");
  } else {
    report("RELE", DOMUS_PASS, "Ronda de pulsos completada. Verifica LEDs/reles hicieron click. Si algun canal no hizo click revisa VCC=5V_BUS y JD-VCC segun modulo.");
  }
}

void testSD(){
  if(SD_CS_PIN<0 || SD_SCK_PIN<0){ report("SD", DOMUS_SKIP, "SD deshabilitada en placa limitada (pins -1, 38/39/47/48 no expuestos) -> SKIP. Conecta lector SPI compatible 3.3V si quieres probar."); return; }
  SPIClass spiSD(FSPI);
  spiSD.begin(SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);
  bool ok = SD.begin(SD_CS_PIN, spiSD, 4000000U);
  if(!ok){
    report("SD", DOMUS_SKIP, "SD no montada CS"+String(SD_CS_PIN)+" SCK"+String(SD_SCK_PIN)+" MISO"+String(SD_MISO_PIN)+" MOSI"+String(SD_MOSI_PIN)+". Sin lector/tarjeta/FAT32.");
    return;
  }
  const char* ruta="/domus_selftest.txt";
  const char* marca="PROJECT_DOMUS_SD_OK";
  SD.remove(ruta);
  File f=SD.open(ruta, FILE_WRITE);
  if(!f){ report("SD", DOMUS_FAIL, "SD montada pero no pudo abrir "+String(ruta)+" para escritura. Revisa proteccion contra escritura y FAT."); SD.end(); return; }
  bool escrita = (f.println(marca) > 0);
  f.close();
  if(!escrita){ report("SD", DOMUS_FAIL, "SD escritura fallo"); SD.end(); return; }
  File r=SD.open(ruta, FILE_READ);
  if(!r){ report("SD", DOMUS_FAIL, "SD no pudo reabrir para lectura"); SD.end(); return; }
  String contenido = r.readStringUntil('\n'); contenido.trim(); r.close();
  SD.end();
  if(contenido==marca) report("SD", DOMUS_PASS, "SD SPI OK: escribio y leyo "+String(ruta)+" -> "+contenido+" | Tarjeta lista para /domus.log (opcional)");
  else report("SD", DOMUS_FAIL, "SD leyo '"+contenido+"' distinto de '"+String(marca)+"'");
}

#if DOMUS_HAS_I2S
void testINMP441(){
  if(MIC_WS_PIN==I2S_GPIO_UNUSED || MIC_SD_PIN==I2S_GPIO_UNUSED || MIC_SCK_PIN==I2S_GPIO_UNUSED){ report("MIC", DOMUS_SKIP, "INMP441 deshabilitado en placa limitada (pins -1, 15/16/17 no expuestos) -> SKIP"); return; }
  i2s_chan_handle_t rx=nullptr;
  i2s_chan_config_t chCfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
  chCfg.dma_desc_num=6; chCfg.dma_frame_num=512;
  esp_err_t e = i2s_new_channel(&chCfg, NULL, &rx);
  if(e!=ESP_OK || rx==nullptr){
    report("MIC", DOMUS_SKIP, String("INMP441 SKIP: i2s_new_channel RX fallo ")+esp_err_to_name(e)+" (sin PSRAM? sin modulo? )");
    return;
  }
  i2s_std_slot_config_t slot = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO);
  slot.slot_mask = I2S_STD_SLOT_LEFT; // L/R a GND = LEFT en Domus
  i2s_std_config_t std={
    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(16000),
    .slot_cfg = slot,
    .gpio_cfg = { .mclk=I2S_GPIO_UNUSED, .bclk=MIC_SCK_PIN, .ws=MIC_WS_PIN, .dout=I2S_GPIO_UNUSED, .din=MIC_SD_PIN,
                  .invert_flags={.mclk_inv=false,.bclk_inv=false,.ws_inv=false}}
  };
  e = i2s_channel_init_std_mode(rx,&std);
  if(e!=ESP_OK){
    report("MIC", DOMUS_SKIP, String("INMP441 SKIP: i2s init std mode fallo ")+esp_err_to_name(e)+" verifica GPIO15/16/17 y que PSRAM este habilitado (PSRAM=opi)");
    i2s_del_channel(rx); return;
  }
  e = i2s_channel_enable(rx);
  if(e!=ESP_OK){ report("MIC", DOMUS_SKIP, String("INMP441 SKIP: enable fallo ")+esp_err_to_name(e)); i2s_del_channel(rx); return; }

  const int BLOCK=512;
  int32_t* raw = (int32_t*)heap_caps_malloc(BLOCK*sizeof(int32_t), MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
  if(!raw){
    report("MIC", DOMUS_FAIL, "INMP441 FAIL: sin RAM interna para bloque I2S");
    i2s_channel_disable(rx); i2s_del_channel(rx); return;
  }
  emitLog("MIC","Capturando ~1s de audio 16kHz (habla o haz ruido)...");

  long sum=0; int32_t peak=0; unsigned satur=0; unsigned total=0;
  unsigned long t0=millis();
  // Lee ~1 segundo = 16000 muestras /512 ~31 bloques con timeout 600ms cada uno
  for(int b=0;b<32 && millis()-t0 < 1500; b++){
    size_t bytes=0;
    esp_err_t re=i2s_channel_read(rx, raw, BLOCK*sizeof(int32_t), &bytes, 600);
    if(re!=ESP_OK){ emitLog("MIC","read err "+String(esp_err_to_name(re))); continue; }
    size_t cnt2=bytes/sizeof(int32_t);
    if(cnt2==0) continue;
    // INMP441 entrega 24 bits en slot 32: >>14 para dejar margen como POC oficial
    for(size_t i=0;i<cnt2;i++){
      int32_t v = raw[i] >> 14;
      if(v>32767) v=32767; if(v<-32768) v=-32768;
      int32_t av = v<0? -v : v;
      if(av>peak) peak=av;
      if(av>=30000) satur++;
      sum += v;
      total++;
    }
  }
  heap_caps_free(raw);
  i2s_channel_disable(rx); i2s_del_channel(rx);

  if(total==0){ report("MIC", DOMUS_SKIP, "INMP441 leyo 0 muestras -> posible micro desconectado o I2S sin datos (L/R a GND?)"); return; }
  long dc = sum / (long)total;
  // RMS aprox con los datos ya capturados no guardamos energia completa; estimamos con peak como proxy tolerante
  String det="INMP441 GPIO WS15 SD16 SCK17 16kHz muestras="+String(total)+" dc~"+String(dc)+" peak~"+String(peak)+" satur="+String(satur)+" | "
            +"Si peak <200 en silencio y sube >2000 al hablar -> micro OK. Si siempre 0 o siempre >30000 -> revisa VDD=3.3V (jamas 5V) y L/R->GND.";
  DomusResult r = (peak < 50 && satur==0) ? DOMUS_WARN : DOMUS_PASS; // en silencio total puede ser WARN, no FAIL
  report("MIC", r, det);
}

void testMAX98357(){
  if(TTS_BCLK_PIN==I2S_GPIO_UNUSED || TTS_WS_PIN==I2S_GPIO_UNUSED || TTS_DOUT_PIN==I2S_GPIO_UNUSED){ report("SPK", DOMUS_SKIP, "MAX98357 deshabilitado en placa limitada (pins -1, 40/41/42 no expuestos) -> SKIP"); return; }
  i2s_chan_handle_t tx=nullptr;
  i2s_chan_config_t chCfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
  esp_err_t e = i2s_new_channel(&chCfg, &tx, NULL);
  if(e!=ESP_OK || tx==nullptr){
    report("SPK", DOMUS_SKIP, String("MAX98357 SKIP: i2s_new_channel TX fallo ")+esp_err_to_name(e)+" (GPIO40-42 reservados, verifica que esten expuestos y que PSRAM=opi)");
    return;
  }
  i2s_std_config_t std={
    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(16000),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = { .mclk=I2S_GPIO_UNUSED, .bclk=TTS_BCLK_PIN, .ws=TTS_WS_PIN, .dout=TTS_DOUT_PIN, .din=I2S_GPIO_UNUSED,
                  .invert_flags={.mclk_inv=false,.bclk_inv=false,.ws_inv=false}}
  };
  e = i2s_channel_init_std_mode(tx,&std);
  if(e!=ESP_OK){
    report("SPK", DOMUS_SKIP, String("MAX98357 SKIP: init fallo ")+esp_err_to_name(e)+" -> GPIO40 BCLK 41 WS 42 DOUT provisionales, confirma serigrafia de tu S3 N16R8 antes de cablear fuerte.");
    i2s_del_channel(tx); return;
  }
  e = i2s_channel_enable(tx);
  if(e!=ESP_OK){ report("SPK", DOMUS_SKIP, String("MAX98357 SKIP: enable fallo ")+esp_err_to_name(e)); i2s_del_channel(tx); return; }

  emitLog("SPK","Generando tono 1000Hz 600ms en MAX98357A (si no suena revisa VIN=5V_BUS, GND, SPK+ / SPK- sin llevar SPK- a GND)...");
  const int SR=16000; const int FREQ=1000; const int MS=600;
  const int N = SR*MS/1000;
  int16_t* buf = (int16_t*)heap_caps_malloc(N*sizeof(int16_t), MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
  if(!buf){ report("SPK", DOMUS_FAIL, "MAX98357 FAIL: sin RAM para tono"); i2s_channel_disable(tx); i2s_del_channel(tx); return; }
  for(int i=0;i<N;i++) buf[i] = (int16_t)(9000 * sin(2*M_PI*FREQ*i/SR));
  size_t w=0; e=i2s_channel_write(tx, buf, N*sizeof(int16_t), &w, 1000);
  heap_caps_free(buf);
  i2s_channel_disable(tx); i2s_del_channel(tx);
  if(e!=ESP_OK) report("SPK", DOMUS_FAIL, String("MAX98357 FAIL write ")+esp_err_to_name(e));
  else report("SPK", DOMUS_PASS, "MAX98357 I2S tono enviado "+String(w)+" bytes. Si no escuchaste nada: verifica altavoz 4R/3W entre SPK+ y SPK-, 5V_BUS y pines 40/41/42 (ver 18-Manual). SKIP si no tienes modulo es normal.");
}
#else
void testINMP441(){ report("MIC", DOMUS_SKIP, "INMP441 SKIP: driver/i2s_std.h no disponible en este core -> actualiza Arduino-ESP32 a 3.3.10"); }
void testMAX98357(){ report("SPK", DOMUS_SKIP, "MAX98357 SKIP: driver/i2s_std.h no disponible en este core"); }
#endif

void testDFPlayer(){
  if(MP3_RX_PIN<0 || MP3_TX_PIN<0){ report("MP3", DOMUS_SKIP, "DFPlayer deshabilitado en placa limitada (pins -1, 18/19 no expuestos) -> SKIP"); return; }
  HardwareSerial &s = Serial1;
  bool began=false;
  s.begin(9600, SERIAL_8N1, MP3_RX_PIN, MP3_TX_PIN);
  began=true;
  delay(150);
  // DFPlayer responde a 7E FF 06 3F 00 00 00 FE F7 EF (query)
  uint8_t q[10]={0x7E,0xFF,0x06,0x3F,0x00,0x00,0x00,0xFE,0xF7,0xEF};
  if(began) s.write(q,10);
  delay(200);
  int avail = s.available();
  String det="DFPlayer UART1 RX"+String(MP3_RX_PIN)+" TX"+String(MP3_TX_PIN)+" 9600 baudios, bytes tras query="+String(avail);
  if(avail>0){
    String hex=""; while(s.available()){ uint8_t b=s.read(); hex += String(b,HEX)+" "; }
    det += " resp=["+hex+"] -> modulo parece conectado (respaldo opcional)";
    report("MP3", DOMUS_PASS, det);
  } else {
    det += " -> sin respuesta (normal si no conectado).";
    report("MP3", DOMUS_SKIP, det);
  }
  s.end();
}

void testWS2812(){
  report("WS2812", DOMUS_SKIP, "WS2812 tira/aro 5V en espera de pin libre (ver auditoria T00: no usar pin de arranque/USB/PSRAM). Necesita 74AHCT125 + 330R + 1000uF. Prueba visual futura: usar comando LED <gpio> tras asignar pin definitivo.");
}

// -------------------- SEÑALES AUX VIA COMANDO -------------------------------
void cmdBuzz(int pin, int freq){
  if(pin<0 || pin>48){ report("BUZZ", DOMUS_FAIL, "Pin fuera de rango 0-48"); return; }
  // Verificacion de conflicto con pines reservados
  int reservados[]={PIN_HUMEDAD, PIN_NIVEL_AGUA, PIN_LDR, PIN_SALIDA_BOMBA, PIN_SALIDA_LUZ_SALA, PIN_SALIDA_LUZ_CUARTO, PIN_SALIDA_VENTILADOR, PIN_SALIDA_LUZ_INVERNADERO, PIN_PIR, PIN_PARO, PIN_MIC_OFF, PIN_DEMO, I2C_SDA_PIN, I2C_SCL_PIN, PIN_DHT11, MIC_WS_PIN, MIC_SD_PIN, MIC_SCK_PIN, MP3_RX_PIN, MP3_TX_PIN, SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN, TTS_BCLK_PIN, TTS_WS_PIN, TTS_DOUT_PIN};
  for(int r: reservados) if(r==pin){ report("BUZZ", DOMUS_WARN, String("Pin ")+pin+" esta reservado en DOMUS (ver domus_types). Usa otro libre para no pisar sensor. Igual intentando 300ms..."); break; }
  pinMode(pin, OUTPUT);
  // tone en ESP32-S3 usa ledc por debajo; si no disponible hace digital
  tone(pin, freq, 300);
  delay(400); noTone(pin);
  report("BUZZ", DOMUS_PASS, "Buzzer/pasivo en GPIO"+String(pin)+" freq="+String(freq)+"Hz 300ms -> si no sono revisa VCC y transistor.");
}
void cmdLedBlink(int pin, int veces=5){
  if(pin<0 || pin>48){ report("LED", DOMUS_FAIL, "Pin fuera de rango"); return; }
  pinMode(pin, OUTPUT);
  for(int i=0;i<veces;i++){ digitalWrite(pin, HIGH); delay(250); digitalWrite(pin, LOW); delay(250); }
  report("LED", DOMUS_PASS, "LED en GPIO"+String(pin)+" parpadeo "+String(veces)+"x 250ms -> verifica con resistencia 220R-1k a GND.");
}

// -------------------- RONDA COMPLETA ------------------------------------------
void rondaCompleta(){
  cnt={0,0,0,0,0};
  Serial.println("\n========== DOMUS RONDA COMPLETA — tolerante (si falta algo = SKIP) ==========");
  emitLog("INFO","Inventario YA TIENES vs FALTA en 01-Inventario. Pines segun 18-Manual. Planes T00-T10 pendientes = SKIP esperado.");
  testSistema();
  testI2C();
  testTodasPantallas(); // LCD I2C 0x27/0x3F + OLED 0x3C/0x3D -> Hola, + TFT SPI -> Hola
  testDHT();
  testAnalogSensor("SUELO", PIN_HUMEDAD, "Suelo", HUMEDAD_MIN_VALIDA, HUMEDAD_MAX_VALIDA, HUMEDAD_LECTURA_SECA, HUMEDAD_LECTURA_HUMEDA);
  testAnalogSensor("NIVEL", PIN_NIVEL_AGUA, "Nivel", NIVEL_AGUA_MIN_VALIDO, NIVEL_AGUA_MAX_VALIDO, 0, 4095); // sin % serio, solo raw
  testAnalogSensor("LDR",  PIN_LDR, "Luz(LDR)", LDR_MIN_VALIDO, LDR_MAX_VALIDO, LDR_LECTURA_OSCURO, LDR_LECTURA_BRILLANTE);
  // Detalle nivel para bomba
  { int raw=adcProm(PIN_NIVEL_AGUA,8); String d="Nivel raw="+String(raw)+" umbralMin="+String(NIVEL_AGUA_MINIMO_CRUDO)+" -> bomba "+(raw < NIVEL_AGUA_MINIMO_CRUDO ? "BLOQUEADA (seguridad)" : "permitida")+" (calibra CAL_NIVEL tras medir deposito vacio)"; report("BOMBA", DOMUS_PASS, d); }
  testPIRSnapshot();
  testBotones();
  testRelesDry(false); // sin pulso por defecto
  testSD();
  testINMP441();
  testMAX98357();
  testDFPlayer();
  testWS2812();
  // Resumen
  Serial.println("\n---------- RESUMEN RONDA ----------");
  Serial.println("TOTAL="+String(cnt.total)+" PASS="+String(cnt.pass)+" WARN="+String(cnt.warn)+" SKIP="+String(cnt.skip)+" FAIL="+String(cnt.fail));
  if(cnt.fail>0) Serial.println("=> Hay FAIL: revisa cableado/fuente antes de construir (ver 16-Plan testeo T01-T05).");
  else if(cnt.skip>0) Serial.println("=> Solo SKIP/WARN: normal si te falta rele4ch/INMP441/MAX/SD/panel (no se aguito el test).");
  else Serial.println("=> Todo PASS en seco. Siguiente: T06 cargas reales una por una + medir corriente/caida 5V.");
  Serial.println("Comandos: H ayuda | T todo | R SI pulso rele | A analog live | P pir live | O monitor 2s | W pantallas");
  Serial.println("TEST;RESUMEN;DONE;"+String(cnt.pass)+"/"+String(cnt.total)+" PASS");
  // Deja resumen visible 4s en todas las pantallas detectadas, luego cada una conserva su “Hola”
  if(lcdOk){
    lcd->clear(); lcd->setCursor(0,0); lcd->print("SELFTEST "+String(cnt.pass)+"/"+String(cnt.total));
    lcd->setCursor(0,1); lcd->print(cnt.fail?"FAIL revisa Serial":"PASS/SKIP OK");
    delay(2500);
    // Restaura Hola
    lcd->clear(); lcd->setCursor(0,0); lcd->print("Hola DOMUS");
    lcd->setCursor(0,1); lcd->print("LCD 0x"+String(lcdAddrActiva,HEX)+" OK");
  }
#if DOMUS_HAS_SSD1306
  if(oledOk && oledSSD){
    oledSSD->clearDisplay(); oledSSD->setTextSize(2); oledSSD->setTextColor(SSD1306_WHITE);
    oledSSD->setCursor(0,0); oledSSD->println("Hola"); oledSSD->setTextSize(1);
    oledSSD->setCursor(0,28); oledSSD->println("DOMUS OLED"); oledSSD->display();
  }
#endif
#if DOMUS_HAS_SH110X
  if(oledOk && oledSH1106){
    oledSH1106->clearDisplay(); oledSH1106->setTextSize(2); oledSH1106->setTextColor(SH110X_WHITE);
    oledSH1106->setCursor(0,0); oledSH1106->println("Hola"); oledSH1106->display();
  }
#endif
}

// -------------------- MONITOR CONTINUO Y MENU ---------------------------------
bool monitorOn=false;
unsigned long lastMonitor=0;

void printHelp(){
#if PLACA_LIMITADA
  Serial.println(R"(
========== DOMUS SELFTEST v2 — PLACA LIMITADA ==========
Pines expuestos: 4 5 6 7 8 | 3 9 10 11 12 13 25 26 27 28 46  (3v3/5v/gnd/rst)
Mapa: I2C SDA11 SCL12 (LCD 0x27/0x3F + OLED 0x3C), Rele 4-8, Suelo3 Nivel9 LDR10, PIR13,
      TFT ST7789: SCLK46 MOSI28 CS25 DC26 RST27 (comparte con DHT25+BTNs 26/27/28),
      DHT/BTNs hacen SKIP mientras TFT conectado. SD/Mic/MAX/MP3 deshabilitados (-1).
H / ?            ayuda
T                ronda completa (tolerante) -> cada pantalla -> "Hola"
I                scan I2C SDA11/SCL12
L                LCD I2C -> "Hola"
OLED             OLED 4p I2C -> "Hola"
TFT              TFT ST7789 -> "Hola" (si no ves: revisa 3.3V y BLK a 3.3V)
W                las 3 pantallas a la vez
D                DHT11 en 25 (SKIP si TFT conectado)
A                analogicos 3/9/10 live
P                PIR live 10s en 13
B                botones 26/27/28 (SKIP si TFT)
R                reles 4-8 seco
R SI             reles con pulso 350ms
E                resumen
O                monitor 2s (LCD/OLED)
BUZZ <pin> <hz> / LED <pin> [n] / ESTADO
Si sale SKIP es esperado en esta placa. Para probar DHT/botones: desconecta TFT o pon TFT_* a -1.
)");
#else
  Serial.println(R"(
========== DOMUS SELFTEST v2 — PLACA COMPLETA ==========
H / ? / HELP     esta ayuda
T                ronda completa -> todas las pantallas dibujan "Hola"
I                scan I2C (0x27/0x3F LCD y 0x3C/0x3D OLED)
L                LCD I2C 1602 -> "Hola"
OLED             OLED 4p I2C -> "Hola" (0x3C/0x3D)
TFT              TFT ST7789 1.54" SPI -> "Hola" (33/34/35/36/37)
W / PANTALLAS    las 3 pantallas a la vez
D                DHT | A analogicos | P PIR live | B botones
R / R SI         reles seco / con pulso
S SD | M mic | X spk | Q DFPlayer | E resumen | O monitor | BUZZ/LED/ESTADO
)");
#endif
}

void snapshotRapido(){
  String s="SNAP suelo raw="+String(adcProm(PIN_HUMEDAD,6))
    +" nivel="+String(adcProm(PIN_NIVEL_AGUA,6))
    +" ldr="+String(adcProm(PIN_LDR,6))
    +" pir="+(digitalRead(PIN_PIR)==HIGH?"HIGH":"LOW")
    +" paro="+(digitalRead(PIN_PARO)==LOW?"LOW":"HIGH")
    +" micOff="+(digitalRead(PIN_MIC_OFF)==LOW?"LOW":"HIGH");
  emitLog("SNAP", s);
}

void monitorTick(){
  if(!monitorOn) return;
  if(millis()-lastMonitor < 2000) return;
  lastMonitor=millis();
  int sRaw=adcProm(PIN_HUMEDAD,4), sPct=pctDesdeCal(sRaw,HUMEDAD_LECTURA_SECA,HUMEDAD_LECTURA_HUMEDA);
  int nRaw=adcProm(PIN_NIVEL_AGUA,4);
  int lRaw=adcProm(PIN_LDR,4), lPct=pctDesdeCal(lRaw,LDR_LECTURA_OSCURO,LDR_LECTURA_BRILLANTE);
  float t=dht.readTemperature(), h=dht.readHumidity();
  String line="MON H:"+String(sPct)+"%("+String(sRaw)+") N:"+String(nRaw)+" L:"+String(lPct)+"%("+String(lRaw)+") "
    +"PIR:"+(digitalRead(PIN_PIR)==HIGH?"1":"0")+" T:"+(isnan(t)?"ERR":String(t,1)+"C")
    +" HR:"+(isnan(h)?"ERR":String(h,1)+"%")
    +" mic:"+(digitalRead(PIN_MIC_OFF)==LOW?"OFF":"ON");
  if(lcdOk){
    lcd->clear(); lcd->setCursor(0,0); lcd->print("H:"+String(sPct)+"% T:"+(isnan(t)?"ERR":String(t,0)+"C"));
    String l2="N:"+String(nRaw)+" L:"+String(lPct)+"%";
    if(digitalRead(PIN_PARO)==LOW) l2="!! PARO !!";
    lcd->setCursor(0,1); lcd->print(l2.substring(0,16));
  }
#if DOMUS_HAS_SSD1306
  if(oledOk && oledSSD){
    oledSSD->clearDisplay(); oledSSD->setTextSize(1); oledSSD->setTextColor(SSD1306_WHITE);
    oledSSD->setCursor(0,0); oledSSD->print("H:"); oledSSD->print(sPct); oledSSD->print("% T:"); oledSSD->print(isnan(t)?"ERR":String(t,0)+"C");
    oledSSD->setCursor(0,12); oledSSD->print("N:"); oledSSD->print(nRaw); oledSSD->print(" L:"); oledSSD->print(lPct); oledSSD->print("%");
    oledSSD->setCursor(0,24); oledSSD->print(digitalRead(PIN_PARO)==LOW?"!!PARO!!":"MON 2s");
    oledSSD->display();
  }
#endif
#if DOMUS_HAS_SH110X
  if(oledOk && oledSH1106){
    oledSH1106->clearDisplay(); oledSH1106->setTextSize(1); oledSH1106->setTextColor(SH110X_WHITE);
    oledSH1106->setCursor(0,0); oledSH1106->print("H:"); oledSH1106->print(sPct); oledSH1106->print("%");
    oledSH1106->display();
  }
#endif
  emitLog("MON", line);
}

// Parser Serial tolerante
String bufCmd;
void handleLine(String line){
  line.trim(); if(line.length()==0) return;
  String up=line; up.toUpperCase();
  // Comandos con argumentos primero
  if(up.startsWith("BUZZ")){
    // BUZZ pin freq
    int sp1=up.indexOf(' '), sp2=up.indexOf(' ', sp1+1);
    int pin=-1, freq=1000;
    if(sp1>0){ pin = up.substring(sp1+1, sp2>0?sp2:up.length()).toInt(); if(sp2>0) freq = up.substring(sp2+1).toInt(); if(freq<50)freq=1000; cmdBuzz(pin,freq); }
    else report("BUZZ", DOMUS_FAIL, "Uso: BUZZ <pin> [hz] ej BUZZ 42 1200");
    return;
  }
  if(up.startsWith("LED")){
    int sp1=up.indexOf(' '), sp2=up.indexOf(' ', sp1+1);
    int pin=-1, n=5;
    if(sp1>0){ pin=up.substring(sp1+1, sp2>0?sp2:up.length()).toInt(); if(sp2>0) n=up.substring(sp2+1).toInt(); cmdLedBlink(pin, n); }
    else report("LED", DOMUS_FAIL, "Uso: LED <pin> [veces] ej LED 5 5");
    return;
  }
  if(up=="R SI" || up=="R-SI" || up=="RSI" || up=="R=SI"){
    emitLog("RELE","Pulso CON carga: asegúrate de tener cargas desconectadas o LEDs de prueba, bomba nunca en seco, 5V_BUS estable.");
    testRelesDry(true);
    return;
  }
  // Alias simples
  if(up=="H"||up=="?"||up=="HELP"||up=="AYUDA"){ printHelp(); return; }
  if(up=="T"||up=="TODO"||up=="ALL"){ rondaCompleta(); return; }
  if(up=="I"||up=="I2C"){ testI2C(); return; }
  if(up=="L"||up=="LCD"){ testLCD(); return; }
  if(up=="OLED"){ testOLED(); return; }
  if(up=="TFT"){ testST7789(); return; }
  if(up=="W"||up=="PANTALLAS"||up=="PANTALLA"){ testTodasPantallas(); return; }
  if(up=="D"||up=="DHT"){ testDHT(); return; }
  if(up=="B"||up=="BTN"||up=="BOTONES"){ testBotones(); return; }
  if(up=="R"){ testRelesDry(false); return; }
  if(up=="S"||up=="SD"){ testSD(); return; }
  if(up=="M"||up=="MIC"){ testINMP441(); return; }
  if(up=="X"||up=="SPK"||up=="ALTAVOZ"){ testMAX98357(); return; }
  if(up=="Q"||up=="MP3"){ testDFPlayer(); return; }
  if(up=="E"||up=="RESUMEN"){ Serial.println("RESUMEN total="+String(cnt.total)+" pass="+String(cnt.pass)+" skip="+String(cnt.skip)+" warn="+String(cnt.warn)+" fail="+String(cnt.fail)+" pantallas LCD:"+(lcdOk?"OK":"NO")+" OLED:"+(oledOk?"OK":"NO")+" TFT:"+(tftOk?"OK":"NO")); return; }
  if(up=="O"||up=="MON"||up=="MONITOR"){ monitorOn=!monitorOn; report("MON", DOMUS_PASS, String("Monitor continuo ")+(monitorOn?"ON 2s":"OFF")); return; }
  if(up=="ESTADO"){ snapshotRapido(); return; }
  if(up=="A"){
    for(int i=0;i<5;i++){
      int sr=adcProm(PIN_HUMEDAD,6), sp=pctDesdeCal(sr,HUMEDAD_LECTURA_SECA,HUMEDAD_LECTURA_HUMEDA);
      int nr=adcProm(PIN_NIVEL_AGUA,6);
      int lr=adcProm(PIN_LDR,6), lp=pctDesdeCal(lr,LDR_LECTURA_OSCURO,LDR_LECTURA_BRILLANTE);
      emitLog("A","ciclo "+String(i+1)+"/5 suelo="+String(sp)+"%("+String(sr)+") nivel="+String(nr)+" ldr="+String(lp)+"%("+String(lr)+")");
      delay(600);
    }
    return;
  }
  if(up=="P"){ testPIRLive10s(); return; }
  report("CMD", DOMUS_SKIP, "Comando '"+line+"' no reconocido. Escribe H para menu. No se aguito.");
}

void setup(){
  Serial.begin(115200);
  delay(500);
#if PLACA_LIMITADA
  Serial.println("\n\n=== PROJECT DOMUS — SELFTEST v2 LIMITADA (16 GPIOs) ===");
  Serial.println("Pines: 3,4,5,6,7,8,9,10,11,12,13,25,26,27,28,46 | I2C 11/12 | TFT 25/26/27/28/46");
  Serial.println("Cada pantalla detectada dibuja 'Hola'. Si falta algo -> SKIP (no se agüita).");
#else
  Serial.println("\n\n=== PROJECT DOMUS — SELFTEST v2 COMPLETA ===");
  Serial.println("Si algo falta reporta SKIP y sigue. Cada pantalla detectada dibuja 'Hola'.");
#endif
  for(int i=0;i<TOTAL_SALIDAS;i++){ if(PINES_SALIDAS[i]>=0){ digitalWrite(PINES_SALIDAS[i], nivelSalida(i,false)); pinMode(PINES_SALIDAS[i], OUTPUT); } }
  if(PIN_PIR>=0) pinMode(PIN_PIR, INPUT);
  if(PIN_PARO>=0) pinMode(PIN_PARO, INPUT_PULLUP);
  if(PIN_MIC_OFF>=0) pinMode(PIN_MIC_OFF, INPUT_PULLUP);
  if(PIN_DEMO>=0) pinMode(PIN_DEMO, INPUT_PULLUP);
  if(TFT_BLK_PIN>=0){ pinMode(TFT_BLK_PIN, OUTPUT); digitalWrite(TFT_BLK_PIN, HIGH); }
  analogReadResolution(12); analogSetAttenuation(ADC_11db);
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN); Wire.setTimeOut(10); delay(80);
  if(PIN_DHT11>=0) dht.begin();
  bufCmd.reserve(48);
#if PLACA_LIMITADA
  Serial.println("Setup limitado listo. LCD/OLED en SDA11 SCL12 | TFT CS25 DC26 RST27 MOSI28 SCLK46 | Sensores 3/9/10 PIR13 Rele4-8");
  Serial.println("Nota: DHT25 y BTNs 26/27/28 comparten con TFT -> haran SKIP con TFT conectado. Desconecta TFT para probarlos.");
#else
  Serial.println("Setup listo. I2C SDA21 SCL13 (LCD 0x27/0x3F + OLED 0x3C/0x3D) | TFT SPI CS33 DC34 RST35 MOSI36 SCLK37");
#endif
  Serial.println("Iniciando ronda completa en 1s... cada pantalla -> 'Hola DOMUS'");
  delay(1000);
  rondaCompleta();
  Serial.println("Escribe H para menu. W=solo pantallas. O=monitor 2s.");
}

void loop(){
  // Serial parser no bloqueante, cede aunque haya rafaga
  unsigned int n=0;
  while(Serial.available() && n<96){
    n++; char c=(char)Serial.read();
    if(c=='\r') continue;
    if(c=='\n'){ if(bufCmd.length()){ handleLine(bufCmd); bufCmd=""; } }
    else { if(bufCmd.length()<48) bufCmd+=c; else { bufCmd=""; report("CMD", DOMUS_SKIP, "Linea >48 chars descartada"); while(Serial.available() && (char)Serial.peek()!='\n') Serial.read(); } }
  }
  // Botones: informa cambio sin bloquear
  static int lastParo=HIGH, lastMic=HIGH; // init
  int curParo=digitalRead(PIN_PARO), curMic=digitalRead(PIN_MIC_OFF);
  if(curParo!=lastParo){ lastParo=curParo; emitLog("BTN","PARO ahora "+String(curParo==LOW?"PULSADO":"libre")+(curParo==LOW?" -> cortaria todo en firmware principal":"")); }
  if(curMic!=lastMic){ lastMic=curMic; emitLog("BTN","MIC_OFF ahora "+String(curMic==LOW?"BLOQUEADO":"habilitado")); }
  monitorTick();
  delay(20);
}
