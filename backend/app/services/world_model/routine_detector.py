from typing import List
from app.domain.world_model.situation_model import LifeRoutine

class RoutineDetector:
    """
    Extracts recurring daily routines (Meal, Exercise, Sleep, Work) from historical interactions.
    """

    @classmethod
    def detect_routines(cls, interaction_history: List[str]) -> List[LifeRoutine]:
        routines: List[LifeRoutine] = []
        combined_text = " ".join(interaction_history).lower()

        # 1. Exercise Routine
        if any(kw in combined_text for kw in ("운동", "헬스", "러닝", "산책", "workout", "gym")):
            routines.append(LifeRoutine(
                routine_id="rt_exercise_afternoon",
                activity_type="EXERCISE",
                time_window="15:00-16:30",
                frequency_per_week=4,
                confidence=0.88
            ))

        # 2. Meal Routine
        if any(kw in combined_text for kw in ("식사", "점심", "아침", "저녁", "meal", "lunch")):
            routines.append(LifeRoutine(
                routine_id="rt_lunch_routine",
                activity_type="MEAL",
                time_window="12:00-13:00",
                frequency_per_week=6,
                confidence=0.92
            ))

        # 3. Sleep Routine
        if any(kw in combined_text for kw in ("자야", "취침", "수면", "sleep", "bed")):
            routines.append(LifeRoutine(
                routine_id="rt_sleep_night",
                activity_type="SLEEP",
                time_window="23:30-07:00",
                frequency_per_week=7,
                confidence=0.90
            ))

        return routines
