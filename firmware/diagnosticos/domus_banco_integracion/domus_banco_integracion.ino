// PROJECT DOMUS — banco mínimo LCD + IR + DRV8833
// SOLO DIAGNÓSTICO. No sustituye casa_inteligente_v4.
// Arranque OFF, un motor por vez y pulso máximo de 500 ms.

#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <IRremote.hpp>
#include <new>

constexpr uint8_t PIN_SDA = 17;
constexpr uint8_t PIN_SCL = 13;
constexpr uint8_t PIN_IR = 12;
constexpr uint8_t PIN_AIN1 = 4;   // canal A: bomba
constexpr uint8_t PIN_BIN1 = 7;   // canal B: ventilador
constexpr unsigned long PULSO_MS = 500;
constexpr uint8_t MAX_CODIGOS = 21;

static_assert(PIN_SDA != PIN_SCL && PIN_IR != PIN_SDA && PIN_IR != PIN_SCL,
              "Pines LCD/IR duplicados");
static_assert(PIN_AIN1 != PIN_BIN1 && PIN_AIN1 != PIN_IR && PIN_BIN1 != PIN_IR,
              "Pines DRV/IR duplicados");

struct CodigoIR {
  uint8_t protocolo;
  uint16_t direccion;
  uint16_t comando;
};

LiquidCrystal_I2C* lcd = nullptr;
uint8_t direccionLcd = 0;
CodigoIR codigos[MAX_CODIGOS]{};
uint8_t totalCodigos = 0;
char entrada[24]{};
uint8_t entradaLen = 0;
unsigned long finPulso = 0;
char canalActivo = '-';

void apagarMotores() {
  digitalWrite(PIN_AIN1, LOW);
  digitalWrite(PIN_BIN1, LOW);
  canalActivo = '-';
  finPulso = 0;
}

void linea16(uint8_t fila, const char* texto) {
  if (!lcd) return;
  char salida[17];
  snprintf(salida, sizeof(salida), "%-16.16s", texto ? texto : "");
  lcd->setCursor(0, fila);
  lcd->print(salida);
}

void mostrarEstado(const char* detalle) {
  char superior[17];
  if (direccionLcd) snprintf(superior, sizeof(superior), "LCD:%02X IR:%02u", direccionLcd, totalCodigos);
  else snprintf(superior, sizeof(superior), "LCD:NO IR:%02u", totalCodigos);
  linea16(0, superior);
  linea16(1, detalle);
}

void detectarLcd() {
  Serial.println("I2C;INICIO;0x08-0x77");
  for (uint8_t dir = 0x08; dir <= 0x77; ++dir) {
    Wire.beginTransmission(dir);
    if (Wire.endTransmission() == 0) {
      Serial.printf("I2C;ENCONTRADO;0x%02X\n", dir);
      if (!direccionLcd) direccionLcd = dir;
    }
  }
  if (!direccionLcd) {
    Serial.println("LCD;NO_DETECTADO");
    return;
  }
  lcd = new (std::nothrow) LiquidCrystal_I2C(direccionLcd, 16, 2);
  if (!lcd) {
    Serial.println("LCD;SIN_MEMORIA");
    return;
  }
  lcd->init();
  lcd->backlight();
  mostrarEstado("DOMUS BANCO OK");
  Serial.printf("LCD;DIRECCION;0x%02X\n", direccionLcd);
}

bool codigoRepetido(uint8_t protocolo, uint16_t direccion, uint16_t comando) {
  for (uint8_t i = 0; i < totalCodigos; ++i) {
    if (codigos[i].protocolo == protocolo && codigos[i].direccion == direccion &&
        codigos[i].comando == comando) return true;
  }
  return false;
}

void leerIr() {
  if (!IrReceiver.decode()) return;
  const auto& d = IrReceiver.decodedIRData;
  const bool repeticion = (d.flags & IRDATA_FLAGS_IS_REPEAT) != 0;
  Serial.printf("IR;PROTO=%u;DIR=0x%04X;CMD=0x%04X;REPEAT=%u\n",
                (unsigned)d.protocol, d.address, d.command, repeticion ? 1 : 0);
  if (!repeticion && !codigoRepetido(d.protocol, d.address, d.command)) {
    if (totalCodigos < MAX_CODIGOS) {
      codigos[totalCodigos++] = {d.protocol, d.address, d.command};
      char mensaje[17];
      snprintf(mensaje, sizeof(mensaje), "IR %02u CMD %04X", totalCodigos, d.command);
      mostrarEstado(mensaje);
      Serial.printf("IR;GUARDADO;%u/%u\n", totalCodigos, MAX_CODIGOS);
    } else {
      Serial.println("IR;LISTA_LLENA;21/21");
    }
  }
  IrReceiver.resume();
}

void listarCodigos() {
  Serial.printf("IR;TOTAL;%u\n", totalCodigos);
  for (uint8_t i = 0; i < totalCodigos; ++i) {
    Serial.printf("IR;%02u;PROTO=%u;DIR=0x%04X;CMD=0x%04X\n", i + 1,
                  codigos[i].protocolo, codigos[i].direccion, codigos[i].comando);
  }
}

void iniciarPulso(char canal) {
  apagarMotores();
  if (canal == 'A') digitalWrite(PIN_AIN1, HIGH);
  else if (canal == 'B') digitalWrite(PIN_BIN1, HIGH);
  else return;
  canalActivo = canal;
  finPulso = millis() + PULSO_MS;
  char mensaje[17];
  snprintf(mensaje, sizeof(mensaje), "MOTOR %c 500ms", canal);
  mostrarEstado(mensaje);
  Serial.printf("MOTOR;%c;PULSO;500ms\n", canal);
}

void ejecutar(const char* comando) {
  if (!strcmp(comando, "A_PULSE")) iniciarPulso('A');
  else if (!strcmp(comando, "B_PULSE")) iniciarPulso('B');
  else if (!strcmp(comando, "STOP")) { apagarMotores(); mostrarEstado("MOTORES OFF"); Serial.println("MOTOR;STOP"); }
  else if (!strcmp(comando, "LCD")) detectarLcd();
  else if (!strcmp(comando, "LISTA")) listarCodigos();
  else if (!strcmp(comando, "IR_CLEAR")) { totalCodigos = 0; mostrarEstado("IR BORRADO"); Serial.println("IR;BORRADO"); }
  else if (!strcmp(comando, "HELP")) Serial.println("CMD;LCD|LISTA|IR_CLEAR|A_PULSE|B_PULSE|STOP");
  else Serial.println("NACK;COMANDO;USE_HELP");
}

void leerSerial() {
  while (Serial.available()) {
    const char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      entrada[entradaLen] = '\0';
      if (entradaLen) ejecutar(entrada);
      entradaLen = 0;
    } else if (entradaLen < sizeof(entrada) - 1) {
      entrada[entradaLen++] = c;
    } else {
      entradaLen = 0;
      Serial.println("NACK;COMANDO;MUY_LARGO");
    }
  }
}

void setup() {
  pinMode(PIN_AIN1, OUTPUT);
  pinMode(PIN_BIN1, OUTPUT);
  apagarMotores();
  Serial.begin(115200);
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setTimeOut(20);
  detectarLcd();
  IrReceiver.begin(PIN_IR, DISABLE_LED_FEEDBACK);
  Serial.println("DOMUS_BANCO_LISTO;HELP para comandos");
}

void loop() {
  leerIr();
  leerSerial();
  if (finPulso && (long)(millis() - finPulso) >= 0) {
    const char terminado = canalActivo;
    apagarMotores();
    mostrarEstado("MOTORES OFF");
    Serial.printf("MOTOR;%c;OFF;TIMEOUT\n", terminado);
  }
}
