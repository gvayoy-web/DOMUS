import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "firmware" / "domus_esqueleto"


class DomusEsqueletoContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sketch = (BASE / "domus_esqueleto.ino").read_text(encoding="utf-8")
        cls.config = (BASE / "domus_config.h").read_text(encoding="utf-8")
        cls.control = (BASE / "domus_control.h").read_text(encoding="utf-8")
        cls.protocol = (BASE / "domus_protocol.h").read_text(encoding="utf-8")

    def test_outputs_remain_disabled_until_physical_validation(self):
        self.assertRegex(self.config, r"SALIDAS_HABILITADAS\s*=\s*false")
        self.assertIn("salidas_deshabilitadas", self.sketch)

    def test_confirmed_hardware_is_integrated(self):
        for token in ("LiquidCrystal_I2C", "DHT dht", "PIN_SUELO", "PIN_NIVEL", "PIN_LUZ", "PIN_PIR"):
            self.assertIn(token, self.sketch + self.config)

    def test_safety_is_independent_of_automation(self):
        safety = self.sketch.split("void revisarSeguridad()", 1)[1].split("void revisarSalud()", 1)[0]
        self.assertIn("BOMBA_MAX_MS", safety)
        self.assertIn("PIN_PARO", safety)
        self.assertLess(self.sketch.index("revisarSeguridad();"), self.sketch.index("revisarAutomatizacion();"))

    def test_calibration_requires_stop_and_persists_with_checksum(self):
        self.assertIn("REQUIERE_PARO", self.sketch)
        self.assertIn("checksumCalibracion", self.sketch)
        self.assertIn('Preferences prefs', self.sketch)

    def test_manual_ownership_and_auto_return_exist(self):
        self.assertIn("Propietario::MANUAL_OFF", self.sketch)
        self.assertIn("Propietario::AUTO", self.sketch)
        self.assertIn('"SALA AUTO"', self.protocol)

    def test_health_recovery_never_turns_outputs_on(self):
        recovery = self.sketch.split("TipoComando::RECUPERAR", 1)[1].split("TipoComando::ESTADO", 1)[0]
        self.assertIn("apagarTodo()", recovery)
        self.assertNotIn("true)", recovery)

    def test_lcd_does_not_present_invalid_adc_as_a_percentage(self):
        display = self.sketch.split("void actualizarPantalla()", 1)[1].split(
            "void cargarCalibracion()", 1
        )[0]
        self.assertIn("sensores.sueloValido && sensores.luzValida", display)
        self.assertIn('"ERR"', display)


if __name__ == "__main__":
    unittest.main(verbosity=2)
