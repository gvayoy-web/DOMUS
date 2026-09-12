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
        # Selección única ALFA_SENSORES: motores derivados en false, sin DRV/IR/DF/buzzer.
        self.assertIn("constexpr PerfilHardware PERFIL_HARDWARE =", self.config)
        self.assertIn("PerfilHardware::ALFA_SENSORES", self.config)
        self.assertIn("HABILITAR_MOTOR_BOMBA = (PERFIL_HARDWARE == PerfilHardware::ALFA_BOMBA_1)", self.config)
        self.assertIn("HABILITAR_MOTOR_VENTILADOR = (PERFIL_HARDWARE == PerfilHardware::ALFA_VENTILADOR_1)", self.config)
        self.assertRegex(self.config, r"CONTROLADOR_DOBLE_IDENTIFICADO\s*=\s*false")
        self.assertIn("constexpr bool IR_HABILITADO = (DOMUS_IR != 0)", self.config)
        self.assertIn("constexpr bool DFPLAYER_HABILITADO = (DOMUS_DF != 0)", self.config)
        self.assertIn("constexpr bool BUZZER_HABILITADO = (DOMUS_BUZZER != 0)", self.config)
        self.assertRegex(
            self.config,
            r"SALIDA_FISICA_HABILITADA\[\]\s*=\s*\{\s*HABILITAR_MOTOR_BOMBA",
        )
        self.assertIn('PERFIL_PRUEBA = nombrePerfil(PERFIL_HARDWARE)', self.config)
        self.assertIn('"ALFA_UN_COSTADO_SIN_IR"', self.config)
        self.assertIn("DOMUS_PERFIL_ALFA", self.config)
        self.assertIn("nombrePerfil(PerfilHardware p)", self.config)
        self.assertIn("salida_sin_etapa_habilitada", self.sketch)

    def test_perfil_hardware_es_seleccion_unica(self):
        self.assertIn("enum class PerfilHardware", self.config)
        self.assertIn("ALFA_SENSORES", self.config)
        self.assertIn("ALFA_BOMBA_1", self.config)
        self.assertIn("ALFA_VENTILADOR_1", self.config)
        # Selección por bandera con valor por defecto seguro.
        self.assertIn("#ifndef DOMUS_PERFIL_ALFA", self.config)
        self.assertIn("DOMUS_PERFIL_ALFA debe ser 0, 1 o 2", self.config)
        # Derivación única: habilitar un motor exige seleccionar su perfil.
        self.assertIn("PERFIL_ALFA_BOMBA_1 = (PERFIL_HARDWARE == PerfilHardware::ALFA_BOMBA_1)", self.config)
        self.assertIn("PERFIL_ALFA_VENTILADOR_1 = (PERFIL_HARDWARE == PerfilHardware::ALFA_VENTILADOR_1)", self.config)
        # El nombre diagnosticado deriva del perfil real, no es fijo.
        self.assertIn("PERFIL_PRUEBA = nombrePerfil(PERFIL_HARDWARE)", self.config)

    def test_matriz_compilacion_casos_pasan_y_prohibidos(self):
        for predicate in ("motoresExclusivos", "alias12Ok", "dfSinAlias"):
            self.assertIn(f"constexpr bool {predicate}(", self.config)
        # Casos que deben compilar.
        self.assertIn("motoresExclusivos(false, false)", self.config)
        self.assertIn("motoresExclusivos(true, false)", self.config)
        self.assertIn("motoresExclusivos(false, true)", self.config)
        # Casos prohibidos afirmados negados.
        self.assertIn("!motoresExclusivos(true, true)", self.config)
        self.assertIn("!alias12Ok(true, true)", self.config)
        self.assertIn("!dfSinAlias(true, true, true)", self.config)
        # Perfil real del build pasa la matriz.
        self.assertIn("motoresExclusivos(HABILITAR_MOTOR_BOMBA, HABILITAR_MOTOR_VENTILADOR)", self.config)
        self.assertIn("alias12Ok(BUZZER_HABILITADO, IR_HABILITADO)", self.config)
        self.assertIn("dfSinAlias(DFPLAYER_HABILITADO, true, LCD_HABILITADO)", self.config)
        self.assertIn("funcionesActivasSinAlias()", self.config)

    def test_ir_df_buzzer_prohibidos_en_alfa(self):
        # IR/DF/buzzer pertenecen al futuro FINAL: en alfa son error de compilación,
        # así PERFIL_PRUEBA siempre describe el binario real.
        self.assertIn("DOMUS_IR == 0", self.config)
        self.assertIn("DOMUS_DF == 0", self.config)
        self.assertIn("DOMUS_BUZZER == 0", self.config)
        self.assertIn("fuera del perfil alfa", self.config)
        for nombre in ('"ALFA_UN_COSTADO_SIN_IR"', '"ALFA_BOMBA_1"', '"ALFA_VENTILADOR_1"'):
            self.assertIn(nombre, self.config)

    def test_ola1_buffers_propios_y_sin_bloqueos(self):
        lcd = (BASE / "domus_lcd.h").read_text(encoding="utf-8")
        voice = (BASE / "domus_voice.h").read_text(encoding="utf-8")
        self.assertIn("feedbackTitulo_[17]", lcd)
        self.assertIn("feedbackSub_[17]", lcd)
        self.assertNotIn("delay(40)", lcd)
        self.assertIn("ultima_[160]", voice)
        self.assertIn("BUZZER_HABILITADO", voice)
        self.assertIn("void actualizar()", voice)
        self.assertIn("voz.actualizar()", self.sketch)
        self.assertIn("BUZZER=", self.sketch)

    def test_jarvis_unico_y_ack_solo_si_acepta(self):
        # alternarIR ya no emite Jarvis: solo feedback + bool.
        self.assertIn("bool alternarIR(Salida s, const char* nomOn, const char* nomOff)", self.sketch)
        self.assertNotIn('alternarIR(SALA, "SALA ON", "SALA OFF", 1, 2)', self.sketch)
        self.assertNotIn('alternarIR(CUARTO, "DORM ON", "DORM OFF", 3, 4)', self.sketch)
        self.assertNotIn('alternarIR(INVERNADERO, "CULTIVO ON", "CULTIVO OFF", 5, 6)', self.sketch)
        self.assertNotIn('alternarIR(VENTILADOR, "VENT ON", "VENT OFF", 7, 8)', self.sketch)
        # Cada ACK vive dentro de la rama exitosa (un NACK previo ya salió de alternarIR).
        for tag in ("ACK;IR;SALA", "ACK;IR;CUARTO", "ACK;IR;CULTIVO", "ACK;IR;VENT"):
            self.assertIn(tag, self.sketch)

    def test_svg_gpio12_reservado(self):
        svg = (ROOT / "visualizaciones" / "domus-alfa-guia-principiantes.svg").read_text(encoding="utf-8")
        self.assertIn("GPIO12 reservado, sin conectar", svg)

    def test_only_drv_build_can_enable_motors(self):
        self.assertIn("SALIDA_FISICA_HABILITADA[salida]", self.sketch)
        self.assertIn("SALIDA_FISICA_HABILITADA[i]?OUTPUT:INPUT", self.sketch)
        self.assertIn("HABILITAR_MOTOR_BOMBA", self.config)
        self.assertIn("HABILITAR_MOTOR_VENTILADOR", self.config)
        self.assertIn("ACTIVA_LOW[] = {false, false, false, false, false}", self.config)

    def test_diagnostics_identify_board_and_sensor_validity(self):
        self.assertIn('PERFIL_PLACA[] = "ESP32-S3-N16R8"', self.config)
        self.assertIn("BANCO;PLACA=%s;PERFIL=%s", self.sketch)
        diagnostic = self.sketch.split("void informarEstado(bool diagnostico)", 1)[1].split(
            "void procesarLinea", 1
        )[0]
        self.assertIn("DIAGNOSTICO;PLACA=%s;PERFIL=%s;DRIVER=", diagnostic)
        self.assertLess(diagnostic.index("DIAGNOSTICO;PLACA="), diagnostic.index("ESTADO;PARO="))
        for flag in ("VS=%d", "VN=%d", "VL=%d", "VA=%d"):
            self.assertIn(flag, self.sketch)

    def test_confirmed_hardware_is_integrated(self):
        for token in ("LiquidCrystal_I2C", "DHT dht", "PIN_SUELO", "PIN_NIVEL", "PIN_LUZ", "PIN_PIR"):
            self.assertIn(token, self.sketch + self.config)

    def test_one_side_pin_map_and_complete_i2c_scan(self):
        for declaration in (
            "PIN_SUELO = 15", "PIN_NIVEL = 16", "PIN_LCD_SDA = 17",
            "PIN_LCD_SCL = 13", "PIN_BOTON = 18",
        ):
            self.assertIn(declaration, self.config)
        for symbol, forbidden_pin in (("PIN_SUELO", 1), ("PIN_NIVEL", 2), ("PIN_LCD_SDA", 21)):
            self.assertNotRegex(self.config, rf"\b{symbol}\s*=\s*{forbidden_pin}\b")
        self.assertIn("direccion = 0x08", self.sketch)
        self.assertIn("direccion <= 0x77", self.sketch)
        self.assertIn("I2C;ENCONTRADO=0x%02X", self.sketch)

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
