"""Train a candidate Spanish keyword classifier; never enables firmware voice.

CPU training; fixed two-second PCM -> log-mel frontend -> small CNN -> int8.
Validation selects epochs. Held-out speakers are evaluated only after training.
"""
import argparse
import hashlib
import json
from pathlib import Path
from dataset import LABELS, audit


def train(records, output, epochs):
    import numpy as np
    import tensorflow as tf
    tf.keras.utils.set_random_seed(20260905)
    tf.config.experimental.enable_op_determinism()
    output.mkdir(parents=True, exist_ok=False)
    mel = tf.signal.linear_to_mel_weight_matrix(40, 257, 16000, 80, 7600)

    def feature(path):
        audio, _ = tf.audio.decode_wav(tf.io.read_file(path), desired_channels=1)
        audio = tf.squeeze(audio, -1)
        audio = tf.pad(audio, [[0, 32000-tf.shape(audio)[0]]])
        spec = tf.abs(tf.signal.stft(audio, 400, 160, fft_length=512))
        return tf.math.log(1e-6 + tf.matmul(spec, mel))[..., tf.newaxis].numpy()

    data = {}
    for split in ("train", "validation", "test"):
        rows = [r for r in records if r["split"] == split]
        x = np.stack([feature(r["path"]) for r in rows]).astype(np.float32)
        y = np.array([LABELS.index(r["label"]) for r in rows], dtype=np.int32)
        data[split] = (x, y)
    x, y = data["train"]
    normalization = tf.keras.layers.Normalization(axis=-1)
    normalization.adapt(x)
    model = tf.keras.Sequential([
        tf.keras.Input(shape=x.shape[1:]), normalization,
        tf.keras.layers.Conv2D(12, 3, strides=2, activation="relu"),
        tf.keras.layers.DepthwiseConv2D(3, activation="relu"),
        tf.keras.layers.Conv2D(24, 1, activation="relu"),
        tf.keras.layers.MaxPooling2D(2),
        tf.keras.layers.Conv2D(24, 3, activation="relu"),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(len(LABELS), activation="softmax")])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    history = model.fit(x, y, validation_data=data["validation"], epochs=epochs,
        batch_size=32, callbacks=[tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=8, restore_best_weights=True)], verbose=2)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    # Calibration of quantization sees training data only.
    converter.representative_dataset = lambda: ([sample[None]] for sample in x[:min(300,len(x))])
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    binary = converter.convert()
    (output / "jarvis_candidate_int8.tflite").write_bytes(binary)
    interpreter = tf.lite.Interpreter(model_content=binary)
    interpreter.allocate_tensors()
    inp, out = interpreter.get_input_details()[0], interpreter.get_output_details()[0]
    scale, zero = inp["quantization"]
    out_scale, out_zero = out["quantization"]
    if scale <= 0 or out_scale <= 0:
        raise ValueError("Cuantización inválida")
    matrix = np.zeros((len(LABELS), len(LABELS)), dtype=int)
    accepted, wrong_accepts = 0, 0
    for sample, truth in zip(*data["test"]):
        quantized = np.clip(np.round(sample / scale + zero), -128, 127).astype(np.int8)
        interpreter.set_tensor(inp["index"], quantized[None])
        interpreter.invoke()
        probs = (interpreter.get_tensor(out["index"])[0].astype(float)-out_zero)*out_scale
        prediction = int(np.argmax(probs))
        matrix[truth,prediction] += 1
        if prediction < 11 and probs[prediction] >= .75:
            accepted += 1
            wrong_accepts += int(prediction != truth)
    recall = np.diag(matrix) / matrix.sum(axis=1)
    report = {
        "status": "CANDIDATE_NOT_VALIDATED_ON_ESP32", "firmware_enabled": False,
        "sha256": hashlib.sha256(binary).hexdigest(), "model_bytes": len(binary),
        "labels": LABELS, "seed": 20260905, "tensorflow": tf.__version__,
        "epochs": len(history.history["loss"]),
        "int8_test_accuracy": float(np.trace(matrix)/matrix.sum()),
        "recall_by_label": dict(zip(LABELS, recall.tolist())),
        "confusion_matrix": matrix.tolist(), "accepted_at_075": accepted,
        "wrong_accepts_at_075": wrong_accepts,
        "input_quantization": [scale, zero], "output_quantization": [out_scale, out_zero],
        "frontend": {"sample_rate":16000,"samples":32000,"frame":400,"hop":160,
            "fft":512,"mel_bins":40,"low_hz":80,"high_hz":7600,"log_epsilon":1e-6},
        "dataset": [{k:r[k] for k in ("speaker","label","split","sha256_pcm")} for r in records],
        "pending": ["equivalent ESP32 frontend and interpreter integration",
            "measured inference time and tensor arena", "one-hour false-wake test",
            "speaker echo and microphone validation", "wake-window/command integration"]}
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output / "labels.json").write_text(json.dumps(LABELS, indent=2), encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("status","sha256","model_bytes","int8_test_accuracy")}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    try:
        records = audit(args.manifest)
        if args.audit_only:
            print(f"DATASET_OK: {len(records)} grabaciones; particiones sin hablantes compartidos")
            return 0
        if args.output is None or not 1 <= args.epochs <= 500:
            raise ValueError("Especificar --output nuevo y --epochs entre 1 y 500")
        train(records, args.output, args.epochs)
    except (ValueError, OSError, ImportError) as error:
        print(f"ENTRENAMIENTO_NO_COMPLETADO: {error}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
