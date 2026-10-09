from typing import Optional, List, Dict
from app.services.context.providers.base import ContextProvider
from app.services.goal.goal_recall_engine import GoalRecallEngine

class FutureContextProvider(ContextProvider):
    """
    Life Goals & Future Planning Context Provider:
    Injects non-controlling goal check-ins and progress celebrations into ContextBuilder prompt.
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[Dict[str, str]]:
        recall_res = GoalRecallEngine.find_relevant_goal_recall(
            user_id=self.user_id,
            user_utterance=current_user_message
        )

        if not recall_res:
            return []

        goal, intent_name, guidance = recall_res
        return [{
            "role": "system",
            "content": (
                f"\n[FUTURE LIFE GOAL & PLANNING NARRATIVE: {intent_name}]\n"
                f"Active Goal: '{goal.title}' ({goal.goal_type.value}, Commitment: {goal.commitment_level:.2f})\n"
                f"{guidance}\n"
                f"Charter Rule: Never scold, pressure, or induce guilt. You are an encouraging companion, not a manager."
            )
        }]
