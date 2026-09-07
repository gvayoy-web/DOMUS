import csv
import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dataset import audit, inspect_wav


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.addCleanup(self.directory.cleanup)

    def wav(self, name="audio.wav", rate=16000, saturated=False):
        path = self.root / name
        with wave.open(str(path), "wb") as stream:
            stream.setparams((1, 2, rate, rate, "NONE", "not compressed"))
            stream.writeframes(b"".join(struct.pack("<h", 32767 if saturated else int(3000*math.sin(i*.1))) for i in range(rate)))
        return path

    def manifest(self, rows):
        path = self.root / "manifest.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["path","speaker","label","split","source","consent"])
            writer.writerows(rows)
        return path

    def test_wav_format_and_clipping(self):
        self.assertEqual(inspect_wav(self.wav())["frames"], 16000)
        with self.assertRaisesRegex(ValueError, "PCM16"):
            inspect_wav(self.wav("wrong.wav", rate=8000))
        with self.assertRaisesRegex(ValueError, "saturadas"):
            inspect_wav(self.wav("clip.wav", saturated=True))

    def test_no_dataset_cannot_claim_training(self):
        with self.assertRaisesRegex(ValueError, "Falta"):
            audit(self.root / "missing.csv")

    def test_synthetic_audio_is_not_accepted_as_real_training(self):
        manifest = self.manifest([["a.wav","p1","JARVIS","train","synthetic","yes"]])
        with self.assertRaisesRegex(ValueError, "reales"):
            audit(manifest)

    def test_exact_pcm_duplicates_are_rejected_across_splits(self):
        self.wav()
        manifest = self.manifest([["audio.wav","p1","JARVIS","train","real","yes"],
                                  ["audio.wav","p2","JARVIS","test","real","yes"]])
        with self.assertRaisesRegex(ValueError, "duplicado"):
            audit(manifest)

    def test_incomplete_classes_are_rejected(self):
        self.wav()
        manifest = self.manifest([["audio.wav","p1","JARVIS","train","real","yes"]])
        with self.assertRaisesRegex(ValueError, "insuficientes"):
            audit(manifest)

    def test_audio_paths_cannot_escape_dataset(self):
        manifest = self.manifest([["../a.wav","p1","JARVIS","train","real","yes"]])
        with self.assertRaisesRegex(ValueError, "fuera"):
            audit(manifest)

    def provenance_manifest(self, source="synthetic", split="train", license="CC0-1.0"):
        self.wav()
        path = self.root / "provenance.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["path","speaker","label","split","source","consent",
                             "license","source_url","origin_id","transcript"])
            writer.writerow(["audio.wav","voice1","JARVIS",split,source,"yes",
                             license,"https://example.invalid/fixture","recording1","jarvis"])
        return path

    def test_synthetic_requires_explicit_flag_and_provenance(self):
        path = self.provenance_manifest()
        records = audit(path, {"train":0,"validation":0,"test":0}, allow_synthetic_train=True)
        self.assertEqual(records[0]["source"], "synthetic")
        self.assertEqual(records[0]["origin_id"], "recording1")
        with self.assertRaisesRegex(ValueError, "procedencia"):
            audit(self.provenance_manifest(license=""), allow_synthetic_train=True)

    def test_synthetic_cannot_contaminate_evaluation(self):
        for split in ("validation", "test"):
            with self.assertRaisesRegex(ValueError, "evaluación real"):
                audit(self.provenance_manifest(split=split), allow_synthetic_train=True)

    def test_truncated_csv_is_rejected_cleanly(self):
        path = self.manifest([["audio.wav","speaker"]])
        with self.assertRaisesRegex(ValueError, "incompletos"):
            audit(path)
