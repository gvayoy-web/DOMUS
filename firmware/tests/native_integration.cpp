// Hardware fakes only. Production functions are inserted by the Python runner.
#include <cassert>
#include <cstring>
#include <string>
#include <vector>
#include "domus_types.h"
#include "domus_calibration.h"
#include "domus_voice_contract.h"
#include <limits>
struct String : std::string {
  using std::string::string;
  String(const std::string &s):std::string(s) {}
  String(int n):std::string(std::to_string(n)) {}
  String(float n,int):std::string(std::to_string(n)) {}
};
constexpr int LOW=0,HIGH=1,TOTAL_SALIDAS=5,PIN_PARO_EMERGENCIA=10;
constexpr int PIN_MIC_OFF=11;
bool micHabilitado=true;
constexpr int MAX_FALLOS_ANTES_DE_ALERTA_PERSISTENTE=3;
constexpr bool MP3_HABILITADO=false;
constexpr unsigned long TIEMPO_MAXIMO_BOMBA_MS=120000, MEMORIA_LIBRE_RECUPERACION_BYTES=65536;
enum PropietarioActuador {PROPIETARIO_NINGUNO, PROPIETARIO_MANUAL_ON,
                         PROPIETARIO_MANUAL_OFF, PROPIETARIO_AUTOMATICO};
int PINES_SALIDAS[5]={4,5,6,7,8}, gpio[64]={};
bool estadoSalidas[5]={}, SALIDA_ACTIVA_EN_BAJO[5]={true,true,true,true,true};
int fallosVerificacionSalida[5]={};
const char *NOMBRES_SALIDAS[5]={"bomba","sala","cuarto","ventilador","invernadero"};
PropietarioActuador propietarioSalidas[5]={};
// Fakes de perfil (nota 54): máscara con TODAS las etapas + driver validado,
// para probar la lógica de despacho/seguridad/timeout con actuadores presentes.
// El rechazo sin etapa y sin driver lo cubren test_casa_candidato.py, el
// contrato de compilación y la matriz (all-false/all-disabled reales).
constexpr bool SALIDA_FISICA_CASA[5]={true,true,true,true,true};
inline bool driverMotoresListo() { return true; }
bool paroEmergenciaActivo=false, modoSeguroActivo=false, watchdogActivo=true, ventanaEscuchaActiva=false;
char motivoModoSeguro[48]="ninguno";
unsigned long bombaEncendidaDesdeMs=0, reloj=1000, heap=100000;
int agua=1000; bool sensorValido=true;
CalibracionDomus calibracion={1,2800,1200,3200,400,600,0};
std::vector<String> eventos;
void emitirEventoLocal(const String &s) {eventos.push_back(s);}
void registrarError(const String&,const String&) {}
void log(const String&,const String&) {}
void reproducirPista(int) {}
void responderJarvis(const String&) {}
String construirRespuestaJarvis(const OrdenActuador&,bool,const ResultadoOrden&) {return "respuesta";}
bool leerNivelAgua(int &salida) {salida=agua;return sensorValido;}
void digitalWrite(int pin,int valor) {gpio[pin]=valor;}
int digitalRead(int pin) {return gpio[pin];}
unsigned long millis() {return reloj;}
void delay(int n) {reloj+=n;}
unsigned long esp_get_free_heap_size() {return heap;}
// ACTUAL_FUNCTIONS
int main() {
  gpio[PIN_PARO_EMERGENCIA]=HIGH;
  gpio[PIN_MIC_OFF]=HIGH;
  for(int profile=0;profile<2;profile++) {
    for(int i=0;i<5;i++) SALIDA_ACTIVA_EN_BAJO[i]=(i==0 || profile==0);
    for(int i=0;i<5;i++) {
      assert(ejecutarOrdenActuador({i,true,ORIGEN_MANUAL,1,"on"}).exito);
      assert(estadoSalidas[i] && digitalRead(PINES_SALIDAS[i])==nivelSalida(i,true));
    }
    activarParoEmergencia("test");
    for(int i=0;i<5;i++) {
      assert(!estadoSalidas[i]);
      assert(!ejecutarOrdenActuador({i,true,ORIGEN_MANUAL,1,"on"}).exito);
    }
    gpio[PIN_PARO_EMERGENCIA]=LOW; assert(!rearmarSistema());
    gpio[PIN_PARO_EMERGENCIA]=HIGH; assert(rearmarSistema());
    assert(!estadoSalidas[0]);
    agua=0; assert(!ejecutarOrdenActuador({0,true,ORIGEN_MANUAL,1,"pump"}).exito);
    agua=1000; sensorValido=false;
    assert(!ejecutarOrdenActuador({0,true,ORIGEN_MANUAL,1,"pump"}).exito);
    sensorValido=true;
    micHabilitado=false;
    assert(!ejecutarOrdenActuador({1,true,ORIGEN_VOZ,1,"mic disabled"}).exito);
    assert(ejecutarOrdenActuador({1,true,ORIGEN_MANUAL,1,"manual allowed"}).exito);
    assert(!ejecutarOrdenActuador({1,false,ORIGEN_VOZ,1,"mic disabled"}).exito);
    assert(estadoSalidas[1]);
    micHabilitado=true; gpio[PIN_MIC_OFF]=LOW;
    assert(!ejecutarOrdenActuador({1,false,ORIGEN_VOZ,1,"physical mic off"}).exito);
    gpio[PIN_MIC_OFF]=HIGH;
    assert(ejecutarOrdenActuador({1,false,ORIGEN_VOZ,1,"voice enabled"}).exito);
    assert(ejecutarOrdenActuador({0,true,ORIGEN_MANUAL,1,"pump"}).exito);
    reloj+=TIEMPO_MAXIMO_BOMBA_MS; verificarLimiteBomba(); assert(!estadoSalidas[0]);
    assert(propietarioSalidas[0]==PROPIETARIO_MANUAL_OFF);
    assert(!ejecutarOrdenActuador({1,true,ORIGEN_VOZ,0.2f,"voice"}).exito);
    for (float bad : {std::numeric_limits<float>::quiet_NaN(),
                      std::numeric_limits<float>::infinity(), -1.0f, 1.01f})
      assert(!ejecutarOrdenActuador({1,true,ORIGEN_VOZ,bad,"invalid confidence"}).exito);
    entrarModoSeguro("test");
    assert(!ejecutarOrdenActuador({1,true,ORIGEN_MANUAL,1,"on"}).exito);
    watchdogActivo=false; assert(!recuperarModoSeguro());
    watchdogActivo=true; heap=100; assert(!recuperarModoSeguro());
    heap=100000; assert(recuperarModoSeguro()); assert(!estadoSalidas[1]);
  }
  assert(!ejecutarOrdenActuador({-1,true,ORIGEN_MANUAL,1,"invalid"}).exito);
  assert(!ejecutarOrdenActuador({5,true,ORIGEN_MANUAL,1,"invalid"}).exito);
}
