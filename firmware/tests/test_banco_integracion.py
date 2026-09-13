from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INO = ROOT / "diagnosticos" / "domus_banco_integracion" / "domus_banco_integracion.ino"


class BancoIntegracionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = INO.read_text(encoding="utf-8")

    def test_mapa_coincide_con_el_banco_actual(self):
        for token in (
            "PIN_LDR = 3", "PIN_IR = 12", "PIN_SCL = 13", "PIN_DHT = 14",
            "PIN_SUELO = 15", "PIN_NIVEL = 16", "PIN_SDA = 17",
        ):
            self.assertIn(token, self.source)

    def test_no_existe_ruta_para_accionar_salidas(self):
        for forbidden in ("PIN_AIN1", "PIN_BIN1", "A_PULSE", "B_PULSE", "digitalWrite(", "pinMode("):
            self.assertNotIn(forbidden, self.source)
        self.assertIn("SIN_SALIDAS", self.source)

    def test_ir_ignora_repeticiones_y_limita_21_codigos(self):
        self.assertIn("MAX_CODIGOS = 21", self.source)
        self.assertIn("IRDATA_FLAGS_IS_REPEAT", self.source)
        self.assertIn("!repeat && !repetido", self.source)

    def test_genera_comandos_de_calibracion_para_copiar(self):
        for token in ("CAL_SECO=", "CAL_HUMEDO=", "CAL_OSCURO=", "CAL_CLARO=", "CAL_NIVEL="):
            self.assertIn(token, self.source)


if __name__ == "__main__":
    unittest.main()
