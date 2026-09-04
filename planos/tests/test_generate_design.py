from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "generate_design.py"
SPEC = importlib.util.spec_from_file_location("domus_generate_design", MODULE_PATH)
assert SPEC and SPEC.loader
generator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = generator
SPEC.loader.exec_module(generator)


def canonical_parts():
    return generator.prepare_raw_model(
        generator.compact_footprint(generator.enhance_parts(generator.build_parts()))
    )


class GenerateDesignTests(unittest.TestCase):
    def test_canonical_model_passes_validation(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            generator, "ROOT", Path(directory)
        ):
            report = generator.validate_model(canonical_parts())

        self.assertEqual(report["resultado"], "OK")
        self.assertEqual(report["cantidad_piezas"], 111)
        self.assertEqual(report["nombres_duplicados"], [])
        self.assertEqual(report["materiales_sin_definir"], [])
        self.assertEqual(report["piezas_con_dimensiones_no_positivas"], [])

    def test_pdf_is_written_inside_selected_package(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            generator, "ROOT", Path(directory)
        ):
            output = generator.write_pdf_v4()

            self.assertEqual(output, Path(directory) / "plano_tecnico_domus.pdf")
            self.assertTrue(output.read_bytes().startswith(b"%PDF"))

    def test_validation_rejects_duplicate_names(self):
        parts = canonical_parts()
        parts.append(parts[0])
        with tempfile.TemporaryDirectory() as directory, patch.object(
            generator, "ROOT", Path(directory)
        ):
            with self.assertRaises(ValueError):
                generator.validate_model(parts)
            report = json.loads(
                (Path(directory) / "verificacion_geometria_v4.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(report["resultado"], "REVISAR")
        self.assertIn("Base negra 800x520", report["nombres_duplicados"])

    def test_zip_contains_exact_package_manifest(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            generator, "ROOT", Path(directory)
        ):
            for name in generator.PACKAGE_FILES:
                (Path(directory) / name).write_bytes(name.encode("utf-8"))
            output = generator.write_package_zip()
            with zipfile.ZipFile(output) as archive:
                names = tuple(archive.namelist())

        self.assertEqual(names, generator.PACKAGE_FILES)


if __name__ == "__main__":
    unittest.main()
