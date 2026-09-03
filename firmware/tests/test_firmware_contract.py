import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIRMWARE = ROOT / "firmware" / "casa_inteligente_v4" / "casa_inteligente_v4.ino"
WORKFLOW = ROOT / ".github" / "workflows" / "firmware-ci.yml"


class FirmwareContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = FIRMWARE.read_text(encoding="utf-8")
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_exactly_five_logical_relays(self):
        self.assertRegex(self.source, r"#define\s+CANTIDAD_RELES\s+5\b")
        self.assertNotRegex(self.source, r"PINES_RELES\s*\[\s*8\s*\]")

    def test_invalid_gpio22_and_fake_wind_sensor_do_not_return(self):
        self.assertNotIn("GPIO22", self.source)
        self.assertNotIn("PIN_VIENTO", self.source)
        self.assertNotIn("leerViento", self.source)

    def test_firmware_has_no_ble_or_network_dependency(self):
        self.assertNotIn("NimBLE", self.source)
        self.assertNotIn("WiFi.h", self.source)
        self.assertNotIn("NimBLE-Arduino", self.workflow)

    def test_lcd_is_the_only_display_dependency(self):
        self.assertIn("LiquidCrystal_I2C", self.source)
        self.assertNotIn("Adafruit_SSD1306", self.source)
        self.assertNotIn("PANTALLA_OLED", self.source)
        self.assertNotIn("Adafruit SSD1306", self.workflow)

    def test_pump_has_level_and_timeout_interlocks(self):
        self.assertIn("nivel_agua_bajo", self.source)
        self.assertIn("TIEMPO_MAXIMO_BOMBA_MS", self.source)
        self.assertIn("verificarLimiteBomba();", self.source)

    def test_emergency_stop_blocks_new_on_orders(self):
        self.assertIn("paroEmergenciaActivo && orden.encender", self.source)
        self.assertIn("activarParoEmergencia", self.source)
        self.assertIn("rearmarSistema", self.source)

    def test_mic_off_and_physical_backup_are_present(self):
        self.assertIn("PIN_MIC_OFF", self.source)
        self.assertIn("PIN_BOTON_DEMO", self.source)
        self.assertIn("revisarControlesFisicos();", self.source)

    def test_micro_sd_has_real_read_write_self_test(self):
        self.assertIn("SD.begin", self.source)
        self.assertIn("domus_selftest.txt", self.source)
        self.assertIn("PROJECT_DOMUS_SD_OK", self.source)

    def test_unvalidated_voice_and_sd_stay_disabled(self):
        self.assertRegex(
            self.source, r"#define\s+JARVIS_LOCAL_HABILITADO\s+false\b"
        )
        self.assertRegex(self.source, r"#define\s+MICROSD_HABILITADA\s+false\b")


if __name__ == "__main__":
    unittest.main(verbosity=2)
