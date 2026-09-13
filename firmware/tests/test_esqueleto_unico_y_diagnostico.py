from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class EsqueletoUnicoYDiagnosticoTests(unittest.TestCase):
    def test_esqueleto_incluye_literalmente_el_producto_con_perfil_actual(self):
        source = (ROOT / "firmware/domus_esqueleto/domus_esqueleto.ino").read_text(encoding="utf-8")
        self.assertIn("#define DOMUS_PERFIL_CASA 3", source)
        self.assertIn('#include "../casa_inteligente_v4/casa_inteligente_v4.ino"', source)
        self.assertNotIn("void setup()", source)
        self.assertNotIn("void loop()", source)

    def test_diagnostico_avanzado_usa_mapa_actual_y_no_acciona_motores(self):
        source = (ROOT / "firmware/diagnosticos/domus_banco_integracion/domus_banco_integracion.ino").read_text(encoding="utf-8")
        for declaration in (
            "PIN_LDR = 3", "PIN_IR = 12", "PIN_SCL = 13", "PIN_DHT = 14",
            "PIN_SUELO = 15", "PIN_NIVEL = 16", "PIN_SDA = 17",
        ):
            self.assertIn(declaration, source)
        self.assertNotIn("A_PULSE", source)
        self.assertNotIn("B_PULSE", source)
        self.assertNotIn("digitalWrite(", source)
        self.assertIn("IR;PROTO=", source)
        self.assertIn("ADC;SUELO=", source)
        self.assertIn("DHT;TEMP_C=", source)

    def test_diagnostico_ofrece_muestras_para_calibrar(self):
        source = (ROOT / "firmware/diagnosticos/domus_banco_integracion/domus_banco_integracion.ino").read_text(encoding="utf-8")
        for command in ("MUESTRA_SECO", "MUESTRA_HUMEDO", "MUESTRA_OSCURO", "MUESTRA_CLARO", "MUESTRA_NIVEL"):
            self.assertIn(command, source)
        self.assertIn("CAL;COPIAR=CAL_SECO=", source)


if __name__ == "__main__":
    unittest.main()
