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
    soil_on_pct: float = 35.0
    soil_off_pct: float = 45.0
    minimum_water_pct: float = 20.0
    pump_max_seconds: float = 120.0
    fan_on_c: float = 28.0
    fan_off_c: float = 26.0
    dark_on_pct: float = 25.0
    dark_off_pct: float = 40.0
    presence_hold_seconds: float = 30.0
    voice_min_confidence: float = 0.75
    max_commands_per_second: int = 12


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
    storage_mounted: bool = False
    storage_files: Dict[str, str] = field(default_factory=dict)
    last_response: str = ""
    emergency_active: bool = False
    safe_mode_active: bool = False
    safe_mode_reason: str = ""
    command_times_s: List[float] = field(default_factory=list)

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
        if self.emergency_active and mode == Mode.MANUAL_ON:
            self._set_state(actuator, False, "bloqueada por paro de emergencia")
            self.log("SAFE", f"Orden rechazada para {actuator.value}: emergencia activa")
            return
        if self.safe_mode_active and mode == Mode.MANUAL_ON:
            self._set_state(actuator, False, "bloqueada por modo seguro")
            self.log("SAFE", f"Orden rechazada para {actuator.value}: modo seguro")
            return
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

    def apply_local_command(
        self, intent: str, confidence: float = 1.0, *, from_voice: bool = True
    ) -> bool:
        """Aplica una intención de Jarvis o un control físico, sin red."""
        self.last_response = ""
        normalized_intent = intent.strip().upper()
        if from_voice and not self.sensors.mic_enabled:
            self.last_response = "Micrófono desactivado."
            self.log("VOICE", "Orden ignorada: MIC OFF")
            return False
        if from_voice and confidence < self.thresholds.voice_min_confidence:
            self.last_response = "No entendí la orden."
            self.log("VOICE", f"Orden rechazada por confianza baja ({confidence:.2f})")
            return False
        if normalized_intent != "PARO" and not self._admit_command():
            self.last_response = "Demasiadas órdenes; inténtalo de nuevo."
            self.log("SAFE", "Orden rechazada por límite de frecuencia")
            return False
        if normalized_intent == "PARO":
            self.emergency_stop()
            self.last_response = "Paro de emergencia activado."
            return True
        if normalized_intent == "REARMAR" and not from_voice:
            self.rearm_emergency()
            self.last_response = "Emergencia rearmada."
            return True
        if normalized_intent == "RECUPERAR" and not from_voice:
            recovered = self.recover_safe_mode()
            self.last_response = (
                "Modo seguro liberado." if recovered else "No es seguro recuperar todavía."
            )
            return recovered
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
        target = mapping.get(normalized_intent)
        if target is None:
            self.last_response = "No entendí la orden."
            self.log("VOICE", f"Intención desconocida: {intent}")
            return False
        if self.emergency_active and target[1] == Mode.MANUAL_ON:
            self.last_response = "No puedo encender dispositivos: paro de emergencia activo."
            self.log("SAFE", "Orden rechazada: paro de emergencia activo")
            return False
        if self.safe_mode_active and target[1] == Mode.MANUAL_ON:
            self.last_response = "No puedo encender dispositivos: modo seguro activo."
            self.log("SAFE", "Orden rechazada: modo seguro activo")
            return False
        self.set_mode(*target)
        actuator, mode = target
        if mode == Mode.AUTO:
            self.last_response = f"{actuator.value} volvió a modo automático."
        elif self.states[actuator]:
            self.last_response = f"He encendido {actuator.value}."
        elif actuator == Actuator.PUMP and not self._water_available():
            self.last_response = "No puedo regar: el depósito no tiene agua suficiente."
        else:
            self.last_response = f"He apagado {actuator.value}."
        return True

    def _admit_command(self) -> bool:
        window_start = self.time_s - 1.0
        self.command_times_s = [t for t in self.command_times_s if t > window_start]
        if len(self.command_times_s) >= self.thresholds.max_commands_per_second:
            return False
        self.command_times_s.append(self.time_s)
        return True

    def mount_storage(self, available: bool = True) -> bool:
        """Simula el lector microSD independiente del ESP32."""
        self.storage_mounted = available
        self.log("SD", "microSD montada" if available else "microSD no disponible")
        return self.storage_mounted

    def write_storage(self, path: str, content: str) -> bool:
        if not self.storage_mounted or not path:
            self.log("SD", "Escritura rechazada: microSD no montada o ruta vacía")
            return False
        self.storage_files[path] = content
        self.log("SD", f"Archivo escrito: {path}")
        return True

    def read_storage(self, path: str) -> Optional[str]:
        if not self.storage_mounted:
            self.log("SD", "Lectura rechazada: microSD no montada")
            return None
        return self.storage_files.get(path)

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
        if self.emergency_active or self.safe_mode_active:
            for actuator in Actuator:
                reason = "PARO DE EMERGENCIA" if self.emergency_active else "MODO SEGURO"
                self._set_state(actuator, False, reason)
            return
        self._evaluate_pump()
        self._evaluate_fan()
        self._evaluate_lights()

    def advance(self, seconds: float = 1.0) -> None:
        if seconds < 0:
            raise ValueError("El tiempo no puede retroceder")
        self.time_s += seconds
        self.evaluate()

    def emergency_stop(self) -> None:
        self.emergency_active = True
        for actuator in Actuator:
            self.modes[actuator] = Mode.MANUAL_OFF
            self._set_state(actuator, False, "PARO DE EMERGENCIA")
        self.log("SAFE", "Todos los actuadores apagados")

    def rearm_emergency(self) -> None:
        """Libera el bloqueo, sin encender cargas ni cambiar MANUAL_OFF."""
        self.emergency_active = False
        self.log("SAFE", "Emergencia rearmada; actuadores permanecen apagados")

    def enter_safe_mode(self, reason: str) -> None:
        """Degrada el sistema sin reiniciarlo y deja diagnóstico disponible."""
        self.safe_mode_active = True
        self.safe_mode_reason = reason or "desconocido"
        for actuator in Actuator:
            self.modes[actuator] = Mode.MANUAL_OFF
            self._set_state(actuator, False, "MODO SEGURO")
        self.log("SAFE", f"Modo seguro activo: {self.safe_mode_reason}")

    def recover_safe_mode(self, *, memory_ok: bool = True) -> bool:
        """Libera el modo seguro sin encender cargas ni restaurar AUTO."""
        if self.emergency_active or not memory_ok:
            self.log("SAFE", "Recuperación rechazada: condición insegura")
            return False
        self.safe_mode_active = False
        self.safe_mode_reason = ""
        self.log("SAFE", "Modo seguro liberado; actuadores permanecen apagados")
        return True

    def reset(self) -> None:
        self.time_s = 0.0
        self.states = {actuator: False for actuator in Actuator}
        self.modes = {actuator: Mode.AUTO for actuator in Actuator}
        self.events.clear()
        self.pump_started_s = None
        self.last_presence_s = None
        self.last_response = ""
        self.emergency_active = False
        self.safe_mode_active = False
        self.safe_mode_reason = ""
        self.command_times_s.clear()
        self.log("BOOT", "Arranque seguro: todas las salidas apagadas")

    def snapshot(self) -> dict:
        return {
            "time_s": self.time_s,
            "sensors": vars(self.sensors).copy(),
            "states": {a.name: self.states[a] for a in Actuator},
            "modes": {a.name: self.modes[a].value for a in Actuator},
            "last_event": self.events[-1].message if self.events else "",
            "last_response": self.last_response,
            "storage_mounted": self.storage_mounted,
            "emergency_active": self.emergency_active,
            "safe_mode_active": self.safe_mode_active,
            "safe_mode_reason": self.safe_mode_reason,
        }
