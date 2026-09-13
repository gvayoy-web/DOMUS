/* DOMUS: lector avanzado IR + calibración. No configura GPIO4-8. */
#include <Arduino.h>
#include <DHT.h>
#include <IRremote.hpp>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <new>

constexpr uint8_t PIN_LDR = 3, PIN_IR = 12, PIN_SCL = 13, PIN_DHT = 14;
constexpr uint8_t PIN_SUELO = 15, PIN_NIVEL = 16, PIN_SDA = 17;
constexpr uint8_t MAX_CODIGOS = 21;
struct CodigoIR { uint8_t protocolo; uint16_t direccion, comando; };
DHT dht(PIN_DHT, DHT11);
LiquidCrystal_I2C* lcd = nullptr;
CodigoIR codigos[MAX_CODIGOS]{};
uint8_t totalCodigos = 0, direccionLcd = 0, entradaLen = 0;
char entrada[32]{};
unsigned long ultimaLecturaMs = 0;

int promedioAdc(uint8_t pin) {
  uint32_t suma = 0;
  for (uint8_t i = 0; i < 16; ++i) suma += analogRead(pin);
  return static_cast<int>(suma / 16);
}
void lineaLcd(uint8_t fila, const char* texto) {
  if (!lcd) return;
  char linea[17]; snprintf(linea, sizeof(linea), "%-16.16s", texto ? texto : "");
  lcd->setCursor(0, fila); lcd->print(linea);
}
void detectarLcd() {
  direccionLcd = 0; Serial.println("I2C;INICIO;0x08-0x77");
  for (uint8_t dir = 0x08; dir <= 0x77; ++dir) {
    Wire.beginTransmission(dir);
    if (Wire.endTransmission() == 0) {
      Serial.printf("I2C;ENCONTRADO;0x%02X\n", dir);
      if (!direccionLcd) direccionLcd = dir;
    }
  }
  if (!direccionLcd) { Serial.println("LCD;NO_DETECTADO"); return; }
  if (!lcd) lcd = new (std::nothrow) LiquidCrystal_I2C(direccionLcd, 16, 2);
  if (!lcd) { Serial.println("LCD;SIN_MEMORIA"); return; }
  lcd->init(); lcd->backlight();
  lineaLcd(0, "DOMUS DIAGNOST."); lineaLcd(1, "SIN MOTORES");
  Serial.printf("LCD;DIRECCION;0x%02X\n", direccionLcd);
}
void imprimirLecturas() {
  const int suelo = promedioAdc(PIN_SUELO), nivel = promedioAdc(PIN_NIVEL), ldr = promedioAdc(PIN_LDR);
  const float temp = dht.readTemperature(), humedad = dht.readHumidity();
  Serial.printf("ADC;SUELO=%d;NIVEL=%d;LDR=%d\n", suelo, nivel, ldr);
  if (isnan(temp) || isnan(humedad)) Serial.println("DHT;INVALIDO");
  else Serial.printf("DHT;TEMP_C=%.1f;HUM_AIRE_PCT=%.1f\n", temp, humedad);
  char a[17], b[17];
  snprintf(a, sizeof(a), "S:%4d N:%4d", suelo, nivel);
  snprintf(b, sizeof(b), "L:%4d IR:%02u", ldr, totalCodigos);
  lineaLcd(0, a); lineaLcd(1, b);
}
bool repetido(const CodigoIR& n) {
  for (uint8_t i = 0; i < totalCodigos; ++i)
    if (codigos[i].protocolo == n.protocolo && codigos[i].direccion == n.direccion && codigos[i].comando == n.comando) return true;
  return false;
}
void revisarIr() {
  if (!IrReceiver.decode()) return;
  const auto& d = IrReceiver.decodedIRData;
  const bool repeat = (d.flags & IRDATA_FLAGS_IS_REPEAT) != 0;
  Serial.printf("IR;PROTO=%u;DIR=0x%04X;CMD=0x%04X;REPEAT=%u\n",
    static_cast<unsigned>(d.protocol), d.address, d.command, repeat ? 1 : 0);
  CodigoIR n{static_cast<uint8_t>(d.protocol), d.address, d.command};
  if (!repeat && !repetido(n)) {
    if (totalCodigos < MAX_CODIGOS) { codigos[totalCodigos++] = n; Serial.printf("IR;GUARDADO;%u/21\n", totalCodigos); }
    else Serial.println("IR;LISTA_LLENA;21/21");
  }
  IrReceiver.resume();
}
void listarIr() {
  Serial.printf("IR;TOTAL=%u\n", totalCodigos);
  for (uint8_t i = 0; i < totalCodigos; ++i)
    Serial.printf("IR;%02u;PROTO=%u;DIR=0x%04X;CMD=0x%04X\n", i, codigos[i].protocolo, codigos[i].direccion, codigos[i].comando);
}
void muestraCalibracion(const char* c) {
  if (!strcmp(c, "MUESTRA_SECO")) Serial.printf("CAL;COPIAR=CAL_SECO=%d\n", promedioAdc(PIN_SUELO));
  else if (!strcmp(c, "MUESTRA_HUMEDO")) Serial.printf("CAL;COPIAR=CAL_HUMEDO=%d\n", promedioAdc(PIN_SUELO));
  else if (!strcmp(c, "MUESTRA_OSCURO")) Serial.printf("CAL;COPIAR=CAL_OSCURO=%d\n", promedioAdc(PIN_LDR));
  else if (!strcmp(c, "MUESTRA_CLARO")) Serial.printf("CAL;COPIAR=CAL_CLARO=%d\n", promedioAdc(PIN_LDR));
  else if (!strcmp(c, "MUESTRA_NIVEL")) Serial.printf("CAL;COPIAR=CAL_NIVEL=%d\n", promedioAdc(PIN_NIVEL));
  else Serial.println("NACK;MUESTRA;USA_HELP");
}
void ejecutar(const char* c) {
  if (!strcmp(c, "LECTURAS")) imprimirLecturas();
  else if (!strcmp(c, "LCD")) detectarLcd();
  else if (!strcmp(c, "IR_LISTA")) listarIr();
  else if (!strcmp(c, "IR_CLEAR")) { totalCodigos = 0; Serial.println("IR;BORRADO"); }
  else if (!strncmp(c, "MUESTRA_", 8)) muestraCalibracion(c);
  else if (!strcmp(c, "HELP")) Serial.println("CMD;LECTURAS|LCD|IR_LISTA|IR_CLEAR|MUESTRA_SECO|MUESTRA_HUMEDO|MUESTRA_OSCURO|MUESTRA_CLARO|MUESTRA_NIVEL");
  else Serial.println("NACK;COMANDO;USA_HELP");
}
void revisarSerial() {
  while (Serial.available()) {
    const char c = static_cast<char>(Serial.read());
    if (c == '\r') continue;
    if (c == '\n') { entrada[entradaLen] = '\0'; if (entradaLen) ejecutar(entrada); entradaLen = 0; }
    else if (entradaLen < sizeof(entrada) - 1) entrada[entradaLen++] = c;
    else { entradaLen = 0; Serial.println("NACK;COMANDO;MUY_LARGO"); }
  }
}
void setup() {
  Serial.begin(115200); analogReadResolution(12); analogSetAttenuation(ADC_11db);
  Wire.begin(PIN_SDA, PIN_SCL); Wire.setTimeOut(20); dht.begin();
  IrReceiver.begin(PIN_IR, DISABLE_LED_FEEDBACK); detectarLcd();
  Serial.println("DOMUS_DIAGNOSTICO_LISTO;SIN_SALIDAS;USA_HELP");
}
void loop() {
  revisarIr(); revisarSerial();
  if (millis() - ultimaLecturaMs >= 2500UL) { ultimaLecturaMs = millis(); imprimirLecturas(); }
  delay(1);
}
