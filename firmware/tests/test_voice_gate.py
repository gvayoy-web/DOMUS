import test_native_safety


class VoiceGateTests(test_native_safety.SafetyIntegrationTests):
    # Inherit the compiler helper, not its test cases.
    test_dispatch_outputs_emergency_recovery_and_timeout_together = None
    test_watchdog_failure_paths_and_calibration_integrity = None
    test_i2c_scan_is_bounded_when_bus_is_stuck = None

    def test_voice_gate_expiry_cancellation_invalid_confidence_and_overflow(self):
        self.run_cpp(r'''
#include <cassert>
#include <limits>
#include <initializer_list>
#include "domus_voice_contract.h"
int main() {
  DomusVoiceGate gate; DomusIntentTarget target{}; float confidence=0;
  auto intent=DomusIntent::LUZ_SALA_1_ON;
  assert(!gate.offer(intent,1,0,true,false,false));
  assert(!gate.offer(intent,1,0,false,true,false));
  assert(!gate.offer(intent,1,0,true,true,true));
  assert(!gate.offer(DomusIntent::DESCONOCIDO,1,0,true,true,false));
  assert(!gate.offer(static_cast<DomusIntent>(255),1,0,true,true,false));
  for(float bad : {std::numeric_limits<float>::quiet_NaN(),
      std::numeric_limits<float>::infinity(),-1.0f,1.1f,.74f})
    assert(!gate.offer(intent,bad,0,true,true,false));
  assert(gate.offer(intent,.9f,0,true,true,false));
  assert(!gate.offer(intent,.9f,0,true,true,false));
  assert(!gate.take(1001,true,false,target,confidence));
  assert(gate.offer(intent,.9f,0xfffffff0u,true,true,false));
  assert(gate.take(20,true,false,target,confidence));
  assert(target.relay==1 && target.on && confidence==.9f);
  assert(!gate.take(20,true,false,target,confidence));
  assert(gate.offer(intent,.9f,20,true,true,false));
  assert(!gate.take(21,false,false,target,confidence));
  assert(!gate.take(22,true,false,target,confidence));
  assert(gate.offer(intent,.9f,30,true,true,false));
  gate.cancel(); assert(!gate.take(31,true,false,target,confidence));
}
''')
