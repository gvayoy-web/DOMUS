"""Pruebas específicas del candidato a producto (notas 53/54, jefatura).

casa_inteligente_v4 como único candidato: perfiles claros, mapa GPIO central,
máscara física por perfil, driver/IR/audio preparados pero deshabilitados y
nombre diagnosticado sin la palabra FINAL. No toca el esqueleto (congelado).
"""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "firmware" / "casa_inteligente_v4" / "casa_inteligente_v4.ino"
DRIVERS = CANDIDATE.with_name("domus_drivers.h")


class CasaCandidatoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = CANDIDATE.read_text(encoding="utf-8")
        cls.drivers = DRIVERS.read_text(encoding="utf-8")

    def test_perfil_casa_es_seleccion_unica(self):
        self.assertIn("enum class PerfilCasa", self.source)
        for perfil in ("BANCO_SIN_ACTUADORES", "LED_SIN_MOTORES", "MOTOR_PENDIENTE_DRIVER"):
            self.assertIn(perfil, self.source)
        self.assertIn("#ifndef DOMUS_PERFIL_CASA", self.source)
        self.assertIn("DOMUS_PERFIL_CASA debe ser 0, 1 o 2", self.source)
        self.assertIn("constexpr PerfilCasa PERFIL_CASA =", self.source)

    def test_mapa_central_espeja_los_defines(self):
        self.assertIn("struct MapaPinesCasa", self.source)
        self.assertIn("constexpr MapaPinesCasa MAPA_CASA = {", self.source)
        for simbolo in (
            "PIN_HUMEDAD", "PIN_NIVEL_AGUA", "PIN_LDR",
            "PIN_SALIDA_BOMBA", "PIN_SALIDA_LUZ_SALA", "PIN_SALIDA_LUZ_CUARTO",
            "PIN_SALIDA_VENTILADOR", "PIN_SALIDA_LUZ_INVERNADERO",
            "PIN_PIR", "PIN_PARO_EMERGENCIA", "PIN_MIC_OFF", "PIN_BOTON_DEMO",
            "I2C_SCL_PIN", "PIN_DHT11", "I2C_SDA_PIN",
        ):
            self.assertIn(simbolo, self.source.split("constexpr MapaPinesCasa MAPA_CASA")[1].split("};", 1)[0])
        self.assertIn("MAPA_CASA.bomba == 4", self.source)
        self.assertIn("MAPA_CASA.sda == 21", self.source)

    def test_mascara_fisica_bloquea_sin_etapa_y_motores(self):
        self.assertIn("constexpr bool SALIDA_FISICA_CASA[TOTAL_SALIDAS]", self.source)
        self.assertIn('"salida_no_instalada"', self.source)
        self.assertIn('"driver_no_listo"', self.source)
        self.assertIn("pinMode(PINES_SALIDAS[i], SALIDA_FISICA_CASA[i] ? OUTPUT : INPUT);", self.source)

    def test_diagnostico_reporta_perfil_sin_final(self):
        self.assertIn("PERFIL_CANDIDATO=", self.source)
        for nombre in (
            '"CANDIDATO_BANCO_SIN_ACTUADORES"',
            '"CANDIDATO_LED_SIN_MOTORES"',
            '"CANDIDATO_MOTOR_PENDIENTE_DRIVER"',
        ):
            self.assertIn(nombre, self.source)
        self.assertNotIn('"FINAL"', self.source)

    def test_driver_ir_audio_preparados_pero_deshabilitados(self):
        self.assertIn("constexpr bool DRIVER_MOTORES_LISTO = false;", self.drivers)
        self.assertIn("struct OrdenMotorDriver", self.drivers)
        self.assertIn("constexpr uint8_t IR_TOTAL_TECLAS = 21;", self.drivers)
        self.assertIn("constexpr bool IR_CANDIDATO_HABILITADO = false;", self.drivers)
        self.assertIn("constexpr bool AUDIO_CANDIDATO_HABILITADO = false;", self.drivers)
        self.assertIn('#include "domus_drivers.h"', self.source)
        self.assertIn("driverMotoresListo()", self.source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
