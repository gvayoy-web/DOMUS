"""Contrato estático del ejecutor HIL seguro del perfil de banco."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HIL = ROOT / "firmware" / "tests" / "test_hil_producto.py"


class HilProductoContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HIL.read_text(encoding="utf-8")

    def test_apunta_al_perfil_de_producto_vigente(self):
        self.assertIn('PROFILE = "BANCO_COMPLETO_S8050_IR"', self.source)
        self.assertIn('DOMUS_PORT', self.source)

    def test_no_ordena_encender_motores(self):
        self.assertNotIn('cmd("RIEGO_ON"', self.source)
        self.assertNotIn('cmd("VENT_ON"', self.source)
        self.assertIn('"RIEGO_OFF", "VENT_OFF"', self.source)

    def test_verifica_bloque_prueba_ir_y_paro(self):
        for token in ('"PRUEBA"', '"IR_LISTA"', '"PARO"', '"REARMAR"'):
            self.assertIn(token, self.source)


if __name__ == "__main__":
    unittest.main()
