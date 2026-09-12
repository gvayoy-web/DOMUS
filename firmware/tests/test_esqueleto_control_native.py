"""Ejecuta el header real domus_control.h en compilador host (nota 53/P2).

A diferencia de test_esqueleto_sim.py (espejo Python), aquí se compilan y
ejecutan las funciones constexpr auténticas: decidirRiego/Ventilador/LuzSala/
Invernadero, porcentajeCalibrado, adcValido, calibracionValida y checksum.
Sin g++ (Windows local) reporta SKIP explícito; corre en CI Ubuntu.
"""
import shutil
import tempfile
import unittest
from pathlib import Path
from test_native_firmware import run_host_process


BASE = Path(__file__).resolve().parents[1] / "domus_esqueleto"


class EsqueletoControlNativeTests(unittest.TestCase):
    def test_control_header_compiles_and_behaves(self):
        compiler = shutil.which("g++") or shutil.which("clang++")
        if not compiler:
            self.skipTest("No host C++ compiler; native control runs on Ubuntu CI")
        code = r'''
#include <cassert>
#include <cstdint>
#include <cstdio>
#include "domus_control.h"
int main() {
  static_assert(porcentajeCalibrado(2000, 3000, 1000) == 50, "invertida");
  static_assert(decidirRiego(35, false) == DecisionAuto::ENCENDER, "riego seco");
  static_assert(decidirRiego(45, true) == DecisionAuto::APAGAR, "riego humedo");
  // Histéresis en tiempo de ejecución (ambos lados de cada banda).
  assert(decidirRiego(30, false) == DecisionAuto::ENCENDER);
  assert(decidirRiego(36, false) == DecisionAuto::NADA);
  assert(decidirRiego(40, true) == DecisionAuto::NADA);
  assert(decidirRiego(50, true) == DecisionAuto::APAGAR);
  assert(decidirVentilador(28.0f, false) == DecisionAuto::ENCENDER);
  assert(decidirVentilador(27.0f, false) == DecisionAuto::NADA);
  assert(decidirVentilador(26.0f, true) == DecisionAuto::APAGAR);
  assert(decidirLuzSala(20, true, false) == DecisionAuto::ENCENDER);
  assert(decidirLuzSala(20, false, false) == DecisionAuto::NADA);
  assert(decidirLuzSala(50, true, true) == DecisionAuto::APAGAR);
  assert(decidirLuzSala(20, false, true) == DecisionAuto::APAGAR);
  assert(decidirInvernadero(20, false) == DecisionAuto::ENCENDER);
  assert(decidirInvernadero(30, false) == DecisionAuto::NADA);
  assert(decidirInvernadero(45, true) == DecisionAuto::APAGAR);
  assert(porcentajeCalibrado(1000, 3000, 1000) == 100);
  assert(porcentajeCalibrado(3000, 3000, 1000) == 0);
  assert(porcentajeCalibrado(2000, 2000, 2000) == 0);
  assert(adcValido(2000) && !adcValido(0) && !adcValido(4095));
  Calibracion c{};
  c.sueloSeco = 2800; c.sueloHumedo = 1200;
  c.luzOscura = 300; c.luzClara = 3000; c.nivelMinimo = 600;
  assert(calibracionValida(c));
  c.checksum = checksumCalibracion(c);
  c.nivelMinimo++;
  assert(c.checksum != checksumCalibracion(c));
  c.nivelMinimo = 600; c.sueloSeco = 0;
  assert(!calibracionValida(c));
  std::puts("ESQUELETO_CONTROL_NATIVO_OK");
  return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix="domus-esq-native-") as directory:
            source = Path(directory) / "test.cpp"
            binary = Path(directory) / "test.exe"
            source.write_text(code, encoding="utf-8")
            result = run_host_process([compiler, "-std=c++17", "-Wall", "-Wextra",
                                       "-I", str(BASE), str(source), "-o", str(binary)], timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = run_host_process([str(binary)], timeout=10, allow_skip=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
