/*
  PROJECT DOMUS — ANIMACION 3 PANTALLAS (placa limitada) v3 SEGURO
  Placa: ESP32-S3 N16R8  FQBN: esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB
  Pines seguros: 4,5,6,7,8,9,10,11,12,13,3 (25-28 flash, 46 strapping -> NO USAR)
  I2C (LCD+OLED) SDA11 SCL12  |  TFT ST7789 SCLK8 MOSI7 CS4 DC5 RST6  |  Sens 3/9/10 PIR13
  Rele deshabilitado en modo anim (comparte 4-8 con TFT). Para reles, desconecta TFT.
  Cada pantalla muestra animacion "Hola" con yield.
*/

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_ST7789.h>
#include <LiquidCrystal_I2C.h>

#define I2C_SDA_PIN 11
#define I2C_SCL_PIN 12
// TFT en pines seguros 4-8 (reles deshabilitados en modo anim) -> evita flash 25-28 y strapping 3/46
#define TFT_CS_PIN   4
#define TFT_DC_PIN   5
#define TFT_RST_PIN  6
#define TFT_MOSI_PIN 7
#define TFT_SCLK_PIN 8
#define TFT_BLK_PIN  -1

#define LCD_ADDR1 0x27
#define LCD_ADDR2 0x3F
#define OLED_ADDR1 0x3C
#define OLED_ADDR2 0x3D

LiquidCrystal_I2C* lcd = nullptr;
Adafruit_SSD1306* oled = nullptr;
Adafruit_ST7789* tft = nullptr;
SPIClass* spiTft = nullptr;

bool lcdOk=false, oledOk=false, tftOk=false;
uint8_t lcdAddr=0, oledAddr=0;

// anim helpers
unsigned long lastAnim=0;
int animFrame=0;

void scanI2C(){
  Serial.println("\n[I2C] Scan SDA11 SCL12...");
  for(uint8_t a=0x03;a<0x78;a++){
    Wire.beginTransmission(a);
    if(Wire.endTransmission()==0) Serial.printf("  Encontrado 0x%02X\n",a);
  }
}

bool initLCD(){
  for(uint8_t a:{LCD_ADDR1,LCD_ADDR2}){
    Wire.beginTransmission(a);
    if(Wire.endTransmission()==0){
      lcd = new LiquidCrystal_I2C(a,16,2);
      lcd->init(); lcd->backlight();
      lcd->clear(); lcd->setCursor(0,0); lcd->print("Hola DOMUS");
      lcd->setCursor(0,1); lcd->print("LCD 0x"); lcd->print(a,HEX); lcd->print(" OK");
      lcdAddr=a; lcdOk=true;
      Serial.printf("[LCD] OK en 0x%02X -> Hola\n",a);
      return true;
    }
  }
  Serial.println("[LCD] SKIP no encontrado 0x27/0x3F");
  return false;
}

bool initOLED(){
  for(uint8_t a:{OLED_ADDR1,OLED_ADDR2}){
    Wire.beginTransmission(a);
    if(Wire.endTransmission()==0){ oledAddr=a; break; }
  }
  if(oledAddr==0){ Serial.println("[OLED] SKIP no encontrado 0x3C/0x3D"); return false; }
  oled = new Adafruit_SSD1306(128,64,&Wire,-1);
  if(!oled->begin(SSD1306_SWITCHCAPVCC, oledAddr)){
    Serial.printf("[OLED] WARN 0x%02X responde pero SSD1306 begin fallo (prueba SH1106)\n",oledAddr);
    delete oled; oled=nullptr;
    // intenta 128x32
    oled = new Adafruit_SSD1306(128,32,&Wire,-1);
    if(!oled->begin(SSD1306_SWITCHCAPVCC, oledAddr)){
      Serial.println("[OLED] FAIL ni 64 ni 32");
      delete oled; oled=nullptr; return false;
    }
  }
  oledOk=true;
  oled->clearDisplay(); oled->setTextColor(SSD1306_WHITE);
  oled->setTextSize(2); oled->setCursor(0,0); oled->println("Hola");
  oled->setTextSize(1); oled->setCursor(0,28); oled->println("DOMUS OLED");
  oled->display();
  Serial.printf("[OLED] OK 0x%02X 128x64 -> Hola\n",oledAddr);
  return true;
}

bool initTFT(){
  // usa pines seguros, no 25-28 flash
  if(TFT_CS_PIN<0 || TFT_DC_PIN<0 || TFT_MOSI_PIN<0 || TFT_SCLK_PIN<0){
    Serial.println("[TFT] SKIP pines -1");
    return false;
  }
  spiTft = new SPIClass(HSPI);
  spiTft->begin(TFT_SCLK_PIN, -1, TFT_MOSI_PIN, TFT_CS_PIN);
  yield();
  if(TFT_RST_PIN>=0) pinMode(TFT_RST_PIN, OUTPUT);
  if(TFT_BLK_PIN>=0){ pinMode(TFT_BLK_PIN, OUTPUT); digitalWrite(TFT_BLK_PIN,HIGH); }
  delay(10); yield();
  tft = new Adafruit_ST7789(spiTft, TFT_CS_PIN, TFT_DC_PIN, TFT_RST_PIN);
  if(!tft){ Serial.println("[TFT] FAIL sin RAM"); return false; }
  tft->init(240,240);
  yield();
  tft->setRotation(0);
  tft->fillScreen(ST77XX_BLACK);
  yield();
  tft->setTextColor(ST77XX_WHITE); tft->setTextSize(3);
  tft->setCursor(70,60); tft->print("Hola");
  tft->setTextSize(1); tft->setCursor(40,100); tft->print("DOMUS ST7789 240x240");
  tftOk=true;
  Serial.printf("[TFT] OK HSPI SCLK%d MOSI%d CS%d DC%d RST%d -> Hola\n", TFT_SCLK_PIN, TFT_MOSI_PIN, TFT_CS_PIN, TFT_DC_PIN, TFT_RST_PIN);
  return true;
}

// ---- ANIMACIONES ----
void animLCDLoop(){
  if(!lcdOk) return;
  // scroll Hola + barra
  static int pos=0;
  lcd->clear();
  lcd->setCursor(pos%12,0);
  lcd->print("Hola DOMUS!!");
  lcd->setCursor(0,1);
  for(int i=0;i<16;i++) lcd->print(i < (animFrame%16) ? (char)255 : ' ');
  pos++; if(pos>16) pos=0;
}

void animOLEDLoop(){
  if(!oledOk || !oled) return;
  oled->clearDisplay();
  // fondo animado: barra progresiva
  int bar = animFrame % 128;
  oled->drawRect(0,0,128,64, SSD1306_WHITE);
  oled->fillRect(2,2,bar,6, SSD1306_WHITE);
  // pelota rebotando
  int x = (animFrame*3) % 120;
  int y = 16 + (abs((animFrame%40)-20));
  oled->fillCircle(x+6, y, 4, SSD1306_WHITE);
  // texto Hola con tamaño que pulsa
  oled->setTextSize( (animFrame%20<10)?2:1 );
  oled->setTextColor(SSD1306_WHITE);
  oled->setCursor(30, 32);
  oled->print("Hola");
  oled->setTextSize(1);
  oled->setCursor(10, 50);
  oled->printf("OLED 0x%02X f%d",oledAddr,animFrame);
  oled->display();
}

void animTFTLoop(){
  if(!tftOk || !tft) return;
  // fondo cambia de color cada frame
  // limpia solo una franja para no parpadear todo
  tft->fillScreen(ST77XX_BLACK);
  // rectangulo rebotando
  int rx = (animFrame*4) % (240-30);
  int ry = 30 + (abs((animFrame%60)-30));
  uint16_t col = tft->color565(255 - (animFrame*3)%255, (animFrame*5)%255, 128);
  tft->fillRect(rx, ry, 30, 20, col);
  tft->drawRect(rx-1, ry-1, 32, 22, ST77XX_WHITE);
  // texto Hola arcoiris
  tft->setTextSize(3);
  for(int i=0;i<4;i++){
    uint16_t c = tft->color565( (i*60 + animFrame*10)%255, 255-(i*40)%255, (i*80)%255 );
    tft->setTextColor(c);
    tft->setCursor(70 + i*2, 70 + i*2);
    if(i==0) tft->print("Hola");
  }
  tft->setTextColor(ST77XX_WHITE);
  tft->setTextSize(2);
  tft->setCursor(20, 120);
  tft->print("DOMUS ST7789");
  tft->setTextSize(1);
  tft->setCursor(10, 150);
  tft->printf("TFT 1.54 anim f%d",animFrame);
  // barra inferior
  int bw = (animFrame*2) % 240;
  tft->fillRect(0,230, bw, 10, ST77XX_GREEN);
  tft->drawRect(0,230,240,10, ST77XX_WHITE);
}

void rondaAnimada(){
  Serial.println("\n=== RONDA ANIMADA 3 PANTALLAS ===");
  scanI2C(); yield(); delay(200); yield();
  initLCD(); yield(); delay(300); yield();
  initOLED(); yield(); delay(300); yield();
  initTFT(); yield(); delay(300); yield();
  int ok = (lcdOk?1:0)+(oledOk?1:0)+(tftOk?1:0);
  Serial.printf("Pantallas OK %d/3  LCD:%s OLED:%s TFT:%s\n", ok, lcdOk?"SI":"NO", oledOk?"SI":"NO", tftOk?"SI":"NO");
  if(ok==0) Serial.println("Ninguna pantalla respondio -> revisa SDA11 SCL12 y TFT SCLK46 MOSI13 CS3 DC9 RST10 VCC 3.3V");
}

void setup(){
  Serial.begin(115200);
  delay(600);
  Serial.println("\n\n=== DOMUS ANIM v3 - 3 pantallas Hola animado SEGURO ===");
  Serial.println("Pines: I2C SDA11 SCL12 | TFT SCLK8 MOSI7 CS4 DC5 RST6 | Sens 3/9/10 PIR13");
  Serial.println("TFT usa 4-8 (reles OFF en anim). Sensores 3/9/10 libres. Evita 25-28 flash.");
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Wire.setTimeOut(10);
  delay(100); yield();
  rondaAnimada();
  Serial.println("Animando 10 FPS... comandos: W=ronda, T=sensores, H=ayuda");
  lastAnim=millis();
}

void testSensoresBasico(){
  Serial.println("\n[SENSORES] Soil3 Nivel9 LDR10 PIR13 Rele4-8");
  for(int p:{3,9,10}){
    int v=0; for(int i=0;i<8;i++){ v+=analogRead(p); delay(2); } v/=8;
    Serial.printf("  GPIO%d raw %d\n",p,v);
  }
  Serial.printf("  PIR13=%s\n", digitalRead(13)==HIGH?"HIGH":"LOW");
  for(int r:{4,5,6,7,8}){
    int lvl = digitalRead(r);
    Serial.printf("  Rele GPIO%d init %s\n",r, lvl==LOW?"LOW":"HIGH");
  }
  if(lcdOk){ lcd->clear(); lcd->setCursor(0,0); lcd->print("Sensores OK"); lcd->setCursor(0,1); lcd->print("Revisar Serial"); }
}

void loop(){
  yield();
  // animacion 10 FPS aprox con yield para WDT
  if(millis()-lastAnim > 120){
    lastAnim=millis();
    animFrame++;
    animLCDLoop(); yield();
    animOLEDLoop(); yield();
    animTFTLoop(); yield();
  }
  // comandos no bloqueantes
  static String buf="";
  while(Serial.available()){
    char c=Serial.read();
    if(c=='\r') continue;
    if(c=='\n'){
      buf.trim(); buf.toUpperCase();
      if(buf=="W"||buf=="ROND"||buf=="ANIM") rondaAnimada();
      else if(buf=="T") testSensoresBasico();
      else if(buf=="H"||buf=="?"||buf=="HELP"){
        Serial.println("Comandos: W=ronda animada, T=sensores, H=ayuda, L=lcd solo, O=oled solo, F=tft solo");
      } else if(buf=="L") initLCD();
      else if(buf=="O") initOLED();
      else if(buf=="F") initTFT();
      else if(buf.length()) Serial.println("CMD no reconocido: "+buf);
      buf="";
    } else {
      if(buf.length()<32) buf+=c;
    }
  }
}
