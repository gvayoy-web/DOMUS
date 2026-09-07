"""Fail-closed validation thresholds. Never tune thresholds on the test split."""
import math
from intents import ACTION_IDS, LABELS


def prediction(scores):
    if len(scores) != len(LABELS) or any(not math.isfinite(float(p)) or not 0 <= p <= 1 for p in scores):
        return None
    # Equal best scores do not constitute an unambiguous command.
    best = max(range(len(scores)), key=lambda i: scores[i])
    if sum(float(p) == float(scores[best]) for p in scores) != 1:
        return None
    return best


def select_thresholds(probabilities, truths, minimum_correct=20):
    if len(probabilities) != len(truths):
        raise ValueError("Predicciones/etiquetas de distinta longitud")
    thresholds = [None] * len(LABELS)
    for label in ACTION_IDS:
        for threshold in (0.75, 0.80, 0.85, 0.90, 0.95, 0.99):
            accepted = [truth for scores, truth in zip(probabilities, truths)
                        if prediction(scores) == label and scores[label] >= threshold]
            if len(accepted) >= minimum_correct and all(t == label for t in accepted):
                thresholds[label] = threshold
                break
    return thresholds


def evaluate(probabilities, truths, thresholds):
    if len(probabilities) != len(truths) or len(thresholds) != len(LABELS):
        raise ValueError("Dimensiones de evaluación inválidas")
    matrix = [[0] * len(LABELS) for _ in LABELS]
    invalid = accepted = wrong = false_actions = 0
    totals = [0] * len(LABELS)
    accepted_correct = [0] * len(LABELS)
    for scores, truth in zip(probabilities, truths):
        if not 0 <= int(truth) < len(LABELS):
            raise ValueError("Etiqueta fuera de rango")
        totals[truth] += 1
        predicted = prediction(scores)
        if predicted is None:
            invalid += 1
            continue
        matrix[truth][predicted] += 1
        threshold = thresholds[predicted]
        if predicted in ACTION_IDS and threshold is not None and 0.75 <= threshold <= 1 and scores[predicted] >= threshold:
            accepted += 1
            wrong += int(predicted != truth)
            false_actions += int(truth not in ACTION_IDS)
            accepted_correct[truth] += int(predicted == truth)
    return {
        "confusion_matrix": matrix, "invalid_predictions": invalid,
        "accuracy": sum(matrix[i][i] for i in range(len(LABELS))) / max(1, sum(totals)),
        "recall_by_label": {name: matrix[i][i] / totals[i] if totals[i] else None for i, name in enumerate(LABELS)},
        "accepted_recall_by_label": {LABELS[i]: accepted_correct[i] / totals[i] if totals[i] else None for i in ACTION_IDS},
        "accepted_commands": accepted, "wrong_accepted_commands": wrong,
        "false_actions_on_noncommands": false_actions,
        "thresholds_by_label": dict(zip(LABELS, thresholds)),
        "firmware_enabled": False,
    }
