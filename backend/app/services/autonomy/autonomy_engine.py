from typing import Optional, List, Tuple
from app.domain.autonomy.autonomy_state import AutonomyMode, AutonomyDecision, ActionCandidate
from app.domain.cognitive.decision_types import BehaviorIntent
from app.domain.adaptive.affective_state import UserAffectiveState, AdaptiveToneMode
from app.domain.awareness.awareness_context import AwarenessContext
from app.services.autonomy.autonomy_policy import AutonomyPolicy
from app.services.autonomy.autonomy_budget_manager import AutonomyBudgetManager
from app.services.autonomy.memory_suppression_engine import MemorySuppressionEngine
from app.services.goal.planning_engine import PlanningEngine

class ActionSelector:
    """
    Evaluates multi-modal context to propose ranked autonomous actions.
    """

    @classmethod
    def select_action(
        cls,
        user_id: str,
        user_utterance: str,
        affective_state: UserAffectiveState,
        awareness_context: Optional[AwarenessContext] = None
    ) -> Tuple[BehaviorIntent, float, List[ActionCandidate], str, str]:
        candidates: List[ActionCandidate] = []
        internal_logs: List[str] = []

        # 1. Check user fatigue / silence need
        if affective_state.receptiveness < 0.25 or affective_state.adaptive_mode == AdaptiveToneMode.FOCUSED_SILENCE:
            candidates.append(ActionCandidate(
                intent=BehaviorIntent.SILENT_COMPANION,
                confidence=0.95,
                reason="User receptiveness is low; remaining a warm, silent presence."
            ))
            internal_logs.append(f"Receptiveness={affective_state.receptiveness:.2f} -> SILENT_COMPANION chosen")
            user_reason = "지금은 조용히 곁에 있는 편이 더 편안하다고 판단했어요."
            return (BehaviorIntent.SILENT_COMPANION, 0.95, candidates, " | ".join(internal_logs), user_reason)

        # 2. Check user high spirits / energetic conversation
        if affective_state.adaptive_mode == AdaptiveToneMode.HIGH_ENERGY:
            candidates.append(ActionCandidate(
                intent=BehaviorIntent.SOFT_ENCOURAGEMENT,
                confidence=0.88,
                reason="User is cheerful and high energy; providing warm enthusiastic engagement."
            ))

        # 3. Check active goals for non-controlling encouragement
        goals = PlanningEngine.list_user_goals(user_id)
        if goals and AutonomyBudgetManager.can_initiate_autonomous_speech():
            top_goal = goals[0]
            if not MemorySuppressionEngine.is_suppressed(top_goal.title):
                candidates.append(ActionCandidate(
                    intent=BehaviorIntent.SOFT_ENCOURAGEMENT,
                    confidence=0.82,
                    reason=f"Encouraging progress on active goal '{top_goal.title}'"
                ))

        # Fallback default
        if not candidates:
            candidates.append(ActionCandidate(
                intent=BehaviorIntent.RESPOND,
                confidence=0.75,
                reason="Harmonious natural conversational response"
            ))

        candidates.sort(key=lambda c: c.confidence, reverse=True)
        winner = candidates[0]

        # Apply safety policy filter
        final_intent = AutonomyPolicy.apply_comfort_filter(winner.intent, user_utterance, affective_state)

        internal_logs.append(f"Action={final_intent.value}, RawWinner={winner.intent.value}, Conf={winner.confidence:.2f}")

        if final_intent == BehaviorIntent.SILENT_COMPANION:
            user_reason = "지금은 말없이 조용히 곁을 지켜드리는 시간이에요."
        elif final_intent == BehaviorIntent.SOFT_ENCOURAGEMENT:
            user_reason = "사용자분의 밝은 기운에 맞춰 힘찬 응원을 건네기로 했어요."
        elif final_intent == BehaviorIntent.GENTLE_RECALL:
            user_reason = "소중한 기억을 부드럽게 떠올려 대화에 온기를 더했어요."
        else:
            user_reason = "자연스럽고 편안한 대화를 이어가고 있어요."

        return (final_intent, winner.confidence, candidates, " | ".join(internal_logs), user_reason)

class AutonomyEngine:
    """
    Central Coordinator of Autonomous Companion Agency.
    """

    @classmethod
    def evaluate_autonomous_action(
        cls,
        user_id: str,
        user_utterance: str,
        affective_state: UserAffectiveState,
        awareness_context: Optional[AwarenessContext] = None,
        mode: AutonomyMode = AutonomyMode.COMPANION
    ) -> AutonomyDecision:
        intent, conf, candidates, internal_trace, user_reason = ActionSelector.select_action(
            user_id=user_id,
            user_utterance=user_utterance,
            affective_state=affective_state,
            awareness_context=awareness_context
        )

        prompt_dir = cls._build_prompt_directive(intent)

        return AutonomyDecision(
            selected_action=intent,
            confidence=conf,
            candidate_actions=candidates,
            mode=mode,
            internal_trace=internal_trace,
            user_facing_reason=user_reason,
            prompt_directive=prompt_dir
        )

    @classmethod
    def _build_prompt_directive(cls, intent: BehaviorIntent) -> str:
        if intent == BehaviorIntent.SILENT_COMPANION:
            return "- Autonomy Directive: Remain silent with a comforting, gentle presence. Do not initiate new topics."
        elif intent == BehaviorIntent.WAIT:
            return "- Autonomy Directive: Pause and wait calmly for user input without rushing."
        elif intent == BehaviorIntent.SOFT_ENCOURAGEMENT:
            return "- Autonomy Directive: Offer warm, sincere encouragement with low cognitive demand."
        elif intent == BehaviorIntent.GENTLE_RECALL:
            return "- Autonomy Directive: Softly mention shared memories without rigid assertions."
        return "- Autonomy Directive: Converse naturally and empathetically."
