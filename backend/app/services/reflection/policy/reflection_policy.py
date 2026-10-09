from typing import Optional, Dict, Any, List
from app.services.reflection.domain.reflection_decision import ReflectionDecision
from app.services.reflection.domain.reflection import ReflectionTrigger, ReflectionPriority

class ReflectionPolicy:
    """
    Rule-based Policy determining when autonomous reflection should be scheduled.
    """

    @staticmethod
    def evaluate(
        user_input: str = "",
        emotion_intensity: float = 0.0,
        memory_importance: float = 0.0,
        relationship_delta: float = 0.0,
        conversation_message_count: int = 1,
        is_manual: bool = False
    ) -> ReflectionDecision:
        reasons: List[str] = []

        # Rule 5: Manual Trigger
        if is_manual:
            return ReflectionDecision(
                should_reflect=True,
                trigger=ReflectionTrigger.MANUAL,
                priority=ReflectionPriority.HIGH,
                reasons=["manual_trigger_invoked"]
            )

        # Rule 1: Significant Emotion
        if emotion_intensity >= 0.75:
            reasons.append(f"significant_emotion_intensity_{emotion_intensity:.2f}")
            return ReflectionDecision(
                should_reflect=True,
                trigger=ReflectionTrigger.SIGNIFICANT_EMOTION,
                priority=ReflectionPriority.HIGH,
                reasons=reasons
            )

        # Rule 2: Important Memory
        if memory_importance >= 0.80:
            reasons.append(f"important_memory_score_{memory_importance:.2f}")
            return ReflectionDecision(
                should_reflect=True,
                trigger=ReflectionTrigger.IMPORTANT_MEMORY,
                priority=ReflectionPriority.HIGH,
                reasons=reasons
            )

        # Rule 3: Relationship Change
        if relationship_delta >= 0.025:
            reasons.append(f"relationship_delta_{relationship_delta:.3f}")
            return ReflectionDecision(
                should_reflect=True,
                trigger=ReflectionTrigger.RELATIONSHIP_CHANGE,
                priority=ReflectionPriority.NORMAL,
                reasons=reasons
            )

        # Rule 4: Meaningful Conversation Milestones
        if conversation_message_count >= 10 and conversation_message_count % 10 == 0:
            reasons.append(f"conversation_length_milestone_{conversation_message_count}")
            return ReflectionDecision(
                should_reflect=True,
                trigger=ReflectionTrigger.CONVERSATION_END,
                priority=ReflectionPriority.NORMAL,
                reasons=reasons
            )

        # Default: No reflection needed for casual short turns
        return ReflectionDecision(
            should_reflect=False,
            trigger=ReflectionTrigger.CONVERSATION_END,
            priority=ReflectionPriority.LOW,
            reasons=["routine_interaction_no_trigger_met"]
        )
