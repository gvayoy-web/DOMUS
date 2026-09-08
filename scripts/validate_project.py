"""Validación única del código y la bóveda técnica de PROJECT DOMUS."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "obsidian" / "proyect domus"
SIMULATOR = ROOT / "assets" / "new" / "deliverables" / "execute" / "01_FINAL_V2" / "simulator"
FIRMWARE_TESTS = ROOT / "firmware" / "tests"
PLAN_TESTS = ROOT / "planos" / "tests"
FIRMWARE = ROOT / "firmware" / "casa_inteligente_v4" / "casa_inteligente_v4.ino"
BENCH_CONFIG = ROOT / "firmware" / "domus_esqueleto" / "domus_config.h"
MASTER_WIRING = VAULT / "18 - Manual maestro de conexiones pin por pin.md"
CURRENT_DECISION = VAULT / "36 - Configuracion final 1 mas 4 reles y planos v4.md"
CURRENT_BENCH_GUIDE = VAULT / "37 - Ronda de pruebas sin compras.md"
CURRENT_BUILD_GUIDE = ROOT / "planos" / "new" / "GUIA_MONTAJE_ULTIMATE.md"
VISUAL_SOURCE = ROOT / "visualizaciones" / "sistema-domus-fragment.html"
VISUAL_STANDALONE = ROOT / "visualizaciones" / "sistema-domus.html"
WIKILINK = re.compile(r"\[\[([^\]|#]+)")

EXPECTED_FIRMWARE_PINS = {
    "PIN_HUMEDAD": 1,
    "PIN_NIVEL_AGUA": 2,
    "PIN_LDR": 3,
    "PIN_RELE_BOMBA": 4,
    "PIN_RELE_LUZ_SALA": 5,
    "PIN_RELE_LUZ_CUARTO": 6,
    "PIN_RELE_VENTILADOR": 7,
    "PIN_RELE_LUZ_INVERNADERO": 8,
    "PIN_PIR": 9,
    "PIN_PARO_EMERGENCIA": 10,
    "PIN_MIC_OFF": 11,
    "PIN_BOTON_DEMO": 12,
    "I2C_SCL_PIN": 13,
    "PIN_DHT11": 14,
    "I2C_SDA_PIN": 21,
}


def run_tests(directory: Path) -> bool:
    sys.path.insert(0, str(directory))
    try:
        suite = unittest.defaultTestLoader.discover(
            str(directory), pattern="test_*.py"
        )
        return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    finally:
        sys.path.remove(str(directory))


def validate_vault() -> list[str]:
    errors: list[str] = []
    markdown_files = list(VAULT.glob("*.md"))
    available = {path.stem.casefold() for path in markdown_files}

    for number in range(38):
        prefix = f"{number:02d} - "
        if not any(path.name.startswith(prefix) for path in markdown_files):
            errors.append(f"Falta una nota de plan con prefijo {prefix!r}")

    for source in markdown_files:
        text = source.read_text(encoding="utf-8")
        for target in WIKILINK.findall(text):
            normalized = target.strip().replace("\\", "/").split("/")[-1]
            if normalized.casefold() not in available:
                errors.append(f"{source.name}: enlace inexistente [[{target}]]")
    return errors


def validate_current_decisions() -> list[str]:
    """Comprueba las decisiones activas que no deben volver a divergir."""
    errors: list[str] = []
    if not CURRENT_DECISION.is_file():
        return ["Falta la nota 36 de configuración final"]

    decision = CURRENT_DECISION.read_text(encoding="utf-8")
    guide = CURRENT_BUILD_GUIDE.read_text(encoding="utf-8")
    config = BENCH_CONFIG.read_text(encoding="utf-8")
    bench_guide = CURRENT_BENCH_GUIDE.read_text(encoding="utf-8")
    required = {
        "Nota 36": (decision, "módulo de 4 relés"),
        "Geometría v4": (decision, "800 × 520 mm"),
        "Guía Ultimate": (guide, "Base total: **800 × 520 mm**"),
        "Firmware de banco": (
            config,
            "constexpr bool ACTIVA_LOW[] = {true, true, true, true, true};",
        ),
        "Perfil N16R8": (config, 'PERFIL_PLACA[] = "ESP32-S3-N16R8"'),
        "Ronda sin compras": (bench_guide, "B01-B05"),
        "Salidas bloqueadas en ronda": (bench_guide, "SALIDAS_HABILITADAS=false"),
    }
    for owner, (text, term) in required.items():
        if " ".join(term.split()).casefold() not in " ".join(text.split()).casefold():
            errors.append(f"{owner}: falta decisión vigente {term!r}")
    return errors


def validate_firmware_wiring_contract() -> list[str]:
    """Evita que firmware y manual de cableado diverjan silenciosamente."""
    errors: list[str] = []
    firmware = FIRMWARE.read_text(encoding="utf-8")
    manual = MASTER_WIRING.read_text(encoding="utf-8")

    for symbol, expected_pin in EXPECTED_FIRMWARE_PINS.items():
        match = re.search(
            rf"^#define\s+{re.escape(symbol)}\s+(\d+)\b",
            firmware,
            flags=re.MULTILINE,
        )
        if not match:
            errors.append(f"Firmware: no se encontró {symbol}")
            continue
        actual_pin = int(match.group(1))
        if actual_pin != expected_pin:
            errors.append(
                f"Firmware: {symbol}=GPIO{actual_pin}; contrato esperado GPIO{expected_pin}"
            )
        if f"`GPIO{actual_pin}`" not in manual and f"GPIO{actual_pin}" not in manual:
            errors.append(
                f"Manual maestro: no documenta {symbol} en GPIO{actual_pin}"
            )

    required_manual_terms = (
        "LCD1602 con backpack I2C de cuatro pines",
        "TP4056 y una celda 1S",
        "INMP441, seis pines",
        "MAX98357A y altavoz",
        "Lector microSD SPI",
        "WS2812 y adaptación de nivel",
        "No unir directamente fuente USB,",
        "no conectar a GND",
    )
    for term in required_manual_terms:
        if term not in manual:
            errors.append(f"Manual maestro: falta requisito {term!r}")
    return errors


def validate_visualization() -> list[str]:
    errors: list[str] = []
    for path in (VISUAL_SOURCE, VISUAL_STANDALONE):
        if not path.is_file():
            errors.append(f"Visualización: falta {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in (
            "PROJECT DOMUS — sistema completo",
            "GPIO21 SDA · 13 SCL",
            "GPIO4–8 · 5 V",
            "TP4056 + 1S",
            "Ningún GPIO admite 5 V",
        ):
            if term not in text:
                errors.append(f"{path.name}: falta {term!r}")
    if VISUAL_SOURCE.is_file() and VISUAL_SOURCE.stat().st_size >= 1_000_000:
        errors.append("Visualización: el fragmento supera 1 MB")
    return errors


def main() -> int:
    tests_ok = (
        run_tests(SIMULATOR)
        and run_tests(FIRMWARE_TESTS)
        and run_tests(PLAN_TESTS)
    )
    vault_errors = (
        validate_vault()
        + validate_current_decisions()
        + validate_firmware_wiring_contract()
        + validate_visualization()
    )
    for error in vault_errors:
        print(f"ERROR PLANES: {error}", file=sys.stderr)

    if tests_ok and not vault_errors:
        print("VALIDACION_OK: lógica, decisiones vigentes, firmware y planos comprobados")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
