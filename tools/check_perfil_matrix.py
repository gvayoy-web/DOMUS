"""Matriz histórica de perfiles del esqueleto alfa v2 (nota 50).

Compila firmware/domus_esqueleto con arduino-cli (local o del PATH):
  PASS esperado: DOMUS_PERFIL_ALFA=0/1/2 (sensores, bomba, ventilador).
  FAIL esperado: perfil 3 inválido, IR/buzzer/DFPlayer (fuera del perfil alfa).
Sale 0 solo si los 3 pasan y los 3 son rechazados por static_assert.
Sin toolchain prográmese --allow-skip (código 0); sin esa opción, la
omisión es fallo (código 2), nunca éxito silencioso.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / ".local-tools" / "arduino-cli" / "bin" / "arduino-cli.exe"
CONFIG = ROOT / ".arduino-local" / "arduino-cli.yaml"
FQBN = "esp32:esp32:esp32s3:FlashSize=16M,PSRAM=opi,PartitionScheme=app3M_fat9M_16MB,CPUFreq=240,LoopCore=1"

PASS_CASES = {
    "alfasensores": ["-DDOMUS_PERFIL_ALFA=0"],
    "alfabomba1": ["-DDOMUS_PERFIL_ALFA=1"],
    "alfaventilador1": ["-DDOMUS_PERFIL_ALFA=2"],
}
FAIL_CASES = {
    "perfil_invalido": (["-DDOMUS_PERFIL_ALFA=3"], "DOMUS_PERFIL_ALFA debe ser 0, 1 o 2"),
    "ir_mas_buzzer_gpio12": (["-DDOMUS_BUZZER=1", "-DDOMUS_IR=1"], "fuera del perfil alfa"),
    "dfplayer_en_17_18": (["-DDOMUS_DF=1"], "fuera del perfil alfa"),
}


def resolve_cli() -> list[str]:
    """arduino-cli local o del PATH (CI). Devuelve base del comando o []."""
    if CLI.is_file():
        return [str(CLI), "--config-file", str(CONFIG)]
    found = shutil.which("arduino-cli")
    if found:
        return [found]
    return []


def compile_case(name: str, flags: list[str]) -> tuple[int, str]:
    build = ROOT / "build" / f"perfil_{name}"
    cmd = resolve_cli() + [
        "compile",
        "--fqbn", FQBN,
        "--build-property", f"compiler.cpp.extra_flags={' '.join(flags)}",
        "--build-path", str(build),
        "--output-dir", str(build) + "-out",
        "firmware/legacy/domus_esqueleto",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    allow_skip = "--allow-skip" in sys.argv[1:]
    if not resolve_cli():
        print("MATRIZ_NO_EJECUTADA: falta arduino-cli (local y PATH)")
        return 0 if allow_skip else 2
    ok = True
    for name, flags in PASS_CASES.items():
        rc, out = compile_case(name, flags)
        status = "PASS" if rc == 0 else "FAIL"
        print(f"[{status}] perfil {name} {' '.join(flags)} (rc={rc})")
        ok = ok and rc == 0
    for name, (flags, marker) in FAIL_CASES.items():
        rc, out = compile_case(name, flags)
        rejected = rc != 0 and marker in out
        print(f"[{'PASS' if rejected else 'FAIL'}] prohibido {name} rechazado={rejected} (rc={rc})")
        ok = ok and rejected
    print("MATRIZ_OK: 3 perfiles compilan, 3 prohibidos rechazados" if ok else "MATRIZ_ROTA")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
