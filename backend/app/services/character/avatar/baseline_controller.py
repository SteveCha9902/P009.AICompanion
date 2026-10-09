import math
import random
import time
from typing import Dict, Any

class BlinkController:
    """Calculates natural blinking state and random intervals (2~7 seconds)."""
    @staticmethod
    def get_blink_value(now_sec: float) -> float:
        # Pseudo-periodic blink with 3.5s base interval + micro variation
        cycle = now_sec % 3.5
        if cycle < 0.15:
            # 150ms blink duration
            return math.sin((cycle / 0.15) * math.pi)
        return 0.0

class BreathingController:
    """Calculates continuous chest/head micro-expansion (4~6 second cycle)."""
    @staticmethod
    def get_breathing_offset(now_sec: float) -> float:
        # 5.0 second breathing period
        return round(math.sin((now_sec / 5.0) * 2 * math.pi) * 0.02, 4)

class MicroExpressionController:
    """Generates subtle organic micro-movements to avoid rigid uncanny valley stillness."""
    @staticmethod
    def get_micro_head_sway(now_sec: float) -> Dict[str, float]:
        # Very gentle sway (±0.5 degrees)
        yaw_sway = round(math.sin(now_sec * 0.7) * 0.5, 3)
        pitch_sway = round(math.cos(now_sec * 0.5) * 0.3, 3)
        return {"yaw_sway": yaw_sway, "pitch_sway": pitch_sway}

class AvatarBaselineController:
    """
    Independent baseline motion generator responsible for life-like presence
    even when no active dialogue is occurring.
    """
    @classmethod
    def get_baseline_parameters(cls, timestamp: float = None) -> Dict[str, Any]:
        t = timestamp or time.time()
        blink = BlinkController.get_blink_value(t)
        breath = BreathingController.get_breathing_offset(t)
        sway = MicroExpressionController.get_micro_head_sway(t)

        return {
            "eye_blink": blink,
            "breathing_scale": 1.0 + breath,
            "head_micro_yaw": sway["yaw_sway"],
            "head_micro_pitch": sway["pitch_sway"]
        }
