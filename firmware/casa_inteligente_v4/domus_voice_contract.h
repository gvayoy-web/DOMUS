#pragma once
#include <stddef.h>
#include <stdint.h>

enum class DomusIntent : uint8_t {
#define DOMUS_INTENT(symbol, relay, on) symbol,
#include "domus_intents.def"
#undef DOMUS_INTENT
  COUNT
};
struct DomusIntentTarget { int8_t relay; bool on; };
constexpr DomusIntentTarget DOMUS_INTENT_TARGETS[] = {
#define DOMUS_INTENT(symbol, relay, on) {relay, on},
#include "domus_intents.def"
#undef DOMUS_INTENT
};

// Range comparisons also reject NaN and infinities without fast-math assumptions.
inline bool domusVoiceConfidenceValid(float confidence, float threshold = 0.75f) {
  return threshold >= 0.75f && threshold <= 1.0f &&
         confidence >= threshold && confidence <= 1.0f;
}

// One pending result, consumed only by the control owner. Not thread-safe:
// transport across tasks must use a FreeRTOS queue, not share this object.
class DomusVoiceGate {
 public:
  static constexpr uint32_t TTL_MS = 1000;
  void cancel() { pending_ = false; }
  bool offer(DomusIntent intent, float confidence, uint32_t now,
             bool enabled, bool modelValidated, bool blocked) {
    if (!enabled || !modelValidated || blocked) { cancel(); return false; }
    if (pending_ && uint32_t(now - at_) > TTL_MS) cancel();
    const size_t id = static_cast<size_t>(intent);
    if (pending_ || id >= static_cast<size_t>(DomusIntent::COUNT) ||
        DOMUS_INTENT_TARGETS[id].relay < 0 || !domusVoiceConfidenceValid(confidence))
      return false;
    intent_ = intent; confidence_ = confidence; at_ = now; pending_ = true;
    return true;
  }
  bool take(uint32_t now, bool enabled, bool blocked, DomusIntentTarget &target,
            float &confidence) {
    if (!pending_) return false;
    cancel();  // exactly once, even when expired/disabled
    if (!enabled || blocked || uint32_t(now - at_) > TTL_MS) return false;
    target = DOMUS_INTENT_TARGETS[static_cast<size_t>(intent_)];
    confidence = confidence_;
    return true;
  }
 private:
  bool pending_ = false;
  DomusIntent intent_ = DomusIntent::DESCONOCIDO;
  float confidence_ = 0;
  uint32_t at_ = 0;
};
