"""Read the exact same append-only intent contract as the firmware."""
import hashlib
import re
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "firmware/casa_inteligente_v4/domus_intents.def"
raw = CONTRACT.read_text(encoding="utf-8")
rows = []
for line in raw.splitlines():
    if not line.strip() or line.lstrip().startswith("//"):
        continue
    match = re.fullmatch(r"DOMUS_INTENT\(([A-Z0-9_]+), (-?\d+), (true|false)\)", line)
    if not match:
        raise ValueError("Contrato de intenciones inválido")
    label, relay, on = match.groups()
    rows.append((label, int(relay), on == "true"))
LABELS = tuple(row[0] for row in rows)
if len(set(LABELS)) != len(LABELS) or not LABELS:
    raise ValueError("Etiquetas vacías o repetidas")
ACTION_IDS = tuple(i for i, row in enumerate(rows) if row[1] >= 0)
# Normalize line endings so Windows and Linux have the same contract identity.
CONTRACT_SHA256 = hashlib.sha256(raw.replace("\r\n", "\n").encode()).hexdigest()
