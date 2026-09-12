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

    for number in range(51):
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
    config = BENCH_CONFIG.read_text(encoding="utf-8")
    bench_guide = CURRENT_BENCH_GUIDE.read_text(encoding="utf-8")
    # Guía Ultimate bajo planos/new fue eliminada del árbol (ver nota 46:150 y
    # nota 50): se verifica solo si existe, no bloquea la validación.
    if CURRENT_BUILD_GUIDE.is_file():
        guide = CURRENT_BUILD_GUIDE.read_text(encoding="utf-8")
    else:
        guide = ""
    required = {
        "Nota 36": (decision, "bomba de 3-6 V"),
        "Geometría v4": (decision, "800 × 520 mm"),
        "Firmware de banco": (
            config,
            "PERFIL_HARDWARE = PerfilHardware::ALFA_SENSORES",
        ),
        "Motor bomba deriva del perfil": (
            config,
            "HABILITAR_MOTOR_BOMBA = (PERFIL_HARDWARE == PerfilHardware::ALFA_BOMBA_1)",
        ),
        "Motor ventilador deriva del perfil": (
            config,
            "HABILITAR_MOTOR_VENTILADOR = (PERFIL_HARDWARE == PerfilHardware::ALFA_VENTILADOR_1)",
        ),
        "Buzzer deshabilitado en alfa": (
            config,
            "constexpr bool BUZZER_HABILITADO = false;",
        ),
        "Perfil N16R8": (config, 'PERFIL_PLACA[] = "ESP32-S3-N16R8"'),
        "Perfil alfa": (config, 'PERFIL_PRUEBA[] = "ALFA_UN_COSTADO_SIN_IR"'),
        "Validación por funciones activas": (config, "funcionesActivasSinAlias"),
        "Ronda sin compras": (bench_guide, "B01-B05"),
    }
    if guide:
        required["Guía Ultimate"] = (guide, "Base total: **800 × 520 mm**")
    for owner, (text, term) in required.items():
        if " ".join(term.split()).casefold() not in " ".join(text.split()).casefold():
            errors.append(f"{owner}: falta decisión vigente {term!r}")
    return errors


def validate_bench_contract() -> list[str]:
    """Contrato del esqueleto alfa vigente (ola 1, notas 46/47/50)."""
    errors: list[str] = []
    config = BENCH_CONFIG.read_text(encoding="utf-8")
    sketch = (ROOT / "firmware" / "domus_esqueleto" / "domus_esqueleto.ino").read_text(encoding="utf-8")
    lcd = (ROOT / "firmware" / "domus_esqueleto" / "domus_lcd.h").read_text(encoding="utf-8")
    voice = (ROOT / "firmware" / "domus_esqueleto" / "domus_voice.h").read_text(encoding="utf-8")
    for token in (
        "PIN_SUELO = 15", "PIN_NIVEL = 16", "PIN_LCD_SDA = 17",
        "PIN_LCD_SCL = 13", "PIN_BOTON = 18",
        "PERFIL_ALFA_BOMBA_1", "PERFIL_ALFA_VENTILADOR_1",
        "listaActiva", "funcionesActivasSinAlias",
    ):
        if token not in config:
            errors.append(f"Banco alfa: falta {token!r} en domus_config.h")
    # Ola 1: buffers propios, buzzer gateado, beep no bloqueante.
    for token in ("feedbackTitulo_[17]", "feedbackSub_[17]"):
        if token not in lcd:
            errors.append(f"LCD: falta buffer propio {token!r} (dangling buf)")
    if "delay(40)" in lcd:
        errors.append("LCD: splash aún usa delay(40) bloqueante")
    for token in ("ultima_[160]", "BUZZER_HABILITADO", "void actualizar()"):
        if token not in voice:
            errors.append(f"Voz: falta {token!r} (ola 1)")
    if "voz.actualizar()" not in sketch:
        errors.append("Esqueleto: loop() no llama voz.actualizar()")
    if "alternarIR(SALA, \"SALA ON\", \"SALA OFF\", 1, 2)" in sketch:
        errors.append("Esqueleto: alternarIR aún emite doble Jarvis (ola 1)")
    # SVG guía vigente.
    guia = ROOT / "visualizaciones" / "domus-alfa-guia-principiantes.svg"
    if guia.is_file():
        svg = guia.read_text(encoding="utf-8")
        if "GPIO12 reservado, sin conectar" not in svg:
            errors.append("SVG guía: GPIO12 aún figura como libre")
    else:
        errors.append("SVG guía: falta domus-alfa-guia-principiantes.svg")
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
            "PROJECT DOMUS — sistema completo v2",
            "GPIO21 SDA · 13 SCL",
            "AIN1=4 · BIN1=7",
            "Fusible 4 A",
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
        + validate_bench_contract()
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
