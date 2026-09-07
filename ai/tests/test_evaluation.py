import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from intents import LABELS, ACTION_IDS, CONTRACT_SHA256
from evaluation import prediction, select_thresholds, evaluate


def scores(index, confidence=.9):
    row = [(1-confidence)/(len(LABELS)-1)] * len(LABELS)
    row[index] = confidence
    return row


class EvaluationTests(unittest.TestCase):
    def test_contract_is_stable_and_actions_explicit(self):
        self.assertEqual(LABELS[5], "RIEGO_ON")
        self.assertEqual(ACTION_IDS, tuple(range(1, 11)))
        self.assertEqual(len(CONTRACT_SHA256), 64)

    def test_nan_inf_ties_and_shape_rejected(self):
        self.assertIsNone(prediction([.1]))
        self.assertIsNone(prediction([.1] * len(LABELS)))
        for bad in (float('nan'), float('inf'), -1., 1.1):
            row = scores(1); row[1] = bad
            self.assertIsNone(prediction(row))

    def test_insufficient_validation_disables_command(self):
        self.assertIsNone(select_thresholds([scores(1)], [1])[1])

    def test_all_ambiguous_predictions_count_as_misses_not_nan(self):
        result = evaluate([[.1] * len(LABELS)], [1], [None] * len(LABELS))
        self.assertEqual(result['invalid_predictions'], 1)
        self.assertEqual(result['accuracy'], 0)
        self.assertEqual(result['recall_by_label'][LABELS[1]], 0)
        self.assertEqual(result['accepted_commands'], 0)

    def test_threshold_uses_validation_and_counts_false_actions(self):
        threshold = select_thresholds([scores(1)] * 20, [1] * 20)
        self.assertEqual(threshold[1], .75)
        result = evaluate([scores(1), scores(1)], [1, 11], threshold)
        self.assertEqual(result['wrong_accepted_commands'], 1)
        self.assertEqual(result['false_actions_on_noncommands'], 1)
        self.assertFalse(result['firmware_enabled'])

    def test_wrong_high_confidence_validation_disables_class(self):
        threshold = select_thresholds([scores(1)] * 20 + [scores(1,.999)], [1]*20+[11])
        self.assertIsNone(threshold[1])
