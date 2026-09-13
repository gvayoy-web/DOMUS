"""Campaña determinista semirreal del gemelo DOMUS.

Ejercita sensores variables, órdenes, fallos, reinicios y enclavamientos. No
simula tensión, corriente, ruido ADC ni tiempos eléctricos de una placa real.
"""
from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "assets/new/deliverables/execute/01_FINAL_V2/simulator/domus_core.py"
SPEC = importlib.util.spec_from_file_location("domus_core_semireal", CORE_PATH)
core_module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = core_module
SPEC.loader.exec_module(core_module)

Actuator = core_module.Actuator
DomusCore = core_module.DomusCore
Mode = core_module.Mode


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(seed: int = 20260906, steps: int = 10_000) -> dict:
    rng = random.Random(seed)
    house = DomusCore()
    house.reset()
    checks = 0
    emergency_injections = safe_mode_injections = resets = sensor_faults = 0

    for step in range(steps):
        house.sensors.soil_pct = max(0, min(100, (house.sensors.soil_pct or 50) + rng.uniform(-2, 2)))
        house.sensors.temperature_c = max(15, min(40, (house.sensors.temperature_c or 25) + rng.uniform(-.4, .4)))
        house.sensors.light_pct = max(0, min(100, (house.sensors.light_pct or 50) + rng.uniform(-4, 4)))
        house.sensors.water_level_pct = max(0, min(100, (house.sensors.water_level_pct or 70) + rng.uniform(-1, .5)))
        house.sensors.presence = rng.random() < .08

        event = rng.random()
        if event < .004:
            house.emergency_stop(); emergency_injections += 1
        elif event < .007:
            house.enter_safe_mode("caida_de_tension_simulada"); safe_mode_injections += 1
        elif event < .010:
            house.reset(); resets += 1
        elif event < .025:
            sensor_faults += 1
            setattr(house.sensors, rng.choice(("soil_pct", "temperature_c", "light_pct", "water_level_pct")), None)
        elif event < .055 and not house.emergency_active and not house.safe_mode_active:
            house.set_mode(rng.choice(tuple(Actuator)), rng.choice(tuple(Mode)))

        house.advance(rng.uniform(.05, 2.0))
        if house.emergency_active or house.safe_mode_active:
            require(not any(house.states.values()), "Una salida quedó activa bajo bloqueo")
        checks += 1
        if house.sensors.water_level_pct is None or house.sensors.water_level_pct < house.thresholds.minimum_water_pct:
            require(not house.states[Actuator.PUMP], "Bomba activa sin nivel seguro")
        checks += 1
        if house.sensors.temperature_c is None and house.modes[Actuator.FAN] == Mode.AUTO:
            require(not house.states[Actuator.FAN], "Ventilador AUTO activo con DHT inválido")
        checks += 1
        if house.sensors.light_pct is None and house.modes[Actuator.GREENHOUSE_LIGHT] == Mode.AUTO:
            require(not house.states[Actuator.GREENHOUSE_LIGHT], "Luz AUTO activa con LDR inválido")
        checks += 1

        if step % 251 == 0:
            was_blocked = house.emergency_active or house.safe_mode_active
            if house.emergency_active:
                house.rearm_emergency()
            if house.safe_mode_active:
                house.recover_safe_mode(memory_ok=True)
            if was_blocked:
                require(not any(house.states.values()), "El rearme encendió una carga")
                checks += 1

    return {"status": "PASS", "seed": seed, "steps": steps,
            "invariant_checks": checks, "emergency_injections": emergency_injections,
            "safe_mode_injections": safe_mode_injections, "simulated_resets": resets,
            "sensor_faults": sensor_faults, "bounded_event_log": len(house.events) <= 250,
            "scope": "gemelo digital semirreal; sin validación eléctrica"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
