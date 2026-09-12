"""Contrato de backends de driver separados (DRV8833 / MX1508), preparados
pero INACTIVOS, con perfil predeterminado NINGUNO.

Verifica por contrato sobre `firmware/casa_inteligente_v4/domus_drivers.h`:
- enum BackendMotor con 3 valores y base uint8_t,
- default NINGUNO via -DDOMUS_DRIVER=0,
- static_assert de rango (otro valor = error de compilacion),
- descriptores por backend SIN GPIO numericos asignados,
- DRIVER_MOTORES_LISTO deriva del backend,
- driverMotoresAplicar seguro por defecto (false, sin GPIO),
- ningun binario ni perfil llamado FINAL.
"""
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DRIVERS = ROOT / "firmware" / "casa_inteligente_v4" / "domus_drivers.h"


class DriverBackendsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = DRIVERS.read_text(encoding="utf-8")

    def test_enum_backend_motor_con_tres_valores(self):
        match = re.search(
            r"enum\s+class\s+BackendMotor\s*:\s*uint8_t\s*\{([^}]*)\}",
            self.src,
        )
        self.assertIsNotNone(match, "enum class BackendMotor : uint8_t {...} ausente")
        cuerpo = match[1]
        for valor in ("NINGUNO", "DRV8833", "MX1508"):
            self.assertIn(valor, cuerpo, f"{valor} ausente en BackendMotor")
        # Orden declarado: NINGUNO primero (valor seguro).
        self.assertLess(cuerpo.index("NINGUNO"), cuerpo.index("DRV8833"))
        self.assertLess(cuerpo.index("DRV8833"), cuerpo.index("MX1508"))

    def test_default_es_ninguno_via_bandera(self):
        self.assertIn("#ifndef DOMUS_DRIVER", self.src)
        self.assertRegex(self.src, r"#define\s+DOMUS_DRIVER\s+0\b")
        # Mapeo 0 -> NINGUNO visible en la seleccion.
        self.assertIn("BACKEND_MOTOR_SELECCIONADO", self.src)
        self.assertIn("BackendMotor::NINGUNO", self.src)

    def test_static_assert_de_rango_presente(self):
        self.assertIn("static_assert(DOMUS_DRIVER", self.src)
        self.assertIn("<= 2", self.src)
        self.assertIn("DOMUS_DRIVER debe ser 0, 1 o 2", self.src)

    def test_descriptores_sin_gpio_numericos(self):
        # Estructura solo con texto: sin campos numericos de pines.
        match = re.search(
            r"struct\s+DescriptorBackendMotor\s*\{([^}]*)\}", self.src
        )
        self.assertIsNotNone(match, "struct DescriptorBackendMotor ausente")
        cuerpo = match[1]
        self.assertIn("const char*", cuerpo)
        self.assertNotIn("int ", cuerpo)
        self.assertNotIn("uint8_t", cuerpo)
        self.assertNotIn("gpio", cuerpo.lower())
        # Un descriptor por backend preparado.
        self.assertIn("DESCRIPTOR_DRV8833", self.src)
        self.assertIn("DESCRIPTOR_MX1508", self.src)
        # Notas de cableado futuro, sin inventar pinouts.
        self.assertIn("AIN1", self.src)
        self.assertIn("AIN2", self.src)
        self.assertIn("BIN1", self.src)
        self.assertIn("BIN2", self.src)
        self.assertIn("nSLEEP", self.src)
        self.assertIn("IN1", self.src)
        self.assertIn("OUT1", self.src)
        # Prohibido asignar GPIO: sin defines de pines de driver ni
        # llamadas que muevan hardware en este header.
        self.assertIsNone(
            re.search(r"#define\s+(DRV8833|MX1508)_\w*PIN\w*\s+\d+", self.src)
        )
        for llamada in ("digitalWrite", "analogWrite", "ledcWrite", "pinMode", "dacWrite"):
            self.assertNotIn(llamada, self.src)

    def test_driver_motores_listo_deriva_del_backend(self):
        self.assertIn("DRIVER_MOTORES_LISTO", self.src)
        # La definicion activa menciona NINGUNO: deriva del backend.
        definiciones = re.findall(
            r"constexpr\s+bool\s+DRIVER_MOTORES_LISTO\s*=[^;]*;", self.src
        )
        self.assertTrue(definiciones, "definicion de DRIVER_MOTORES_LISTO ausente")
        self.assertTrue(
            any("NINGUNO" in d for d in definiciones),
            "DRIVER_MOTORES_LISTO debe derivar de backend != NINGUNO",
        )
        self.assertIn("driverMotoresListo()", self.src)

    def test_driver_motores_aplicar_seguro_por_defecto(self):
        match = re.search(
            r"bool\s+driverMotoresAplicar\s*\([^)]*\)\s*\{([^}]*)\}",
            self.src,
            re.S,
        )
        self.assertIsNotNone(match, "driverMotoresAplicar(canal, activar) ausente")
        cuerpo = match[1]
        self.assertIn("return false", cuerpo)
        for llamada in ("digitalWrite", "analogWrite", "ledcWrite", "pinMode", "dacWrite"):
            self.assertNotIn(llamada, cuerpo)

    def test_ningun_binario_ni_perfil_llamado_final(self):
        self.assertNotIn('"FINAL"', self.src)
        self.assertNotIn("CANDIDATO_FINAL", self.src)
        self.assertNotIn("PERFIL_FINAL", self.src)
        self.assertNotIn("BINARIO_FINAL", self.src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
