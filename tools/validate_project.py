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
PLAN_TESTS = ROOT / "hardware" / "planos" / "tests"
FIRMWARE = ROOT / "firmware" / "casa_inteligente_v4" / "casa_inteligente_v4.ino"
BENCH_CONFIG = ROOT / "firmware" / "legacy" / "domus_esqueleto" / "domus_config.h"
MASTER_WIRING = VAULT / "47 - Guia visual principiante conexiones alfa.md"
CURRENT_DECISION = VAULT / "36 - Configuracion final 1 mas 4 reles y planos v4.md"
CURRENT_BENCH_GUIDE = VAULT / "37 - Ronda de pruebas sin compras.md"
CURRENT_BUILD_GUIDE = ROOT / "hardware" / "planos" / "GUIA_MONTAJE_ULTIMATE.md"
VISUAL_SOURCE = ROOT / "visualizaciones" / "sistema-domus-fragment.html"
VISUAL_STANDALONE = ROOT / "visualizaciones" / "sistema-domus.html"
WIKILINK = re.compile(r"\[\[([^\]|#]+)")

EXPECTED_MAPA_PINS = {    "suelo": 15, "nivel": 16, "ldr": 3,
    "bomba": 4, "sala": 5, "cuarto": 6, "vent": 7, "inv": 8,
    "pir": 9, "paro": 10, "micOff": 11, "demo": 18,
    "scl": 13, "dht": 14, "sda": 17, "ir": 12,
}
TOTAL_SALIDAS_FIRMWARE = 5


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
    # Guía Ultimate canónica bajo hardware/planos (nota 54). Sus pruebas viven
    # junto al paquete para que la validación no acepte otra copia divergente.
    if CURRENT_BUILD_GUIDE.is_file():
        guide = CURRENT_BUILD_GUIDE.read_text(encoding="utf-8")
    else:
        guide = ""
    required = {
        "Nota 36": (decision, "bomba de 3-6 V"),
        "Geometría v4": (decision, "800 × 520 mm"),
        "Firmware de banco": (
            config,
            "constexpr PerfilHardware PERFIL_HARDWARE =",
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
            "constexpr bool BUZZER_HABILITADO = (DOMUS_BUZZER != 0)",
        ),
        "IR/DF/buzzer prohibidos en alfa": (config, "fuera del perfil alfa"),
        "Banderas seleccionables": (config, "#ifndef DOMUS_PERFIL_ALFA"),
        "Perfil N16R8": (config, 'PERFIL_PLACA[] = "ESP32-S3-N16R8"'),
        "Perfil alfa": (config, "PERFIL_PRUEBA = nombrePerfil(PERFIL_HARDWARE)"),
        "Nombre alfa por defecto": (config, '"ALFA_UN_COSTADO_SIN_IR"'),
        "Validación por funciones activas": (config, "funcionesActivasSinAlias"),
        "Ronda sin compras": (bench_guide, "B01-B05"),
    }
    if guide:
        required["Guía Ultimate"] = (guide, "Base total: **800 × 520 mm**")
    for owner, (text, term) in required.items():
        if " ".join(term.split()).casefold() not in " ".join(text.split()).casefold():
            errors.append(f"{owner}: falta decisión vigente {term!r}")
    return errors


def validate_casa_candidato() -> list[str]:
    """Contrato del candidato a producto (notas 53/54, jefatura)."""
    errors: list[str] = []
    candidate = ROOT / "firmware" / "casa_inteligente_v4" / "casa_inteligente_v4.ino"
    drivers = candidate.with_name("domus_drivers.h")
    if not drivers.is_file():
        return ["Candidato: falta domus_drivers.h (interfaces futuras)"]
    source = candidate.read_text(encoding="utf-8")
    header = drivers.read_text(encoding="utf-8")
    for token in (
        "enum class PerfilCasa", "BANCO_SIN_ACTUADORES",
        "LED_SIN_MOTORES", "MOTOR_PENDIENTE_DRIVER",
        "#ifndef DOMUS_PERFIL_CASA", "constexpr PerfilCasa PERFIL_CASA =",
        "struct MapaPinesCasa", "constexpr MapaPinesCasa MAPA_CASA = {",
        "constexpr bool SALIDA_FISICA_CASA[TOTAL_SALIDAS]",
        '"salida_no_instalada"', '"driver_no_listo"',
        "PERFIL_CANDIDATO=", '"CANDIDATO_BANCO_SIN_ACTUADORES"',
        '"CANDIDATO_LED_SIN_MOTORES"', '"CANDIDATO_MOTOR_PENDIENTE_DRIVER"',
    ):
        if token not in source:
            errors.append(f"Candidato: falta {token!r} en casa_inteligente_v4.ino")
    if '"FINAL"' in source:
        errors.append("Candidato: ningún binario puede llamarse FINAL (F1-F7)")
    for token in (
        "#define DOMUS_DRIVER_VALIDADO 0",
        "BACKEND_MOTOR_SELECCIONADO != BackendMotor::NINGUNO",
        "DOMUS_DRIVER_VALIDADO == 1",
        "constexpr bool AUDIO_CANDIDATO_HABILITADO = false;",
    ):
        if token not in header:
            errors.append(f"Candidato: falta {token!r} en domus_drivers.h")
    for token in ('#include "domus_ir_casa.h"', "constexpr bool IR_CASA_HABILITADO"):
        if token not in source:
            errors.append(f"Candidato: falta IR activo {token!r} en casa_inteligente_v4.ino")
    return errors


def validate_hardware_bundle() -> list[str]:
    """El modelo 3D canónico debe conservar juntos OBJ y su MTL."""
    errors: list[str] = []
    hardware = ROOT / "hardware"
    obj = hardware / "project_domus.obj"
    mtl = hardware / "project_domus.mtl"
    guide = ROOT / "hardware" / "GUIA_MONTAJE.md"
    generator = ROOT / "tools" / "generate_design.py"
    for path in (obj, mtl, guide, generator):
        if not path.is_file():
            errors.append(f"Hardware: falta {path.relative_to(ROOT)}")
    if errors:
        return errors
    if "mtllib project_domus.mtl" not in obj.read_text(encoding="utf-8", errors="replace"):
        errors.append("Hardware: project_domus.obj no enlaza project_domus.mtl")
    guide_text = guide.read_text(encoding="utf-8")
    for token in ("hardware/project_domus.obj", "hardware/project_domus.mtl"):
        if token not in guide_text:
            errors.append(f"Hardware: GUIA_MONTAJE.md no referencia {token}")
    generator_text = generator.read_text(encoding="utf-8")
    for token in (
        'HARDWARE_DIR / "project_domus.obj"',
        'HARDWARE_DIR / "project_domus.mtl"',
        "HARDWARE_DIR / 'plano_tecnico_domus.pdf'",
        'HARDWARE_DIR / "verificacion_geometria_v4.json"',
    ):
        if token not in generator_text:
            errors.append(f"Hardware: generador no usa ruta canónica {token}")
    return errors


def validate_bench_contract() -> list[str]:
    """Contrato del esqueleto alfa vigente (ola 1, notas 46/47/50)."""
    errors: list[str] = []
    config = BENCH_CONFIG.read_text(encoding="utf-8")
    legacy = ROOT / "firmware" / "legacy" / "domus_esqueleto"
    sketch = (legacy / "domus_esqueleto.ino").read_text(encoding="utf-8")
    lcd = (legacy / "domus_lcd.h").read_text(encoding="utf-8")
    voice = (legacy / "domus_voice.h").read_text(encoding="utf-8")
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
    """Evita que firmware y guía de cableado diverjan silenciosamente."""
    errors: list[str] = []
    firmware = FIRMWARE.read_text(encoding="utf-8")
    manual = MASTER_WIRING.read_text(encoding="utf-8")

    block = firmware.split("constexpr MapaPinesCasa MAPA_CASA = {", 1)
    if len(block) != 2:
        return ["Firmware: no se encontró MAPA_CASA como fuente única"]
    numbers = [int(n) for n in re.findall(r"\b(\d+)\b", block[1].split("};", 1)[0])]
    fields = list(EXPECTED_MAPA_PINS)
    if len(numbers) < len(fields) + TOTAL_SALIDAS_FIRMWARE:
        errors.append("Firmware: MAPA_CASA incompleto frente a EXPECTED_MAPA_PINS")
    else:
        for campo, esperado in EXPECTED_MAPA_PINS.items():
            actual = numbers[fields.index(campo)]
            if actual != esperado:
                errors.append(
                    f"Firmware: MAPA_CASA.{campo}=GPIO{actual}; contrato esperado GPIO{esperado}"
                )
        salidas = numbers[len(fields):len(fields) + TOTAL_SALIDAS_FIRMWARE]
        if salidas != [4, 5, 6, 7, 8]:
            errors.append(f"Firmware: MAPA_CASA.salidas={salidas}; esperado [4, 5, 6, 7, 8]")
    for campo, esperado in EXPECTED_MAPA_PINS.items():
        if campo in ("bomba", "vent"):
            continue  # Motores fuera de la guía alfa (nota 49, prueba separada)
        if f"GPIO{esperado}" not in manual:
            errors.append(
                f"Guía alfa: no documenta {campo} en GPIO{esperado}"
            )

    required_manual_terms = (
        "GPIO12 reservado",
        "3V3",
        "GND",
        "10 k",
    )
    for term in required_manual_terms:
        if term not in manual:
            errors.append(f"Guía alfa: falta requisito {term!r}")
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
        + validate_casa_candidato()
        + validate_hardware_bundle()
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
