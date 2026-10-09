from typing import Optional, List
from app.domain.proactive.proactive_context import (
    ProactiveOpportunity,
    ProactiveTriggerType,
    ProactiveDialogueStyle
)
from app.domain.awareness.awareness_context import AwarenessContext
from app.services.memory.relationship.memory_store import RelationshipMemoryStore
from app.services.proactive.user_receptiveness import UserReceptivenessEngine
from app.services.proactive.budget_manager import ProactiveBudgetManager
from app.services.proactive.interest_engine import InterestEngine
from app.services.proactive.diversity_engine import ProactiveDiversityEngine
from app.services.proactive.conversation_starter import ConversationStarterGenerator

class ProactiveOpportunityDetector:
    """
    Synthesizes User Receptiveness, Frequency Budget, Interest Maturation,
    and Conversational Diversity to detect and select the single best Proactive Opportunity.
    """

    @classmethod
    def detect_best_proactive_opportunity(
        cls,
        user_id: str,
        last_user_message: str = "",
        awareness_context: Optional[AwarenessContext] = None,
        idle_seconds: float = 60.0
    ) -> Optional[ProactiveOpportunity]:
        # 1. Budget check (30 min cooldown in NORMAL mode, Opt-Out check)
        if not ProactiveBudgetManager.can_initiate_proactive():
            return None

        # 2. User Receptiveness check (Fatigue, terse response, abrupt idle)
        receptiveness_score = UserReceptivenessEngine.evaluate_receptiveness(
            last_user_message=last_user_message,
            awareness_context=awareness_context,
            idle_seconds=idle_seconds
        )
        if not UserReceptivenessEngine.is_user_receptive(receptiveness_score):
            return None

        # 3. Retrieve user memories and find due interest candidates
        memories = RelationshipMemoryStore.list_user_memories(user_id)
        due_candidates = InterestEngine.get_due_memory_candidates(memories)

        if not due_candidates:
            return None

        # 4. Proactive Priority Queue (Select top 1 candidate)
        # Filter out recently used topics
        valid_candidates = [
            (mem, score, days) for (mem, score, days) in due_candidates
            if not ProactiveDiversityEngine.is_topic_recently_used(mem.memory_type.value)
        ]

        if not valid_candidates:
            valid_candidates = due_candidates # Fallback if all recently used

        # Top candidate
        top_mem, base_score, days_passed = valid_candidates[0]

        # Calculate final priority score
        final_priority = round(base_score * receptiveness_score, 3)

        # Select cyclic dialogue style
        style = ProactiveDiversityEngine.get_next_style()
        starter = ConversationStarterGenerator.generate_starter(top_mem, style)

        opportunity = ProactiveOpportunity(
            trigger_type=ProactiveTriggerType.MEMORY_FOLLOWUP,
            memory_id=top_mem.id,
            memory_type=top_mem.memory_type,
            topic=top_mem.memory_type.value,
            priority_score=final_priority,
            dialogue_style=style,
            suggested_starter=starter,
            receptiveness_score=receptiveness_score
        )

        # Record usage & consume budget
        ProactiveDiversityEngine.record_usage(top_mem.memory_type.value, starter)
        ProactiveBudgetManager.record_proactive_utterance()

        return opportunity
