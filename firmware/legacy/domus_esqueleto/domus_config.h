#pragma once
#include <stdint.h>

// PROJECT DOMUS v3 — banco alfa por un solo costado, sin IR.
// Placa: ESP32-S3 N16R8. Alimentación banco: USB / fuente regulada.
// Alimentación final (cuando llegue): extensión 120 V AC -> cargador USB ESP32
// + fuente cerrada 5 V/5 A -> portafusible 4 A lento -> switch 5 A DC -> bus 5 V.
// El 120 V NUNCA entra a la maqueta ni a la protoboard.
//
// Perfil actual:
// - Solo usa el costado físicamente accesible de la protoboard.
// - IR y controlador doble quedan fuera hasta identificarlos y congelar el mapa final.
// - Sala, cuarto e iluminación de cultivo son LED; motores bloqueados por defecto.
namespace Config {
// ÚNICA selección del perfil de motores (notas 49/50). Todo lo demás deriva.
// ALFA_SENSORES: GPIO4 y GPIO7 bloqueados (banco normal).
// ALFA_BOMBA_1: solo GPIO4. ALFA_VENTILADOR_1: solo GPIO7.
// Para una prueba vigilada se cambia SOLO esta línea; nunca ambas cargas.
enum class PerfilHardware : uint8_t { ALFA_SENSORES, ALFA_BOMBA_1, ALFA_VENTILADOR_1 };
// ÚNICA selección del perfil de motores (notas 49/50). Todo lo demás deriva.
// 0 = ALFA_SENSORES (GPIO4 y GPIO7 bloqueados, banco normal).
// 1 = ALFA_BOMBA_1 (solo GPIO4). 2 = ALFA_VENTILADOR_1 (solo GPIO7).
// Se cambia editando aquí o con bandera de compilación -DDOMUS_PERFIL_ALFA=N.
// CI construye los tres valores válidos; otro valor falla en compilación.
#ifndef DOMUS_PERFIL_ALFA
#define DOMUS_PERFIL_ALFA 0
#endif
static_assert(DOMUS_PERFIL_ALFA >= 0 && DOMUS_PERFIL_ALFA <= 2,
              "DOMUS_PERFIL_ALFA debe ser 0, 1 o 2");
constexpr PerfilHardware PERFIL_HARDWARE =
    DOMUS_PERFIL_ALFA == 1 ? PerfilHardware::ALFA_BOMBA_1 :
    DOMUS_PERFIL_ALFA == 2 ? PerfilHardware::ALFA_VENTILADOR_1 :
                             PerfilHardware::ALFA_SENSORES;
constexpr bool HABILITAR_MOTOR_BOMBA = (PERFIL_HARDWARE == PerfilHardware::ALFA_BOMBA_1);
constexpr bool HABILITAR_MOTOR_VENTILADOR = (PERFIL_HARDWARE == PerfilHardware::ALFA_VENTILADOR_1);
constexpr bool CONTROLADOR_DOBLE_IDENTIFICADO = false;
// Banderas seleccionables por compilación (0/1). Los valores por defecto son
// el banco alfa seguro; cualquier combinación que comparta GPIO falla en
// compilación por los static_assert de la matriz (nota 50).
#ifndef DOMUS_IR
#define DOMUS_IR 0
#endif
#ifndef DOMUS_DF
#define DOMUS_DF 0
#endif
#ifndef DOMUS_BUZZER
#define DOMUS_BUZZER 0
#endif
constexpr bool IR_HABILITADO = (DOMUS_IR != 0);
constexpr bool DFPLAYER_HABILITADO = (DOMUS_DF != 0);  // true solo con DFPlayer + microSD cableados.
// Buzzer: deshabilitado en alfa. GPIO12 queda RESERVADO, SIN CONECTAR.
// No configurar ni escribir GPIO12 mientras siga en false (ver domus_voice.h).
// Se habilita solo con -DDOMUS_BUZZER=1 y sin IR (comparten GPIO12).
constexpr bool BUZZER_HABILITADO = (DOMUS_BUZZER != 0);
constexpr const char PERFIL_PLACA[] = "ESP32-S3-N16R8";
// Nombre diagnosticado: deriva del perfil REALMENTE seleccionado, no es fijo.
// DIAGNOSTICO/BANCO/DOMUS_LISTO reportan este valor (nota 50).
constexpr const char* nombrePerfil(PerfilHardware p) {
  return p == PerfilHardware::ALFA_BOMBA_1 ? "ALFA_BOMBA_1" :
         p == PerfilHardware::ALFA_VENTILADOR_1 ? "ALFA_VENTILADOR_1" :
         "ALFA_UN_COSTADO_SIN_IR";
}
constexpr const char* PERFIL_PRUEBA = nombrePerfil(PERFIL_HARDWARE);
constexpr bool LCD_HABILITADO = true;
constexpr bool DHT_HABILITADO = true;
constexpr uint8_t DHT_TIPO = 11; // Cambiar a 22 solo tras identificar el modulo.
constexpr uint32_t BOMBA_MAX_MS = 10000; // banco 10 s. Final 120000.
constexpr uint32_t SENSOR_INTERVALO_MS = 1000;
constexpr uint32_t DHT_INTERVALO_MS = 2200;
constexpr uint32_t LCD_INTERVALO_MS = 250; // UI fluida; el repintado real se limita.
constexpr uint32_t PIR_RETENCION_MS = 30000;
constexpr uint32_t WATCHDOG_TIMEOUT_MS = 5000;
constexpr uint32_t HEAP_CRITICO_BYTES = 24000;
// Sensores / entradas
constexpr uint8_t PIN_SUELO = 15, PIN_NIVEL = 16, PIN_LUZ = 3;
constexpr uint8_t PIN_PIR = 9, PIN_PARO = 10, PIN_SILENCIO = 11, PIN_BOTON = 18;
constexpr uint8_t PIN_DHT = 14, PIN_LCD_SDA = 17, PIN_LCD_SCL = 13;
// Salidas lógicas 5 cargas: 0 bomba, 1 sala, 2 cuarto, 3 ventilador, 4 invernadero.
constexpr uint8_t PINES[] = {4, 5, 6, 7, 8};
// Buzzer pasivo temporal en GPIO12. SOLO activo si BUZZER_HABILITADO.
// En ALFA_UN_COSTADO_SIN_IR permanece deshabilitado: GPIO12 reservado, sin conectar.
constexpr uint8_t PIN_BUZZER = 12;
// IR receptor (VS1838B/TSOP1838/HX1838 en placa): S/OUT a este pin.
// FINAL-ONLY: no pertenece al perfil alfa. Solo se valida si IR_HABILITADO.
constexpr uint8_t PIN_IR = 12;
// DFPlayer Mini Serial1 (opcional). ESP_RX <- DF_TX, ESP_TX -> DF_RX (con 1 k).
// FINAL-ONLY: no pertenece al perfil alfa. Solo se valida si DFPLAYER_HABILITADO.
constexpr uint8_t PIN_DF_RX = 18, PIN_DF_TX = 17;
constexpr uint32_t DF_BAUDIOS = 9600;
// Audio futuro: sin mapa asignado en este perfil para impedir duplicar GPIO.
// Habilitación física: LEDs ya (sala/cuarto/invernadero), motores solo con DRV.
constexpr bool SALIDA_FISICA_HABILITADA[] = {
  HABILITAR_MOTOR_BOMBA, true, true, HABILITAR_MOTOR_VENTILADOR, true
};
// El alfa usa LED/S8050 activos HIGH. El controlador doble sigue pendiente de identificar.
constexpr bool ACTIVA_LOW[] = {false, false, false, false, false};
// Jarvis voz (runtime, no flash): volumen DFPlayer 0-30.
constexpr uint8_t JARVIS_VOL_DEF = 20, JARVIS_VOL_MIN = 0, JARVIS_VOL_MAX = 30;
// Reservas: no cablear 19/20 (USB nativo S3).
// Validación por FUNCIONES ACTIVAS (nota 46:234): solo se comprueban los GPIO
// que el perfil realmente usa. Una combinación habilitada que comparta GPIO
// falla en compilación. Los pines FINAL-ONLY (IR/DF) no entran si están off.
constexpr uint8_t RESERVADOS[] = {3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18};
constexpr bool pinesUnicos() {
  for (unsigned i = 0; i < sizeof(RESERVADOS); ++i)
    for (unsigned j = i + 1; j < sizeof(RESERVADOS); ++j)
      if (RESERVADOS[i] == RESERVADOS[j]) return false;
  return true;
}
// Alias históricos derivados de la selección única (nota 49):
// ALFA_BOMBA_1 -> solo GPIO4; ALFA_VENTILADOR_1 -> solo GPIO7; nunca ambos.
constexpr bool PERFIL_ALFA_BOMBA_1 = (PERFIL_HARDWARE == PerfilHardware::ALFA_BOMBA_1);
constexpr bool PERFIL_ALFA_VENTILADOR_1 = (PERFIL_HARDWARE == PerfilHardware::ALFA_VENTILADOR_1);
// Matriz de compilación (nota 50): predicados parametrizados. Los casos
// prohibidos se afirman NEGADOS para probar el rechazo sin romper el build.
constexpr bool motoresExclusivos(bool bomba, bool vent) { return !(bomba && vent); }
constexpr bool alias12Ok(bool buzzer, bool ir) { return !(buzzer && ir); }  // GPIO12
constexpr bool dfSinAlias(bool df, bool botonActivo, bool lcdActivo) {
  if (!df) return true;
  if (botonActivo) return false;  // DF_RX=18 choca con BOTON
  if (lcdActivo) return false;    // DF_TX=17 choca con SDA
  return true;
}
// Lista explícita de GPIO usados por FUNCIONES ACTIVAS del perfil.
// Cada entrada se añade solo si su función está habilitada: así un pin
// FINAL-ONLY (IR/DF/buzzer) no contamina al perfil alfa aunque comparta número.
constexpr uint8_t listaActiva(uint8_t idx) {
  // Orden: 0 suelo,1 nivel,2 luz,3 pir,4 paro,5 silencio,6 boton,7 dht,8 sda,9 scl,
  // 10..14 salidas 0..4 (255 si bloqueada),15 buzzer,16 ir,17 df_rx,18 df_tx.
  return idx == 0 ? PIN_SUELO : idx == 1 ? PIN_NIVEL : idx == 2 ? PIN_LUZ :
    idx == 3 ? PIN_PIR : idx == 4 ? PIN_PARO : idx == 5 ? PIN_SILENCIO :
    idx == 6 ? PIN_BOTON : idx == 7 ? (DHT_HABILITADO ? PIN_DHT : 255) :
    idx == 8 ? (LCD_HABILITADO ? PIN_LCD_SDA : 255) :
    idx == 9 ? (LCD_HABILITADO ? PIN_LCD_SCL : 255) :
    idx == 10 ? (SALIDA_FISICA_HABILITADA[0] ? PINES[0] : 255) :
    idx == 11 ? (SALIDA_FISICA_HABILITADA[1] ? PINES[1] : 255) :
    idx == 12 ? (SALIDA_FISICA_HABILITADA[2] ? PINES[2] : 255) :
    idx == 13 ? (SALIDA_FISICA_HABILITADA[3] ? PINES[3] : 255) :
    idx == 14 ? (SALIDA_FISICA_HABILITADA[4] ? PINES[4] : 255) :
    idx == 15 ? (BUZZER_HABILITADO ? PIN_BUZZER : 255) :
    idx == 16 ? (IR_HABILITADO ? PIN_IR : 255) :
    idx == 17 ? (DFPLAYER_HABILITADO ? PIN_DF_RX : 255) :
    idx == 18 ? (DFPLAYER_HABILITADO ? PIN_DF_TX : 255) : 255;
}
constexpr bool funcionesActivasSinAlias() {
  for (uint8_t i = 0; i < 19; ++i) {
    const uint8_t a = listaActiva(i);
    if (a == 255) continue;
    for (uint8_t j = i + 1; j < 19; ++j) {
      const uint8_t b = listaActiva(j);
      if (b == 255) continue;
      if (a == b) return false;
    }
  }
  return true;
}
static_assert(pinesUnicos(), "GPIO duplicado");
static_assert(funcionesActivasSinAlias(), "Alias GPIO entre funciones HABILITADAS del perfil");
// Matriz: casos que deben compilar.
static_assert(motoresExclusivos(false, false), "ALFA_SENSORES debe compilar");
static_assert(motoresExclusivos(true, false), "ALFA_BOMBA_1 debe compilar");
static_assert(motoresExclusivos(false, true), "ALFA_VENTILADOR_1 debe compilar");
static_assert(alias12Ok(false, false) && alias12Ok(true, false) && alias12Ok(false, true),
              "Usos individuales de GPIO12 deben compilar");
static_assert(dfSinAlias(false, true, true), "DF off debe compilar con boton/LCD");
// Matriz: casos prohibidos (afirmados negados para no romper el build).
static_assert(!motoresExclusivos(true, true), "Ambas cargas deben rechazarse");
static_assert(!alias12Ok(true, true), "IR+buzzer en GPIO12 deben rechazarse");
static_assert(!dfSinAlias(true, true, true), "DF+boton/LCD en 18/17 deben rechazarse");
// Perfil real seleccionado en este build.
// IR, DFPlayer y buzzer pertenecen al futuro perfil FINAL, no al alfa:
// mientras la selección sea alfa, habilitar cualquiera de ellos es error.
// Así PERFIL_PRUEBA siempre describe el binario real (nota 50).
static_assert(DOMUS_IR == 0, "IR fuera del perfil alfa (reservado al futuro FINAL)");
static_assert(DOMUS_DF == 0, "DFPlayer fuera del perfil alfa (reservado al futuro FINAL)");
static_assert(DOMUS_BUZZER == 0, "Buzzer fuera del perfil alfa: GPIO12 reservado, sin conectar");
static_assert(motoresExclusivos(HABILITAR_MOTOR_BOMBA, HABILITAR_MOTOR_VENTILADOR),
              "El perfil alfa permite un solo motor por prueba");
static_assert(alias12Ok(BUZZER_HABILITADO, IR_HABILITADO),
              "GPIO12 compartido por funciones habilitadas");
static_assert(dfSinAlias(DFPLAYER_HABILITADO, true, LCD_HABILITADO),
              "DFPlayer comparte GPIO con boton/LCD en este perfil");
static_assert(!BUZZER_HABILITADO || PIN_BUZZER != 255, "Buzzer habilitado sin pin");
static_assert(BOMBA_MAX_MS > 0 && BOMBA_MAX_MS <= 120000, "Tiempo bomba invalido");
static_assert(DHT_TIPO == 11 || DHT_TIPO == 22, "DHT_TIPO debe ser 11 o 22");
static_assert(sizeof(PINES) == sizeof(ACTIVA_LOW), "Tabla de salidas inconsistente");
static_assert(sizeof(PINES) == sizeof(SALIDA_FISICA_HABILITADA), "Mascara fisica inconsistente");
} // namespace Config
