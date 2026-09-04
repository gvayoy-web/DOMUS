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

    def test_automatic_controls_have_separate_hysteresis_thresholds(self):
        self.assertRegex(
            self.source, r"#define\s+UMBRAL_HUMEDAD_SECA_PCT\s+35\b"
        )
        self.assertRegex(
            self.source, r"#define\s+UMBRAL_HUMEDAD_HUMEDA_PCT\s+45\b"
        )
        self.assertIn("pct >= UMBRAL_HUMEDAD_HUMEDA_PCT", self.source)
        self.assertRegex(
            self.source, r"#define\s+UMBRAL_TEMP_ALTA_C\s+28\.0\b"
        )
        self.assertRegex(
            self.source, r"#define\s+UMBRAL_TEMP_NORMAL_C\s+26\.0\b"
        )
        self.assertIn("tempC <= UMBRAL_TEMP_NORMAL_C", self.source)

    def test_emergency_stop_blocks_new_on_orders(self):
        self.assertIn("paroEmergenciaActivo && orden.encender", self.source)
        self.assertIn("activarParoEmergencia", self.source)
        self.assertIn("rearmarSistema", self.source)

    def test_health_supervisor_degrades_without_restart_loop(self):
        self.assertIn("MEMORIA_LIBRE_CRITICA_BYTES", self.source)
        self.assertIn("entrarModoSeguro(\"memoria_critica\")", self.source)
        self.assertIn("reiniciosCriticosConsecutivos >= 3", self.source)
        self.assertIn("modoSeguroActivo && orden.encender", self.source)
        self.assertIn("RECUPERAR", self.source)
        self.assertNotIn('esp_restart();', self.source)

    def test_voice_circuit_breaker_prevents_partial_init_crashes(self):
        self.assertIn("VOZ_MAX_FALLOS_CONSECUTIVOS", self.source)
        self.assertIn("VOZ_TIEMPO_MAX_CICLO_US", self.source)
        self.assertIn("multinet == NULL || modelo_mn == NULL", self.source)
        self.assertIn("EVENTO;VOZ_SUSPENDIDA", self.source)
        self.assertIn("models == NULL", self.source)

    def test_serial_flood_is_limited_but_emergency_bypasses_limit(self):
        self.assertIn("MAX_COMANDOS_POR_SEGUNDO", self.source)
        self.assertIn('comando != "PARO" && !permitirComandoSerial()', self.source)
        self.assertIn("limite_de_frecuencia", self.source)

    def test_critical_sensor_failures_cut_automatic_outputs(self):
        self.assertIn("RIEGO_BLOQUEADO_SENSOR", self.source)
        self.assertIn("VENT_BLOQUEADO_SENSOR", self.source)
        self.assertIn("LUCES_AUTO_BLOQUEADAS_SENSOR", self.source)

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

    def test_compile_time_pin_registry_prevents_duplicates(self):
        self.assertIn("PINES_RESERVADOS_DOMUS", self.source)
        self.assertIn("constexpr bool pinesDomusSonUnicos()", self.source)
        self.assertIn(
            'static_assert(pinesDomusSonUnicos(), "Hay GPIO duplicados en el mapa DOMUS")',
            self.source,
        )

    def test_all_assigned_optional_buses_are_reserved(self):
        registry = self.source.split(
            "constexpr int PINES_RESERVADOS_DOMUS[] = {", 1
        )[1].split("};", 1)[0]
        for symbol in (
            "MIC_WS_PIN",
            "MIC_SD_PIN",
            "MIC_SCK_PIN",
            "MP3_RX_PIN",
            "MP3_TX_PIN",
            "SD_SCK_PIN",
            "SD_MISO_PIN",
            "SD_MOSI_PIN",
            "SD_CS_PIN",
        ):
            self.assertIn(symbol, registry)

    def test_safety_threshold_order_is_checked_at_compile_time(self):
        for expression in (
            "UMBRAL_HUMEDAD_SECA_PCT < UMBRAL_HUMEDAD_HUMEDA_PCT",
            "UMBRAL_LUZ_OSCURO_PCT < UMBRAL_LUZ_CLARO_PCT",
            "UMBRAL_TEMP_NORMAL_C < UMBRAL_TEMP_ALTA_C",
            "MEMORIA_LIBRE_CRITICA_BYTES < MEMORIA_LIBRE_RECUPERACION_BYTES",
        ):
            self.assertIn(f"static_assert({expression}", self.source)

    def test_relays_are_preloaded_off_before_output_mode(self):
        preload = "digitalWrite(PINES_RELES[i], RELE_ACTIVO_EN_LOW ? HIGH : LOW);"
        output = "pinMode(PINES_RELES[i], OUTPUT);"
        setup = self.source.split("void setup()", 1)[1]
        self.assertLess(setup.index(preload), setup.index(output))


if __name__ == "__main__":
    unittest.main(verbosity=2)
