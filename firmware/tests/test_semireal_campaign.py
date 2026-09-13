import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("semireal", ROOT / "tools/run_semireal_campaign.py")
semireal = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = semireal
SPEC.loader.exec_module(semireal)


class SemirealCampaignTests(unittest.TestCase):
    def test_10k_step_campaign_preserves_safety_invariants(self):
        report = semireal.run()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["steps"], 10_000)
        self.assertGreaterEqual(report["invariant_checks"], 40_000)
        self.assertTrue(report["bounded_event_log"])
        for key in ("emergency_injections", "safe_mode_injections", "simulated_resets", "sensor_faults"):
            self.assertGreater(report[key], 0)


if __name__ == "__main__":
    unittest.main()
