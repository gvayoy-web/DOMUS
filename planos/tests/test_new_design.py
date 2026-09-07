from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


NEW_ROOT = Path(__file__).resolve().parents[1] / "new"
class NewDesignTests(unittest.TestCase):
    def test_v4_generator_is_valid_python_and_report_is_current(self):
        source = (NEW_ROOT / "generate_design.py").read_text(encoding="utf-8")
        compile(source, str(NEW_ROOT / "generate_design.py"), "exec")
        saved = json.loads(
            (NEW_ROOT / "verificacion_geometria_v4.json").read_text(encoding="utf-8")
        )
        self.assertIn("BASE_W = 800", source)
        self.assertIn("BASE_D = 520", source)
        self.assertEqual(saved["resultado"], "OK")
        self.assertEqual(saved["envolvente_base_mm"], [800, 520, 12])
        self.assertEqual(saved["cantidad_piezas"], 111)

    def test_ultimate_cut_list_matches_selected_geometry(self):
        with (NEW_ROOT / "lista_corte_ultimate.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            rows = {row["codigo"]: row for row in csv.DictReader(stream)}
        self.assertEqual(rows["B-01"]["medida_mm"], "800 × 520")
        self.assertEqual(rows["C-01"]["medida_mm"], "344 × 260")
        self.assertEqual(rows["I-01"]["medida_mm"], "200 × 280")
        self.assertEqual(rows["P-01"]["medida_mm"], "200 × 156")

    def test_current_viewer_contains_only_v4_key_dimensions(self):
        viewer = (NEW_ROOT / "modelo_3d_interactivo.html").read_text(encoding="utf-8")
        self.assertIn("800 × 520", viewer)
        self.assertIn("344 × 260", viewer)
        self.assertNotIn("<b>1000 × 650</b>", viewer)


if __name__ == "__main__":
    unittest.main()
