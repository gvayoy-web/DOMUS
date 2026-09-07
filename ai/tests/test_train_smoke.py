"""Only plumbing test: random signals are NOT a Spanish speech dataset.

Temporary candidate files are deleted; no synthetic-trained model is shipped.
"""
import importlib.util
import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dataset import LABELS
from intents import CONTRACT_SHA256
from train import train


class TrainingPlumbingTest(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("tensorflow"), "TensorFlow not installed; smoke runs in AI CI")
    def test_fit_quantize_and_evaluate_temporary_random_fixture(self):
        import numpy as np
        rng = np.random.default_rng(123)
        with tempfile.TemporaryDirectory(prefix="domus-ai-test-") as directory:
            root = Path(directory)
            records = []
            for split in ("train","validation","test"):
                for i,label in enumerate(LABELS):
                    path = root / f"{split}-{i}.wav"
                    with wave.open(str(path), "wb") as stream:
                        stream.setparams((1,2,16000,32000,"NONE","not compressed"))
                        stream.writeframes(rng.integers(-1000,1000,32000,dtype=np.int16).astype("<i2").tobytes())
                    records.append({"path":str(path),"label":label,"speaker":split,
                                    "split":split,"sha256_pcm":"SYNTHETIC_TEST_FIXTURE"})
            output = root / "output"
            train(records, output, 1)
            report = json.loads((output/"report.json").read_text())
            self.assertFalse(report["firmware_enabled"])
            json.dumps(report, allow_nan=False)
            self.assertGreaterEqual(report["int8_test_accuracy"], 0)
            self.assertLessEqual(report["int8_test_accuracy"], 1)
            self.assertEqual(len(report["confusion_matrix"]),len(LABELS))
            self.assertGreater(report["model_bytes"],100)
            self.assertLessEqual(report["model_bytes"], 1024 * 1024)
            self.assertEqual(report["intent_contract_sha256"], CONTRACT_SHA256)
            self.assertEqual(report["epochs"], 1)
            status = json.loads((output/"status.json").read_text())
            self.assertEqual(status["status"], "CANDIDATE_NOT_VALIDATED_ON_ESP32")
            self.assertFalse(status["firmware_enabled"])
            self.assertEqual(status["sha256"], report["sha256"])
            self.assertTrue((output/"checkpoint.keras").is_file())
            with np.load(output/"frontend_reference.npz") as reference:
                self.assertEqual(reference["features"].shape, (198, 40, 1))
                self.assertEqual(reference["mel"].shape, (257, 40))
                self.assertTrue(np.isfinite(reference["features"]).all())
