/*
  ============================================================================
  CASA INTELIGENTE AUTOSOSTENIBLE - FIRMWARE v5 (JARVIS LOCAL + BLE + WIFI)
  ============================================================================
  Placa: ESP32-S3 N16R8 (16MB Flash / 8MB PSRAM OPI)
  Autor: Isaac | Proyecto de feria de ciencias

  NOTA DE MIGRACIÓN:
  Este firmware es ahora la única fuente de control. La voz local se mantiene
  protegida por una bandera hasta
  que exista un modelo español entrenado y validado con el micrófono real.

  ============================================================================
  POR QUÉ CAMBIÓ TODO ESTE ARCHIVO RESPECTO A v3
  ============================================================================
  v3 usaba BluetoothSerial (Bluetooth Classic / SPP). El ESP32-S3 NO tiene
  radio de Bluetooth Classic, solo Bluetooth LE. Espressif lo documenta
  explícitamente, y el propio core Arduino-ESP32 no compila BluetoothSerial
  para variantes S3. Es decir: v3 no podía funcionar en este hardware, sin
  importar cuánto se depurara el resto del código.

  v4 reemplaza toda la capa de comunicación por BLE GATT (NimBLE-Arduino),
  manteniendo el mismo vocabulario de comandos de texto (RIEGO_ON, ESTADO, etc.).

  NOVEDADES DE v3 -> v4:
    - BLE GATT en vez de Bluetooth Classic: única forma de que este código
      corra en un ESP32-S3 real. Un solo servicio con dos características:
      una donde el celular escribe comandos (WRITE) y otra donde el ESP32
      notifica respuestas (NOTIFY) - el celular se suscribe a esa notificación.
    - ACK/NACK REAL POR COMANDO: cada comando de control ahora responde
      "ACK;<comando>;<estado_logico_gpio>" o "NACK;<comando>;<motivo>"
      inmediatamente, en vez de depender de que la app adivine comparando
      snapshots de ESTADO. Esto resuelve el problema #6 del feedback: ya
      no se confirman comandos "por casualidad" cuando llega cualquier
      ESTADO no relacionado.
    - HUMEDAD CALIBRADA EN PORCENTAJE: además del valor crudo ADC, el
      firmware ahora expone HUM_PCT (0-100%) usando dos constantes de
      calibración (tierra seca / tierra húmeda) en vez de mostrar un
      número crudo como "2437" sin significado para el usuario.
    - VOZ CORREGIDA: la condición "afe_data != NULL" que hacía que MultiNet
      corriera siempre (sin importar el wake word) se reemplazó por una
      máquina de estados explícita con ventana de escucha real.
    - VOZ: agregado el comando de invernadero, que existía por Bluetooth
      pero no por voz.
    - COLA DE COMANDOS NO APLICA AQUÍ: el firmware siempre fue un simple
      receptor/ejecutor, la cola con TTL vive del lado de la app (ver
      La cola de comandos no vive en el firmware: este archivo recibe y ejecuta,
      pero si recibe un comando corrupto lo rechaza con NACK en vez
      de solo loguearlo, para que la app pueda reaccionar en vivo.
    - SENSOR DE TEMPERATURA/HUMEDAD AMBIENTAL (DHT11): nuevo sensor físico,
      separado del sensor de humedad de TIERRA que ya existía. El DHT11 mide
      el aire (°C y %HR ambiental), no la tierra de la maceta - son dos
      magnitudes físicas distintas y así se documentan por separado en
      ESTADO (TEMP_C / HUM_AIRE_PCT vs HUM_PCT de tierra). Se usa además
      para automatizar el ventilador por temperatura, no solo por comando
      manual.
    - SENSOR DE LUZ AMBIENTAL (LDR / fotoresistor): nuevo sensor físico,
      expuesto como LUZ_PCT (0-100%, calibrado igual que la humedad de
      tierra) y usado para decidir automáticamente si tiene sentido
      encender las luces (evita, por ejemplo, prender "Luz Sala" en pleno
      día si el usuario la dejó en automático).

  Todo lo de v3 se mantiene igual: watchdog, verificación de estado lógico
  de relés (renombrada para no prometer más de lo que hace), sistema de
  errores circular, recuperación I2C, detección automática OLED/LCD,
  riego automático, módulo MP3.

  ============================================================================
  HERRAMIENTAS ACTUALES (Arduino IDE, firmware base):
    Board: "ESP32S3 Dev Module"
    PSRAM: "OPI PSRAM"
    Flash Size: "16MB"
    Partition Scheme: seleccionar después de medir modelos y PicoTTS; no usar
    un esquema OTA hasta definir una tabla compatible con los 16 MB de flash.

  LIBRERÍAS A INSTALAR (ver versiones exactas probadas en el README):
    1. "NimBLE-Arduino"      - h2zero (BLE ligero, reemplaza BluetoothSerial)
    2. "LiquidCrystal I2C"   - Frank de Brabander (para BLOQUE LCD)
    3. "Adafruit SSD1306"    - Adafruit (para BLOQUE OLED)
    4. "Adafruit GFX Library"- Adafruit (dependencia de SSD1306)
    5. "DHT sensor library"  - Adafruit (para el DHT11 de temperatura/humedad)
    6. "Adafruit Unified Sensor" - Adafruit (dependencia de DHT sensor library)

  VOZ FINAL PENDIENTE:
    - detector TinyML de "Jarvis" + clasificador español int8
    - PicoTTS español + MAX98357A
    El bloque ESP-SR bajo bandera es legado y no debe activarse como solución
    española; será reemplazado cuando existan los artefactos validados.
  ============================================================================
*/

// Jarvis local en español requiere un modelo TinyML entrenado para este
// hardware. Mientras no exista ese artefacto, el resto de la casa debe seguir
// compilando y funcionando sin el SDK de voz.
#define JARVIS_LOCAL_HABILITADO false

#include <Wire.h>
#include <NimBLEDevice.h>
#if JARVIS_LOCAL_HABILITADO
#include "esp_afe_sr_iface.h"
#include "esp_afe_sr_models.h"
#include "esp_mn_iface.h"
#include "esp_mn_models.h"
#include "esp_mn_speech_commands.h"
#include "driver/i2s.h"
#endif
#include "esp_task_wdt.h"   // watchdog de hardware
#include "esp_system.h"     // esp_get_free_heap_size(), esp_restart()

// ---- Librerías de pantalla (ambos bloques, se usa el que corresponda) ----
#include <LiquidCrystal_I2C.h>      // ==== BLOQUE LCD ====
#include <Adafruit_GFX.h>           // ==== BLOQUE OLED ====
#include <Adafruit_SSD1306.h>       // ==== BLOQUE OLED ====

// ---- Sensor de temperatura/humedad ambiental ----
#include <DHT.h>                    // "DHT sensor library" de Adafruit (DHT11/DHT22)

// ============================================================================
// SECCIÓN 1: MAPA DE PINES - REVISAR/CALIBRAR A MANO
// ============================================================================
// A diferencia de v3: con BLE (no Bluetooth Classic) el ADC2 NO se desactiva,
// pero se mantienen los sensores en pines ADC1 de todas formas por ser más
// estables y porque ya está cableado así en el kit.

// --- Bus I2C compartido (pantalla, sea cual sea) ---
#define I2C_SDA_PIN     21   // GPIO21
#define I2C_SCL_PIN     22   // GPIO22
// Direcciones esperadas (se detectan automáticamente, no hace falta tocarlas):
#define DIR_OLED_1      0x3C
#define DIR_OLED_2      0x3D
#define DIR_LCD_1       0x27
#define DIR_LCD_2       0x3F

// --- Micrófono I2S (INMP441) ---
#define MIC_WS_PIN      15   // WS  (Word Select)
#define MIC_SD_PIN      16   // SD  (Serial Data / audio)
#define MIC_SCK_PIN     17   // SCK (bit clock)
// Fijos en el módulo (no son GPIO configurables):
//   VDD -> 3.3V (¡JAMÁS 5V, se quema el chip!)   GND -> GND   L/R -> GND

// --- Sensores analógicos (ADC1) ---
#define PIN_HUMEDAD     1    // GPIO1 - ADC1_CH0 (humedad de TIERRA, capacitivo)
#define PIN_VIENTO      2    // GPIO2 - ADC1_CH1
#define PIN_LDR         3    // GPIO3 - ADC1_CH2 (fotoresistor / luz ambiental)
// RECORDATORIO FÍSICO: el motor DC del sensor de viento SIEMPRE debe pasar
// primero por el divisor de voltaje (resistencias del kit, ej. 10k+10k) o el
// diodo Zener de 3.3V antes de tocar este pin. Nunca directo.
// RECORDATORIO FÍSICO (LDR): el fotoresistor va en divisor de voltaje con
// una resistencia fija (típicamente 10k) entre 3.3V y GND; PIN_LDR lee el
// punto medio del divisor, nunca el LDR solo contra 3.3V.

// --- Sensor de temperatura/humedad AMBIENTAL (DHT11) ---
// Distinto del sensor de humedad de TIERRA (PIN_HUMEDAD): el DHT11 mide el
// aire alrededor de la maceta/casa, no la tierra dentro de ella.
#define PIN_DHT11       14   // GPIO14 - pin de datos del DHT11
#define TIPO_DHT        DHT11
DHT dht(PIN_DHT11, TIPO_DHT);

// --- Módulo de relés de 8 canales (5V, activo en LOW en la mayoría) ---
#define RELE_ACTIVO_EN_LOW true   // CALIBRAR: cambiar a false si tu módulo es al revés

#define PIN_RELE_BOMBA           4
#define PIN_RELE_LUZ_SALA        5
#define PIN_RELE_LUZ_CUARTO      6
#define PIN_RELE_VENTILADOR      7
#define PIN_RELE_LUZ_INVERNADERO 8
#define PIN_RELE_LIBRE_1         9
#define PIN_RELE_LIBRE_2         10
#define PIN_RELE_LIBRE_3         11

const int PINES_RELES[8] = {
  PIN_RELE_BOMBA, PIN_RELE_LUZ_SALA, PIN_RELE_LUZ_CUARTO, PIN_RELE_VENTILADOR,
  PIN_RELE_LUZ_INVERNADERO, PIN_RELE_LIBRE_1, PIN_RELE_LIBRE_2, PIN_RELE_LIBRE_3
};
const char* NOMBRES_RELES[8] = {
  "Bomba", "Luz Sala", "Luz Cuarto", "Ventilador",
  "Luz Inv.", "Libre1", "Libre2", "Libre3"
};

// --- Módulo MP3 (DFPlayer / TF-16P) - respuestas habladas, OPCIONAL ---
// Se conecta por UART. Usamos Serial1 del ESP32-S3 en pines libres.
#define MP3_RX_PIN      18   // hacia TX del módulo MP3
#define MP3_TX_PIN      19   // hacia RX del módulo MP3
#define MP3_HABILITADO  false // legado opcional; Jarvis final usará PicoTTS + MAX98357A
// Pistas sugeridas a grabar en la microSD del módulo (archivos 0001.mp3, etc):
//   0001.mp3 = "Regando ahora"      0002.mp3 = "Riego detenido"
//   0003.mp3 = "Luz encendida"      0004.mp3 = "Luz apagada"
//   0005.mp3 = "Ventilador activado" 0006.mp3 = "Sistema listo"

// ============================================================================
// SECCIÓN 2: CONSTANTES DE CALIBRACIÓN - AJUSTAR CON MEDICIONES REALES
// ============================================================================
// Cómo calibrar humedad: sube este firmware, abre el Monitor Serial, mete el
// sensor en tierra bien seca y anota el número en HUMEDAD_LECTURA_SECA, luego
// en tierra recién regada y anota el número en HUMEDAD_LECTURA_HUMEDA.
// El firmware convierte cualquier lectura entre esos dos extremos a un
// porcentaje 0-100% (0% = tan seco como tu medición seca, 100% = tan húmedo
// como tu medición húmeda). Los sensores capacitivos típicos dan MENOS
// voltaje (número más bajo) cuanta más humedad hay, por eso "seca" suele ser
// el número MÁS ALTO. Si tu sensor es al revés, simplemente estos dos
// números quedan invertidos y la fórmula se ajusta sola.
#define HUMEDAD_LECTURA_SECA     2800   // ADC crudo en tierra seca (0% humedad)
#define HUMEDAD_LECTURA_HUMEDA   1200   // ADC crudo en tierra recién regada (100%)
#define UMBRAL_HUMEDAD_SECA_PCT  35     // el riego automático se activa por debajo de este %

#define HUMEDAD_MIN_VALIDA      50     // por debajo/encima de este rango, se asume
#define HUMEDAD_MAX_VALIDA      4095   // sensor desconectado o en corto -> se ignora
#define VIENTO_MIN_VALIDO       0
#define VIENTO_MAX_VALIDO       4095

// Calibración del LDR (fotoresistor), mismo principio que la humedad de
// tierra: dos lecturas de referencia se convierten a un 0-100% de luz.
// Para calibrar: abre el Monitor Serial, tapa el LDR con la mano (oscuridad)
// y anota el ADC crudo en LDR_LECTURA_OSCURO; luego ilumínalo con una
// linterna/luz directa y anota en LDR_LECTURA_BRILLANTE.
#define LDR_LECTURA_OSCURO      3200   // ADC crudo casi sin luz (0%)
#define LDR_LECTURA_BRILLANTE   400    // ADC crudo con luz directa (100%)
#define LDR_MIN_VALIDO          0
#define LDR_MAX_VALIDO          4095
#define UMBRAL_LUZ_OSCURO_PCT   25     // por debajo de este % se considera "oscuro" para automatización

// DHT11: rango físico real del sensor (fuera de esto, se descarta la lectura)
#define DHT_TEMP_MIN_VALIDA_C    0.0
#define DHT_TEMP_MAX_VALIDA_C    50.0
#define DHT_HUM_MIN_VALIDA_PCT   20.0
#define DHT_HUM_MAX_VALIDA_PCT   90.0
#define DHT_INTERVALO_LECTURA_MS 2500   // el DHT11 no soporta lecturas más rápidas que ~1s, se deja margen

// Ventilador automático por temperatura ambiental (además de su control
// manual por BLE/voz, igual que el riego automático respeta el modo manual)
#define UMBRAL_TEMP_ALTA_C       28.0   // por encima de esto, se enciende el ventilador solo

// Anti-rebote de voz: exige que el mismo comando no se repita antes de este
// tiempo, para evitar que una sola frase dispare la acción varias veces
#define DEBOUNCE_VOZ_MS         2000

// Ventana de escucha activa tras detectar el wake word. Antes de v4, la
// condición de v3 hacía que MultiNet corriera siempre (ver comentario en
// revisarVoz()); ahora solo procesa comandos dentro de esta ventana.
#define VENTANA_ESCUCHA_MS      5000

// Intervalo de refresco de pantalla y de verificación de riego automático
#define INTERVALO_PANTALLA_MS   1500
#define INTERVALO_RIEGO_MS      5000
#define TIEMPO_MAXIMO_BOMBA_MS  120000UL // corte de seguridad: 2 minutos continuos

// --- Watchdog de hardware ---
#define WATCHDOG_TIMEOUT_S      8

// --- Sistema de errores en memoria (buffer circular) ---
#define MAX_ERRORES_GUARDADOS   6
#define LONGITUD_MAX_ERROR      40

// --- I2C: reintentos ante fallo transitorio de pantalla ---
#define I2C_MAX_REINTENTOS      3
#define I2C_ESPERA_REINTENTO_MS 150

// --- BLE ---
#define BLE_NOMBRE_DISPOSITIVO  "CasaInteligente"
// UUIDs propios (generados para este proyecto, no son estándar de ningún
// perfil BLE conocido - es lo correcto para un servicio custom).
#define BLE_UUID_SERVICIO       "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
#define BLE_UUID_CARAC_ESCRITURA "6e400002-b5a3-f393-e0a9-e50e24dcca9e" // celular -> ESP32
#define BLE_UUID_CARAC_NOTIFICAR "6e400003-b5a3-f393-e0a9-e50e24dcca9e" // ESP32 -> celular

// ============================================================================
// SECCIÓN 3: OBJETOS GLOBALES
// ============================================================================
HardwareSerial SerialMP3(1); // UART1 para el módulo MP3

// ---- BLE ----
NimBLEServer* servidorBLE = nullptr;
NimBLECharacteristic* caracNotificar = nullptr;
volatile bool clienteBleConectado = false;

// ---- Pantalla: solo se crea el objeto del tipo que se detectó ----
enum TipoPantalla { PANTALLA_NINGUNA, PANTALLA_OLED, PANTALLA_LCD };
TipoPantalla pantallaActiva = PANTALLA_NINGUNA;

LiquidCrystal_I2C* lcd = nullptr;                       // ==== BLOQUE LCD ====
Adafruit_SSD1306* oled = nullptr;                        // ==== BLOQUE OLED ====
#define OLED_ANCHO 128
#define OLED_ALTO  64   // cambiar a 32 si tu OLED es de 128x32
#define OLED_RESET -1

// Estado de los 8 relés
bool estadoReles[8] = {false, false, false, false, false, false, false, false};

// Toda fuente de control pasa por el mismo contrato. Esto evita que BLE,
// automatización y voz mantengan estados incompatibles entre sí.
enum OrigenOrden { ORIGEN_SISTEMA, ORIGEN_MANUAL, ORIGEN_AUTOMATICO, ORIGEN_VOZ, ORIGEN_WIFI };
enum PropietarioActuador { PROPIETARIO_NINGUNO, PROPIETARIO_MANUAL, PROPIETARIO_AUTOMATICO };

struct OrdenActuador {
  int indiceRele;
  bool encender;
  OrigenOrden origen;
  float confianza;
  const char* nombre;
};

struct ResultadoOrden {
  bool exito;
  bool cambioReal;
  const char* motivo;
};

PropietarioActuador propietarioReles[8] = {
  PROPIETARIO_NINGUNO, PROPIETARIO_NINGUNO, PROPIETARIO_NINGUNO, PROPIETARIO_NINGUNO,
  PROPIETARIO_NINGUNO, PROPIETARIO_NINGUNO, PROPIETARIO_NINGUNO, PROPIETARIO_NINGUNO
};
unsigned long bombaEncendidaDesdeMs = 0;

// Motor de voz (ESP-SR/TinyML), únicamente cuando se ha validado un modelo.
#if JARVIS_LOCAL_HABILITADO
static esp_afe_sr_iface_t *afe_handle = NULL;
static esp_afe_sr_data_t *afe_data = NULL;
model_iface_data_t *modelo_mn = NULL;
esp_mn_iface_t *multinet = NULL;
#endif
unsigned long ultimoComandoVozMs = 0;
int ultimoComandoVozID = -1;

// Máquina de estados de la ventana de escucha (reemplaza el bug de v3)
bool ventanaEscuchaActiva = false;
unsigned long inicioVentanaEscuchaMs = 0;

// Últimas lecturas válidas de sensores (para no mostrar basura si un sensor
// falla momentáneamente)
int ultimaHumedadValida = -1;       // ADC crudo, humedad de TIERRA
int ultimoVientoValido = -1;
int ultimoHumedadPctValido = -1;    // % calibrado, humedad de TIERRA
int ultimoLdrCrudoValido = -1;
int ultimoLuzPctValido = -1;        // % calibrado, luz ambiental (LDR)
float ultimaTempCValida = -1.0;     // °C, DHT11 (aire)
float ultimaHumAireValida = -1.0;   // %HR ambiental, DHT11 (aire)
unsigned long ultimaLecturaDhtMs = 0;

// ============================================================================
// SECCIÓN 3B: SISTEMA DE ERRORES (buffer circular, visible en pantalla)
// ============================================================================
struct RegistroError {
  char mensaje[LONGITUD_MAX_ERROR];
  unsigned long momentoMs;
  bool ocupado;
};

RegistroError bufferErrores[MAX_ERRORES_GUARDADOS];
int indiceErrorActual = 0;
unsigned long totalErroresAcumulados = 0; // contador histórico, no se resetea al sobreescribir

void log(const String &etiqueta, const String &mensaje);
void enviarPorBLE(const String &linea); // adelantado, se define en Sección 11

void registrarError(const String &origen, const String &mensaje) {
  String completo = origen + ": " + mensaje;
  strncpy(bufferErrores[indiceErrorActual].mensaje, completo.c_str(), LONGITUD_MAX_ERROR - 1);
  bufferErrores[indiceErrorActual].mensaje[LONGITUD_MAX_ERROR - 1] = '\0';
  bufferErrores[indiceErrorActual].momentoMs = millis();
  bufferErrores[indiceErrorActual].ocupado = true;

  indiceErrorActual = (indiceErrorActual + 1) % MAX_ERRORES_GUARDADOS;
  totalErroresAcumulados++;

  log("ERROR", completo);
}

String obtenerUltimoError() {
  int idx = (indiceErrorActual - 1 + MAX_ERRORES_GUARDADOS) % MAX_ERRORES_GUARDADOS;
  if (!bufferErrores[idx].ocupado) return "";
  return String(bufferErrores[idx].mensaje);
}

String construirReporteDiagnostico() {
  String r = "DIAGNOSTICO;";
  r += "UPTIME_S=" + String(millis() / 1000) + ";";
  r += "MEM_LIBRE=" + String(esp_get_free_heap_size()) + ";";
  r += "ERRORES_TOTAL=" + String(totalErroresAcumulados) + ";";
  r += "ULTIMO_ERROR=" + (obtenerUltimoError().length() > 0 ? obtenerUltimoError() : "ninguno") + ";";
  r += "PANTALLA=" + String(pantallaActiva == PANTALLA_OLED ? "OLED" : (pantallaActiva == PANTALLA_LCD ? "LCD" : "NINGUNA")) + ";";
  return r;
}

// ============================================================================
// SECCIÓN 4: COMANDOS DE VOZ
// ============================================================================
enum ComandoVoz {
  CMD_RIEGO_ON = 0, CMD_RIEGO_OFF,
  CMD_LUZ_SALA_ON, CMD_LUZ_SALA_OFF,
  CMD_LUZ_CUARTO_ON, CMD_LUZ_CUARTO_OFF,
  CMD_VENTILADOR_ON, CMD_VENTILADOR_OFF,
  CMD_INVERNADERO_ON, CMD_INVERNADERO_OFF,
  CMD_TOTAL
};

// ============================================================================
// SECCIÓN 5: UTILIDAD DE LOG CON TIMESTAMP
// ============================================================================
void log(const String &etiqueta, const String &mensaje) {
  Serial.print("[");
  Serial.print(millis());
  Serial.print("ms][");
  Serial.print(etiqueta);
  Serial.print("] ");
  Serial.println(mensaje);
}

// ============================================================================
// SECCIÓN 6: DETECCIÓN AUTOMÁTICA DE PANTALLA (I2C SCAN)
// ============================================================================
bool escanearBusI2C(bool &hayOled, bool &hayLcd, uint8_t &dirOled, uint8_t &dirLcd) {
  hayOled = false;
  hayLcd = false;
  int dispositivosEncontrados = 0;

  for (uint8_t dir = 1; dir < 127; dir++) {
    Wire.beginTransmission(dir);
    uint8_t error = Wire.endTransmission();
    if (error == 0) {
      dispositivosEncontrados++;
      log("I2C", "Dispositivo encontrado en 0x" + String(dir, HEX));
      if (dir == DIR_OLED_1 || dir == DIR_OLED_2) { hayOled = true; dirOled = dir; }
      if (dir == DIR_LCD_1  || dir == DIR_LCD_2)  { hayLcd = true;  dirLcd  = dir; }
    }
  }
  return dispositivosEncontrados > 0;
}

void detectarPantalla() {
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  delay(50);

  bool hayOled = false, hayLcd = false;
  uint8_t dirOledEncontrada = 0, dirLcdEncontrada = 0;
  bool busRespondio = false;

  for (int intento = 1; intento <= I2C_MAX_REINTENTOS && !busRespondio; intento++) {
    busRespondio = escanearBusI2C(hayOled, hayLcd, dirOledEncontrada, dirLcdEncontrada);
    if (!busRespondio) {
      log("I2C", "Intento " + String(intento) + "/" + String(I2C_MAX_REINTENTOS) + ": bus I2C sin respuesta, reintentando...");
      delay(I2C_ESPERA_REINTENTO_MS);
    }
  }

  if (!busRespondio) {
    registrarError("I2C", "Bus sin ningun dispositivo tras " + String(I2C_MAX_REINTENTOS) + " intentos. Revisar cableado SDA/SCL.");
  }

  if (hayOled) {
    // ==== BLOQUE OLED ====
    oled = new Adafruit_SSD1306(OLED_ANCHO, OLED_ALTO, &Wire, OLED_RESET);
    if (oled->begin(SSD1306_SWITCHCAPVCC, dirOledEncontrada)) {
      pantallaActiva = PANTALLA_OLED;
      log("PANTALLA", "OLED SSD1306 detectada en 0x" + String(dirOledEncontrada, HEX));
    } else {
      log("PANTALLA", "OLED detectada en el bus pero begin() falló");
      delete oled;
      oled = nullptr;
    }
  } else if (hayLcd) {
    // ==== BLOQUE LCD ====
    lcd = new LiquidCrystal_I2C(dirLcdEncontrada, 16, 2);
    lcd->init();
    lcd->backlight();
    pantallaActiva = PANTALLA_LCD;
    log("PANTALLA", "LCD 1602 detectado en 0x" + String(dirLcdEncontrada, HEX));
  } else {
    pantallaActiva = PANTALLA_NINGUNA;
    log("PANTALLA", "Ninguna pantalla detectada, sistema seguirá en modo headless");
  }
}

// ---- Pantalla de bienvenida ----
void mostrarBienvenida() {
  if (pantallaActiva == PANTALLA_OLED) {
    oled->clearDisplay();
    oled->setTextSize(1);
    oled->setTextColor(SSD1306_WHITE);
    oled->setCursor(0, 0);
    oled->println("CASA INTELIGENTE");
    oled->drawLine(0, 10, 128, 10, SSD1306_WHITE);
    oled->setCursor(0, 20);
    oled->println("Autosostenible");
    oled->setCursor(0, 40);
    oled->println("Iniciando sistema...");
    oled->display();
  } else if (pantallaActiva == PANTALLA_LCD) {
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print("Casa Inteligente");
    lcd->setCursor(0, 1);
    lcd->print("Iniciando...");
  }
}

// ---- Pantalla principal de estado (llamada periódicamente en el loop) ----
void actualizarPantallaEstado(int humedadPct, int viento, bool humedadValida, bool vientoValido, float tempC = -1.0, bool tempValida = false) {
  if (pantallaActiva == PANTALLA_OLED) {
    oled->clearDisplay();
    oled->setTextSize(1);
    oled->setTextColor(SSD1306_WHITE);

    oled->setCursor(0, 0);
    oled->print("CASA INTELIGENTE");
    oled->drawLine(0, 9, 128, 9, SSD1306_WHITE);

    oled->setCursor(0, 14);
    oled->print("Hum.tierra: ");
    oled->print(humedadValida ? (String(humedadPct) + "%") : "ERR");

    oled->setCursor(0, 24);
    oled->print("Viento:");
    oled->print(vientoValido ? String(viento) : "ERR");
    oled->print(" Temp:");
    oled->print(tempValida ? (String(tempC, 0) + "C") : "ERR");

    oled->drawLine(0, 34, 128, 34, SSD1306_WHITE);
    oled->setCursor(0, 38);
    oled->print("Activo:");

    String activos = "";
    for (int i = 0; i < 8; i++) {
      if (estadoReles[i]) {
        activos += NOMBRES_RELES[i];
        activos += " ";
      }
    }
    if (activos == "") activos = "(nada encendido)";
    oled->setCursor(0, 48);
    if (activos.length() > 21) activos = activos.substring(0, 21);
    oled->print(activos);

    oled->setCursor(0, 57);
    oled->print(JARVIS_LOCAL_HABILITADO ? "Voz: ON " : "Voz: OFF");
    oled->print(clienteBleConectado ? " BLE:ON" : " BLE:--");

    oled->display();

  } else if (pantallaActiva == PANTALLA_LCD) {
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print("H:");
    lcd->print(humedadValida ? (String(humedadPct) + "%") : "ERR");
    lcd->print(" T:");
    lcd->print(tempValida ? (String(tempC, 0) + "C") : "ERR");

    lcd->setCursor(0, 1);
    String linea2 = "";
    if (estadoReles[0]) linea2 += "B ";
    if (estadoReles[1]) linea2 += "LS ";
    if (estadoReles[2]) linea2 += "LC ";
    if (estadoReles[3]) linea2 += "V ";
    if (estadoReles[4]) linea2 += "LI ";
    if (linea2 == "") linea2 = "Todo apagado";
    lcd->print(linea2);
  }
}

// ---- Pantalla de error: muestra el último error registrado ----
void mostrarPantallaError() {
  String ultimoError = obtenerUltimoError();
  if (ultimoError.length() == 0) return;

  if (pantallaActiva == PANTALLA_OLED) {
    oled->clearDisplay();
    oled->setTextSize(1);
    oled->setTextColor(SSD1306_WHITE);
    oled->setCursor(0, 0);
    oled->print("!! ERROR !!");
    oled->drawLine(0, 9, 128, 9, SSD1306_WHITE);

    int inicio = 0;
    int lineaY = 14;
    while (inicio < (int)ultimoError.length() && lineaY < 60) {
      int fin = min(inicio + 21, (int)ultimoError.length());
      oled->setCursor(0, lineaY);
      oled->print(ultimoError.substring(inicio, fin));
      inicio = fin;
      lineaY += 10;
    }
    oled->display();

  } else if (pantallaActiva == PANTALLA_LCD) {
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print("ERROR:");
    lcd->setCursor(0, 1);
    lcd->print(ultimoError.substring(0, min(16, (int)ultimoError.length())));
  }
}

// ---- Pantalla de "escuchando" cuando se detecta wake word ----
void mostrarEscuchando() {
  if (pantallaActiva == PANTALLA_OLED) {
    oled->clearDisplay();
    oled->setTextSize(2);
    oled->setTextColor(SSD1306_WHITE);
    oled->setCursor(10, 20);
    oled->print("Escuchando");
    oled->setTextSize(1);
    oled->setCursor(30, 45);
    oled->print("Di un comando...");
    oled->display();
  } else if (pantallaActiva == PANTALLA_LCD) {
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print("Escuchando...");
  }
}

// ============================================================================
// SECCIÓN 7: MÓDULO MP3 (respuestas habladas, opcional)
// ============================================================================
void reproducirPista(uint8_t numeroPista) {
  if (!MP3_HABILITADO) return;
  uint8_t comando[10] = {0x7E, 0xFF, 0x06, 0x03, 0x00, 0x00, numeroPista, 0x00, 0x00, 0xEF};
  uint16_t suma = 0;
  for (int i = 1; i <= 6; i++) suma += comando[i];
  uint16_t checksum = -suma;
  comando[7] = (checksum >> 8) & 0xFF;
  comando[8] = checksum & 0xFF;
  SerialMP3.write(comando, 10);
  log("MP3", "Reproduciendo pista " + String(numeroPista));
}

// ============================================================================
// SECCIÓN 8: CONTROL DE RELÉS
// ============================================================================
// Contador de fallos de verificación por relé.
int fallosVerificacionRele[8] = {0, 0, 0, 0, 0, 0, 0, 0};
#define MAX_FALLOS_ANTES_DE_ALERTA_PERSISTENTE 3

// IMPORTANTE (corrección del feedback #5 de v3): esta función NO verifica
// físicamente que el relé conmutó, ni que la carga real cambió de estado.
// Verifica únicamente que el GPIO del ESP32 quedó en el nivel lógico que
// se le acaba de ordenar. Un cable suelto entre el ESP32 y el módulo de
// relés, o un relé dañado, pueden hacer que esto devuelva true aunque nada
// haya cambiado físicamente. Para detectar el estado físico real del relé
// haría falta una señal de realimentación por hardware (ej. leer el propio
// contacto NO/NC del relé hacia un pin de entrada), que este kit no tiene.
bool verificarEstadoLogicoGpio(int indice, bool estadoEsperado) {
  int nivelEsperado = estadoEsperado
    ? (RELE_ACTIVO_EN_LOW ? LOW : HIGH)
    : (RELE_ACTIVO_EN_LOW ? HIGH : LOW);
  int nivelReal = digitalRead(PINES_RELES[indice]);
  return nivelReal == nivelEsperado;
}

// Devuelve true si el cambio de GPIO se aplicó y quedó confirmado. Los
// llamadores (BLE, voz) usan este valor de retorno para construir un
// ACK o NACK real, en vez de asumir éxito silenciosamente.
bool encenderRele(int indice, bool anunciarPorVoz = true) {
  if (indice < 0 || indice >= 8) {
    registrarError("RELE", "Indice invalido solicitado: " + String(indice));
    return false;
  }
  if (estadoReles[indice]) return true; // ya encendido, se considera éxito idempotente

  digitalWrite(PINES_RELES[indice], RELE_ACTIVO_EN_LOW ? LOW : HIGH);
  delay(5); // pequeña espera para que el relé mecánico termine de conmutar antes de releer

  if (!verificarEstadoLogicoGpio(indice, true)) {
    fallosVerificacionRele[indice]++;
    registrarError("RELE", String(NOMBRES_RELES[indice]) + " no confirmo encendido en GPIO (revisar cableado)");
    if (fallosVerificacionRele[indice] >= MAX_FALLOS_ANTES_DE_ALERTA_PERSISTENTE) {
      registrarError("RELE", String(NOMBRES_RELES[indice]) + " fallo repetido, revisar hardware");
    }
    return false;
  }

  fallosVerificacionRele[indice] = 0;
  estadoReles[indice] = true;
  log("RELE", String(NOMBRES_RELES[indice]) + " -> ENCENDIDO (GPIO confirmado)");

  if (anunciarPorVoz && MP3_HABILITADO) {
    if (indice == 0) reproducirPista(1);       // "Regando ahora"
    else if (indice == 3) reproducirPista(5);  // "Ventilador activado"
    else reproducirPista(3);                    // "Luz encendida" (genérico)
  }
  return true;
}

bool apagarRele(int indice, bool anunciarPorVoz = true) {
  if (indice < 0 || indice >= 8) {
    registrarError("RELE", "Indice invalido solicitado: " + String(indice));
    return false;
  }
  if (!estadoReles[indice]) return true; // ya apagado, éxito idempotente

  digitalWrite(PINES_RELES[indice], RELE_ACTIVO_EN_LOW ? HIGH : LOW);
  delay(5);

  if (!verificarEstadoLogicoGpio(indice, false)) {
    fallosVerificacionRele[indice]++;
    registrarError("RELE", String(NOMBRES_RELES[indice]) + " no confirmo apagado en GPIO (posible rele pegado)");
    return false;
  }

  fallosVerificacionRele[indice] = 0;
  estadoReles[indice] = false;
  log("RELE", String(NOMBRES_RELES[indice]) + " -> APAGADO (GPIO confirmado)");

  if (anunciarPorVoz && MP3_HABILITADO) {
    if (indice == 0) reproducirPista(2);       // "Riego detenido"
    else reproducirPista(4);                    // "Luz apagada" (genérico)
  }
  return true;
}

String construirRespuestaJarvis(const OrdenActuador &orden, bool estadoAnterior,
                                const ResultadoOrden &resultado) {
  if (!resultado.exito) {
    if (String(resultado.motivo) == "confianza_baja") return "No entendi la orden.";
    return "No pude completar la orden. Revisa el dispositivo.";
  }

  const String nombre = String(NOMBRES_RELES[orden.indiceRele]);
  if (estadoAnterior == orden.encender) {
    return orden.encender
      ? "El dispositivo " + nombre + " ya estaba encendido."
      : "El dispositivo " + nombre + " ya estaba apagado.";
  }
  return orden.encender
    ? "He encendido " + nombre + "."
    : "He apagado " + nombre + ".";
}

// Punto único de salida para PicoTTS. Por ahora deja la frase observable en
// Serial; cuando se integre el motor, esta función entregará el texto a su
// cola de audio sin cambiar el despachador ni las reglas de la casa.
void responderJarvis(const String &texto) {
  log("JARVIS_TEXTO", texto);
}

ResultadoOrden ejecutarOrdenActuador(const OrdenActuador &orden) {
  if (orden.indiceRele < 0 || orden.indiceRele >= 8) {
    registrarError("ORDEN", "Indice de rele fuera de rango");
    return {false, false, "indice_invalido"};
  }

  // Una confianza baja jamás puede modificar la casa. Las fuentes que no
  // dependen de inferencia deben enviar 1.0.
  if (orden.origen == ORIGEN_VOZ && orden.confianza < 0.75f) {
    log("VOZ", "Orden rechazada por baja confianza: " + String(orden.confianza, 2));
    ResultadoOrden rechazo = {false, false, "confianza_baja"};
    responderJarvis(construirRespuestaJarvis(orden, estadoReles[orden.indiceRele], rechazo));
    return rechazo;
  }

  const bool estadoAnterior = estadoReles[orden.indiceRele];
  const bool exito = orden.encender
    ? encenderRele(orden.indiceRele, false)
    : apagarRele(orden.indiceRele, false);
  if (!exito) {
    ResultadoOrden fallo = {false, false, "gpio_no_confirmado"};
    if (orden.origen == ORIGEN_VOZ) {
      responderJarvis(construirRespuestaJarvis(orden, estadoAnterior, fallo));
    }
    return fallo;
  }

  // Una orden manual/voz/Wi-Fi toma propiedad incluso si fue idempotente.
  // Así el automático no apagará después algo que el usuario decidió dejar ON.
  if (orden.encender) {
    propietarioReles[orden.indiceRele] = (orden.origen == ORIGEN_AUTOMATICO)
      ? PROPIETARIO_AUTOMATICO : PROPIETARIO_MANUAL;
    if (orden.indiceRele == 0 && !estadoAnterior) bombaEncendidaDesdeMs = millis();
  } else {
    propietarioReles[orden.indiceRele] = PROPIETARIO_NINGUNO;
    if (orden.indiceRele == 0) bombaEncendidaDesdeMs = 0;
  }

  log("ORDEN", String(orden.nombre ? orden.nombre : "SIN_NOMBRE") +
      ";origen=" + String((int)orden.origen) +
      ";estado=" + String(orden.encender ? 1 : 0));
  ResultadoOrden resultado = {true, estadoAnterior != orden.encender, "ok"};
  if (orden.origen == ORIGEN_VOZ) {
    responderJarvis(construirRespuestaJarvis(orden, estadoAnterior, resultado));
  }
  return resultado;
}

void verificarLimiteBomba() {
  if (!estadoReles[0] || bombaEncendidaDesdeMs == 0) return;
  if (millis() - bombaEncendidaDesdeMs < TIEMPO_MAXIMO_BOMBA_MS) return;

  registrarError("SEGURIDAD", "Bomba detenida por tiempo maximo continuo");
  OrdenActuador corte = {0, false, ORIGEN_SISTEMA, 1.0f, "BOMBA_TIMEOUT"};
  ResultadoOrden resultado = ejecutarOrdenActuador(corte);
  if (resultado.exito) enviarPorBLE("EVENTO;BOMBA_TIMEOUT;0");
}

// ============================================================================
// SECCIÓN 9: LECTURA Y VALIDACIÓN DE SENSORES
// ============================================================================
int leerSensorPromediado(int pin, int muestras = 8) {
  long suma = 0;
  for (int i = 0; i < muestras; i++) {
    suma += analogRead(pin);
    delayMicroseconds(200);
  }
  return suma / muestras;
}

int fallosConsecutivosHumedad = 0;
int fallosConsecutivosViento = 0;
#define MAX_FALLOS_ANTES_DE_REGISTRAR 3

// Convierte una lectura ADC cruda a porcentaje 0-100% usando las constantes
// de calibración de la Sección 2. Funciona sin importar si "seca" es el
// número más alto o más bajo (soporta sensores de cualquier polaridad).
int convertirHumedadAPorcentaje(int lecturaCruda) {
  long rango = (long)HUMEDAD_LECTURA_HUMEDA - (long)HUMEDAD_LECTURA_SECA;
  if (rango == 0) return 0; // evita división por cero si no se calibró
  long pct = ((long)lecturaCruda - HUMEDAD_LECTURA_SECA) * 100L / rango;
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  return (int)pct;
}

bool leerHumedad(int &crudoSalida, int &pctSalida) {
  int lectura = leerSensorPromediado(PIN_HUMEDAD);
  if (lectura < HUMEDAD_MIN_VALIDA || lectura > HUMEDAD_MAX_VALIDA) {
    fallosConsecutivosHumedad++;
    if (fallosConsecutivosHumedad >= MAX_FALLOS_ANTES_DE_REGISTRAR) {
      registrarError("SENSOR", "Humedad fuera de rango repetidamente, revisar conexion");
      fallosConsecutivosHumedad = 0;
    }
    return false;
  }
  fallosConsecutivosHumedad = 0;
  crudoSalida = lectura;
  pctSalida = convertirHumedadAPorcentaje(lectura);
  ultimaHumedadValida = lectura;
  ultimoHumedadPctValido = pctSalida;
  return true;
}

bool leerViento(int &valorSalida) {
  int lectura = leerSensorPromediado(PIN_VIENTO);
  if (lectura < VIENTO_MIN_VALIDO || lectura > VIENTO_MAX_VALIDO) {
    fallosConsecutivosViento++;
    if (fallosConsecutivosViento >= MAX_FALLOS_ANTES_DE_REGISTRAR) {
      registrarError("SENSOR", "Viento fuera de rango repetidamente, revisar conexion");
      fallosConsecutivosViento = 0;
    }
    return false;
  }
  fallosConsecutivosViento = 0;
  valorSalida = lectura;
  ultimoVientoValido = lectura;
  return true;
}

// ---- LDR (fotoresistor) - luz ambiental ----
int fallosConsecutivosLdr = 0;

// Igual principio que convertirHumedadAPorcentaje(): funciona sin importar
// si "oscuro" es el número ADC más alto o más bajo, según cómo hayas armado
// el divisor de voltaje del LDR.
int convertirLdrAPorcentaje(int lecturaCruda) {
  long rango = (long)LDR_LECTURA_BRILLANTE - (long)LDR_LECTURA_OSCURO;
  if (rango == 0) return 0;
  long pct = ((long)lecturaCruda - LDR_LECTURA_OSCURO) * 100L / rango;
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  return (int)pct;
}

bool leerLuz(int &crudoSalida, int &pctSalida) {
  int lectura = leerSensorPromediado(PIN_LDR);
  if (lectura < LDR_MIN_VALIDO || lectura > LDR_MAX_VALIDO) {
    fallosConsecutivosLdr++;
    if (fallosConsecutivosLdr >= MAX_FALLOS_ANTES_DE_REGISTRAR) {
      registrarError("SENSOR", "LDR fuera de rango repetidamente, revisar conexion");
      fallosConsecutivosLdr = 0;
    }
    return false;
  }
  fallosConsecutivosLdr = 0;
  crudoSalida = lectura;
  pctSalida = convertirLdrAPorcentaje(lectura);
  ultimoLdrCrudoValido = lectura;
  ultimoLuzPctValido = pctSalida;
  return true;
}

// ---- DHT11 - temperatura y humedad AMBIENTAL (aire, no tierra) ----
// A diferencia de los sensores analógicos de arriba, el DHT11 tiene su
// propio protocolo de un solo cable y ya viene con validación de checksum
// dentro de la librería - por eso aquí solo se valida el RANGO físico
// razonable, no se promedia como los sensores ADC (el DHT11 es lento,
// máximo ~1 lectura/segundo, promediar 8 muestras lo saturaría).
bool leerAmbiente(float &tempCSalida, float &humAireSalida) {
  if (millis() - ultimaLecturaDhtMs < DHT_INTERVALO_LECTURA_MS) {
    // Todavía no toca leer de nuevo: devuelve la última lectura válida en
    // vez de forzar al DHT11 fuera de su límite de velocidad.
    if (ultimaTempCValida < 0) return false;
    tempCSalida = ultimaTempCValida;
    humAireSalida = ultimaHumAireValida;
    return true;
  }
  ultimaLecturaDhtMs = millis();

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    registrarError("SENSOR", "DHT11 no respondio (lectura NaN), revisar cableado/pin 14");
    return false;
  }
  if (temp < DHT_TEMP_MIN_VALIDA_C || temp > DHT_TEMP_MAX_VALIDA_C ||
      hum < DHT_HUM_MIN_VALIDA_PCT || hum > DHT_HUM_MAX_VALIDA_PCT) {
    registrarError("SENSOR", "DHT11 fuera de rango fisico razonable, se ignora esta lectura");
    return false;
  }

  ultimaTempCValida = temp;
  ultimaHumAireValida = hum;
  tempCSalida = temp;
  humAireSalida = hum;
  return true;
}

// ============================================================================
// SECCIÓN 10: RIEGO AUTOMÁTICO (no bloqueante)
// ============================================================================
unsigned long ultimaVerificacionRiego = 0;

void verificarRiegoAutomatico() {
  if (millis() - ultimaVerificacionRiego < INTERVALO_RIEGO_MS) return;
  ultimaVerificacionRiego = millis();

  int crudo, pct;
  if (!leerHumedad(crudo, pct)) return; // sensor con error, no toca el riego

  if (pct < UMBRAL_HUMEDAD_SECA_PCT && !estadoReles[0]) {
    log("AUTO", "Tierra seca (" + String(pct) + "%), activando riego automático");
    OrdenActuador orden = {0, true, ORIGEN_AUTOMATICO, 1.0f, "RIEGO_AUTO_ON"};
    if (ejecutarOrdenActuador(orden).exito) {
      enviarPorBLE("EVENTO;RIEGO_AUTO_ON;" + String(pct));
    }
  } else if (pct >= UMBRAL_HUMEDAD_SECA_PCT && estadoReles[0] &&
             propietarioReles[0] == PROPIETARIO_AUTOMATICO) {
    // Solo apaga automáticamente si fue el modo automático quien lo prendió;
    // si el usuario lo encendió manualmente por voz/BLE, se respeta su
    // decisión y no se apaga solo.
    log("AUTO", "Humedad suficiente (" + String(pct) + "%), apagando riego automático");
    OrdenActuador orden = {0, false, ORIGEN_AUTOMATICO, 1.0f, "RIEGO_AUTO_OFF"};
    if (ejecutarOrdenActuador(orden).exito) {
      enviarPorBLE("EVENTO;RIEGO_AUTO_OFF;" + String(pct));
    }
  }
}

// Misma filosofía que verificarRiegoAutomatico(): solo actúa si el estado
// actual del relé fue decisión del propio modo automático, para no pisar
// una decisión manual del usuario (índice 3 = Ventilador, ver PINES_RELES).
unsigned long ultimaVerificacionVentilador = 0;

void verificarVentiladorAutomatico() {
  if (millis() - ultimaVerificacionVentilador < INTERVALO_RIEGO_MS) return;
  ultimaVerificacionVentilador = millis();

  float tempC, humAire;
  if (!leerAmbiente(tempC, humAire)) return; // DHT11 con error, no toca el ventilador

  if (tempC > UMBRAL_TEMP_ALTA_C && !estadoReles[3]) {
    log("AUTO", "Temperatura alta (" + String(tempC, 1) + "C), activando ventilador automático");
    OrdenActuador orden = {3, true, ORIGEN_AUTOMATICO, 1.0f, "VENT_AUTO_ON"};
    if (ejecutarOrdenActuador(orden).exito) {
      enviarPorBLE("EVENTO;VENT_AUTO_ON;" + String(tempC, 1));
    }
  } else if (tempC <= UMBRAL_TEMP_ALTA_C && estadoReles[3] &&
             propietarioReles[3] == PROPIETARIO_AUTOMATICO) {
    log("AUTO", "Temperatura normal (" + String(tempC, 1) + "C), apagando ventilador automático");
    OrdenActuador orden = {3, false, ORIGEN_AUTOMATICO, 1.0f, "VENT_AUTO_OFF"};
    if (ejecutarOrdenActuador(orden).exito) {
      enviarPorBLE("EVENTO;VENT_AUTO_OFF;" + String(tempC, 1));
    }
  }
}

// ============================================================================
// SECCIÓN 11: BLE - COMANDOS DESDE EL CELULAR (reemplaza Bluetooth Classic)
// ============================================================================
// Comandos de texto esperados (idénticos vocabulario a v3, solo cambia el
// transporte de Bluetooth Classic a BLE):
//   RIEGO_ON / RIEGO_OFF | LUZ1_ON / LUZ1_OFF | LUZ2_ON / LUZ2_OFF
//   VENT_ON / VENT_OFF   | INVER_ON / INVER_OFF | ESTADO | DIAGNOSTICO
//
// Respuestas nuevas en v4:
//   "ACK;<comando>;<estado_logico_0_o_1>"   -> el comando se aplicó y se confirmó por GPIO
//   "NACK;<comando>;<motivo>"               -> el comando no pudo confirmarse o fue rechazado

String construirReporteEstado() {
  String r = "ESTADO;";
  for (int i = 0; i < 8; i++) {
    r += NOMBRES_RELES[i];
    r += "=";
    r += estadoReles[i] ? "1" : "0";
    r += ";";
  }
  r += "HUM=" + String(ultimaHumedadValida) + ";";       // humedad de TIERRA, crudo ADC
  r += "HUM_PCT=" + String(ultimoHumedadPctValido) + ";"; // humedad de TIERRA, calibrada
  r += "VIE=" + String(ultimoVientoValido) + ";";
  r += "TEMP_C=" + String(ultimaTempCValida, 1) + ";";        // DHT11, temperatura AMBIENTAL
  r += "HUM_AIRE_PCT=" + String(ultimaHumAireValida, 1) + ";"; // DHT11, humedad AMBIENTAL (no confundir con HUM_PCT de tierra)
  r += "LUZ_PCT=" + String(ultimoLuzPctValido) + ";";          // LDR, luz ambiental calibrada
  return r;
}

const char* COMANDOS_VALIDOS[] = {
  "RIEGO_ON", "RIEGO_OFF", "LUZ1_ON", "LUZ1_OFF", "LUZ2_ON", "LUZ2_OFF",
  "VENT_ON", "VENT_OFF", "INVER_ON", "INVER_OFF", "ESTADO", "DIAGNOSTICO"
};
const int CANTIDAD_COMANDOS_VALIDOS = 12;

bool esComandoValido(const String &comando) {
  for (int i = 0; i < CANTIDAD_COMANDOS_VALIDOS; i++) {
    if (comando == COMANDOS_VALIDOS[i]) return true;
  }
  return false;
}

// Aplica un comando de control de relé y envía ACK/NACK real. Centraliza la
// lógica que antes estaba repetida ocho veces en procesarComandoBluetooth().
void ejecutarComandoRele(const String &comando, int indice, bool encender,
                         OrigenOrden origen = ORIGEN_MANUAL, float confianza = 1.0f) {
  OrdenActuador orden = {indice, encender, origen, confianza, comando.c_str()};
  ResultadoOrden resultado = ejecutarOrdenActuador(orden);
  if (resultado.exito) {
    enviarPorBLE("ACK;" + comando + ";" + String(estadoReles[indice] ? 1 : 0));
  } else {
    enviarPorBLE("NACK;" + comando + ";" + String(resultado.motivo));
  }
}

void procesarComandoTexto(String comando) {
  comando.trim();
  comando.toUpperCase();

  if (comando.length() == 0) return;

  if (comando.length() > 20) {
    registrarError("BLE", "Comando descartado por longitud invalida (" + String(comando.length()) + " caracteres)");
    enviarPorBLE("NACK;" + comando.substring(0, 20) + ";longitud_invalida");
    return;
  }

  if (!esComandoValido(comando)) {
    registrarError("BLE", "Comando no reconocido: " + comando);
    enviarPorBLE("NACK;" + comando + ";no_reconocido");
    return;
  }

  log("BLE", "Comando recibido: " + comando);

       if (comando == "RIEGO_ON")  ejecutarComandoRele(comando, 0, true);
  else if (comando == "RIEGO_OFF") ejecutarComandoRele(comando, 0, false);
  else if (comando == "LUZ1_ON")   ejecutarComandoRele(comando, 1, true);
  else if (comando == "LUZ1_OFF")  ejecutarComandoRele(comando, 1, false);
  else if (comando == "LUZ2_ON")   ejecutarComandoRele(comando, 2, true);
  else if (comando == "LUZ2_OFF")  ejecutarComandoRele(comando, 2, false);
  else if (comando == "VENT_ON")   ejecutarComandoRele(comando, 3, true);
  else if (comando == "VENT_OFF")  ejecutarComandoRele(comando, 3, false);
  else if (comando == "INVER_ON")  ejecutarComandoRele(comando, 4, true);
  else if (comando == "INVER_OFF") ejecutarComandoRele(comando, 4, false);
  else if (comando == "ESTADO")    enviarPorBLE(construirReporteEstado());
  else if (comando == "DIAGNOSTICO") enviarPorBLE(construirReporteDiagnostico());
}

void enviarPorBLE(const String &linea) {
  if (!clienteBleConectado || caracNotificar == nullptr) return;
  caracNotificar->setValue((uint8_t*)linea.c_str(), linea.length());
  caracNotificar->notify();
}

class CallbacksServidorBLE : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer* servidor, NimBLEConnInfo& infoConexion) override {
    clienteBleConectado = true;
    log("BLE", "Cliente conectado");
  }
  void onDisconnect(NimBLEServer* servidor, NimBLEConnInfo& infoConexion, int razon) override {
    clienteBleConectado = false;
    log("BLE", "Cliente desconectado, reanudando advertising");
    NimBLEDevice::startAdvertising();
  }
};

class CallbacksEscrituraBLE : public NimBLECharacteristicCallbacks {
  void onWrite(NimBLECharacteristic* caracteristica, NimBLEConnInfo& infoConexion) override {
    std::string valor = caracteristica->getValue();
    if (valor.length() == 0) return;
    String comando = String(valor.c_str());
    procesarComandoTexto(comando);
  }
};

void inicializarBLE() {
  NimBLEDevice::init(BLE_NOMBRE_DISPOSITIVO);
  // MTU más grande que el default (23 bytes) para que ESTADO/DIAGNOSTICO
  // quepan en una sola notificación sin fragmentarse.
  NimBLEDevice::setMTU(185);

  servidorBLE = NimBLEDevice::createServer();
  servidorBLE->setCallbacks(new CallbacksServidorBLE());

  NimBLEService* servicio = servidorBLE->createService(BLE_UUID_SERVICIO);

  NimBLECharacteristic* caracEscritura = servicio->createCharacteristic(
    BLE_UUID_CARAC_ESCRITURA,
    NIMBLE_PROPERTY::WRITE
  );
  caracEscritura->setCallbacks(new CallbacksEscrituraBLE());

  caracNotificar = servicio->createCharacteristic(
    BLE_UUID_CARAC_NOTIFICAR,
    NIMBLE_PROPERTY::NOTIFY
  );

  NimBLEAdvertising* advertising = NimBLEDevice::getAdvertising();
  advertising->addServiceUUID(BLE_UUID_SERVICIO);
  advertising->setName(BLE_NOMBRE_DISPOSITIVO);
  NimBLEDevice::startAdvertising();

  log("BLE", "Advertising iniciado, nombre visible: " + String(BLE_NOMBRE_DISPOSITIVO));
}

// ============================================================================
// SECCIÓN 12: RECONOCIMIENTO DE VOZ LOCAL (ESP-SR)
// ============================================================================
#if JARVIS_LOCAL_HABILITADO
// NOTA SOBRE ESPAÑOL: el soporte de español en MultiNet depende de la
// versión de ESP-SR instalada. Verifica en github.com/espressif/esp-sr qué
// modelos trae la tuya. Si no hay español, usa comandos en inglés como
// alternativa - es una limitación de la librería, no de este código.

void inicializarVoz() {
  log("VOZ", "Inicializando motor de reconocimiento...");

  afe_handle = (esp_afe_sr_iface_t*)&ESP_AFE_SR_HANDLE;
  afe_config_t afe_config = AFE_CONFIG_DEFAULT();
  afe_data = afe_handle->create_from_config(&afe_config);

  if (afe_data == NULL) {
    registrarError("VOZ", "No se pudo inicializar AFE. Revisar INMP441 (WS/SD/SCK) y PSRAM.");
    return;
  }

  srmodel_list_t *models = esp_srmodel_init("model");
  char *nombre_modelo_mn = esp_srmodel_filter(models, ESP_MN_PREFIX, NULL);
  if (nombre_modelo_mn == NULL) {
    registrarError("VOZ", "Modelo MultiNet no encontrado. Revisar particion SPIFFS/modelo.");
    return;
  }

  multinet = esp_mn_handle_from_name(nombre_modelo_mn);
  modelo_mn = multinet->create(nombre_modelo_mn, 6000);

  esp_mn_commands_clear();
  esp_mn_commands_add(CMD_RIEGO_ON,        "riego encender");
  esp_mn_commands_add(CMD_RIEGO_OFF,       "riego apagar");
  esp_mn_commands_add(CMD_LUZ_SALA_ON,     "luz sala encender");
  esp_mn_commands_add(CMD_LUZ_SALA_OFF,    "luz sala apagar");
  esp_mn_commands_add(CMD_LUZ_CUARTO_ON,   "luz cuarto encender");
  esp_mn_commands_add(CMD_LUZ_CUARTO_OFF,  "luz cuarto apagar");
  esp_mn_commands_add(CMD_VENTILADOR_ON,   "ventilador encender");
  esp_mn_commands_add(CMD_VENTILADOR_OFF,  "ventilador apagar");
  esp_mn_commands_add(CMD_INVERNADERO_ON,  "invernadero encender");   // NUEVO en v4:
  esp_mn_commands_add(CMD_INVERNADERO_OFF, "invernadero apagar");    // faltaba en v3
  esp_mn_commands_update();

  multinet->print_active_speech_commands(modelo_mn);
  log("VOZ", "Motor de voz listo");
}

void procesarResultadoVoz(int comandoID) {
  unsigned long ahora = millis();
  if (comandoID == ultimoComandoVozID && (ahora - ultimoComandoVozMs) < DEBOUNCE_VOZ_MS) {
    log("VOZ", "Comando repetido ignorado (debounce)");
    return;
  }
  ultimoComandoVozID = comandoID;
  ultimoComandoVozMs = ahora;

  log("VOZ", "Comando detectado, ID: " + String(comandoID));

  int indice = -1;
  bool encender = false;
  String comandoTexto = "";
  switch (comandoID) {
    case CMD_RIEGO_ON:        indice = 0; encender = true;  comandoTexto = "RIEGO_ON"; break;
    case CMD_RIEGO_OFF:       indice = 0; encender = false; comandoTexto = "RIEGO_OFF"; break;
    case CMD_LUZ_SALA_ON:     indice = 1; encender = true;  comandoTexto = "LUZ1_ON"; break;
    case CMD_LUZ_SALA_OFF:    indice = 1; encender = false; comandoTexto = "LUZ1_OFF"; break;
    case CMD_LUZ_CUARTO_ON:   indice = 2; encender = true;  comandoTexto = "LUZ2_ON"; break;
    case CMD_LUZ_CUARTO_OFF:  indice = 2; encender = false; comandoTexto = "LUZ2_OFF"; break;
    case CMD_VENTILADOR_ON:   indice = 3; encender = true;  comandoTexto = "VENT_ON"; break;
    case CMD_VENTILADOR_OFF:  indice = 3; encender = false; comandoTexto = "VENT_OFF"; break;
    case CMD_INVERNADERO_ON:  indice = 4; encender = true;  comandoTexto = "INVER_ON"; break;
    case CMD_INVERNADERO_OFF: indice = 4; encender = false; comandoTexto = "INVER_OFF"; break;
    default: log("VOZ", "ID de comando no mapeado"); return;
  }
  OrdenActuador orden = {indice, encender, ORIGEN_VOZ, 1.0f, comandoTexto.c_str()};
  ResultadoOrden resultado = ejecutarOrdenActuador(orden);
  // La app también se entera de los comandos disparados por voz, no solo
  // los que ella misma mandó, para que la UI no se quede desincronizada.
  enviarPorBLE((resultado.exito ? "ACK;" : "NACK;") + comandoTexto + ";voz");
}

// Máquina de estados de la ventana de escucha. Corrige el bug de v3 donde
// "afe_data != NULL" (verdadero casi siempre) hacía que MultiNet corriera
// de forma continua en vez de solo tras el wake word.
void revisarVoz() {
  if (afe_data == NULL) return; // el motor no se inicializó correctamente, evita crash

  afe_fetch_result_t* resultado = afe_handle->fetch(afe_data);
  if (!resultado || resultado->ret_value == ESP_FAIL) return;

  if (resultado->wakeup_state == WAKENET_DETECTED) {
    log("VOZ", "Palabra de activación detectada, abriendo ventana de escucha");
    ventanaEscuchaActiva = true;
    inicioVentanaEscuchaMs = millis();
    mostrarEscuchando();
  }

  // Cierra la ventana sola si expiró, sin esperar a la siguiente vuelta de detect()
  if (ventanaEscuchaActiva && (millis() - inicioVentanaEscuchaMs > VENTANA_ESCUCHA_MS)) {
    ventanaEscuchaActiva = false;
    log("VOZ", "Ventana de escucha cerrada (timeout sin comando)");
  }

  // Solo se corre MultiNet (que consume CPU) mientras la ventana está
  // abierta - ya no de forma continua como en v3.
  if (ventanaEscuchaActiva) {
    esp_mn_state_t estado_mn = multinet->detect(modelo_mn, resultado->data);
    if (estado_mn == ESP_MN_STATE_DETECTED) {
      esp_mn_results_t *resultados_mn = multinet->get_results(modelo_mn);
      if (resultados_mn->num > 0) {
        procesarResultadoVoz(resultados_mn->command_id[0]);
      }
      // Un comando reconocido cierra la ventana de inmediato; no hace falta
      // esperar el timeout completo para volver a exigir el wake word.
      ventanaEscuchaActiva = false;
    }
  }
}
#endif // JARVIS_LOCAL_HABILITADO

// ============================================================================
// SECCIÓN 13: SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(300);
  log("SISTEMA", "=== Casa Inteligente Autosostenible v5 - Iniciando ===");

  esp_task_wdt_config_t configWdt = {
    .timeout_ms = WATCHDOG_TIMEOUT_S * 1000,
    .idle_core_mask = 0,
    .trigger_panic = true
  };
  esp_task_wdt_init(&configWdt);
  esp_task_wdt_add(NULL);
  log("SISTEMA", "Watchdog activo, timeout=" + String(WATCHDOG_TIMEOUT_S) + "s");

  for (int i = 0; i < 8; i++) {
    // Precarga el nivel inactivo antes de habilitar la salida para reducir
    // pulsos breves durante el arranque en módulos activos en LOW.
    digitalWrite(PINES_RELES[i], RELE_ACTIVO_EN_LOW ? HIGH : LOW);
    pinMode(PINES_RELES[i], OUTPUT);
    propietarioReles[i] = PROPIETARIO_NINGUNO;
  }
  log("SISTEMA", "Relés inicializados (todos apagados)");

  detectarPantalla();
  mostrarBienvenida();

  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  dht.begin();
  log("SISTEMA", "DHT11 inicializado (temperatura/humedad ambiental)");

  if (MP3_HABILITADO) {
    SerialMP3.begin(9600, SERIAL_8N1, MP3_RX_PIN, MP3_TX_PIN);
    delay(500);
    log("MP3", "UART iniciado para módulo reproductor");
  }

  inicializarBLE();
  #if JARVIS_LOCAL_HABILITADO
    inicializarVoz();
  #else
    log("VOZ", "Jarvis local deshabilitado: falta modelo TinyML español validado");
  #endif

  if (MP3_HABILITADO) reproducirPista(6); // "Sistema listo"
  delay(1000);
  log("SISTEMA", "=== Sistema listo ===");
}

// ============================================================================
// SECCIÓN 14: LOOP PRINCIPAL (no bloqueante)
// ============================================================================
unsigned long ultimaActualizacionPantalla = 0;
#define DURACION_PANTALLA_ERROR_MS 4000

void loop() {
  esp_task_wdt_reset();

  // 1. Voz: máxima prioridad, se revisa en cada vuelta
  #if JARVIS_LOCAL_HABILITADO
    revisarVoz();
  #endif

  // 2. BLE: los comandos llegan por callback (onWrite), no hace falta
  //    revisar nada aquí de forma activa - NimBLE corre en su propia tarea.

  // 3. Riego automático (internamente respeta su propio intervalo, no bloquea)
  verificarRiegoAutomatico();

  // Corte independiente del sensor: una bomba jamás queda encendida sin límite.
  verificarLimiteBomba();

  // 3b. Ventilador automático por temperatura (mismo patrón no bloqueante)
  verificarVentiladorAutomatico();

  // 4. Pantalla: se refresca solo cada INTERVALO_PANTALLA_MS
  if (millis() - ultimaActualizacionPantalla > INTERVALO_PANTALLA_MS) {
    unsigned long idxUltimo = (indiceErrorActual - 1 + MAX_ERRORES_GUARDADOS) % MAX_ERRORES_GUARDADOS;
    bool hayErrorReciente = bufferErrores[idxUltimo].ocupado &&
                             (millis() - bufferErrores[idxUltimo].momentoMs) < DURACION_PANTALLA_ERROR_MS;

    if (hayErrorReciente) {
      mostrarPantallaError();
    } else {
      int humedadCrudo = 0, humedadPct = 0, viento = 0, ldrCrudo = 0, luzPct = 0;
      float tempC = 0, humAire = 0;
      bool humedadValida = leerHumedad(humedadCrudo, humedadPct);
      bool vientoValido = leerViento(viento);
      bool ldrValido = leerLuz(ldrCrudo, luzPct);
      bool tempValida = leerAmbiente(tempC, humAire);
      actualizarPantallaEstado(humedadPct, viento, humedadValida, vientoValido, tempC, tempValida);
    }
    ultimaActualizacionPantalla = millis();
  }
}
