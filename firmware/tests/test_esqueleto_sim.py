"""Gemelo especifico del esqueleto alfa (notas 46/50/51).

Espeja las reglas puras de firmware/domus_esqueleto/domus_control.h y los
guards de pedirSalida()/revisarSeguridad() de domus_esqueleto.ino, sin
hardware. Cada umbral se verifica primero como literal del header: si el
firmware cambia un umbral, el contrato falla antes de que la simulacion mienta.
"""
import re
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parents[1] / "domus_esqueleto"
CONTROL = (BASE / "domus_control.h").read_text(encoding="utf-8")
SKETCH = (BASE / "domus_esqueleto.ino").read_text(encoding="utf-8")


def decidir_riego(humedad_pct, bomba_encendida):
    if not bomba_encendida and humedad_pct <= 35:
        return "ENCENDER"
    if bomba_encendida and humedad_pct >= 45:
        return "APAGAR"
    return "NADA"


def decidir_ventilador(temp, encendido):
    if not encendido and temp >= 28.0:
        return "ENCENDER"
    if encendido and temp <= 26.0:
        return "APAGAR"
    return "NADA"


def decidir_luz_sala(luz_pct, presencia, encendida):
    if not encendida and presencia and luz_pct <= 30:
        return "ENCENDER"
    if encendida and (not presencia or luz_pct >= 45):
        return "APAGAR"
    return "NADA"


def decidir_invernadero(luz_pct, encendida):
    if not encendida and luz_pct <= 25:
        return "ENCENDER"
    if encendida and luz_pct >= 40:
        return "APAGAR"
    return "NADA"


def porcentaje_calibrado(valor, cero, cien):
    if cero == cien:
        return 0
    calculado = (valor - cero) * 100 // (cien - cero)
    return max(0, min(100, calculado))


class Bomba:
    """Modelo minimo de pedirSalida(BOMBA) + revisarSeguridad + rearme."""

    def __init__(self, nivel_minimo=600):
        self.encendida = False
        self.bloqueada = False
        self.calibrada = False
        self.nivel_minimo = nivel_minimo
        self.inicio = 0
        self.ahora = 0

    def pedir(self, activar, nivel):
        if not activar:
            self.encendida = False
            return True
        if self.bloqueada or not self.calibrada:
            return False
        if nivel < self.nivel_minimo:
            return False
        if not self.encendida:
            self.inicio = self.ahora
        self.encendida = True
        return True

    def tick(self, nivel, bomba_max_ms=10000):
        self.ahora += 1000
        if not self.encendida:
            return
        if nivel < self.nivel_minimo or (self.ahora - self.inicio) >= bomba_max_ms:
            self.encendida = False
            self.bloqueada = True


class EsqueletoContractTests(unittest.TestCase):
    def test_umbrales_son_literales_del_header(self):
        for literal in (
            "humedadPct <= 35", "humedadPct >= 45",
            "temp >= 28.0f", "temp <= 26.0f",
            "luzPct <= 30", "luzPct >= 45",
            "luzPct <= 25", "luzPct >= 40",
        ):
            self.assertIn(literal, CONTROL)
        self.assertIn("BOMBA_MAX_MS = 10000", (BASE / "domus_config.h").read_text(encoding="utf-8"))

    def test_riego_con_histeresis(self):
        self.assertEqual(decidir_riego(30, False), "ENCENDER")
        self.assertEqual(decidir_riego(35, False), "ENCENDER")
        self.assertEqual(decidir_riego(36, False), "NADA")
        self.assertEqual(decidir_riego(40, True), "NADA")
        self.assertEqual(decidir_riego(44, True), "NADA")
        self.assertEqual(decidir_riego(45, True), "APAGAR")
        self.assertEqual(decidir_riego(50, True), "APAGAR")

    def test_ventilador_con_histeresis(self):
        self.assertEqual(decidir_ventilador(28.0, False), "ENCENDER")
        self.assertEqual(decidir_ventilador(30.0, False), "ENCENDER")
        self.assertEqual(decidir_ventilador(27.0, False), "NADA")
        self.assertEqual(decidir_ventilador(27.0, True), "NADA")
        self.assertEqual(decidir_ventilador(26.0, True), "APAGAR")

    def test_luces_sala_e_invernadero(self):
        self.assertEqual(decidir_luz_sala(20, True, False), "ENCENDER")
        self.assertEqual(decidir_luz_sala(20, False, False), "NADA")
        self.assertEqual(decidir_luz_sala(50, True, True), "APAGAR")
        self.assertEqual(decidir_luz_sala(20, False, True), "APAGAR")
        self.assertEqual(decidir_invernadero(20, False), "ENCENDER")
        self.assertEqual(decidir_invernadero(30, False), "NADA")
        self.assertEqual(decidir_invernadero(30, True), "NADA")
        self.assertEqual(decidir_invernadero(45, True), "APAGAR")

    def test_porcentaje_calibrado_acepta_polaridad_invertida(self):
        self.assertEqual(porcentaje_calibrado(2000, 3000, 1000), 50)
        self.assertEqual(porcentaje_calibrado(1000, 3000, 1000), 100)
        self.assertEqual(porcentaje_calibrado(3000, 3000, 1000), 0)
        self.assertEqual(porcentaje_calibrado(5000, 3000, 1000), 0)
        self.assertEqual(porcentaje_calibrado(0, 3000, 1000), 100)
        self.assertEqual(porcentaje_calibrado(2000, 2000, 2000), 0)

    def test_bomba_exige_calibracion_nivel_y_bloquea(self):
        b = Bomba(nivel_minimo=600)
        self.assertFalse(b.pedir(True, 800))  # sin calibrar
        b.calibrada = True
        self.assertFalse(b.pedir(True, 500))  # nivel bajo
        self.assertTrue(b.pedir(True, 800))
        for _ in range(9):
            b.tick(800)
        self.assertTrue(b.encendida)  # 9 s < 10 s timeout
        b.tick(800)
        self.assertFalse(b.encendida)  # timeout 10 s
        self.assertTrue(b.bloqueada)
        self.assertFalse(b.pedir(True, 800))  # requiere rearme
        b.bloqueada = False  # REARMAR deja salidas OFF y desbloquea
        self.assertTrue(b.pedir(True, 800))

    def test_bomba_corta_por_nivel_aunque_haya_tiempo(self):
        b = Bomba(nivel_minimo=600)
        b.calibrada = True
        self.assertTrue(b.pedir(True, 800))
        b.tick(800)
        b.tick(100)
        self.assertFalse(b.encendida)
        self.assertTrue(b.bloqueada)

    def test_sketch_conserva_las_guards_modeladas(self):
        for token in (
            "calibracion_requerida", "nivel_no_aprobado", "bomba_requiere_rearme",
            "BOMBA_MAX_MS", "EVENTO;BOMBA_BLOQUEADA;REARMAR_REQUERIDO",
        ):
            self.assertIn(token, SKETCH)


if __name__ == "__main__":
    unittest.main(verbosity=2)
