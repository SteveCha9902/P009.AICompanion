from typing import Dict, List, Optional
from app.domain.personality.personality_vector import CharacterDNA

class PersonalityDriftMonitor:
    """
    Monitors personality consistency across multiple conversation turns and sessions.
    Detects when simulated conversational tone drifts more than 0.20 away from baseline CharacterDNA
    and calculates corrective pull factors.
    """

    DRIFT_TOLERANCE = 0.20 # Maximum allowed divergence from DNA
    _turn_history: List[Dict[str, float]] = []

    @classmethod
    def record_turn_expression(cls, warmth: float, humor: float, empathy: float) -> None:
        cls._turn_history.append({
            "warmth": warmth,
            "humor": humor,
            "empathy": empathy
        })
        if len(cls._turn_history) > 50:
            cls._turn_history.pop(0)

    @classmethod
    def check_and_correct_drift(cls, current_dna: CharacterDNA) -> CharacterDNA:
        """
        Calculates moving average of recent turns and bounds values within DNA baseline +/- tolerance.
        """
        if len(cls._turn_history) < 5:
            return current_dna # Insufficient sample

        avg_humor = sum(t["humor"] for t in cls._turn_history) / len(cls._turn_history)
        avg_warmth = sum(t["warmth"] for t in cls._turn_history) / len(cls._turn_history)

        corrected = current_dna.model_copy()

        # If humor has drifted too far (e.g. from 0.35 to 0.75), clamp back towards DNA baseline
        if abs(avg_humor - current_dna.humor) > cls.DRIFT_TOLERANCE:
            # Anchor back to baseline DNA
            corrected.humor = current_dna.humor

        if abs(avg_warmth - current_dna.warmth) > cls.DRIFT_TOLERANCE:
            corrected.warmth = current_dna.warmth

        return corrected

    @classmethod
    def clear(cls) -> None:
        cls._turn_history.clear()
