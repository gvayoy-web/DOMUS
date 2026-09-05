// Hardware fakes only. Production functions are inserted by the Python runner.
#include <cassert>
#include <cstring>
#include <string>
#include <vector>
#include "domus_types.h"
#include "domus_calibration.h"
struct String : std::string {
  using std::string::string;
  String(const std::string &s):std::string(s) {}
  String(int n):std::string(std::to_string(n)) {}
  String(float n,int):std::string(std::to_string(n)) {}
};
constexpr int LOW=0,HIGH=1,CANTIDAD_RELES=5,PIN_PARO_EMERGENCIA=10;
constexpr int MAX_FALLOS_ANTES_DE_ALERTA_PERSISTENTE=3;
constexpr bool MP3_HABILITADO=false;
constexpr unsigned long TIEMPO_MAXIMO_BOMBA_MS=120000, MEMORIA_LIBRE_RECUPERACION_BYTES=65536;
enum PropietarioActuador {PROPIETARIO_NINGUNO, PROPIETARIO_MANUAL_ON,
                         PROPIETARIO_MANUAL_OFF, PROPIETARIO_AUTOMATICO};
int PINES_RELES[5]={4,5,6,7,8}, gpio[64]={};
bool estadoReles[5]={}, SALIDA_ACTIVA_EN_LOW[5]={true,true,true,true,true};
int fallosVerificacionRele[5]={};
const char *NOMBRES_RELES[5]={"bomba","sala","cuarto","ventilador","invernadero"};
PropietarioActuador propietarioReles[5]={};
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
  for(int profile=0;profile<2;profile++) {
    for(int i=0;i<5;i++) SALIDA_ACTIVA_EN_LOW[i]=(i==0 || profile==0);
    for(int i=0;i<5;i++) {
      assert(ejecutarOrdenActuador({i,true,ORIGEN_MANUAL,1,"on"}).exito);
      assert(estadoReles[i] && digitalRead(PINES_RELES[i])==nivelSalida(i,true));
    }
    activarParoEmergencia("test");
    for(int i=0;i<5;i++) {
      assert(!estadoReles[i]);
      assert(!ejecutarOrdenActuador({i,true,ORIGEN_MANUAL,1,"on"}).exito);
    }
    gpio[PIN_PARO_EMERGENCIA]=LOW; assert(!rearmarSistema());
    gpio[PIN_PARO_EMERGENCIA]=HIGH; assert(rearmarSistema());
    assert(!estadoReles[0]);
    agua=0; assert(!ejecutarOrdenActuador({0,true,ORIGEN_MANUAL,1,"pump"}).exito);
    agua=1000; sensorValido=false;
    assert(!ejecutarOrdenActuador({0,true,ORIGEN_MANUAL,1,"pump"}).exito);
    sensorValido=true;
    assert(ejecutarOrdenActuador({0,true,ORIGEN_MANUAL,1,"pump"}).exito);
    reloj+=TIEMPO_MAXIMO_BOMBA_MS; verificarLimiteBomba(); assert(!estadoReles[0]);
    assert(propietarioReles[0]==PROPIETARIO_MANUAL_OFF);
    assert(!ejecutarOrdenActuador({1,true,ORIGEN_VOZ,0.2f,"voice"}).exito);
    entrarModoSeguro("test");
    assert(!ejecutarOrdenActuador({1,true,ORIGEN_MANUAL,1,"on"}).exito);
    watchdogActivo=false; assert(!recuperarModoSeguro());
    watchdogActivo=true; heap=100; assert(!recuperarModoSeguro());
    heap=100000; assert(recuperarModoSeguro()); assert(!estadoReles[1]);
  }
  assert(!ejecutarOrdenActuador({-1,true,ORIGEN_MANUAL,1,"invalid"}).exito);
  assert(!ejecutarOrdenActuador({5,true,ORIGEN_MANUAL,1,"invalid"}).exito);
}
