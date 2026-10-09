import math
from datetime import datetime, timezone
from app.db.models.emotion import EmotionState, EmotionType

class DecayEngine:
    """
    Decays current emotional state based on time elapsed since the last trigger.
    """

    def _decay_value(self, current: float, baseline: float, time_diff_sec: float, half_life_sec: float) -> float:
        """
        Exponential decay towards a baseline.
        """
        if time_diff_sec <= 0:
            return current
        
        decay_factor = math.exp(-math.log(2) * time_diff_sec / half_life_sec)
        # Shift current towards baseline
        decayed = baseline + (current - baseline) * decay_factor
        return decayed

    def apply_decay(self, current_state: EmotionState, current_time: datetime = None) -> EmotionState:
        """
        Returns a new EmotionState with decayed values. Does NOT mutate the DB object directly.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)
            
        last_time = current_state.last_trigger_at or current_state.updated_at
        if not last_time:
            return current_state
            
        # Ensure timezone compatibility
        if last_time.tzinfo is None and current_time.tzinfo is not None:
            current_time = current_time.replace(tzinfo=None)
        elif last_time.tzinfo is not None and current_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=None)

        time_diff = (current_time - last_time).total_seconds()
        
        # If less than 1 minute passed, minimal decay
        if time_diff < 60:
            return current_state

        # Half-lives (in seconds)
        # Valence and Arousal decay faster (e.g., 30 mins)
        fast_hl = 30 * 60
        # Tension decays very fast (e.g., 10 mins)
        tension_hl = 10 * 60
        # Warmth and Engagement decay slower (e.g., 2 hours)
        slow_hl = 120 * 60

        new_valence = self._decay_value(current_state.valence, 0.0, time_diff, fast_hl)
        new_arousal = self._decay_value(current_state.arousal, 0.0, time_diff, fast_hl)
        new_tension = self._decay_value(current_state.tension, 0.0, time_diff, tension_hl)
        new_warmth = self._decay_value(current_state.warmth, 0.5, time_diff, slow_hl)
        new_engagement = self._decay_value(current_state.engagement, 0.5, time_diff, slow_hl)
        
        primary = current_state.primary_emotion
        # If intensity drops low enough, revert to CALM
        if abs(new_valence) < 0.2 and new_arousal < 0.2 and new_tension < 0.2:
            primary = EmotionType.CALM

        decayed_state = EmotionState(
            companion_id=current_state.companion_id,
            primary_emotion=primary,
            valence=new_valence,
            arousal=new_arousal,
            warmth=new_warmth,
            engagement=new_engagement,
            tension=new_tension,
            confidence=getattr(current_state, "confidence", 1.0) or 1.0,
            last_trigger_at=current_state.last_trigger_at # Keep original trigger time
        )
        return decayed_state

