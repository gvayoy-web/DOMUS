import unittest

from domus_core import Actuator, DomusCore, Mode


class DomusCoreTests(unittest.TestCase):
    def setUp(self):
        self.domus = DomusCore()
        self.domus.reset()

    def test_safe_boot(self):
        self.assertTrue(all(not state for state in self.domus.states.values()))

    def test_irrigation_hysteresis(self):
        self.domus.sensors.soil_pct = 35
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.PUMP])
        self.domus.sensors.soil_pct = 44
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.PUMP])
        self.domus.sensors.soil_pct = 45
        self.domus.evaluate()
        self.assertFalse(self.domus.states[Actuator.PUMP])

    def test_low_water_blocks_pump(self):
        self.domus.sensors.soil_pct = 10
        self.domus.sensors.water_level_pct = 5
        self.domus.evaluate()
        self.assertFalse(self.domus.states[Actuator.PUMP])

    def test_pump_timeout_requires_rearm(self):
        self.domus.apply_local_command("RIEGO_ON")
        self.domus.advance(121)
        self.assertFalse(self.domus.states[Actuator.PUMP])
        self.assertEqual(self.domus.modes[Actuator.PUMP], Mode.MANUAL_OFF)

    def test_manual_off_is_not_overridden(self):
        self.domus.sensors.temperature_c = 35
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.FAN])
        self.domus.apply_local_command("VENTILADOR_OFF")
        self.domus.advance(30)
        self.assertFalse(self.domus.states[Actuator.FAN])

    def test_return_to_auto(self):
        self.domus.sensors.temperature_c = 35
        self.domus.apply_local_command("VENTILADOR_OFF")
        self.domus.return_to_auto(Actuator.FAN)
        self.assertTrue(self.domus.states[Actuator.FAN])

    def test_fan_hysteresis(self):
        self.domus.sensors.temperature_c = 28
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.FAN])
        self.domus.sensors.temperature_c = 27
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.FAN])
        self.domus.sensors.temperature_c = 26
        self.domus.evaluate()
        self.assertFalse(self.domus.states[Actuator.FAN])

    def test_living_light_requires_dark_and_presence(self):
        self.domus.sensors.light_pct = 10
        self.domus.sensors.presence = False
        self.domus.evaluate()
        self.assertFalse(self.domus.states[Actuator.LIVING_LIGHT])
        self.domus.sensors.presence = True
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.LIVING_LIGHT])

    def test_presence_hold_expires(self):
        self.domus.sensors.light_pct = 10
        self.domus.sensors.presence = True
        self.domus.evaluate()
        self.domus.sensors.presence = False
        self.domus.advance(31)
        self.assertFalse(self.domus.states[Actuator.LIVING_LIGHT])

    def test_greenhouse_light_hysteresis(self):
        self.domus.sensors.light_pct = 25
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.GREENHOUSE_LIGHT])
        self.domus.sensors.light_pct = 39
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.GREENHOUSE_LIGHT])
        self.domus.sensors.light_pct = 40
        self.domus.evaluate()
        self.assertFalse(self.domus.states[Actuator.GREENHOUSE_LIGHT])

    def test_sensor_failure_is_fail_safe(self):
        self.domus.sensors.soil_pct = 10
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.PUMP])
        self.domus.sensors.soil_pct = None
        self.domus.evaluate()
        self.assertFalse(self.domus.states[Actuator.PUMP])

    def test_low_confidence_voice_is_rejected(self):
        accepted = self.domus.apply_local_command("RIEGO_ON", confidence=0.60)
        self.assertFalse(accepted)
        self.assertFalse(self.domus.states[Actuator.PUMP])

    def test_emergency_stop(self):
        for actuator in Actuator:
            self.domus.set_mode(actuator, Mode.MANUAL_ON)
        self.domus.emergency_stop()
        self.assertTrue(all(not state for state in self.domus.states.values()))
        self.assertTrue(all(mode == Mode.MANUAL_OFF for mode in self.domus.modes.values()))

    def test_all_five_actuators_accept_manual_on_and_off(self):
        commands = {
            Actuator.PUMP: ("RIEGO_ON", "RIEGO_OFF"),
            Actuator.LIVING_LIGHT: ("LUZ_SALA_ON", "LUZ_SALA_OFF"),
            Actuator.BEDROOM_LIGHT: ("LUZ_CUARTO_ON", "LUZ_CUARTO_OFF"),
            Actuator.FAN: ("VENTILADOR_ON", "VENTILADOR_OFF"),
            Actuator.GREENHOUSE_LIGHT: ("INVERNADERO_ON", "INVERNADERO_OFF"),
        }
        for actuator, (on_command, off_command) in commands.items():
            self.assertTrue(self.domus.apply_local_command(on_command, from_voice=False))
            self.assertTrue(self.domus.states[actuator])
            self.assertTrue(self.domus.apply_local_command(off_command, from_voice=False))
            self.assertFalse(self.domus.states[actuator])

    def test_mic_off_rejects_voice_but_not_physical_control(self):
        self.domus.sensors.mic_enabled = False
        self.assertFalse(self.domus.apply_local_command("VENTILADOR_ON"))
        self.assertFalse(self.domus.states[Actuator.FAN])
        self.assertTrue(
            self.domus.apply_local_command("VENTILADOR_ON", from_voice=False)
        )
        self.assertTrue(self.domus.states[Actuator.FAN])

    def test_micro_sd_read_write_contract(self):
        self.assertFalse(self.domus.write_storage("estado.txt", "ok"))
        self.assertTrue(self.domus.mount_storage())
        self.assertTrue(self.domus.write_storage("estado.txt", "ok"))
        self.assertEqual(self.domus.read_storage("estado.txt"), "ok")

    def test_jarvis_response_matches_result(self):
        self.assertTrue(self.domus.apply_local_command("LUZ_SALA_ON"))
        self.assertEqual(self.domus.last_response, "He encendido Luz sala.")
        self.domus.sensors.water_level_pct = 0
        self.assertTrue(self.domus.apply_local_command("RIEGO_ON"))
        self.assertEqual(
            self.domus.last_response,
            "No puedo regar: el depósito no tiene agua suficiente.",
        )

    def test_emergency_blocks_reactivation_until_rearmed(self):
        self.domus.emergency_stop()
        self.assertFalse(
            self.domus.apply_local_command("VENTILADOR_ON", from_voice=False)
        )
        self.assertFalse(self.domus.states[Actuator.FAN])
        self.assertTrue(self.domus.emergency_active)
        self.domus.rearm_emergency()
        self.assertFalse(self.domus.emergency_active)
        self.assertEqual(self.domus.modes[Actuator.FAN], Mode.MANUAL_OFF)
        self.domus.apply_local_command("VENTILADOR_ON", from_voice=False)
        self.assertTrue(self.domus.states[Actuator.FAN])

    def test_safe_mode_blocks_outputs_until_explicit_recovery(self):
        self.domus.apply_local_command("VENTILADOR_ON", from_voice=False)
        self.domus.enter_safe_mode("memoria_critica")
        self.assertTrue(all(not state for state in self.domus.states.values()))
        self.assertFalse(
            self.domus.apply_local_command("LUZ_SALA_ON", from_voice=False)
        )
        self.assertFalse(self.domus.recover_safe_mode(memory_ok=False))
        self.assertTrue(self.domus.safe_mode_active)
        self.assertTrue(self.domus.recover_safe_mode(memory_ok=True))
        self.assertTrue(all(not state for state in self.domus.states.values()))
        self.assertTrue(all(mode == Mode.MANUAL_OFF for mode in self.domus.modes.values()))

    def test_command_rate_limit_preserves_emergency_stop(self):
        for _ in range(self.domus.thresholds.max_commands_per_second):
            self.assertTrue(
                self.domus.apply_local_command("LUZ_SALA_OFF", from_voice=False)
            )
        self.assertFalse(
            self.domus.apply_local_command("LUZ_SALA_ON", from_voice=False)
        )
        self.assertTrue(self.domus.apply_local_command("PARO", from_voice=False))
        self.assertTrue(self.domus.emergency_active)


if __name__ == "__main__":
    unittest.main(verbosity=2)
