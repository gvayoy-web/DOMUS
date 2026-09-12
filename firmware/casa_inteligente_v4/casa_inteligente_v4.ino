/*
  ============================================================================
  PROJECT DOMUS - FIRMWARE v6 OFFLINE
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

  v6 elimina las dependencias de aplicación móvil y BLE. El mismo vocabulario
  de comandos (RIEGO_ON, ESTADO, etc.) queda disponible localmente por USB
  Serial para diagnóstico y pruebas, además de los controles físicos.

  CAMBIOS PRINCIPALES DE v6:
    - ACK/NACK REAL POR COMANDO: cada comando de control ahora responde
      "ACK;<comando>;<estado_logico_gpio>" o "NACK;<comando>;<motivo>"
      inmediatamente por Serial, sin transporte de red.
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
  errores circular, recuperación I2C, detección automática del LCD1602,
  riego automático, módulo MP3.

  ============================================================================
  HERRAMIENTAS ACTUALES (Arduino IDE, firmware base):
    Board: "ESP32S3 Dev Module"
    PSRAM: "OPI PSRAM"
    Flash Size: "16MB"
    Partition Scheme: seleccionar después de medir modelos y PicoTTS; no usar
    un esquema OTA hasta definir una tabla compatible con los 16 MB de flash.

  LIBRERÍAS A INSTALAR (ver versiones exactas probadas en el README):
    1. "LiquidCrystal I2C"   - Frank de Brabander (para BLOQUE LCD)
    2. "DHT sensor library"  - Adafruit (para el DHT11 de temperatura/humedad)
    3. "Adafruit Unified Sensor" - Adafruit (dependencia de DHT sensor library)

  VOZ FINAL PENDIENTE:
    - detector TinyML de "Jarvis" + clasificador español int8
    - PicoTTS español + MAX98357A
    El bloque ESP-SR bajo bandera es legado y no debe activarse como solución
    española; será reemplazado cuando existan los artefactos validados.
  ============================================================================
*/

// MIGRACIÓN FASE E PASO 1 (nota 46, nota 52): la abstracción de relés se
// sustituye por SalidaDomus (TOTAL_SALIDAS, MAPA_CASA.salidas, estadoSalidas,
// propietarioSalidas, solicitar/desactivarSalida, verificarNivelLogicoSalida).
// Renombre mecánico, cero cambios de comportamiento: reglas de seguridad,
// histéresis, propiedad manual y protocolo quedan intactos. Pasos pendientes:
// drivers por perfil (FINAL), IR como entrada, audio por cola y validación
// física. El esqueleto alfa sigue siendo el firmware de banco vigente.
// Estado formal: CANDIDATO (ver nota 53); FINAL solo tras puertas F1-F7.

// Jarvis local en español requiere un modelo TinyML entrenado para este
// hardware. Mientras no exista ese artefacto, el resto de la casa debe seguir
// compilando y funcionando sin el SDK de voz.
#define JARVIS_LOCAL_HABILITADO false
#ifndef MICROSD_HABILITADA
#define MICROSD_HABILITADA false
#endif

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <limits.h>
#include <Preferences.h>
#include <new>
#include <atomic>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "domus_types.h"
#include "domus_calibration.h"
#include "domus_voice_contract.h"
#include "domus_drivers.h"
#include "esp_heap_caps.h"
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

// ---- Pantalla oficial del proyecto ----
#include <LiquidCrystal_I2C.h>

// ---- Sensor de temperatura/humedad ambiental ----
#include <DHT.h>                    // "DHT sensor library" de Adafruit (DHT11/DHT22)

// ============================================================================
// SECCIÓN 1: MAPA DE PINES - REVISAR/CALIBRAR A MANO
// ============================================================================
// Los sensores analógicos permanecen en ADC1 para reducir conflictos.

// --- Bus I2C compartido (pantalla, sea cual sea) ---
// Direcciones esperadas (se detectan automáticamente, no hace falta tocarlas):
#define DIR_LCD_1       0x27
#define DIR_LCD_2       0x3F

// --- Micrófono I2S (INMP441, FUTURO sin pines asignados) ---
// SIN ASIGNAR en el candidato: el mapa autorizado 15/16/17 ya los usa para
// suelo/nivel/SDA (nota 46/47/55). Se asignan con F4, nunca antes.
#define MIC_WS_PIN      -1
#define MIC_SD_PIN      -1
#define MIC_SCK_PIN     -1
#define TTS_BCLK_PIN    40   // provisional: confirmar exposición en placa
#define TTS_WS_PIN      41
#define TTS_DOUT_PIN    42
// Fijos en el módulo (no son GPIO configurables):
//   VDD -> 3.3V (¡JAMÁS 5V, se quema el chip!)   GND -> GND   L/R -> GND

// --- Sensores y controles: VALORES SOLO EN MAPA_CASA (abajo) ---
// Costado accesible autorizado (nota 46/47/55). No existen #define de pines
// del candidato fuera de MAPA_CASA: cualquier GPIO nuevo entra por el struct.
// RECORDATORIO FÍSICO (LDR): el fotoresistor va en divisor de voltaje con
// una resistencia fija (típicamente 10k) entre 3.3V y GND; MAPA_CASA.ldr lee el
// punto medio del divisor, nunca el LDR solo contra 3.3V.

// --- Sensor de temperatura/humedad AMBIENTAL (DHT11) ---
// Distinto del sensor de humedad de TIERRA (suelo): el DHT11 mide el
// aire alrededor de la maceta/casa, no la tierra dentro de ella.
#define TIPO_DHT        DHT11

// --- Cinco salidas con su etapa física según perfil (nota 53/54) ---
// Bomba y ventilador exigen driver confirmado (F1) y permanecen bloqueados en
// los tres perfiles actuales. Las tres luces son LED individuales con
// resistencia propia y son activas en HIGH en el perfil económico.
// Si se instala una etapa distinta, calibrar esta tabla y el perfil.
#define TOTAL_SALIDAS 5

// Mantener 0 para el cableado original. Seleccionar 1 únicamente
// después de montar la alternativa descrita en la nota 21 de Obsidian.
#ifndef DOMUS_SALIDAS_ECONOMICAS
#define DOMUS_SALIDAS_ECONOMICAS 0
#endif
const bool SALIDA_ACTIVA_EN_BAJO[TOTAL_SALIDAS] = {
  true, !DOMUS_SALIDAS_ECONOMICAS, !DOMUS_SALIDAS_ECONOMICAS,
  !DOMUS_SALIDAS_ECONOMICAS, !DOMUS_SALIDAS_ECONOMICAS
};
const char* NOMBRES_SALIDAS[TOTAL_SALIDAS] = {
  "Bomba", "Luz Sala", "Luz Cuarto", "Ventilador",
  "Luz Inv."
};

// --- Perfil del candidato y mapa central (nota 53/54, jefatura) ---
// 0 = BANCO_SIN_ACTUADORES (todo bloqueado). 1 = LED_SIN_MOTORES.
// 2 = MOTOR_PENDIENTE_DRIVER (motores bloqueados hasta F1; declara la
// intención del cableado futuro, no habilita nada hoy). El nombre de producto
// final no se usa en ningún binario (ver puertas F1-F7). Selección por
// bandera -DDOMUS_PERFIL_CASA=N.
#ifndef DOMUS_PERFIL_CASA
#define DOMUS_PERFIL_CASA 0
#endif
enum class PerfilCasa : uint8_t { BANCO_SIN_ACTUADORES, LED_SIN_MOTORES, MOTOR_PENDIENTE_DRIVER };
static_assert(DOMUS_PERFIL_CASA >= 0 && DOMUS_PERFIL_CASA <= 2,
              "DOMUS_PERFIL_CASA debe ser 0, 1 o 2");
constexpr PerfilCasa PERFIL_CASA =
    DOMUS_PERFIL_CASA == 1 ? PerfilCasa::LED_SIN_MOTORES :
    DOMUS_PERFIL_CASA == 2 ? PerfilCasa::MOTOR_PENDIENTE_DRIVER :
                             PerfilCasa::BANCO_SIN_ACTUADORES;
constexpr const char* nombrePerfilCasa(PerfilCasa p) {
  return p == PerfilCasa::LED_SIN_MOTORES ? "CANDIDATO_LED_SIN_MOTORES" :
         p == PerfilCasa::MOTOR_PENDIENTE_DRIVER ? "CANDIDATO_MOTOR_PENDIENTE_DRIVER" :
         "CANDIDATO_BANCO_SIN_ACTUADORES";
}
// Mapa GPIO central: ÚNICA fuente de pines del candidato (nota 55).
// Costado accesible autorizado (nota 46/47): suelo 15, nivel 16, SDA 17,
// demo/modo 18. Todo el firmware lee MAPA_CASA; no existen #define de pines.
struct MapaPinesCasa {
  int suelo, nivel, ldr;
  int bomba, sala, cuarto, vent, inv;
  int pir, paro, micOff, demo, scl, dht, sda;
  int salidas[TOTAL_SALIDAS];
};
constexpr MapaPinesCasa MAPA_CASA = {
  15, 16, 3,
  4, 5, 6, 7, 8,
  9, 10, 11, 18, 13, 14, 17,
  {4, 5, 6, 7, 8}
};
DHT dht(MAPA_CASA.dht, TIPO_DHT);
static_assert(MAPA_CASA.bomba == 4 && MAPA_CASA.sala == 5 && MAPA_CASA.cuarto == 6 &&
              MAPA_CASA.vent == 7 && MAPA_CASA.inv == 8, "Mapa de salidas del candidato");
static_assert(MAPA_CASA.suelo == 15 && MAPA_CASA.nivel == 16 && MAPA_CASA.sda == 17 &&
              MAPA_CASA.demo == 18 && MAPA_CASA.scl == 13, "Costado accesible autorizado");
static_assert(MAPA_CASA.bomba == MAPA_CASA.salidas[0] && MAPA_CASA.sala == MAPA_CASA.salidas[1] &&
              MAPA_CASA.cuarto == MAPA_CASA.salidas[2] && MAPA_CASA.vent == MAPA_CASA.salidas[3] &&
              MAPA_CASA.inv == MAPA_CASA.salidas[4], "Campos y arreglo de salidas unidos");
// Habilitación física derivada del perfil. Los motores quedan bloqueados en
// los tres perfiles vigentes (ver DRIVER_MOTORES_LISTO en domus_drivers.h).
constexpr bool SALIDA_FISICA_CASA[TOTAL_SALIDAS] = {
  false,
  PERFIL_CASA != PerfilCasa::BANCO_SIN_ACTUADORES,
  PERFIL_CASA != PerfilCasa::BANCO_SIN_ACTUADORES,
  false,
  PERFIL_CASA != PerfilCasa::BANCO_SIN_ACTUADORES
};

// --- Módulo MP3 (DFPlayer / TF-16P) - SIN ASIGNAR (FINAL-ONLY) ---
// Sin pines en el candidato: GPIO18 es el botón demo/modo del costado
// autorizado. Se asigna UART con F5, nunca antes.
#define MP3_RX_PIN      -1
#define MP3_TX_PIN      -1
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
// como tu medición húmeda). El sensor confirmado es resistivo; la polaridad
// exacta se determina con estas dos mediciones y la fórmula acepta ambos casos.
#define HUMEDAD_LECTURA_SECA     2800   // ADC crudo en tierra seca (0% humedad)
#define HUMEDAD_LECTURA_HUMEDA   1200   // ADC crudo en tierra recién regada (100%)
#define UMBRAL_HUMEDAD_SECA_PCT  35     // el riego automático se activa por debajo de este %
#define UMBRAL_HUMEDAD_HUMEDA_PCT 45    // y se apaga al alcanzar este %, evitando oscilaciones

#define HUMEDAD_MIN_VALIDA      50     // los rieles ADC se tratan como fallo
#define HUMEDAD_MAX_VALIDA      4045
#define NIVEL_AGUA_MIN_VALIDO          16
#define NIVEL_AGUA_MAX_VALIDO          4079
#define NIVEL_AGUA_MUESTRAS_ESTABLES   3
#define NIVEL_AGUA_MINIMO_CRUDO        600 // PROVISIONAL: calibrar con deposito casi vacio
#define PIR_RETENCION_MS              30000UL

// Calibración del LDR (fotoresistor), mismo principio que la humedad de
// tierra: dos lecturas de referencia se convierten a un 0-100% de luz.
// Para calibrar: abre el Monitor Serial, tapa el LDR con la mano (oscuridad)
// y anota el ADC crudo en LDR_LECTURA_OSCURO; luego ilumínalo con una
// linterna/luz directa y anota en LDR_LECTURA_BRILLANTE.
#define LDR_LECTURA_OSCURO      3200   // ADC crudo casi sin luz (0%)
#define LDR_LECTURA_BRILLANTE   400    // ADC crudo con luz directa (100%)
#define LDR_MIN_VALIDO          16
#define LDR_MAX_VALIDO          4079
#define UMBRAL_LUZ_OSCURO_PCT   25     // por debajo de este % se considera "oscuro" para automatización
#define UMBRAL_LUZ_CLARO_PCT    40     // histéresis: apagar solo al superar este valor

// DHT11: rango físico real del sensor (fuera de esto, se descarta la lectura)
#define DHT_TEMP_MIN_VALIDA_C    0.0
#define DHT_TEMP_MAX_VALIDA_C    50.0
#define DHT_HUM_MIN_VALIDA_PCT   20.0
#define DHT_HUM_MAX_VALIDA_PCT   90.0
#define DHT_INTERVALO_LECTURA_MS 2500   // el DHT11 no soporta lecturas más rápidas que ~1s, se deja margen

// Ventilador automático por temperatura ambiental (además de su control
// manual por controles físicos/Serial/voz, igual que el riego automático)
#define UMBRAL_TEMP_ALTA_C       28.0   // a partir de esto, se enciende el ventilador solo
#define UMBRAL_TEMP_NORMAL_C     26.0   // se apaga al bajar hasta aquí (histéresis de 2 °C)

// Anti-rebote de voz: exige que el mismo comando no se repita antes de este
// tiempo, para evitar que una sola frase dispare la acción varias veces
#define DEBOUNCE_VOZ_MS         2000
#define VOZ_MAX_FALLOS_CONSECUTIVOS 3
#define VOZ_TIEMPO_MAX_CICLO_US 250000UL

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

// --- Supervisor de salud y degradación segura ---
// El supervisor no reinicia por memoria baja: apaga cargas y mantiene Serial
// disponible para diagnóstico. Así se evita convertir una falta de memoria
// transitoria en un bucle de reinicios.
#define MEMORIA_LIBRE_CRITICA_BYTES       32768UL
#define MEMORIA_LIBRE_RECUPERACION_BYTES  65536UL
#define INTERVALO_SUPERVISOR_MS            2000UL
#define TIEMPO_ARRANQUE_ESTABLE_MS        60000UL
#define MAX_COMANDOS_POR_SEGUNDO             12

// --- Sistema de errores en memoria (buffer circular) ---
#define MAX_ERRORES_GUARDADOS   6
#define LONGITUD_MAX_ERROR      40

// --- I2C: reintentos ante fallo transitorio de pantalla ---
#define I2C_MAX_REINTENTOS      3
#define I2C_ESPERA_REINTENTO_MS 150
#define I2C_TIMEOUT_MS 10

// --- Lector microSD SPI independiente (pines provisionales) ---
#define SD_SCK_PIN   38
#define SD_MISO_PIN  39
#define SD_MOSI_PIN  47
#define SD_CS_PIN    48

// Contrato de hardware comprobado también por el compilador. Incluye los
// pines activos y los reservados para módulos opcionales para impedir que una
// ampliación futura reutilice silenciosamente una señal ya ocupada.
constexpr int PINES_RESERVADOS_DOMUS[] = {
  MAPA_CASA.suelo, MAPA_CASA.nivel, MAPA_CASA.ldr,
  MAPA_CASA.bomba, MAPA_CASA.sala, MAPA_CASA.cuarto,
  MAPA_CASA.vent, MAPA_CASA.inv,
  MAPA_CASA.pir, MAPA_CASA.paro, MAPA_CASA.micOff, MAPA_CASA.demo,
  MAPA_CASA.scl, MAPA_CASA.dht, MAPA_CASA.sda,
  SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN,
  TTS_BCLK_PIN, TTS_WS_PIN, TTS_DOUT_PIN
};

constexpr bool pinesDomusSonUnicos() {
  const size_t cantidad = sizeof(PINES_RESERVADOS_DOMUS) /
                          sizeof(PINES_RESERVADOS_DOMUS[0]);
  for (size_t i = 0; i < cantidad; ++i) {
    for (size_t j = i + 1; j < cantidad; ++j) {
      if (PINES_RESERVADOS_DOMUS[i] == PINES_RESERVADOS_DOMUS[j]) return false;
    }
  }
  return true;
}

static_assert(TOTAL_SALIDAS == 5, "DOMUS requiere exactamente cinco cargas");
static_assert(pinesDomusSonUnicos(), "Hay GPIO duplicados en el mapa DOMUS");
static_assert(UMBRAL_HUMEDAD_SECA_PCT < UMBRAL_HUMEDAD_HUMEDA_PCT,
              "Histeresis de suelo invertida");
static_assert(UMBRAL_LUZ_OSCURO_PCT < UMBRAL_LUZ_CLARO_PCT,
              "Histeresis de luz invertida");
static_assert(UMBRAL_TEMP_NORMAL_C < UMBRAL_TEMP_ALTA_C,
              "Histeresis de temperatura invertida");
static_assert(MEMORIA_LIBRE_CRITICA_BYTES < MEMORIA_LIBRE_RECUPERACION_BYTES,
              "La recuperacion debe exigir mas memoria que el modo seguro");

// ============================================================================
// SECCIÓN 3: OBJETOS GLOBALES
// ============================================================================
HardwareSerial SerialMP3(1); // UART1 para el módulo MP3
SPIClass spiMicroSD(FSPI);
std::atomic<bool> microSdMontada{false};
std::atomic<uint32_t> sdDescartados{0};
std::atomic<uint32_t> sdErrores{0};
std::atomic<int> sdUltimaPrueba{0}; // 0 pendiente/no probada, 1 correcta, -1 fallo
QueueHandle_t colaSD = nullptr;
String bufferComandoSerial;
bool descartarComandoHastaNuevaLinea = false;
bool micHabilitado = true;
bool paroEmergenciaActivo = false;
bool modoSeguroActivo = false;
bool watchdogActivo = false;
CalibracionDomus calibracion = {1, HUMEDAD_LECTURA_SECA, HUMEDAD_LECTURA_HUMEDA,
  LDR_LECTURA_OSCURO, LDR_LECTURA_BRILLANTE, NIVEL_AGUA_MINIMO_CRUDO, 0};
CalibracionDomus calibracionPendiente = calibracion;
bool calibracionGuardada = false;
uint8_t direccionLcdActiva = 0;
char motivoModoSeguro[48] = "ninguno";
bool ultimoBotonDemo = HIGH;
unsigned long ultimoCambioBotonDemoMs = 0;
unsigned long memoriaLibreMinima = ULONG_MAX;
unsigned long ultimaRevisionSaludMs = 0;
unsigned long inicioVentanaComandosMs = 0;
uint8_t comandosEnVentana = 0;
bool contadorReiniciosEstabilizado = false;
RTC_DATA_ATTR uint8_t reiniciosCriticosConsecutivos = 0;

// ---- Pantalla: solo se crea el objeto del tipo que se detectó ----
enum TipoPantalla { PANTALLA_NINGUNA, PANTALLA_LCD };
TipoPantalla pantallaActiva = PANTALLA_NINGUNA;

LiquidCrystal_I2C* lcd = nullptr;

// Estado de las cinco cargas físicas del diseño vigente.
bool estadoSalidas[TOTAL_SALIDAS] = {false, false, false, false, false};

// Toda fuente de control pasa por el mismo contrato. Esto evita que controles
// físicos, Serial, automatización y voz mantengan estados incompatibles.
enum PropietarioActuador {
  PROPIETARIO_NINGUNO,
  PROPIETARIO_MANUAL_ON,
  PROPIETARIO_MANUAL_OFF,
  PROPIETARIO_AUTOMATICO
};

PropietarioActuador propietarioSalidas[TOTAL_SALIDAS] = {
  PROPIETARIO_NINGUNO, PROPIETARIO_NINGUNO, PROPIETARIO_NINGUNO,
  PROPIETARIO_NINGUNO, PROPIETARIO_NINGUNO
};
unsigned long bombaEncendidaDesdeMs = 0;

// Motor de voz (ESP-SR/TinyML), únicamente cuando se ha validado un modelo.
#if JARVIS_LOCAL_HABILITADO
static esp_afe_sr_iface_t *afe_handle = NULL;
static esp_afe_sr_data_t *afe_data = NULL;
model_iface_data_t *modelo_mn = NULL;
esp_mn_iface_t *multinet = NULL;
bool motorVozListo = false;
bool vozSuspendidaPorSalud = false;
uint8_t fallosVozConsecutivos = 0;
#endif
unsigned long ultimoComandoVozMs = 0;
int ultimoComandoVozID = -1;

// Máquina de estados de la ventana de escucha (reemplaza el bug de v3)
bool ventanaEscuchaActiva = false;
unsigned long inicioVentanaEscuchaMs = 0;

// Últimas lecturas válidas de sensores (para no mostrar basura si un sensor
// falla momentáneamente)
int ultimaHumedadValida = -1;       // ADC crudo, humedad de TIERRA
int ultimoNivelAguaValido = -1;
bool ultimaPresenciaValida = false;
unsigned long ultimaPresenciaMs = 0;
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
void emitirEventoLocal(const String &linea);
bool leerNivelAgua(int &valorSalida);
bool probarMicroSD();
void registrarLineaMicroSD(const String &linea);
void activarParoEmergencia(const char* motivo);
bool rearmarSistema();
void entrarModoSeguro(const char* motivo);
bool recuperarModoSeguro();
void supervisarSalud();
bool permitirComandoSerial();

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
  r += "PERFIL_CANDIDATO=" + String(nombrePerfilCasa(PERFIL_CASA)) + ";";
  r += "UPTIME_S=" + String(millis() / 1000) + ";";
  r += "MEM_LIBRE=" + String(esp_get_free_heap_size()) + ";";
  r += "RAM_INTERNA=" + String(heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT)) + ";";
  r += "RAM_INTERNA_MIN=" + String(heap_caps_get_minimum_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT)) + ";";
  r += "RAM_BLOQUE_MAX=" + String(heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT)) + ";";
  r += "PSRAM_LIBRE=" + String(heap_caps_get_free_size(MALLOC_CAP_SPIRAM)) + ";";
  r += "PSRAM_MIN=" + String(heap_caps_get_minimum_free_size(MALLOC_CAP_SPIRAM)) + ";";
  r += "PSRAM_BLOQUE_MAX=" + String(heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM)) + ";";
  r += "ERRORES_TOTAL=" + String(totalErroresAcumulados) + ";";
  r += "ULTIMO_ERROR=" + (obtenerUltimoError().length() > 0 ? obtenerUltimoError() : "ninguno") + ";";
  r += "PANTALLA=" + String(pantallaActiva == PANTALLA_LCD ? "LCD" : "NINGUNA") + ";";
  r += "MEM_MIN=" + String(memoriaLibreMinima == ULONG_MAX ? 0 : memoriaLibreMinima) + ";";
  r += "MODO_SEGURO=" + String(modoSeguroActivo ? "ON" : "OFF") + ";";
  r += "MOTIVO_SEGURO=" + String(motivoModoSeguro) + ";";
  r += "REINICIOS_CRITICOS=" + String(reiniciosCriticosConsecutivos) + ";";
  r += "WATCHDOG=" + String(watchdogActivo ? "ON" : "FALLO") + ";";
  r += "CALIBRACION=" + String(calibracionGuardada ? "NVS" : "PROVISIONAL") + ";";
  r += "SD_DESCARTADOS=" + String(sdDescartados.load()) + ";";
  r += "SD_ERRORES=" + String(sdErrores.load()) + ";";
  r += "SD_PRUEBA=" + String(sdUltimaPrueba.load()) + ";";
  #if JARVIS_LOCAL_HABILITADO
    r += "VOZ=" + String(vozSuspendidaPorSalud ? "SUSPENDIDA" : (motorVozListo ? "LISTA" : "NO_LISTA")) + ";";
  #else
    r += "VOZ=DESHABILITADA;";
  #endif
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
// SECCIÓN 5B: ALMACENAMIENTO MICROSD LOCAL
// ============================================================================
void registrarLineaMicroSD(const String &linea) {
  if (!microSdMontada || colaSD == nullptr) return;
  if (linea.length() >= sizeof(TrabajoSD::linea)) { sdDescartados++; return; }
  TrabajoSD trabajo = {};
  trabajo.momento = millis();
  linea.toCharArray(trabajo.linea, sizeof(trabajo.linea));
  if (xQueueSend(colaSD, &trabajo, 0) != pdTRUE) sdDescartados++;
}

bool probarMicroSD() {
  if (!microSdMontada) return false;
  const char* ruta = "/domus_selftest.txt";
  const char* marca = "PROJECT_DOMUS_SD_OK";

  SD.remove(ruta);
  File salida = SD.open(ruta, FILE_WRITE);
  if (!salida) return false;
  bool escrita = salida.println(marca) == strlen(marca) + 2;
  salida.close();
  if (!escrita) return false;

  File entrada = SD.open(ruta, FILE_READ);
  if (!entrada) return false;
  String contenido = entrada.readStringUntil('\n');
  entrada.close();
  contenido.trim();
  return contenido == marca;
}

// Solo esta tarea posee el bus SD: ninguna orden de control espera a la tarjeta.
void tareaMicroSD(void*) {
  spiMicroSD.begin(SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN, SD_CS_PIN);
  microSdMontada = SD.begin(SD_CS_PIN, spiMicroSD, 4000000U);
  sdUltimaPrueba = probarMicroSD() ? 1 : -1;
  if (sdUltimaPrueba != 1) {
    microSdMontada = false;
    sdErrores++;
  }
  TrabajoSD trabajo;
  while (microSdMontada && xQueueReceive(colaSD, &trabajo, portMAX_DELAY) == pdTRUE) {
    bool ok = true;
    if (trabajo.prueba) {
      ok = probarMicroSD();
      sdUltimaPrueba = ok ? 1 : -1;
    } else {
      File archivo = SD.open("/domus.log", FILE_APPEND);
      ok = bool(archivo);
      if (ok && archivo.size() + sizeof(trabajo.linea) + 16 > 256UL * 1024) {
        archivo.close();
        ok = !SD.exists("/domus.prev.log") || SD.remove("/domus.prev.log");
        if (ok) ok = SD.rename("/domus.log", "/domus.prev.log");
        if (ok) { archivo = SD.open("/domus.log", FILE_APPEND); ok = bool(archivo); }
      }
      if (ok) {
        char registro[216];
        int longitud = snprintf(registro, sizeof(registro), "%lu;%s\n",
                                (unsigned long)trabajo.momento, trabajo.linea);
        ok = longitud > 0 && longitud < (int)sizeof(registro) &&
          archivo.write((const uint8_t*)registro, longitud) == (size_t)longitud;
      }
      archivo.close();
    }
    if (!ok) { sdErrores++; microSdMontada = false; }
  }
  SD.end();
  vTaskDelete(NULL);
}

bool solicitarPruebaSD() {
  if (!microSdMontada || colaSD == nullptr) return false;
  TrabajoSD trabajo = {};
  trabajo.prueba = true;
  return xQueueSend(colaSD, &trabajo, 0) == pdTRUE;
}

void inicializarMicroSD() {
  if (!MICROSD_HABILITADA) return;
  colaSD = xQueueCreate(8, sizeof(TrabajoSD));
  if (colaSD == nullptr || xTaskCreate(tareaMicroSD, "domus-sd", 6144, NULL, 1, NULL) != pdPASS) {
    if (colaSD != nullptr) { vQueueDelete(colaSD); colaSD = nullptr; }
    sdErrores++;
    registrarError("SD", "Sin recursos; registro desactivado");
  }
}

// ============================================================================
// SECCIÓN 6: DETECCIÓN DEL LCD1602 (I2C SCAN)
// ============================================================================
bool escanearBusI2C(bool &hayLcd, uint8_t &dirLcd) {
  hayLcd = false;
  int dispositivosEncontrados = 0;

  const uint8_t direcciones[] = {DIR_LCD_1, DIR_LCD_2};
  for (uint8_t dir : direcciones) {
    Wire.beginTransmission(dir);
    uint8_t error = Wire.endTransmission();
    if (error == 0) {
      dispositivosEncontrados++;
      log("I2C", "Dispositivo encontrado en 0x" + String(dir, HEX));
      if (dir == DIR_LCD_1  || dir == DIR_LCD_2)  { hayLcd = true;  dirLcd  = dir; }
    }
  }
  return dispositivosEncontrados > 0;
}

void detectarPantalla() {
  if (!Wire.begin(MAPA_CASA.sda, MAPA_CASA.scl)) {
    registrarError("I2C", "No se pudo iniciar; sin pantalla");
    return;
  }
  Wire.setTimeOut(I2C_TIMEOUT_MS);
  delay(50);

  bool hayLcd = false;
  uint8_t dirLcdEncontrada = 0;
  bool busRespondio = false;

  for (int intento = 1; intento <= I2C_MAX_REINTENTOS && !busRespondio; intento++) {
    busRespondio = escanearBusI2C(hayLcd, dirLcdEncontrada);
    if (!busRespondio) {
      log("I2C", "Intento " + String(intento) + "/" + String(I2C_MAX_REINTENTOS) + ": bus I2C sin respuesta, reintentando...");
      delay(I2C_ESPERA_REINTENTO_MS);
    }
  }

  if (!busRespondio) {
    registrarError("I2C", "Bus sin ningun dispositivo tras " + String(I2C_MAX_REINTENTOS) + " intentos. Revisar cableado SDA/SCL.");
  }

  if (hayLcd) {
    lcd = new (std::nothrow) LiquidCrystal_I2C(dirLcdEncontrada, 16, 2);
    if (lcd == nullptr) {
      registrarError("LCD", "Sin memoria; sin pantalla");
      return;
    }
    direccionLcdActiva = dirLcdEncontrada;
    lcd->init();
    lcd->backlight();
    pantallaActiva = PANTALLA_LCD;
    log("PANTALLA", "LCD 1602 detectado en 0x" + String(dirLcdEncontrada, HEX));
  } else {
    pantallaActiva = PANTALLA_NINGUNA;
    log("PANTALLA", "Ninguna pantalla detectada, sistema seguirá en modo headless");
  }
}

bool pantallaDisponible() {
  if (pantallaActiva != PANTALLA_LCD || lcd == nullptr) return false;
  Wire.beginTransmission(direccionLcdActiva);
  if (Wire.endTransmission() == 0) return true;
  pantallaActiva = PANTALLA_NINGUNA;
  registrarError("LCD", "Desconectada; control sigue activo");
  return false;
}

// ---- Pantalla de bienvenida ----
void mostrarBienvenida() {
  if (!pantallaDisponible()) return;
  lcd->clear();
  lcd->setCursor(0, 0);
  lcd->print("PROJECT DOMUS");
  lcd->setCursor(0, 1);
  lcd->print("Iniciando...");
}

// ---- Pantalla principal de estado (llamada periódicamente en el loop) ----
void actualizarPantallaEstado(int humedadPct, int nivelAgua, bool humedadValida, bool nivelValido, float tempC = -1.0, bool tempValida = false) {
  if (!pantallaDisponible()) return;
  lcd->clear();
  lcd->setCursor(0, 0);
  lcd->print("H:");
  lcd->print(humedadValida ? (String(humedadPct) + "%") : "ERR");
  lcd->print(" T:");
  lcd->print(tempValida ? (String(tempC, 0) + "C") : "ERR");

  lcd->setCursor(0, 1);
  String linea2 = "";
  if (paroEmergenciaActivo) linea2 = "!! EMERGENCIA !!";
  else {
    if (estadoSalidas[0]) linea2 += "B ";
    if (estadoSalidas[1]) linea2 += "LS ";
    if (estadoSalidas[2]) linea2 += "LC ";
    if (estadoSalidas[3]) linea2 += "V ";
    if (estadoSalidas[4]) linea2 += "LI ";
    if (linea2 == "") {
      if (!nivelValido) linea2 = "Nivel ERR";
      else if (nivelAgua < calibracion.nivelMinimo) linea2 = "Nivel bajo";
      else linea2 = "Todo apagado";
    }
  }
  lcd->print(linea2.substring(0, 16));
}

// ---- Pantalla de error: muestra el último error registrado ----
void mostrarPantallaError() {
  String ultimoError = obtenerUltimoError();
  if (ultimoError.length() == 0) return;

  if (!pantallaDisponible()) return;
  lcd->clear();
  lcd->setCursor(0, 0);
  lcd->print("ERROR:");
  lcd->setCursor(0, 1);
  lcd->print(ultimoError.substring(0, min(16, (int)ultimoError.length())));
}

// ---- Pantalla de "escuchando" cuando se detecta wake word ----
void mostrarEscuchando() {
  if (!pantallaDisponible()) return;
  lcd->clear();
  lcd->setCursor(0, 0);
  lcd->print("Escuchando...");
  lcd->setCursor(0, 1);
  lcd->print(micHabilitado ? "Di una orden" : "MIC OFF");
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
int fallosVerificacionSalida[TOTAL_SALIDAS] = {0, 0, 0, 0, 0};
#define MAX_FALLOS_ANTES_DE_ALERTA_PERSISTENTE 3

// IMPORTANTE (corrección del feedback #5 de v3): esta función NO verifica
// físicamente que el relé conmutó, ni que la carga real cambió de estado.
// Verifica únicamente que el GPIO del ESP32 quedó en el nivel lógico que
// se le acaba de ordenar. Un cable suelto entre el ESP32 y el módulo de
// relés, o un relé dañado, pueden hacer que esto devuelva true aunque nada
// haya cambiado físicamente. Para detectar el estado físico real del relé
// haría falta una señal de realimentación por hardware (ej. leer el propio
// contacto NO/NC del relé hacia un pin de entrada), que este kit no tiene.
int nivelSalida(int indice, bool encendida) {
  return encendida == SALIDA_ACTIVA_EN_BAJO[indice] ? LOW : HIGH;
}

bool verificarNivelLogicoSalida(int indice, bool estadoEsperado) {
  int nivelEsperado = nivelSalida(indice, estadoEsperado);
  int nivelReal = digitalRead(MAPA_CASA.salidas[indice]);
  return nivelReal == nivelEsperado;
}

// Devuelve true si el cambio de GPIO se aplicó y quedó confirmado. Los
// llamadores (Serial, botones y voz) usan este valor de retorno para construir un
// ACK o NACK real, en vez de asumir éxito silenciosamente.
bool solicitarSalida(int indice, bool anunciarPorVoz = true) {
  if (indice < 0 || indice >= TOTAL_SALIDAS) {
    registrarError("RELE", "Indice invalido solicitado: " + String(indice));
    return false;
  }
  if (estadoSalidas[indice]) return true; // ya encendido, se considera éxito idempotente

  digitalWrite(MAPA_CASA.salidas[indice], nivelSalida(indice, true));
  delay(5); // pequeña espera para que el relé mecánico termine de conmutar antes de releer

  if (!verificarNivelLogicoSalida(indice, true)) {
    fallosVerificacionSalida[indice]++;
    registrarError("RELE", String(NOMBRES_SALIDAS[indice]) + " no confirmo encendido en GPIO (revisar cableado)");
    if (fallosVerificacionSalida[indice] >= MAX_FALLOS_ANTES_DE_ALERTA_PERSISTENTE) {
      registrarError("RELE", String(NOMBRES_SALIDAS[indice]) + " fallo repetido, revisar hardware");
    }
    return false;
  }

  fallosVerificacionSalida[indice] = 0;
  estadoSalidas[indice] = true;
  log("RELE", String(NOMBRES_SALIDAS[indice]) + " -> ENCENDIDO (GPIO confirmado)");

  if (anunciarPorVoz && MP3_HABILITADO) {
    if (indice == 0) reproducirPista(1);       // "Regando ahora"
    else if (indice == 3) reproducirPista(5);  // "Ventilador activado"
    else reproducirPista(3);                    // "Luz encendida" (genérico)
  }
  return true;
}

bool desactivarSalida(int indice, bool anunciarPorVoz = true) {
  if (indice < 0 || indice >= TOTAL_SALIDAS) {
    registrarError("RELE", "Indice invalido solicitado: " + String(indice));
    return false;
  }
  if (!estadoSalidas[indice]) return true; // ya apagado, éxito idempotente

  digitalWrite(MAPA_CASA.salidas[indice], nivelSalida(indice, false));
  delay(5);

  if (!verificarNivelLogicoSalida(indice, false)) {
    fallosVerificacionSalida[indice]++;
    registrarError("RELE", String(NOMBRES_SALIDAS[indice]) + " no confirmo apagado en GPIO (posible rele pegado)");
    return false;
  }

  fallosVerificacionSalida[indice] = 0;
  estadoSalidas[indice] = false;
  log("RELE", String(NOMBRES_SALIDAS[indice]) + " -> APAGADO (GPIO confirmado)");

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

  const String nombre = String(NOMBRES_SALIDAS[orden.indiceRele]);
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
  if (orden.indiceRele < 0 || orden.indiceRele >= TOTAL_SALIDAS) {
    registrarError("ORDEN", "Indice de rele fuera de rango");
    return {false, false, "indice_invalido"};
  }

  // Revalidar al ejecutar: MIC OFF también invalida resultados ya calculados.
  if (orden.origen == ORIGEN_VOZ &&
      (!micHabilitado || digitalRead(MAPA_CASA.micOff) == LOW)) {
    return {false, false, "mic_off"};
  }

  // Una confianza baja jamás puede modificar la casa. Las fuentes que no
  // dependen de inferencia deben enviar 1.0.
  if (orden.origen == ORIGEN_VOZ && !domusVoiceConfidenceValid(orden.confianza)) {
    log("VOZ", "Orden rechazada por baja confianza: " + String(orden.confianza, 2));
    ResultadoOrden rechazo = {false, false, "confianza_baja"};
    responderJarvis(construirRespuestaJarvis(orden, estadoSalidas[orden.indiceRele], rechazo));
    return rechazo;
  }

  if (paroEmergenciaActivo && orden.encender) {
    log("SEGURIDAD", "Encendido rechazado: paro de emergencia activo");
    return {false, false, "paro_emergencia"};
  }

  if (modoSeguroActivo && orden.encender) {
    log("SEGURIDAD", "Encendido rechazado: modo seguro activo");
    return {false, false, "modo_seguro"};
  }

  // Motores primero por driver (F1) y después por etapa del perfil: el motivo
  // reportado distingue "sin driver validado" de "sin etapa instalada".
  if (orden.encender && (orden.indiceRele == 0 || orden.indiceRele == 3) &&
      !driverMotoresListo()) {
    log("SEGURIDAD", "Encendido rechazado: driver de motores no validado (F1)");
    return {false, false, "driver_no_listo"};
  }

  // Habilitación física del perfil: ninguna fuente enciende una salida sin
  // etapa instalada (nota 53/54/55).
  if (orden.encender && !SALIDA_FISICA_CASA[orden.indiceRele]) {
    log("SEGURIDAD", "Encendido rechazado: salida sin etapa en este perfil");
    return {false, false, "salida_no_instalada"};
  }

  // El nivel del depósito es una interlock física: ninguna fuente puede
  // encender la bomba si la lectura falta o está por debajo del mínimo.
  if (orden.indiceRele == 0 && orden.encender) {
    int nivelAgua = 0;
    if (!leerNivelAgua(nivelAgua) || nivelAgua < calibracion.nivelMinimo) {
      registrarError("SEGURIDAD", "Bomba bloqueada por nivel de agua bajo o invalido");
      ResultadoOrden bloqueo = {false, false, "nivel_agua_bajo"};
      if (orden.origen == ORIGEN_VOZ) {
        responderJarvis("No puedo regar: el deposito no tiene agua suficiente.");
      }
      return bloqueo;
    }
  }

  const bool estadoAnterior = estadoSalidas[orden.indiceRele];
  const bool exito = orden.encender
    ? solicitarSalida(orden.indiceRele, false)
    : desactivarSalida(orden.indiceRele, false);
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
    propietarioSalidas[orden.indiceRele] = (orden.origen == ORIGEN_AUTOMATICO)
      ? PROPIETARIO_AUTOMATICO : PROPIETARIO_MANUAL_ON;
    if (orden.indiceRele == 0 && !estadoAnterior) bombaEncendidaDesdeMs = millis();
  } else {
    if (orden.origen == ORIGEN_AUTOMATICO) {
      propietarioSalidas[orden.indiceRele] = PROPIETARIO_NINGUNO;
    } else {
      // Un apagado manual, por voz o por seguridad persiste hasta recibir
      // explícitamente el comando *_AUTO (o hasta un reinicio controlado).
      propietarioSalidas[orden.indiceRele] = PROPIETARIO_MANUAL_OFF;
    }
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
  if (!estadoSalidas[0] || bombaEncendidaDesdeMs == 0) return;
  if (millis() - bombaEncendidaDesdeMs < TIEMPO_MAXIMO_BOMBA_MS) return;

  registrarError("SEGURIDAD", "Bomba detenida por tiempo maximo continuo");
  OrdenActuador corte = {0, false, ORIGEN_SISTEMA, 1.0f, "BOMBA_TIMEOUT"};
  ResultadoOrden resultado = ejecutarOrdenActuador(corte);
  if (resultado.exito) emitirEventoLocal("EVENTO;BOMBA_TIMEOUT;0");
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
int fallosConsecutivosNivelAgua = 0;
uint8_t muestrasNivelAguaValidasConsecutivas = 0;
#define MAX_FALLOS_ANTES_DE_REGISTRAR 3

// Convierte una lectura ADC cruda a porcentaje 0-100% usando las constantes
// de calibración de la Sección 2. Funciona sin importar si "seca" es el
// número más alto o más bajo (soporta sensores de cualquier polaridad).
int convertirHumedadAPorcentaje(int lecturaCruda) {
  long rango = (long)calibracion.sueloHumedo - (long)calibracion.sueloSeco;
  if (rango == 0) return 0; // evita división por cero si no se calibró
  long pct = ((long)lecturaCruda - calibracion.sueloSeco) * 100L / rango;
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  return (int)pct;
}

bool leerHumedad(int &crudoSalida, int &pctSalida) {
  int lectura = leerSensorPromediado(MAPA_CASA.suelo);
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

bool leerNivelAgua(int &valorSalida) {
  int lectura = leerSensorPromediado(MAPA_CASA.nivel);
  if (lectura < NIVEL_AGUA_MIN_VALIDO || lectura > NIVEL_AGUA_MAX_VALIDO) {
    muestrasNivelAguaValidasConsecutivas = 0;
    fallosConsecutivosNivelAgua++;
    if (fallosConsecutivosNivelAgua >= MAX_FALLOS_ANTES_DE_REGISTRAR) {
      registrarError("SENSOR", "Nivel de agua fuera de rango, revisar conexion");
      fallosConsecutivosNivelAgua = 0;
    }
    return false;
  }
  fallosConsecutivosNivelAgua = 0;
  valorSalida = lectura;
  ultimoNivelAguaValido = lectura;
  if (muestrasNivelAguaValidasConsecutivas < NIVEL_AGUA_MUESTRAS_ESTABLES) {
    muestrasNivelAguaValidasConsecutivas++;
  }
  return muestrasNivelAguaValidasConsecutivas >= NIVEL_AGUA_MUESTRAS_ESTABLES;
}

// ---- LDR (fotoresistor) - luz ambiental ----
int fallosConsecutivosLdr = 0;

// Igual principio que convertirHumedadAPorcentaje(): funciona sin importar
// si "oscuro" es el número ADC más alto o más bajo, según cómo hayas armado
// el divisor de voltaje del LDR.
int convertirLdrAPorcentaje(int lecturaCruda) {
  long rango = (long)calibracion.luzClara - (long)calibracion.luzOscura;
  if (rango == 0) return 0;
  long pct = ((long)lecturaCruda - calibracion.luzOscura) * 100L / rango;
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  return (int)pct;
}

bool leerLuz(int &crudoSalida, int &pctSalida) {
  int lectura = leerSensorPromediado(MAPA_CASA.ldr);
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

  int nivelAgua = 0;
  bool nivelValido = leerNivelAgua(nivelAgua);
  if (!nivelValido || nivelAgua < calibracion.nivelMinimo) {
    if (estadoSalidas[0]) {
      OrdenActuador corte = {0, false, ORIGEN_SISTEMA, 1.0f, "NIVEL_AGUA_BAJO"};
      if (ejecutarOrdenActuador(corte).exito) {
        emitirEventoLocal("EVENTO;RIEGO_BLOQUEADO_NIVEL;0");
      }
    }
    return;
  }

  int crudo, pct;
  if (!leerHumedad(crudo, pct)) {
    // Si el riego fue automático, una pérdida del sensor crítico debe cortar
    // la bomba inmediatamente. Una orden manual conserva el límite máximo
    // independiente de dos minutos.
    if (estadoSalidas[0] && propietarioSalidas[0] == PROPIETARIO_AUTOMATICO) {
      OrdenActuador corte = {0, false, ORIGEN_AUTOMATICO, 1.0f, "HUMEDAD_INVALIDA"};
      ejecutarOrdenActuador(corte);
      emitirEventoLocal("EVENTO;RIEGO_BLOQUEADO_SENSOR;0");
    }
    return;
  }

  if (pct <= UMBRAL_HUMEDAD_SECA_PCT && !estadoSalidas[0] &&
      propietarioSalidas[0] != PROPIETARIO_MANUAL_OFF) {
    log("AUTO", "Tierra seca (" + String(pct) + "%), activando riego automático");
    OrdenActuador orden = {0, true, ORIGEN_AUTOMATICO, 1.0f, "RIEGO_AUTO_ON"};
    if (ejecutarOrdenActuador(orden).exito) {
      emitirEventoLocal("EVENTO;RIEGO_AUTO_ON;" + String(pct));
    }
  } else if (pct >= UMBRAL_HUMEDAD_HUMEDA_PCT && estadoSalidas[0] &&
             propietarioSalidas[0] == PROPIETARIO_AUTOMATICO) {
    // Solo apaga automáticamente si fue el modo automático quien lo prendió;
    // si el usuario lo encendió manualmente por voz/Serial, se respeta su
    // decisión y no se apaga solo.
    log("AUTO", "Humedad suficiente (" + String(pct) + "%), apagando riego automático");
    OrdenActuador orden = {0, false, ORIGEN_AUTOMATICO, 1.0f, "RIEGO_AUTO_OFF"};
    if (ejecutarOrdenActuador(orden).exito) {
      emitirEventoLocal("EVENTO;RIEGO_AUTO_OFF;" + String(pct));
    }
  }
}

// Misma filosofía que verificarRiegoAutomatico(): solo actúa si el estado
// actual del relé fue decisión del propio modo automático, para no pisar
// una decisión manual del usuario (índice 3 = Ventilador, ver MAPA_CASA.salidas).
unsigned long ultimaVerificacionVentilador = 0;

void verificarVentiladorAutomatico() {
  if (millis() - ultimaVerificacionVentilador < INTERVALO_RIEGO_MS) return;
  ultimaVerificacionVentilador = millis();

  float tempC, humAire;
  if (!leerAmbiente(tempC, humAire)) {
    if (estadoSalidas[3] && propietarioSalidas[3] == PROPIETARIO_AUTOMATICO) {
      OrdenActuador corte = {3, false, ORIGEN_AUTOMATICO, 1.0f, "DHT_INVALIDO"};
      ejecutarOrdenActuador(corte);
      emitirEventoLocal("EVENTO;VENT_BLOQUEADO_SENSOR;0");
    }
    return;
  }

  if (tempC >= UMBRAL_TEMP_ALTA_C && !estadoSalidas[3] &&
      propietarioSalidas[3] != PROPIETARIO_MANUAL_OFF) {
    log("AUTO", "Temperatura alta (" + String(tempC, 1) + "C), activando ventilador automático");
    OrdenActuador orden = {3, true, ORIGEN_AUTOMATICO, 1.0f, "VENT_AUTO_ON"};
    if (ejecutarOrdenActuador(orden).exito) {
      emitirEventoLocal("EVENTO;VENT_AUTO_ON;" + String(tempC, 1));
    }
  } else if (tempC <= UMBRAL_TEMP_NORMAL_C && estadoSalidas[3] &&
             propietarioSalidas[3] == PROPIETARIO_AUTOMATICO) {
    log("AUTO", "Temperatura normal (" + String(tempC, 1) + "C), apagando ventilador automático");
    OrdenActuador orden = {3, false, ORIGEN_AUTOMATICO, 1.0f, "VENT_AUTO_OFF"};
    if (ejecutarOrdenActuador(orden).exito) {
      emitirEventoLocal("EVENTO;VENT_AUTO_OFF;" + String(tempC, 1));
    }
  }
}

// La sala se enciende únicamente con oscuridad y presencia. La retención
// evita que el PIR apague la luz entre pulsos. El invernadero usa solo el LDR.
unsigned long ultimaVerificacionLuces = 0;

void verificarLucesAutomaticas() {
  if (millis() - ultimaVerificacionLuces < 500UL) return;
  ultimaVerificacionLuces = millis();

  ultimaPresenciaValida = digitalRead(MAPA_CASA.pir) == HIGH;
  if (ultimaPresenciaValida) ultimaPresenciaMs = millis();

  int ldrCrudo = 0, luzPct = 0;
  if (!leerLuz(ldrCrudo, luzPct)) {
    const int lucesAutomaticas[] = {1, 4};
    bool huboCorte = false;
    for (int indice : lucesAutomaticas) {
      if (estadoSalidas[indice] && propietarioSalidas[indice] == PROPIETARIO_AUTOMATICO) {
        OrdenActuador corte = {indice, false, ORIGEN_AUTOMATICO, 1.0f, "LDR_INVALIDO"};
        ejecutarOrdenActuador(corte);
        huboCorte = true;
      }
    }
    if (huboCorte) emitirEventoLocal("EVENTO;LUCES_AUTO_BLOQUEADAS_SENSOR;0");
    return;
  }

  bool presenciaReciente = ultimaPresenciaMs != 0 &&
                           millis() - ultimaPresenciaMs <= PIR_RETENCION_MS;
  if (propietarioSalidas[1] != PROPIETARIO_MANUAL_ON &&
      propietarioSalidas[1] != PROPIETARIO_MANUAL_OFF) {
    if (!estadoSalidas[1] && luzPct <= UMBRAL_LUZ_OSCURO_PCT && presenciaReciente) {
      OrdenActuador orden = {1, true, ORIGEN_AUTOMATICO, 1.0f, "LUZ_SALA_AUTO_ON"};
      ejecutarOrdenActuador(orden);
    } else if (estadoSalidas[1] && propietarioSalidas[1] == PROPIETARIO_AUTOMATICO &&
               (luzPct >= UMBRAL_LUZ_CLARO_PCT || !presenciaReciente)) {
      OrdenActuador orden = {1, false, ORIGEN_AUTOMATICO, 1.0f, "LUZ_SALA_AUTO_OFF"};
      ejecutarOrdenActuador(orden);
    }
  }

  if (propietarioSalidas[4] != PROPIETARIO_MANUAL_ON &&
      propietarioSalidas[4] != PROPIETARIO_MANUAL_OFF) {
    if (!estadoSalidas[4] && luzPct <= UMBRAL_LUZ_OSCURO_PCT) {
      OrdenActuador orden = {4, true, ORIGEN_AUTOMATICO, 1.0f, "LUZ_INVER_AUTO_ON"};
      ejecutarOrdenActuador(orden);
    } else if (estadoSalidas[4] && propietarioSalidas[4] == PROPIETARIO_AUTOMATICO &&
               luzPct >= UMBRAL_LUZ_CLARO_PCT) {
      OrdenActuador orden = {4, false, ORIGEN_AUTOMATICO, 1.0f, "LUZ_INVER_AUTO_OFF"};
      ejecutarOrdenActuador(orden);
    }
  }
}

// ============================================================================
// SECCIÓN 11: COMANDOS LOCALES POR USB SERIAL
// ============================================================================
// Comandos de texto terminados en salto de línea:
//   RIEGO_ON / RIEGO_OFF | LUZ1_ON / LUZ1_OFF | LUZ2_ON / LUZ2_OFF
//   VENT_ON / VENT_OFF   | INVER_ON / INVER_OFF | ESTADO | DIAGNOSTICO
//
//   "ACK;<comando>;<estado_logico_0_o_1>"   -> el comando se aplicó y se confirmó por GPIO
//   "NACK;<comando>;<motivo>"               -> el comando no pudo confirmarse o fue rechazado

String construirReporteEstado() {
  String r = "ESTADO;";
  for (int i = 0; i < TOTAL_SALIDAS; i++) {
    r += NOMBRES_SALIDAS[i];
    r += "=";
    r += estadoSalidas[i] ? "1" : "0";
    r += ";";
  }
  r += "HUM=" + String(ultimaHumedadValida) + ";";       // humedad de TIERRA, crudo ADC
  r += "HUM_PCT=" + String(ultimoHumedadPctValido) + ";"; // humedad de TIERRA, calibrada
  r += "NIVEL_AGUA=" + String(ultimoNivelAguaValido) + ";";
  r += "PIR=" + String(ultimaPresenciaValida ? 1 : 0) + ";";
  r += "TEMP_C=" + String(ultimaTempCValida, 1) + ";";        // DHT11, temperatura AMBIENTAL
  r += "HUM_AIRE_PCT=" + String(ultimaHumAireValida, 1) + ";"; // DHT11, humedad AMBIENTAL (no confundir con HUM_PCT de tierra)
  r += "LUZ_PCT=" + String(ultimoLuzPctValido) + ";";          // LDR, luz ambiental calibrada
  r += "MIC=" + String(micHabilitado ? "ON" : "OFF") + ";";
  r += "SD=" + String(microSdMontada ? "ON" : "OFF") + ";";
  r += "EMERGENCIA=" + String(paroEmergenciaActivo ? "ON" : "OFF") + ";";
  r += "MODO_SEGURO=" + String(modoSeguroActivo ? "ON" : "OFF") + ";";
  return r;
}

const char* COMANDOS_VALIDOS[] = {
  "RIEGO_ON", "RIEGO_OFF", "LUZ1_ON", "LUZ1_OFF", "LUZ2_ON", "LUZ2_OFF",
  "VENT_ON", "VENT_OFF", "INVER_ON", "INVER_OFF",
  "RIEGO_AUTO", "LUZ1_AUTO", "LUZ2_AUTO", "VENT_AUTO", "INVER_AUTO",
  "ESTADO", "DIAGNOSTICO", "PARO", "REARMAR", "RECUPERAR",
  "MIC_ESTADO", "SD_PRUEBA"
};
const int CANTIDAD_COMANDOS_VALIDOS =
  sizeof(COMANDOS_VALIDOS) / sizeof(COMANDOS_VALIDOS[0]);

bool esComandoValido(const String &comando) {
  for (int i = 0; i < CANTIDAD_COMANDOS_VALIDOS; i++) {
    if (comando == COMANDOS_VALIDOS[i]) return true;
  }
  return false;
}

bool permitirComandoSerial() {
  const unsigned long ahora = millis();
  if (ahora - inicioVentanaComandosMs >= 1000UL) {
    inicioVentanaComandosMs = ahora;
    comandosEnVentana = 0;
  }
  if (comandosEnVentana >= MAX_COMANDOS_POR_SEGUNDO) return false;
  comandosEnVentana++;
  return true;
}

// Aplica un comando de control de relé y envía ACK/NACK real. Centraliza la
// lógica que antes estaba repetida por cada carga en procesarComandoBluetooth().
void ejecutarComandoRele(const String &comando, int indice, bool encender,
                         OrigenOrden origen = ORIGEN_MANUAL, float confianza = 1.0f) {
  OrdenActuador orden = {indice, encender, origen, confianza, comando.c_str()};
  ResultadoOrden resultado = ejecutarOrdenActuador(orden);
  if (resultado.exito) {
    emitirEventoLocal("ACK;" + comando + ";" + String(estadoSalidas[indice] ? 1 : 0));
  } else {
    emitirEventoLocal("NACK;" + comando + ";" + String(resultado.motivo));
  }
}

void restaurarModoAutomatico(const String &comando, int indice) {
  if (indice < 0 || indice >= TOTAL_SALIDAS) {
    emitirEventoLocal("NACK;" + comando + ";indice_invalido");
    return;
  }
  propietarioSalidas[indice] = PROPIETARIO_AUTOMATICO;
  log("MODO", String(NOMBRES_SALIDAS[indice]) + " -> AUTO");
  emitirEventoLocal("ACK;" + comando + ";AUTO");
}

void activarParoEmergencia(const char* motivo) {
  paroEmergenciaActivo = true;
  for (int i = 0; i < TOTAL_SALIDAS; i++) {
    OrdenActuador orden = {i, false, ORIGEN_SISTEMA, 1.0f, motivo};
    ejecutarOrdenActuador(orden);
  }
  emitirEventoLocal("EVENTO;PARO_EMERGENCIA;ACTIVO");
}

void entrarModoSeguro(const char* motivo) {
  if (modoSeguroActivo) return;
  modoSeguroActivo = true;
  strncpy(motivoModoSeguro, motivo ? motivo : "desconocido", sizeof(motivoModoSeguro) - 1);
  motivoModoSeguro[sizeof(motivoModoSeguro) - 1] = '\0';
  ventanaEscuchaActiva = false;

  for (int i = 0; i < TOTAL_SALIDAS; i++) {
    OrdenActuador orden = {i, false, ORIGEN_SISTEMA, 1.0f, "MODO_SEGURO"};
    ejecutarOrdenActuador(orden);
  }
  emitirEventoLocal("EVENTO;MODO_SEGURO;" + String(motivoModoSeguro));
}

bool recuperarModoSeguro() {
  if (!watchdogActivo) {
    emitirEventoLocal("NACK;RECUPERAR;watchdog_no_disponible");
    return false;
  }
  if (!modoSeguroActivo) {
    emitirEventoLocal("ACK;RECUPERAR;YA_ESTABLE");
    return true;
  }
  if (paroEmergenciaActivo) {
    emitirEventoLocal("NACK;RECUPERAR;paro_emergencia");
    return false;
  }
  const unsigned long memoriaLibre = esp_get_free_heap_size();
  if (memoriaLibre < MEMORIA_LIBRE_RECUPERACION_BYTES) {
    emitirEventoLocal("NACK;RECUPERAR;memoria_insuficiente");
    return false;
  }

  modoSeguroActivo = false;
  strncpy(motivoModoSeguro, "ninguno", sizeof(motivoModoSeguro));
  motivoModoSeguro[sizeof(motivoModoSeguro) - 1] = '\0';
  // Las cargas permanecen MANUAL_OFF. El operador debe devolver cada una a
  // AUTO o encenderla explícitamente después de revisar el diagnóstico.
  emitirEventoLocal("ACK;RECUPERAR;SEGURO");
  return true;
}

bool rearmarSistema() {
  if (digitalRead(MAPA_CASA.paro) == LOW) {
    emitirEventoLocal("NACK;REARMAR;boton_emergencia_presionado");
    return false;
  }
  paroEmergenciaActivo = false;
  // El rearme no enciende nada ni devuelve cargas a AUTO por sí solo.
  emitirEventoLocal("ACK;REARMAR;SEGURO");
  return true;
}

void cargarCalibracion() {
  Preferences prefs;
  if (prefs.begin("domus-cal", true)) {
    CalibracionDomus leida = {};
    if (prefs.getBytesLength("config") == sizeof(leida) &&
        prefs.getBytes("config", &leida, sizeof(leida)) == sizeof(leida) &&
        calibracionValida(leida) && leida.checksum == checksumCalibracion(leida)) {
      calibracion = leida;
      calibracionGuardada = true;
    }
    prefs.end();
  }
  calibracionPendiente = calibracion;
}

bool procesarCalibracion(const String &comando) {
  if (!comando.startsWith("CAL_")) return false;
  if (comando == "CAL_VER") {
    emitirEventoLocal("CAL;SECO=" + String(calibracionPendiente.sueloSeco) +
      ";HUMEDO=" + String(calibracionPendiente.sueloHumedo) +
      ";OSCURO=" + String(calibracionPendiente.luzOscura) +
      ";CLARO=" + String(calibracionPendiente.luzClara) +
      ";NIVEL=" + String(calibracionPendiente.nivelMinimo));
    return true;
  }
  // NVS solo se modifica con paro enclavado y todas las salidas apagadas.
  bool apagadas = true;
  for (bool estado : estadoSalidas) apagadas = apagadas && !estado;
  if (!paroEmergenciaActivo || !apagadas) {
    emitirEventoLocal("NACK;CAL;requiere_paro");
    return true;
  }
  if (comando == "CAL_GUARDAR") {
    if (!calibracionValida(calibracionPendiente)) {
      emitirEventoLocal("NACK;CAL;rangos_invalidos");
      return true;
    }
    calibracionPendiente.checksum = checksumCalibracion(calibracionPendiente);
    // Una misma configuración no vuelve a desgastar la flash.
    bool guardada = calibracionGuardada &&
      calibracion.checksum == calibracionPendiente.checksum;
    if (!guardada) {
      Preferences prefs;
      if (prefs.begin("domus-cal", false)) {
        guardada = prefs.putBytes("config", &calibracionPendiente,
                                 sizeof(calibracionPendiente)) == sizeof(calibracionPendiente);
        prefs.end();
      }
    }
    if (guardada) {
      calibracion = calibracionPendiente;
      calibracionGuardada = true;
      muestrasNivelAguaValidasConsecutivas = 0;
    }
    emitirEventoLocal(guardada ? "ACK;CAL_GUARDAR;OK" : "NACK;CAL;error_nvs");
    return true;
  }
  if (comando == "CAL_CANCELAR") {
    calibracionPendiente = calibracion;
    emitirEventoLocal("ACK;CAL_CANCELAR;OK");
    return true;
  }
  int separador = comando.indexOf('=');
  if (separador < 0) { emitirEventoLocal("NACK;CAL;sintaxis"); return true; }
  String numero = comando.substring(separador + 1);
  if (numero.length() == 0 || numero.length() > 4) {
    emitirEventoLocal("NACK;CAL;numero_invalido"); return true;
  }
  for (unsigned int i = 0; i < numero.length(); i++) {
    if (numero[i] < '0' || numero[i] > '9') {
      emitirEventoLocal("NACK;CAL;numero_invalido"); return true;
    }
  }
  int valor = numero.toInt();
  if (valor > 4095) { emitirEventoLocal("NACK;CAL;fuera_de_adc"); return true; }
  String clave = comando.substring(0, separador);
  if (clave == "CAL_SECO") calibracionPendiente.sueloSeco = valor;
  else if (clave == "CAL_HUMEDO") calibracionPendiente.sueloHumedo = valor;
  else if (clave == "CAL_OSCURO") calibracionPendiente.luzOscura = valor;
  else if (clave == "CAL_CLARO") calibracionPendiente.luzClara = valor;
  else if (clave == "CAL_NIVEL") calibracionPendiente.nivelMinimo = valor;
  else { emitirEventoLocal("NACK;CAL;clave_invalida"); return true; }
  emitirEventoLocal("ACK;CAL;PENDIENTE_GUARDAR");
  return true;
}

void procesarComandoTexto(String comando) {
  comando.trim();
  comando.toUpperCase();

  if (comando.length() == 0) return;

  if (comando.length() > 20) {
    registrarError("COMANDO", "Longitud invalida (" + String(comando.length()) + " caracteres)");
    emitirEventoLocal("NACK;" + comando.substring(0, 20) + ";longitud_invalida");
    return;
  }

  // PARO siempre atraviesa el limitador. El resto se limita para que una
  // terminal defectuosa no monopolice CPU, memoria ni escritura en microSD.
  if (comando != "PARO" && !permitirComandoSerial()) {
    emitirEventoLocal("NACK;" + comando + ";limite_de_frecuencia");
    return;
  }

  if (procesarCalibracion(comando)) return;
  if (!esComandoValido(comando)) {
    registrarError("COMANDO", "No reconocido: " + comando);
    emitirEventoLocal("NACK;" + comando + ";no_reconocido");
    return;
  }

  log("SERIAL", "Comando recibido: " + comando);

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
  else if (comando == "RIEGO_AUTO") restaurarModoAutomatico(comando, 0);
  else if (comando == "LUZ1_AUTO")  restaurarModoAutomatico(comando, 1);
  else if (comando == "LUZ2_AUTO")  restaurarModoAutomatico(comando, 2);
  else if (comando == "VENT_AUTO")  restaurarModoAutomatico(comando, 3);
  else if (comando == "INVER_AUTO") restaurarModoAutomatico(comando, 4);
  else if (comando == "ESTADO")    emitirEventoLocal(construirReporteEstado());
  else if (comando == "DIAGNOSTICO") emitirEventoLocal(construirReporteDiagnostico());
  else if (comando == "PARO") activarParoEmergencia("PARO_SERIAL");
  else if (comando == "REARMAR") rearmarSistema();
  else if (comando == "RECUPERAR") recuperarModoSeguro();
  else if (comando == "MIC_ESTADO") emitirEventoLocal(String("MIC;") + (micHabilitado ? "ON" : "OFF"));
  else if (comando == "SD_PRUEBA") emitirEventoLocal(solicitarPruebaSD() ? "ACK;SD_PRUEBA;ENCOLADA" : "NACK;SD_PRUEBA;NO_DISPONIBLE");
}

void emitirEventoLocal(const String &linea) {
  Serial.println(linea);
  registrarLineaMicroSD(linea);
}

void revisarComandosSerial() {
  // Ceder al lazo principal aun cuando el host transmita continuamente.
  unsigned int bytesProcesados = 0;
  while (Serial.available() > 0 && bytesProcesados < 128) {
    bytesProcesados++;
    char caracter = (char)Serial.read();
    if (descartarComandoHastaNuevaLinea) {
      if (caracter == '\n') descartarComandoHastaNuevaLinea = false;
      continue;
    }
    if (caracter == '\r') continue;
    if (caracter == '\n') {
      if (bufferComandoSerial.length() > 0) {
        procesarComandoTexto(bufferComandoSerial);
        bufferComandoSerial = "";
      }
      continue;
    }
    if (bufferComandoSerial.length() < 40) {
      bufferComandoSerial += caracter;
    } else {
      bufferComandoSerial = "";
      descartarComandoHastaNuevaLinea = true;
      emitirEventoLocal("NACK;SERIAL;buffer_excedido");
    }
  }
}

void revisarControlesFisicos() {
  bool nuevoMicHabilitado = digitalRead(MAPA_CASA.micOff) != LOW;
  if (nuevoMicHabilitado != micHabilitado) {
    micHabilitado = nuevoMicHabilitado;
    if (!micHabilitado) ventanaEscuchaActiva = false;
    emitirEventoLocal(String("EVENTO;MIC;") + (micHabilitado ? "ON" : "OFF"));
  }

  if (digitalRead(MAPA_CASA.paro) == LOW) {
    if (!paroEmergenciaActivo) activarParoEmergencia("PARO_FISICO");
  }

  bool botonDemo = digitalRead(MAPA_CASA.demo);
  if (botonDemo != ultimoBotonDemo && millis() - ultimoCambioBotonDemoMs >= 40UL) {
    ultimoCambioBotonDemoMs = millis();
    ultimoBotonDemo = botonDemo;
    if (botonDemo == LOW && !paroEmergenciaActivo) {
      OrdenActuador orden = {
        1, !estadoSalidas[1], ORIGEN_MANUAL, 1.0f, "BOTON_DEMO_LUZ_SALA"
      };
      ResultadoOrden resultado = ejecutarOrdenActuador(orden);
      emitirEventoLocal(resultado.exito
        ? String("ACK;BOTON_LUZ_SALA;") + (estadoSalidas[1] ? "1" : "0")
        : String("NACK;BOTON_LUZ_SALA;") + resultado.motivo);
    }
  }
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
  motorVozListo = false;
  vozSuspendidaPorSalud = false;
  fallosVozConsecutivos = 0;

  afe_handle = (esp_afe_sr_iface_t*)&ESP_AFE_SR_HANDLE;
  afe_config_t afe_config = AFE_CONFIG_DEFAULT();
  afe_data = afe_handle->create_from_config(&afe_config);

  if (afe_data == NULL) {
    registrarError("VOZ", "No se pudo inicializar AFE. Revisar INMP441 (WS/SD/SCK) y PSRAM.");
    return;
  }

  srmodel_list_t *models = esp_srmodel_init("model");
  if (models == NULL) {
    registrarError("VOZ", "No se pudo cargar la lista de modelos");
    vozSuspendidaPorSalud = true;
    return;
  }
  char *nombre_modelo_mn = esp_srmodel_filter(models, ESP_MN_PREFIX, NULL);
  if (nombre_modelo_mn == NULL) {
    registrarError("VOZ", "Modelo MultiNet no encontrado. Revisar particion SPIFFS/modelo.");
    return;
  }

  multinet = esp_mn_handle_from_name(nombre_modelo_mn);
  if (multinet == NULL) {
    registrarError("VOZ", "Interfaz MultiNet no disponible");
    vozSuspendidaPorSalud = true;
    return;
  }
  modelo_mn = multinet->create(nombre_modelo_mn, 6000);
  if (modelo_mn == NULL) {
    registrarError("VOZ", "No se pudo crear el modelo MultiNet");
    vozSuspendidaPorSalud = true;
    return;
  }

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
  motorVozListo = true;
  log("VOZ", "Motor de voz listo");
}

void registrarFalloVoz(const char* motivo) {
  if (fallosVozConsecutivos < 255) fallosVozConsecutivos++;
  log("VOZ", "Fallo " + String(fallosVozConsecutivos) + ": " + String(motivo));
  if (fallosVozConsecutivos >= VOZ_MAX_FALLOS_CONSECUTIVOS) {
    vozSuspendidaPorSalud = true;
    motorVozListo = false;
    ventanaEscuchaActiva = false;
    emitirEventoLocal("EVENTO;VOZ_SUSPENDIDA;" + String(motivo));
  }
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
  emitirEventoLocal((resultado.exito ? "ACK;" : "NACK;") + comandoTexto + ";voz");
}

// Máquina de estados de la ventana de escucha. Corrige el bug de v3 donde
// "afe_data != NULL" (verdadero casi siempre) hacía que MultiNet corriera
// de forma continua en vez de solo tras el wake word.
void revisarVoz() {
  if (!motorVozListo || vozSuspendidaPorSalud || afe_handle == NULL ||
      afe_data == NULL || multinet == NULL || modelo_mn == NULL) return;

  const unsigned long inicioCicloUs = micros();

  afe_fetch_result_t* resultado = afe_handle->fetch(afe_data);
  if (!resultado || resultado->ret_value == ESP_FAIL) {
    registrarFalloVoz("afe_fetch");
    return;
  }

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

  const unsigned long duracionCicloUs = micros() - inicioCicloUs;
  if (duracionCicloUs > VOZ_TIEMPO_MAX_CICLO_US) {
    registrarFalloVoz("tiempo_excedido");
  } else {
    fallosVozConsecutivos = 0;
  }
}
#endif // JARVIS_LOCAL_HABILITADO

// ============================================================================
// SECCIÓN 12B: SUPERVISOR DE SALUD
// ============================================================================
bool esReinicioCritico(esp_reset_reason_t motivo) {
  return motivo == ESP_RST_PANIC || motivo == ESP_RST_INT_WDT ||
         motivo == ESP_RST_TASK_WDT || motivo == ESP_RST_WDT ||
         motivo == ESP_RST_BROWNOUT;
}

void supervisarSalud() {
  const unsigned long ahora = millis();
  if (ahora - ultimaRevisionSaludMs < INTERVALO_SUPERVISOR_MS) return;
  ultimaRevisionSaludMs = ahora;

  const unsigned long memoriaLibre = esp_get_free_heap_size();
  if (memoriaLibre < memoriaLibreMinima) memoriaLibreMinima = memoriaLibre;

  if (memoriaLibre < MEMORIA_LIBRE_CRITICA_BYTES) {
    entrarModoSeguro("memoria_critica");
  }

  // Tras un minuto estable se rompe la cadena de reinicios críticos. El dato
  // vive en RTC RAM y no desgasta la flash/NVS.
  if (!contadorReiniciosEstabilizado && ahora >= TIEMPO_ARRANQUE_ESTABLE_MS) {
    reiniciosCriticosConsecutivos = 0;
    contadorReiniciosEstabilizado = true;
    log("SALUD", "Arranque estable confirmado; contador de reinicios limpiado");
  }
}

// ============================================================================
// SECCIÓN 13: SETUP
// ============================================================================
bool inicializarWatchdog() {
  esp_task_wdt_config_t configWdt = {
    .timeout_ms = WATCHDOG_TIMEOUT_S * 1000,
    .idle_core_mask = 0,
    .trigger_panic = true
  };
  esp_err_t resultado = esp_task_wdt_init(&configWdt);
  if (resultado == ESP_ERR_INVALID_STATE) {
    resultado = esp_task_wdt_reconfigure(&configWdt);
  }
  if (resultado != ESP_OK) return false;
  if (esp_task_wdt_status(NULL) != ESP_OK && esp_task_wdt_add(NULL) != ESP_OK) return false;
  return esp_task_wdt_reset() == ESP_OK;
}

void setup() {
  Serial.begin(115200);
  delay(300);
  log("SISTEMA", "=== PROJECT DOMUS v6 offline - Iniciando ===");

  const esp_reset_reason_t motivoReinicio = esp_reset_reason();
  if (esReinicioCritico(motivoReinicio)) {
    if (reiniciosCriticosConsecutivos < 255) reiniciosCriticosConsecutivos++;
  } else {
    reiniciosCriticosConsecutivos = 0;
  }
  const bool arrancarEnModoSeguro = reiniciosCriticosConsecutivos >= 3;

  // Reserva una sola vez el búfer de entrada para evitar realocaciones y
  // fragmentación del heap durante una sesión larga de diagnóstico.
  bufferComandoSerial.reserve(41);

  pinMode(MAPA_CASA.paro, INPUT_PULLUP);
  pinMode(MAPA_CASA.micOff, INPUT_PULLUP);
  pinMode(MAPA_CASA.demo, INPUT_PULLUP);
  micHabilitado = digitalRead(MAPA_CASA.micOff) != LOW;

  for (int i = 0; i < TOTAL_SALIDAS; i++) {
    // Precarga el nivel inactivo antes de habilitar la salida para reducir
    // pulsos breves durante el arranque en módulos activos en LOW.
    // Arranque OFF: las salidas sin etapa quedan en INPUT (nota 53/54).
    digitalWrite(MAPA_CASA.salidas[i], nivelSalida(i, false));
    pinMode(MAPA_CASA.salidas[i], SALIDA_FISICA_CASA[i] ? OUTPUT : INPUT);
    propietarioSalidas[i] = PROPIETARIO_NINGUNO;
  }
  log("SISTEMA", "Salidas inicializadas (todas apagadas)");
  watchdogActivo = inicializarWatchdog();
  if (!watchdogActivo) entrarModoSeguro("watchdog_no_disponible");
  else log("SISTEMA", "Watchdog verificado: " + String(WATCHDOG_TIMEOUT_S) + "s");
  cargarCalibracion();

  if (arrancarEnModoSeguro) {
    entrarModoSeguro("reinicios_criticos_consecutivos");
  }

  detectarPantalla();
  mostrarBienvenida();

  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  pinMode(MAPA_CASA.pir, INPUT);
  inicializarMicroSD();

  dht.begin();
  log("SISTEMA", "DHT11 inicializado (temperatura/humedad ambiental)");

  if (MP3_HABILITADO) {
    SerialMP3.begin(9600, SERIAL_8N1, MP3_RX_PIN, MP3_TX_PIN);
    delay(500);
    log("MP3", "UART iniciado para módulo reproductor");
  }

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
  if (watchdogActivo && esp_task_wdt_reset() != ESP_OK) {
    watchdogActivo = false;
    entrarModoSeguro("watchdog_reset_fallo");
  }

  // 1. Seguridad y controles físicos tienen prioridad máxima.
  revisarControlesFisicos();
  supervisarSalud();

  // 2. Voz local: nunca escucha con MIC OFF o emergencia activa.
  #if JARVIS_LOCAL_HABILITADO
    if (micHabilitado && !paroEmergenciaActivo && !modoSeguroActivo) revisarVoz();
  #endif

  // 3. Diagnóstico/control local por USB, sin red ni aplicación móvil.
  revisarComandosSerial();

  // 4. Automatización local. En modo seguro queda suspendida para no generar
  // intentos repetidos de encendido ni más presión sobre memoria/registros.
  if (!modoSeguroActivo) {
    verificarRiegoAutomatico();
    verificarVentiladorAutomatico();
    verificarLucesAutomaticas();
  }

  // Corte independiente: se mantiene aun si el supervisor está degradado.
  verificarLimiteBomba();

  // 5. Pantalla: se refresca solo cada INTERVALO_PANTALLA_MS.
  if (millis() - ultimaActualizacionPantalla > INTERVALO_PANTALLA_MS) {
    unsigned long idxUltimo = (indiceErrorActual - 1 + MAX_ERRORES_GUARDADOS) % MAX_ERRORES_GUARDADOS;
    bool hayErrorReciente = bufferErrores[idxUltimo].ocupado &&
                             (millis() - bufferErrores[idxUltimo].momentoMs) < DURACION_PANTALLA_ERROR_MS;

    if (hayErrorReciente) {
      mostrarPantallaError();
    } else {
      int humedadCrudo = 0, humedadPct = 0, nivelAgua = 0, ldrCrudo = 0, luzPct = 0;
      float tempC = 0, humAire = 0;
      bool humedadValida = leerHumedad(humedadCrudo, humedadPct);
      bool nivelValido = leerNivelAgua(nivelAgua);
      leerLuz(ldrCrudo, luzPct);
      bool tempValida = leerAmbiente(tempC, humAire);
      actualizarPantallaEstado(humedadPct, nivelAgua, humedadValida, nivelValido, tempC, tempValida);
    }
    ultimaActualizacionPantalla = millis();
  }
}
