import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from test_native_firmware import SKETCH, function


class SafetyIntegrationTests(unittest.TestCase):
    def run_cpp(self, code):
        compiler = shutil.which("g++") or shutil.which("clang++")
        if not compiler:
            self.skipTest("Host C++ compiler required; runs in Ubuntu CI")
        with tempfile.TemporaryDirectory(prefix="domus-safety-") as directory:
            source = Path(directory) / "test.cpp"
            binary = Path(directory) / "test.exe"
            source.write_text(code, encoding="utf-8")
            result = subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", "-I", str(SKETCH.parent),
                                     str(source), "-o", str(binary)], capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_dispatch_outputs_emergency_recovery_and_timeout_together(self):
        source = SKETCH.read_text(encoding="utf-8")
        signatures = ["int nivelSalida(int indice, bool encendida)",
            "bool verificarEstadoLogicoGpio(int indice, bool estadoEsperado)",
            "bool encenderRele(int indice, bool anunciarPorVoz = true)",
            "bool apagarRele(int indice, bool anunciarPorVoz = true)",
            "ResultadoOrden ejecutarOrdenActuador(const OrdenActuador &orden)",
            "void verificarLimiteBomba()", "void activarParoEmergencia(const char* motivo)",
            "void entrarModoSeguro(const char* motivo)", "bool recuperarModoSeguro()", "bool rearmarSistema()"]
        template = Path(__file__).with_name("native_integration.cpp").read_text(encoding="utf-8")
        self.run_cpp(template.replace("// ACTUAL_FUNCTIONS", "\n".join(function(source, s) for s in signatures)))

    def test_watchdog_failure_paths_and_calibration_integrity(self):
        source = SKETCH.read_text(encoding="utf-8")
        code = r'''
#include <cassert>
#include <cstddef>
#include "domus_calibration.h"
constexpr int ESP_OK=0, ESP_ERR_INVALID_STATE=1, WATCHDOG_TIMEOUT_S=8;
using esp_err_t=int;
struct esp_task_wdt_config_t {int timeout_ms; int idle_core_mask; bool trigger_panic;};
int init=0, reconfig=0, status=0, add=0, reset=0;
esp_err_t esp_task_wdt_init(esp_task_wdt_config_t *c) {assert(c->timeout_ms==8000);return init;}
esp_err_t esp_task_wdt_reconfigure(esp_task_wdt_config_t*) {return reconfig;}
esp_err_t esp_task_wdt_status(void*) {return status;}
esp_err_t esp_task_wdt_add(void*) {return add;}
esp_err_t esp_task_wdt_reset() {return reset;}
'''
        code += function(source, "bool inicializarWatchdog()")
        code += r'''
int main() {
  assert(inicializarWatchdog()); init=1; assert(inicializarWatchdog());
  reconfig=2; assert(!inicializarWatchdog()); reconfig=0;
  status=2; add=2; assert(!inicializarWatchdog()); add=0; assert(inicializarWatchdog());
  reset=2; assert(!inicializarWatchdog()); reset=0; init=2; assert(!inicializarWatchdog());
  CalibracionDomus c={1,2800,1200,3200,400,600,0}; assert(calibracionValida(c));
  c.checksum=checksumCalibracion(c); c.nivelMinimo++;
  assert(c.checksum!=checksumCalibracion(c));
  c.sueloSeco=c.sueloHumedo; assert(!calibracionValida(c));
  c.sueloSeco=0; assert(!calibracionValida(c));
  c.sueloSeco=3000; c.luzClara=4095; assert(!calibracionValida(c));
  c.luzClara=400; c.version=99; assert(!calibracionValida(c));
}
'''
        self.run_cpp(code)

    def test_i2c_scan_is_bounded_when_bus_is_stuck(self):
        source = SKETCH.read_text(encoding="utf-8")
        code = r'''
#include <cassert>
#include <cstdint>
#include <string>
constexpr int HEX=16;
constexpr uint8_t DIR_LCD_1=0x27,DIR_LCD_2=0x3f;
struct String:std::string {
  using std::string::string;
  String(uint8_t n,int):std::string(std::to_string(n)) {}
};
void log(const char*,const std::string&) {}
struct Bus {
  int calls=0; uint8_t current=0; int responding=-1;
  void beginTransmission(uint8_t addr) {current=addr;}
  int endTransmission() {calls++;return current==responding?0:5;}
} Wire;
'''
        code += function(source, "bool escanearBusI2C(bool &hayLcd, uint8_t &dirLcd)")
        code += r'''
int main() {
  bool found=true; uint8_t address=0;
  assert(!escanearBusI2C(found,address)); assert(!found && Wire.calls==2);
  Wire.calls=0; Wire.responding=0x27;
  assert(escanearBusI2C(found,address)); assert(found && address==0x27 && Wire.calls==2);
  Wire.calls=0; Wire.responding=0x3f;
  assert(escanearBusI2C(found,address)); assert(found && address==0x3f && Wire.calls==2);
}
'''
        self.run_cpp(code)
