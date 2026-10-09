from typing import Optional, List, Tuple
from app.domain.goal.goal import Goal, GoalStatus
from app.services.goal.planning_engine import PlanningEngine
from app.services.goal.dday_engine import DDayEngine

class GoalRecallEngine:
    """
    Identifies natural, non-controlling opportunities to recall active goals and celebrate progress.
    Strictly follows 'Companion, Not Manager' charter.
    """

    @classmethod
    def find_relevant_goal_recall(
        cls,
        user_id: str,
        user_utterance: str
    ) -> Optional[Tuple[Goal, str, str]]:
        """
        Returns (Goal, IntentName, GuidancePrompt)
        """
        active_goals = PlanningEngine.list_user_goals(user_id)
        if not active_goals:
            return None

        # Check if user mentioned words matching any active goal
        matched_goal = None
        for g in active_goals:
            keywords = g.title.split()
            if any(k in user_utterance for k in keywords if len(k) >= 2):
                matched_goal = g
                break

        if not matched_goal:
            return None

        # Check if user indicates milestone completion
        if any(w in user_utterance for w in ("해냈어", "성공했어", "마쳤어", "완료했어", "합격했어")):
            return (
                matched_goal,
                "CELEBRATE_PROGRESS",
                f"Heartfelt Celebration: Cheer genuinely for the user's progress on '{matched_goal.title}'! Express warm pride and happiness."
            )

        # Check D-Day if target date exists
        dday_text = ""
        if matched_goal.target_date_str:
            dday_info = DDayEngine.calculate_dday(matched_goal.title, matched_goal.target_date_str)
            if dday_info:
                dday_text = f" (D-Day note: {dday_info.dday_tag})"

        # Standard gentle inquiry
        return (
            matched_goal,
            "GOAL_REVIEW",
            f"Gentle Non-Controlling Check-in: User previously shared interest in '{matched_goal.title}'{dday_text}. "
            f"Ask lightly and warmly how it is going, without demanding accountability or inducing guilt."
        )
