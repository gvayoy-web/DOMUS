"""Gemelo digital offline de PROJECT DOMUS.

No contiene Bluetooth, Wi-Fi, sockets, HTTP ni dependencias móviles. Las mismas
reglas pueden trasladarse después al firmware del ESP32-S3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Mode(str, Enum):
    AUTO = "AUTO"
    MANUAL_ON = "MANUAL_ON"
    MANUAL_OFF = "MANUAL_OFF"


class Actuator(str, Enum):
    PUMP = "Bomba"
    LIVING_LIGHT = "Luz sala"
    BEDROOM_LIGHT = "Luz dormitorio"
    FAN = "Ventilador"
    GREENHOUSE_LIGHT = "Luz invernadero"


@dataclass
class Sensors:
    soil_pct: Optional[float] = 55.0
    temperature_c: Optional[float] = 25.0
    air_humidity_pct: Optional[float] = 60.0
    light_pct: Optional[float] = 60.0
    water_level_pct: Optional[float] = 80.0
    presence: bool = False
    mic_enabled: bool = True


@dataclass
class Thresholds:
    soil_on_pct: float = 30.0
    soil_off_pct: float = 45.0
    minimum_water_pct: float = 20.0
    pump_max_seconds: float = 120.0
    fan_on_c: float = 29.0
    fan_off_c: float = 27.0
    dark_on_pct: float = 20.0
    dark_off_pct: float = 35.0
    presence_hold_seconds: float = 30.0
    voice_min_confidence: float = 0.75


@dataclass
class Event:
    time_s: float
    level: str
    message: str


@dataclass
class DomusCore:
    sensors: Sensors = field(default_factory=Sensors)
    thresholds: Thresholds = field(default_factory=Thresholds)
    time_s: float = 0.0
    states: Dict[Actuator, bool] = field(
        default_factory=lambda: {actuator: False for actuator in Actuator}
    )
    modes: Dict[Actuator, Mode] = field(
        default_factory=lambda: {actuator: Mode.AUTO for actuator in Actuator}
    )
    events: List[Event] = field(default_factory=list)
    pump_started_s: Optional[float] = None
    last_presence_s: Optional[float] = None

    def log(self, level: str, message: str) -> None:
        if self.events and self.events[-1].message == message:
            return
        self.events.append(Event(self.time_s, level, message))
        if len(self.events) > 250:
            del self.events[:-250]

    def _set_state(self, actuator: Actuator, enabled: bool, reason: str) -> None:
        if self.states[actuator] == enabled:
            return
        self.states[actuator] = enabled
        if actuator == Actuator.PUMP:
            self.pump_started_s = self.time_s if enabled else None
        self.log("ACT", f"{actuator.value}: {'ON' if enabled else 'OFF'} — {reason}")

    def set_mode(self, actuator: Actuator, mode: Mode) -> None:
        self.modes[actuator] = mode
        self.log("MODE", f"{actuator.value} → {mode.value}")
        if mode == Mode.MANUAL_ON:
            if actuator == Actuator.PUMP and not self._water_available():
                self._set_state(actuator, False, "bloqueada por depósito bajo")
                self.log("SAFE", "Orden manual de bomba rechazada: depósito bajo")
            else:
                self._set_state(actuator, True, "orden física/manual")
        elif mode == Mode.MANUAL_OFF:
            self._set_state(actuator, False, "orden física/manual")

    def return_to_auto(self, actuator: Actuator) -> None:
        self.set_mode(actuator, Mode.AUTO)
        self.evaluate()

    def apply_local_command(self, intent: str, confidence: float = 1.0) -> bool:
        """Aplica una intención local de botones o Jarvis, sin transporte de red."""
        if confidence < self.thresholds.voice_min_confidence:
            self.log("VOICE", f"Orden rechazada por confianza baja ({confidence:.2f})")
            return False
        mapping = {
            "RIEGO_ON": (Actuator.PUMP, Mode.MANUAL_ON),
            "RIEGO_OFF": (Actuator.PUMP, Mode.MANUAL_OFF),
            "RIEGO_AUTO": (Actuator.PUMP, Mode.AUTO),
            "LUZ_SALA_ON": (Actuator.LIVING_LIGHT, Mode.MANUAL_ON),
            "LUZ_SALA_OFF": (Actuator.LIVING_LIGHT, Mode.MANUAL_OFF),
            "LUZ_SALA_AUTO": (Actuator.LIVING_LIGHT, Mode.AUTO),
            "LUZ_CUARTO_ON": (Actuator.BEDROOM_LIGHT, Mode.MANUAL_ON),
            "LUZ_CUARTO_OFF": (Actuator.BEDROOM_LIGHT, Mode.MANUAL_OFF),
            "LUZ_CUARTO_AUTO": (Actuator.BEDROOM_LIGHT, Mode.AUTO),
            "VENTILADOR_ON": (Actuator.FAN, Mode.MANUAL_ON),
            "VENTILADOR_OFF": (Actuator.FAN, Mode.MANUAL_OFF),
            "VENTILADOR_AUTO": (Actuator.FAN, Mode.AUTO),
            "INVERNADERO_ON": (Actuator.GREENHOUSE_LIGHT, Mode.MANUAL_ON),
            "INVERNADERO_OFF": (Actuator.GREENHOUSE_LIGHT, Mode.MANUAL_OFF),
            "INVERNADERO_AUTO": (Actuator.GREENHOUSE_LIGHT, Mode.AUTO),
        }
        target = mapping.get(intent.strip().upper())
        if target is None:
            self.log("VOICE", f"Intención desconocida: {intent}")
            return False
        self.set_mode(*target)
        return True

    def _water_available(self) -> bool:
        level = self.sensors.water_level_pct
        return level is not None and level >= self.thresholds.minimum_water_pct

    def _evaluate_pump(self) -> None:
        if not self._water_available():
            self._set_state(Actuator.PUMP, False, "protección por depósito bajo/fallo")
            if self.sensors.water_level_pct is None:
                self.log("SAFE", "Bomba bloqueada: sensor de nivel sin lectura")
            elif self.sensors.water_level_pct < self.thresholds.minimum_water_pct:
                self.log("SAFE", "Bomba bloqueada: depósito bajo")
            return

        if self.states[Actuator.PUMP] and self.pump_started_s is not None:
            elapsed = self.time_s - self.pump_started_s
            if elapsed >= self.thresholds.pump_max_seconds:
                self._set_state(Actuator.PUMP, False, "límite máximo de seguridad")
                self.modes[Actuator.PUMP] = Mode.MANUAL_OFF
                self.log("SAFE", "Bomba detenida por tiempo máximo; requiere rearme")
                return

        if self.modes[Actuator.PUMP] != Mode.AUTO:
            return
        soil = self.sensors.soil_pct
        if soil is None:
            self._set_state(Actuator.PUMP, False, "fallo del sensor de suelo")
            self.log("SAFE", "Riego automático suspendido: humedad inválida")
        elif not self.states[Actuator.PUMP] and soil <= self.thresholds.soil_on_pct:
            self._set_state(Actuator.PUMP, True, "tierra seca")
        elif self.states[Actuator.PUMP] and soil >= self.thresholds.soil_off_pct:
            self._set_state(Actuator.PUMP, False, "humedad suficiente")

    def _evaluate_fan(self) -> None:
        if self.modes[Actuator.FAN] != Mode.AUTO:
            return
        temp = self.sensors.temperature_c
        if temp is None:
            self._set_state(Actuator.FAN, False, "fallo de temperatura")
            self.log("SAFE", "Ventilación automática suspendida: DHT sin lectura")
        elif not self.states[Actuator.FAN] and temp >= self.thresholds.fan_on_c:
            self._set_state(Actuator.FAN, True, "temperatura alta")
        elif self.states[Actuator.FAN] and temp <= self.thresholds.fan_off_c:
            self._set_state(Actuator.FAN, False, "temperatura normal")

    def _evaluate_lights(self) -> None:
        light = self.sensors.light_pct
        if self.sensors.presence:
            self.last_presence_s = self.time_s

        if self.modes[Actuator.LIVING_LIGHT] == Mode.AUTO:
            recent_presence = (
                self.last_presence_s is not None
                and self.time_s - self.last_presence_s <= self.thresholds.presence_hold_seconds
            )
            should_on = light is not None and light <= self.thresholds.dark_on_pct and recent_presence
            should_off = (
                light is None
                or light >= self.thresholds.dark_off_pct
                or not recent_presence
            )
            if should_on:
                self._set_state(Actuator.LIVING_LIGHT, True, "oscuridad y presencia")
            elif should_off:
                self._set_state(Actuator.LIVING_LIGHT, False, "sin presencia o luz suficiente")

        if self.modes[Actuator.GREENHOUSE_LIGHT] == Mode.AUTO:
            if light is None:
                self._set_state(Actuator.GREENHOUSE_LIGHT, False, "fallo del LDR")
            elif not self.states[Actuator.GREENHOUSE_LIGHT] and light <= self.thresholds.dark_on_pct:
                self._set_state(Actuator.GREENHOUSE_LIGHT, True, "oscuridad")
            elif self.states[Actuator.GREENHOUSE_LIGHT] and light >= self.thresholds.dark_off_pct:
                self._set_state(Actuator.GREENHOUSE_LIGHT, False, "luz suficiente")

        # El dormitorio no debe encenderse solo: queda bajo botón/Jarvis local.
        if self.modes[Actuator.BEDROOM_LIGHT] == Mode.AUTO:
            self._set_state(Actuator.BEDROOM_LIGHT, False, "AUTO seguro sin presencia dedicada")

    def evaluate(self) -> None:
        self._evaluate_pump()
        self._evaluate_fan()
        self._evaluate_lights()

    def advance(self, seconds: float = 1.0) -> None:
        if seconds < 0:
            raise ValueError("El tiempo no puede retroceder")
        self.time_s += seconds
        self.evaluate()

    def emergency_stop(self) -> None:
        for actuator in Actuator:
            self.modes[actuator] = Mode.MANUAL_OFF
            self._set_state(actuator, False, "PARO DE EMERGENCIA")
        self.log("SAFE", "Todos los actuadores apagados")

    def reset(self) -> None:
        self.time_s = 0.0
        self.states = {actuator: False for actuator in Actuator}
        self.modes = {actuator: Mode.AUTO for actuator in Actuator}
        self.events.clear()
        self.pump_started_s = None
        self.last_presence_s = None
        self.log("BOOT", "Arranque seguro: todas las salidas apagadas")

    def snapshot(self) -> dict:
        return {
            "time_s": self.time_s,
            "sensors": vars(self.sensors).copy(),
            "states": {a.name: self.states[a] for a in Actuator},
            "modes": {a.name: self.modes[a].value for a in Actuator},
            "last_event": self.events[-1].message if self.events else "",
        }
