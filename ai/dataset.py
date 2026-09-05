"""Validate consented, locally stored Spanish command recordings before training."""
import array
import csv
import hashlib
import sys
import wave
from collections import Counter, defaultdict
from pathlib import Path

LABELS = ("JARVIS", "LUZ_SALA_1_ON", "LUZ_SALA_1_OFF", "LUZ_CUARTO_ON",
          "LUZ_CUARTO_OFF", "RIEGO_ON", "RIEGO_OFF", "VENTILADOR_ON",
          "VENTILADOR_OFF", "INVERNADERO_ON", "INVERNADERO_OFF",
          "DESCONOCIDO", "RUIDO", "SILENCIO")
SPLITS = ("train", "validation", "test")


def inspect_wav(path):
    with wave.open(str(path), "rb") as wav:
        if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getcomptype()) != (1, 2, 16000, "NONE"):
            raise ValueError(f"{path.name}: se requiere PCM16 mono 16000 Hz")
        frames = wav.getnframes()
        if not 8000 <= frames <= 32000:
            raise ValueError(f"{path.name}: duración debe estar entre 0.5 y 2 segundos; no se recorta silenciosamente")
        raw = wav.readframes(frames)
        if len(raw) != frames * 2:
            raise ValueError(f"{path.name}: WAV truncado")
    samples = array.array("h", raw)
    if sys.byteorder != "little":
        samples.byteswap()
    clipping = sum(abs(x) >= 32760 for x in samples) / frames
    if clipping > 0.01:
        raise ValueError(f"{path.name}: más de 1% de muestras saturadas")
    return {"sha256_pcm": hashlib.sha256(raw).hexdigest(),
            "rms": (sum(x*x for x in samples) / frames) ** 0.5 / 32768,
            "frames": frames, "clipping": clipping}


def audit(manifest, minimum_counts=None):
    manifest = Path(manifest).resolve()
    if not manifest.is_file():
        raise ValueError(f"Falta el manifiesto de audios reales: {manifest}")
    minimum_counts = minimum_counts or {"train": 20, "validation": 5, "test": 5}
    records, hashes = [], set()
    speakers = defaultdict(set)
    counts = Counter()
    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"path", "speaker", "label", "split", "source", "consent"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Columnas requeridas: " + ",".join(sorted(required)))
        for line, row in enumerate(reader, 2):
            if row["source"] != "real" or row["consent"] != "yes":
                raise ValueError(f"Fila {line}: solo grabaciones reales con consentimiento")
            if row["label"] not in LABELS or row["split"] not in SPLITS or not row["speaker"].strip():
                raise ValueError(f"Fila {line}: etiqueta, hablante o partición inválida")
            path = (manifest.parent / row["path"]).resolve()
            if not path.is_relative_to(manifest.parent):
                raise ValueError(f"Fila {line}: audio fuera de la carpeta del dataset")
            info = inspect_wav(path)
            if info["sha256_pcm"] in hashes:
                raise ValueError(f"Fila {line}: audio duplicado; posible contaminación de evaluación")
            hashes.add(info["sha256_pcm"])
            if info["rms"] < 0.0001 and row["label"] != "SILENCIO":
                raise ValueError(f"Fila {line}: audio sin señal para clase de voz/ruido")
            speakers[row["speaker"]].add(row["split"])
            counts[row["split"], row["label"]] += 1
            records.append({**row, **info, "path": str(path)})
    if any(len(partitions) != 1 for partitions in speakers.values()):
        raise ValueError("Un hablante aparece en más de una partición")
    missing = [f"{split}/{label}: {counts[split,label]}/{minimum_counts[split]}"
               for split in SPLITS for label in LABELS if counts[split,label] < minimum_counts[split]]
    if missing:
        raise ValueError("Datos insuficientes: " + "; ".join(missing))
    return records
