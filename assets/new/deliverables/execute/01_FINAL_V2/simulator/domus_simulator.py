"""Simulador gráfico offline de PROJECT DOMUS.

Ejecutar con: python domus_simulator.py
No abre puertos, no usa red y funciona con la biblioteca estándar de Python.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from domus_core import Actuator, DomusCore, Mode


class DomusSimulator(tk.Tk):
    TICK_MS = 250
    SIM_SECONDS_PER_TICK = 1.0

    def __init__(self) -> None:
        super().__init__()
        self.title("PROJECT DOMUS — laboratorio virtual offline")
        self.geometry("1180x760")
        self.minsize(960, 650)
        self.core = DomusCore()
        self.core.reset()
        self.running = False
        self.last_event_count = 0
        self.sensor_vars: dict[str, tk.Variable] = {}
        self.state_labels: dict[Actuator, ttk.Label] = {}
        self.mode_labels: dict[Actuator, ttk.Label] = {}
        self._build_ui()
        self._sync_sensors()
        self._refresh()
        self.after(self.TICK_MS, self._tick)

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("On.TLabel", foreground="#087f5b", font=("Segoe UI", 11, "bold"))
        style.configure("Off.TLabel", foreground="#c92a2a", font=("Segoe UI", 11, "bold"))
        style.configure("Mode.TLabel", font=("Consolas", 9))

        header = ttk.Frame(self, padding=(16, 12))
        header.pack(fill="x")
        ttk.Label(header, text="PROJECT DOMUS · laboratorio virtual", style="Title.TLabel").pack(side="left")
        self.clock_label = ttk.Label(header, text="t = 0 s", style="Subtitle.TLabel")
        self.clock_label.pack(side="right")

        controls = ttk.Frame(self, padding=(16, 0, 16, 10))
        controls.pack(fill="x")
        self.run_button = ttk.Button(controls, text="▶ Ejecutar", command=self._toggle_run)
        self.run_button.pack(side="left")
        ttk.Button(controls, text="+1 s", command=lambda: self._advance(1)).pack(side="left", padx=4)
        ttk.Button(controls, text="+10 s", command=lambda: self._advance(10)).pack(side="left", padx=4)
        ttk.Button(controls, text="+120 s", command=lambda: self._advance(120)).pack(side="left", padx=4)
        ttk.Button(controls, text="Reiniciar", command=self._reset).pack(side="left", padx=(18, 4))
        ttk.Button(controls, text="PARO DE EMERGENCIA", command=self._emergency).pack(side="right")
        ttk.Button(controls, text="Rearmar", command=self._rearm).pack(side="right", padx=4)
        ttk.Button(controls, text="Recuperar", command=self._recover).pack(side="right", padx=4)
        ttk.Button(controls, text="Simular fallo crítico", command=self._safe_mode).pack(side="right", padx=4)

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        left = ttk.Frame(body, padding=10)
        middle = ttk.Frame(body, padding=10)
        right = ttk.Frame(body, padding=10)
        body.add(left, weight=1)
        body.add(middle, weight=1)
        body.add(right, weight=2)

        self._build_sensor_panel(left)
        self._build_actuator_panel(middle)
        self._build_log_panel(right)

    def _add_scale(self, parent, row, key, label, start, end, initial, unit) -> None:
        var = tk.DoubleVar(value=initial)
        self.sensor_vars[key] = var
        value = ttk.Label(parent, text=f"{initial:.0f} {unit}", width=10)
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=(8, 0))
        value.grid(row=row, column=1, sticky="e", pady=(8, 0))
        scale = ttk.Scale(parent, from_=start, to=end, variable=var)
        scale.grid(row=row + 1, column=0, columnspan=2, sticky="ew")

        def update(*_):
            number = var.get()
            value.configure(text=f"{number:.1f} {unit}")
            self._sync_sensors()
            self.core.evaluate()
            self._refresh()

        var.trace_add("write", update)

    def _build_sensor_panel(self, panel) -> None:
        ttk.Label(panel, text="Sensores virtuales", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=0)
        self._add_scale(panel, 1, "soil", "Humedad de tierra", 0, 100, 55, "%")
        self._add_scale(panel, 3, "temperature", "Temperatura ambiental", 0, 50, 25, "°C")
        self._add_scale(panel, 5, "humidity", "Humedad del aire", 20, 90, 60, "%")
        self._add_scale(panel, 7, "light", "Luz ambiental", 0, 100, 60, "%")
        self._add_scale(panel, 9, "water", "Nivel del depósito", 0, 100, 80, "%")

        self.presence_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            panel,
            text="PIR: presencia detectada",
            variable=self.presence_var,
            command=self._sensor_toggle,
        ).grid(row=11, column=0, columnspan=2, sticky="w", pady=(14, 4))

        self.mic_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            panel,
            text="MIC ON (interruptor físico)",
            variable=self.mic_var,
            command=self._sensor_toggle,
        ).grid(row=12, column=0, columnspan=2, sticky="w", pady=4)

        failures = ttk.LabelFrame(panel, text="Inyección de fallos", padding=8)
        failures.grid(row=13, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        self.fail_soil = tk.BooleanVar(value=False)
        self.fail_dht = tk.BooleanVar(value=False)
        self.fail_ldr = tk.BooleanVar(value=False)
        self.fail_level = tk.BooleanVar(value=False)
        for text, var in [
            ("Falla humedad de tierra", self.fail_soil),
            ("Falla DHT", self.fail_dht),
            ("Falla LDR", self.fail_ldr),
            ("Falla nivel de agua", self.fail_level),
        ]:
            ttk.Checkbutton(failures, text=text, variable=var, command=self._sensor_toggle).pack(anchor="w")

    def _build_actuator_panel(self, panel) -> None:
        ttk.Label(panel, text="Actuadores locales", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            panel,
            text="AUTO / ON físico / OFF físico. Una orden manual permanece hasta volver a AUTO.",
            wraplength=300,
        ).pack(anchor="w", pady=(0, 8))
        for actuator in Actuator:
            frame = ttk.LabelFrame(panel, text=actuator.value, padding=8)
            frame.pack(fill="x", pady=5)
            status_row = ttk.Frame(frame)
            status_row.pack(fill="x")
            status = ttk.Label(status_row, text="OFF", style="Off.TLabel")
            status.pack(side="left")
            mode = ttk.Label(status_row, text="AUTO", style="Mode.TLabel")
            mode.pack(side="right")
            self.state_labels[actuator] = status
            self.mode_labels[actuator] = mode
            buttons = ttk.Frame(frame)
            buttons.pack(fill="x", pady=(6, 0))
            ttk.Button(buttons, text="AUTO", command=lambda a=actuator: self._set_mode(a, Mode.AUTO)).pack(side="left")
            ttk.Button(buttons, text="ON", command=lambda a=actuator: self._set_mode(a, Mode.MANUAL_ON)).pack(side="left", padx=3)
            ttk.Button(buttons, text="OFF", command=lambda a=actuator: self._set_mode(a, Mode.MANUAL_OFF)).pack(side="left")

    def _build_log_panel(self, panel) -> None:
        ttk.Label(panel, text="Registro y diagnóstico", style="Title.TLabel").pack(anchor="w")
        self.summary = ttk.Label(panel, text="", justify="left", font=("Consolas", 10))
        self.summary.pack(fill="x", pady=(6, 8))
        self.log = tk.Text(panel, height=24, state="disabled", font=("Consolas", 9), wrap="word")
        self.log.pack(fill="both", expand=True)

    def _sync_sensors(self) -> None:
        if not self.sensor_vars:
            return
        self.core.sensors.soil_pct = None if self.fail_soil.get() else self.sensor_vars["soil"].get()
        self.core.sensors.temperature_c = None if self.fail_dht.get() else self.sensor_vars["temperature"].get()
        self.core.sensors.air_humidity_pct = None if self.fail_dht.get() else self.sensor_vars["humidity"].get()
        self.core.sensors.light_pct = None if self.fail_ldr.get() else self.sensor_vars["light"].get()
        self.core.sensors.water_level_pct = None if self.fail_level.get() else self.sensor_vars["water"].get()
        self.core.sensors.presence = self.presence_var.get()
        self.core.sensors.mic_enabled = self.mic_var.get()

    def _sensor_toggle(self) -> None:
        self._sync_sensors()
        self.core.evaluate()
        self._refresh()

    def _set_mode(self, actuator: Actuator, mode: Mode) -> None:
        self._sync_sensors()
        self.core.set_mode(actuator, mode)
        self.core.evaluate()
        self._refresh()

    def _advance(self, seconds: float) -> None:
        self._sync_sensors()
        self.core.advance(seconds)
        self._refresh()

    def _toggle_run(self) -> None:
        self.running = not self.running
        self.run_button.configure(text="⏸ Pausar" if self.running else "▶ Ejecutar")

    def _reset(self) -> None:
        self.running = False
        self.run_button.configure(text="▶ Ejecutar")
        self.core.reset()
        self.last_event_count = 0
        self._sync_sensors()
        self._refresh(clear_log=True)

    def _emergency(self) -> None:
        self.core.emergency_stop()
        self._refresh()

    def _rearm(self) -> None:
        self.core.rearm_emergency()
        self._refresh()

    def _recover(self) -> None:
        self.core.recover_safe_mode()
        self._refresh()

    def _safe_mode(self) -> None:
        self.core.enter_safe_mode("fallo crítico simulado")
        self._refresh()

    def _tick(self) -> None:
        if self.running:
            self._advance(self.SIM_SECONDS_PER_TICK)
        self.after(self.TICK_MS, self._tick)

    def _refresh(self, clear_log: bool = False) -> None:
        self.clock_label.configure(text=f"t = {self.core.time_s:.0f} s")
        for actuator in Actuator:
            enabled = self.core.states[actuator]
            self.state_labels[actuator].configure(
                text="ON" if enabled else "OFF",
                style="On.TLabel" if enabled else "Off.TLabel",
            )
            self.mode_labels[actuator].configure(text=self.core.modes[actuator].value)

        s = self.core.sensors
        self.summary.configure(
            text=(
                f"Tierra: {self._fmt(s.soil_pct, '%')}\n"
                f"Ambiente: {self._fmt(s.temperature_c, '°C')} / {self._fmt(s.air_humidity_pct, '%HR')}\n"
                f"Luz: {self._fmt(s.light_pct, '%')}\n"
                f"Depósito: {self._fmt(s.water_level_pct, '%')}\n"
                f"PIR: {'ACTIVO' if s.presence else 'libre'} · MIC: {'ON' if s.mic_enabled else 'OFF'}\n"
                f"Emergencia: {'ACTIVA' if self.core.emergency_active else 'libre'} · "
                f"Modo seguro: {'ACTIVO' if self.core.safe_mode_active else 'libre'}"
                f"{f' ({self.core.safe_mode_reason})' if self.core.safe_mode_active else ''}"
            )
        )

        if clear_log:
            self.log.configure(state="normal")
            self.log.delete("1.0", "end")
            self.log.configure(state="disabled")
        if len(self.core.events) > self.last_event_count:
            self.log.configure(state="normal")
            for event in self.core.events[self.last_event_count:]:
                self.log.insert("end", f"[{event.time_s:7.1f}s] {event.level:5} {event.message}\n")
            self.log.see("end")
            self.log.configure(state="disabled")
            self.last_event_count = len(self.core.events)

    @staticmethod
    def _fmt(value, unit: str) -> str:
        return "ERROR" if value is None else f"{value:.1f}{unit}"


if __name__ == "__main__":
    DomusSimulator().mainloop()
