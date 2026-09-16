"""Pruebas de la pantalla final LCD1602 I2C (rama task/lcd-final).

Verifica el header real domus_pantalla.h compilandolo con g++ mediante
fakes minimos de Arduino/LiquidCrystal_I2C (patron del repo: sin
compilador se reporta skipTest explicito) y revisa por texto que el
header no use pausas bloqueantes y que el borrado total este acotado.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from test_native_firmware import run_host_process


ROOT = Path(__file__).resolve().parents[2]
SKETCH_DIR = ROOT / "firmware" / "casa_inteligente_v4"
HEADER = SKETCH_DIR / "domus_pantalla.h"
SKETCH = SKETCH_DIR / "casa_inteligente_v4.ino"

FAKE_ARDUINO_H = """\
#pragma once
#include <stdint.h>
#include <cstdio>
#include <cstring>
#include <cmath>
unsigned long millis();
"""

FAKE_LCD_H = """\
#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>
class LiquidCrystal_I2C {
 public:
  LiquidCrystal_I2C(uint8_t d, uint8_t c, uint8_t f)
      : direccion(d), columnas(c), filas(f), cursorC(0), cursorR(0),
        escrituras(0), iconos(0) {
    limpiarCeldas();
  }
  void init() {}
  void backlight() {}
  void clear() {
    ++barridos;
    limpiarCeldas();
    cursorC = 0;
    cursorR = 0;
  }
  void setCursor(uint8_t c, uint8_t r) {
    ++movimientosCursor;
    cursorC = c;
    cursorR = r;
  }
  size_t print(char ch) {
    ++escrituras;
    if (cursorR < 2 && cursorC < 16) celdas[cursorR][cursorC] = ch;
    ++cursorC;
    return 1;
  }
  void createChar(uint8_t, uint8_t[]) { ++iconos; }
  static int barridos;
  static int movimientosCursor;
  int escrituras;
  int iconos;
  char celdas[2][16];

 private:
  void limpiarCeldas() {
    for (int f = 0; f < 2; ++f)
      for (int c = 0; c < 16; ++c) celdas[f][c] = ' ';
  }
  uint8_t direccion, columnas, filas, cursorC, cursorR;
};
int LiquidCrystal_I2C::barridos = 0;
int LiquidCrystal_I2C::movimientosCursor = 0;
"""

HARNESS_CPP = """\
#include <cstdio>
#include <cstring>
#include "domus_pantalla.h"

static unsigned long g_ahora = 0;
unsigned long millis() { return g_ahora; }

static int fallos = 0;
#define CHEQUEA(cond) \\
  do { \\
    if (!(cond)) { ++fallos; std::printf("FALLO:%d\\n", __LINE__); } \\
  } while (0)

static DatosPantallaFinal datosBase() {
  DatosPantallaFinal d;
  d.tempC = 25.0f; d.tempValida = true;
  d.humAire = 60.0f; d.humAireValida = true;
  d.sueloPct = 45; d.sueloValido = true;
  d.nivelRaw = 1500; d.nivelPct = 47; d.nivelValido = true; d.nivelMin = 600;
  d.luzPct = 70; d.luzValida = true;
  d.presencia = true;
  for (int i = 0; i < 5; ++i) d.salidas[i] = SAL_OFF;
  d.emergencia = false; d.modoSeguro = false; d.error = "";
  d.escuchando = false; d.micOn = true;
  return d;
}

int main() {
  {
    int base = fallos;
    PantallaFinal p;
    p.begin(nullptr);
    DatosPantallaFinal d = datosBase();
    char l0[17], l1[17];
    for (uint8_t v = 0; v < 5; ++v) {
      p.formatear(v, d, l0, l1);
      CHEQUEA(std::strlen(l0) == 16 && std::strlen(l1) == 16);
    }
    p.formatear(2, d, l0, l1);
    CHEQUEA(l1[12] == ' ' && l1[15] == ' ');
    char largo[41];
    for (int i = 0; i < 40; ++i) largo[i] = (char)('A' + (i % 26));
    largo[40] = '\\0';
    d.error = largo;
    p.formatear(4, d, l0, l1);
    CHEQUEA(std::strlen(l1) == 16 && std::memcmp(l1, largo, 16) == 0);
    for (int i = 0; i < 5; ++i) d.salidas[i] = SAL_AUTO;
    d.error = "";
    p.formatear(3, d, l0, l1);
    CHEQUEA(std::strlen(l0) == 16 && std::strlen(l1) == 16);
    if (fallos == base) std::puts("FMT_OK");
  }
  {
    int base = fallos;
    PantallaFinal p;
    p.begin(nullptr);
    DatosPantallaFinal d = datosBase();
    p.irA(1);
    d.emergencia = true;
    CHEQUEA(p.efectiva(d) == 4);
    d.emergencia = false;
    d.modoSeguro = true;
    CHEQUEA(p.efectiva(d) == 4);
    d.modoSeguro = false;
    d.error = "FALLO X";
    CHEQUEA(p.efectiva(d) == 4);
    d.error = "";
    p.irA(2);
    CHEQUEA(p.efectiva(d) == 2);
    g_ahora = 5000;
    d.emergencia = true;
    p.tick(d);
    CHEQUEA(std::strstr(p.linea(0), "EMERGENCIA") != nullptr);
    if (fallos == base) std::puts("PRIO_OK");
  }
  {
    int base = fallos;
    PantallaFinal p;
    p.begin(nullptr);
    DatosPantallaFinal d = datosBase();
    d.tempValida = false;
    d.humAireValida = false;
    d.sueloValido = false;
    d.nivelValido = false;
    d.luzValida = false;
    char l0[17], l1[17];
    p.formatear(0, d, l0, l1);
    CHEQUEA(std::strstr(l0, "ERR") && std::strstr(l1, "ERR"));
    p.formatear(1, d, l0, l1);
    CHEQUEA(std::strstr(l0, "ERR") && std::strstr(l1, "ERR"));
    p.formatear(2, d, l0, l1);
    CHEQUEA(std::strstr(l0, "ERR") != nullptr);
    d = datosBase();
    p.formatear(0, d, l0, l1);
    CHEQUEA(std::strstr(l0, "25") && !std::strstr(l0, "ERR"));
    p.formatear(1, d, l0, l1);
    CHEQUEA(std::strstr(l0, "45") && !std::strstr(l0, "ERR"));
    CHEQUEA(std::strstr(l1, "47%") && !std::strstr(l1, "1500"));
    if (fallos == base) std::puts("ERR_OK");
  }
  {
    int base = fallos;
    LiquidCrystal_I2C lcd(0x27, 16, 2);
    PantallaFinal p;
    g_ahora = 0;
    LiquidCrystal_I2C::barridos = 0;
    LiquidCrystal_I2C::movimientosCursor = 0;
    p.begin(&lcd);
    CHEQUEA(LiquidCrystal_I2C::barridos == 1);
    DatosPantallaFinal d = datosBase();
    p.tick(d);
    CHEQUEA(std::strstr(p.linea(0), "PROJECT DOMUS") != nullptr);
    CHEQUEA(LiquidCrystal_I2C::barridos == 1);
    g_ahora = 5000;
    p.tick(d);
    CHEQUEA(LiquidCrystal_I2C::barridos == 1);
    int movs = LiquidCrystal_I2C::movimientosCursor;
    p.tick(d);
    CHEQUEA(LiquidCrystal_I2C::movimientosCursor == movs);
    p.siguiente();
    p.tick(d);
    CHEQUEA(p.indice() == 1);
    p.mostrarIR(7, 0x00FF, 0x0019);
    p.tick(d);
    CHEQUEA(std::strstr(p.linea(0), "P7 A00FF") != nullptr);
    CHEQUEA(std::strstr(p.linea(1), "0x0019") != nullptr);
    g_ahora = 10001;
    p.tick(d);
    CHEQUEA(std::strstr(p.linea(0), "Suelo") != nullptr);
    if (fallos == base) std::puts("TICK_OK");
  }
  return fallos == 0 ? 0 : 1;
}
"""


class PantallaFinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.header = HEADER.read_text(encoding="utf-8")
        cls.sketch = SKETCH.read_text(encoding="utf-8")

    def test_header_tiene_formato_fijo_sombra_e_iconos(self):
        self.assertIn("%-16.16s", self.header)
        self.assertIn("[2][17]", self.header)
        self.assertIn("setCursor", self.header)
        self.assertIn("createChar", self.header)
        self.assertIn("PROJECT DOMUS", self.header)
        self.assertIn("class PantallaFinal", self.header)
        self.assertIn("NUM_PANTALLAS = 5", self.header)
        self.assertIn("P_EMERGENCIA = 4", self.header)
        for estado in ("\"ON\"", "\"OFF\"", "\"AUTO\"", "\"BLOQ\"", "\"ERR\""):
            self.assertIn(estado, self.header)

    def test_header_sin_pausas_y_borrado_acotado(self):
        self.assertNotIn("delay(", self.header)
        usos = self.header.count("clear()")
        self.assertGreaterEqual(usos, 1)
        self.assertLessEqual(usos, 2)
        for linea in self.header.splitlines():
            if "clear()" in linea:
                self.assertIn("lcd_->clear();", linea)

    def test_ino_delega_dibujo_en_la_clase(self):
        for fragmento in (
            '#include "domus_pantalla.h"',
            "PantallaFinal pantallaFinal;",
            "pantallaFinal.begin(lcd);",
            "pantallaFinal.tick(d);",
            "pantallaFinal.siguiente();",
            "refrescarPantallaFinal();",
            "clasificarSalidaFinal",
            "escanearBusI2C",
            "INTERVALO_PANTALLA_MS",
            "ultimoCambioBotonDemoMs",
        ):
            self.assertIn(fragmento, self.sketch)
        for funcion_vieja in (
            "void mostrarBienvenida",
            "void actualizarPantallaEstado",
            "void mostrarPantallaError",
            "void mostrarEscuchando",
            "mostrarEscuchando()",
        ):
            self.assertNotIn(funcion_vieja, self.sketch)

    def test_modo_solo_navega_y_sensores_se_inicializan_antes_de_refrescar(self):
        controles = self.sketch.split("void revisarControlesFisicos()", 1)[1].split("\n}", 1)[0]
        self.assertIn("pantallaFinal.siguiente();", controles)
        self.assertIn("ACK;MODO_LCD;", controles)
        self.assertNotIn("ejecutarOrdenActuador", controles)
        self.assertNotIn("BOTON_LUZ_SALA", controles)

        setup = self.sketch.split("void setup()", 1)[1].split("\n}", 1)[0]
        self.assertIn("pantallaFinal.begin(lcd);", setup)
        self.assertIn("analogReadResolution(12);", setup)
        self.assertIn("dht.begin();", setup)
        self.assertNotIn("refrescarPantallaFinal();", setup)

    def test_nativo_formato_prioridad_err_y_diferencial(self):
        compiler = shutil.which("g++") or shutil.which("clang++")
        if not compiler:
            self.skipTest("No host C++ compiler; native LCD checks run on Ubuntu CI")
        with tempfile.TemporaryDirectory(prefix="domus-pantalla-") as directory:
            include = Path(directory) / "include"
            include.mkdir()
            (include / "Arduino.h").write_text(FAKE_ARDUINO_H, encoding="utf-8")
            (include / "LiquidCrystal_I2C.h").write_text(FAKE_LCD_H, encoding="utf-8")
            cpp = Path(directory) / "test.cpp"
            cpp.write_text(HARNESS_CPP, encoding="utf-8")
            binary = Path(directory) / "test.exe"
            compiled = run_host_process(
                [compiler, "-std=c++17", "-Wall", "-Wextra",
                 "-I", str(include), "-I", str(SKETCH_DIR),
                 str(cpp), "-o", str(binary)],
                timeout=60,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            result = run_host_process([str(binary)], timeout=10, allow_skip=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            salida = result.stdout.decode()
            for token in ("FMT_OK", "PRIO_OK", "ERR_OK", "TICK_OK"):
                self.assertIn(token, salida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
