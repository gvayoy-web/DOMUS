from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INO = ROOT / "diagnosticos" / "domus_banco_integracion" / "domus_banco_integracion.ino"
SVG = ROOT.parent / "visualizaciones" / "domus-banco-lcd-ir-drv8833.svg"


class BancoIntegracionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = INO.read_text(encoding="utf-8")
        cls.diagram = SVG.read_text(encoding="utf-8")

    def test_mapa_temporal_coincide_con_diagrama(self):
        for token in (
            "PIN_SDA = 17", "PIN_SCL = 13", "PIN_IR = 12",
            "PIN_AIN1 = 4", "PIN_BIN1 = 7",
        ):
            self.assertIn(token, self.source)
        for token in ("GPIO17", "GPIO13", "GPIO12", "GPIO4", "GPIO7"):
            self.assertIn(token, self.diagram)

    def test_motores_arrancan_off_y_solo_pulsan_500_ms(self):
        self.assertIn("constexpr unsigned long PULSO_MS = 500", self.source)
        self.assertIn("void apagarMotores()", self.source)
        setup = self.source.split("void setup()", 1)[1].split("void loop()", 1)[0]
        self.assertIn("apagarMotores();", setup)
        pulso = self.source.split("void iniciarPulso", 1)[1].split("void ejecutar", 1)[0]
        self.assertLess(pulso.index("apagarMotores();"), pulso.index("digitalWrite"))

    def test_ir_ignora_repeticiones_y_limita_21_codigos(self):
        self.assertIn("MAX_CODIGOS = 21", self.source)
        self.assertIn("IRDATA_FLAGS_IS_REPEAT", self.source)
        self.assertIn("!repeticion && !codigoRepetido", self.source)


if __name__ == "__main__":
    unittest.main()
