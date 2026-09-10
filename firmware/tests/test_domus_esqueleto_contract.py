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
        # Motores (bomba/vent) bloqueados hasta DRV medido; LED ya validados.
        self.assertRegex(self.config, r"HABILITAR_BOMBA\s*=\s*false")
        self.assertRegex(self.config, r"USAR_DRV8833\s*=\s*false")
        self.assertRegex(self.config, r"DFPLAYER_HABILITADO\s*=\s*false")
        self.assertRegex(
            self.config,
            r"SALIDA_FISICA_HABILITADA\[\]\s*=\s*\{\s*HABILITAR_BOMBA\s*&&\s*USAR_DRV8833",
        )
        self.assertIn('PERFIL_PRUEBA[] = "BANCO_IR_LCD"', self.config)
        self.assertIn("salida_sin_etapa_habilitada", self.sketch)

    def test_only_drv_build_can_enable_motors(self):
        self.assertIn("SALIDA_FISICA_HABILITADA[salida]", self.sketch)
        self.assertIn("SALIDA_FISICA_HABILITADA[i]?OUTPUT:INPUT", self.sketch)
        self.assertIn("HABILITAR_BOMBA && USAR_DRV8833", self.config)
        self.assertIn("ACTIVA_LOW[] = {false, false, false, false, false}", self.config)

    def test_diagnostics_identify_board_and_sensor_validity(self):
        self.assertIn('PERFIL_PLACA[] = "ESP32-S3-N16R8"', self.config)
        self.assertIn("BANCO;PLACA=%s;PERFIL=%s", self.sketch)
        diagnostic = self.sketch.split("void informarEstado(bool diagnostico)", 1)[1].split(
            "void procesarLinea", 1
        )[0]
        self.assertIn("DIAGNOSTICO;PLACA=%s;PERFIL=%s;DRV=", diagnostic)
        self.assertLess(diagnostic.index("DIAGNOSTICO;PLACA="), diagnostic.index("ESTADO;PARO="))
        for flag in ("VS=%d", "VN=%d", "VL=%d", "VA=%d"):
            self.assertIn(flag, self.sketch)

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
        lcd = (BASE / "domus_lcd.h").read_text(encoding="utf-8")
        self.assertIn("CAL PENDIENTE", lcd)
        self.assertIn("DHT SIN DATOS", lcd)
        self.assertIn("sueloValido", lcd)
        self.assertIn("luzValida", lcd)
        self.assertIn("S:---", lcd)

    def test_diagnostic_bursts_are_paced_for_uart_fifo(self):
        body = self.sketch.split("void informarEstado(bool diagnostico)", 1)[1].split(
            "void alternarIR", 1
        )[0]
        # Cada línea de la ráfaga DIAGNOSTICO/ESTADO/SALUD/BANCO cede el UART.
        self.assertGreaterEqual(body.count("Serial.flush();"), 4)
        lista = self.sketch.split("TipoComando::IR_LISTA", 1)[1].split(
            "TipoComando::IR_BORRAR", 1
        )[0]
        self.assertIn("Serial.flush();", lista)

    def test_ir_remote_cannot_bypass_physical_safety(self):
        ir = (BASE / "domus_ir.h").read_text(encoding="utf-8")
        self.assertIn("IRDATA_FLAGS_IS_REPEAT", ir)
        self.assertIn("T_NINGUNA", ir)
        self.assertIn("TECLA NUEVA", self.sketch)
        safety_first = self.sketch.index("revisarSeguridad();")
        self.assertLess(safety_first, self.sketch.index("revisarIR();"))
        self.assertLess(safety_first, self.sketch.index("revisarAutomatizacion();"))
        self.assertIn("PIN_PARO", self.sketch.split("void revisarSeguridad()", 1)[1].split(
            "void revisarSalud()", 1)[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
