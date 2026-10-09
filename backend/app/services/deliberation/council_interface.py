from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.domain.cognitive.decision_types import BehaviorIntent
from app.domain.deliberation.deliberation_types import CouncilRole, CouncilOpinion

class ICouncilAdvisor(ABC):
    @abstractmethod
    def evaluate(self, user_id: str, text_input: str, context_data: Optional[Dict[str, Any]] = None) -> CouncilOpinion:
        pass

class MemoryAdvisor(ICouncilAdvisor):
    def evaluate(self, user_id: str, text_input: str, context_data: Optional[Dict[str, Any]] = None) -> CouncilOpinion:
        ctx = context_data or {}
        has_mem = ctx.get("has_relevant_memory", False)
        if has_mem:
            return CouncilOpinion(
                role=CouncilRole.MEMORY,
                suggested_intent=BehaviorIntent.RECALL,
                confidence=0.85,
                weight=1.0,
                reason="Relevant past experience or shared history exists."
            )
        return CouncilOpinion(
            role=CouncilRole.MEMORY,
            suggested_intent=BehaviorIntent.RESPOND,
            confidence=0.50,
            weight=0.8,
            reason="No strong past memory hook found."
        )

class RelationshipAdvisor(ICouncilAdvisor):
    def evaluate(self, user_id: str, text_input: str, context_data: Optional[Dict[str, Any]] = None) -> CouncilOpinion:
        ctx = context_data or {}
        is_fatigued = ctx.get("user_fatigued", False)
        if is_fatigued:
            return CouncilOpinion(
                role=CouncilRole.RELATIONSHIP,
                suggested_intent=BehaviorIntent.LISTEN,
                confidence=0.92,
                weight=1.2,
                reason="User is tired or distressed; emotional comfort and listening prioritized."
            )
        return CouncilOpinion(
            role=CouncilRole.RELATIONSHIP,
            suggested_intent=BehaviorIntent.RESPOND,
            confidence=0.80,
            weight=1.0,
            reason="Standard warm conversational pacing."
        )

class GoalAdvisor(ICouncilAdvisor):
    def evaluate(self, user_id: str, text_input: str, context_data: Optional[Dict[str, Any]] = None) -> CouncilOpinion:
        ctx = context_data or {}
        active_goal = ctx.get("active_goal", None)
        if active_goal and not ctx.get("user_fatigued", False):
            return CouncilOpinion(
                role=CouncilRole.GOAL,
                suggested_intent=BehaviorIntent.GOAL_REVIEW,
                confidence=0.75,
                weight=0.9,
                reason="Gentle check-in on active life goal is appropriate."
            )
        return CouncilOpinion(
            role=CouncilRole.GOAL,
            suggested_intent=BehaviorIntent.RESPOND,
            confidence=0.40,
            weight=0.6,
            reason="Goal check-in not urgent or user is currently resting."
        )

class WorldModelAdvisor(ICouncilAdvisor):
    def evaluate(self, user_id: str, text_input: str, context_data: Optional[Dict[str, Any]] = None) -> CouncilOpinion:
        ctx = context_data or {}
        has_hypotheses = ctx.get("has_situation_hypotheses", False)
        if has_hypotheses:
            return CouncilOpinion(
                role=CouncilRole.WORLD_MODEL,
                suggested_intent=BehaviorIntent.UNDERSTAND_CONTEXT,
                confidence=0.88,
                weight=1.1,
                reason="Multi-hypothesis situation understanding and environmental context match."
            )
        return CouncilOpinion(
            role=CouncilRole.WORLD_MODEL,
            suggested_intent=BehaviorIntent.RESPOND,
            confidence=0.60,
            weight=0.8,
            reason="No complex situation hypotheses present."
        )

class AutonomyAdvisor(ICouncilAdvisor):
    def evaluate(self, user_id: str, text_input: str, context_data: Optional[Dict[str, Any]] = None) -> CouncilOpinion:
        ctx = context_data or {}
        high_load = ctx.get("high_cognitive_load", False)
        if high_load:
            return CouncilOpinion(
                role=CouncilRole.AUTONOMY,
                suggested_intent=BehaviorIntent.SILENT_COMPANION,
                confidence=0.90,
                weight=1.0,
                reason="High user cognitive load; silent companion presence recommended."
            )
        return CouncilOpinion(
            role=CouncilRole.AUTONOMY,
            suggested_intent=BehaviorIntent.WAIT,
            confidence=0.50,
            weight=0.7,
            reason="Standard conversational pacing."
        )
