import unittest

from domus_core import Actuator, DomusCore, Mode


class DomusCoreTests(unittest.TestCase):
    def setUp(self):
        self.domus = DomusCore()
        self.domus.reset()

    def test_safe_boot(self):
        self.assertTrue(all(not state for state in self.domus.states.values()))

    def test_irrigation_hysteresis(self):
        self.domus.sensors.soil_pct = 25
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.PUMP])
        self.domus.sensors.soil_pct = 38
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.PUMP])
        self.domus.sensors.soil_pct = 46
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
        self.domus.sensors.temperature_c = 30
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.FAN])
        self.domus.sensors.temperature_c = 28
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
        self.domus.sensors.light_pct = 10
        self.domus.evaluate()
        self.assertTrue(self.domus.states[Actuator.GREENHOUSE_LIGHT])
        self.domus.sensors.light_pct = 28
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
