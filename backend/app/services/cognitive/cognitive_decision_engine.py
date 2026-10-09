from typing import Optional, List
from app.domain.cognitive.cognitive_state import CompanionCognitiveState, TemporalContext, TimeOfDay
from app.domain.cognitive.decision_types import BehaviorIntent, BehaviorDecision, CandidateIntent
from app.services.cognitive.conflict_resolver import ConflictResolver
from app.services.cognitive.balance_monitor import ConversationBalanceMonitor
from app.services.awareness.awareness_coordinator import AwarenessEngineCoordinator
from app.services.shared_reality.joint_attention_engine import JointAttentionEngine
from app.services.adaptive.affective_estimator import AffectiveStateEstimator
from app.services.adaptive.adaptive_behavior_planner import AdaptiveBehaviorPlanner
from app.services.memory.relationship.memory_store import RelationshipMemoryStore
from app.services.memory.relationship.recall_engine import RecallRankingEngine
from app.services.proactive.opportunity_detector import ProactiveOpportunityDetector

class CognitiveDecisionEngine:
    """
    Central Brain of Companion Cognitive Operating System (CCOS).
    Synthesizes multimodal layers, resolves conflicts, and outputs a deterministic BehaviorDecision with trace logging.
    """

    @classmethod
    def evaluate_decision(
        cls,
        user_id: str,
        user_utterance: str,
        idle_seconds: float = 60.0
    ) -> BehaviorDecision:
        # 1. Gather all Cognitive Layers
        awareness_ctx = AwarenessEngineCoordinator.get_current_awareness_context()
        shared_reality_ctx = JointAttentionEngine.get_active_context()

        # Affective
        raw_affective = AffectiveStateEstimator.estimate_affective_state(user_utterance, awareness_ctx)
        planned_affective = AdaptiveBehaviorPlanner.plan_behavior(raw_affective)

        # Memories
        user_mems = RelationshipMemoryStore.list_user_memories(user_id)
        recalled_tuples = RecallRankingEngine.rank_and_select_memories(
            memories=user_mems,
            user_utterance=user_utterance,
            awareness_context=awareness_ctx,
            shared_reality_context=shared_reality_ctx,
            top_k=2
        )
        recalled_mems = [t[0] for t in recalled_tuples]

        # Proactive
        proactive_opp = ProactiveOpportunityDetector.detect_best_proactive_opportunity(
            user_id=user_id,
            last_user_message=user_utterance,
            awareness_context=awareness_ctx,
            idle_seconds=idle_seconds
        )

        # Temporal
        temporal_ctx = TemporalContext.current()

        cognitive_state = CompanionCognitiveState(
            awareness_context=awareness_ctx,
            shared_reality_context=shared_reality_ctx,
            affective_state=planned_affective,
            recalled_memories=recalled_mems,
            proactive_opportunity=proactive_opp,
            temporal_context=temporal_ctx
        )

        # 2. Resolve Conflicts through Priority Policy
        winner_intent, confidence, candidates, trace_reason = ConflictResolver.resolve_candidates(
            state=cognitive_state,
            user_utterance=user_utterance
        )

        # 3. Record in Meta-Cognition Balance Monitor
        ConversationBalanceMonitor.record_intent(winner_intent)

        # 4. Map Avatar & Voice & Prompt Directives
        avatar_expr = "neutral"
        voice_rate = 1.0
        voice_pitch = 1.0

        if winner_intent == BehaviorIntent.SILENCE:
            avatar_expr = "thinking"
            voice_rate = 0.95
            voice_pitch = 0.98
        elif winner_intent == BehaviorIntent.ENCOURAGE:
            avatar_expr = "smile"
            voice_rate = 1.08
            voice_pitch = 1.05
        elif winner_intent == BehaviorIntent.RECALL:
            avatar_expr = "thinking"
            voice_rate = 0.95
        elif winner_intent == BehaviorIntent.LISTEN:
            avatar_expr = "listening"
            voice_rate = 0.90
            voice_pitch = 0.98
        elif winner_intent == BehaviorIntent.OBSERVE:
            avatar_expr = "speaking"

        prompt_directive = cls._build_cognitive_prompt_directive(winner_intent, cognitive_state)

        return BehaviorDecision(
            selected_intent=winner_intent,
            confidence=confidence,
            candidate_intents=candidates,
            primary_layer=cls._map_layer_name(winner_intent),
            trace_reason=trace_reason,
            prompt_directive=prompt_directive,
            avatar_expression=avatar_expr,
            voice_rate=voice_rate,
            voice_pitch=voice_pitch
        )

    @classmethod
    def _map_layer_name(cls, intent: BehaviorIntent) -> str:
        if intent in (BehaviorIntent.SILENCE, BehaviorIntent.LISTEN, BehaviorIntent.ENCOURAGE):
            return "AFFECTIVE"
        elif intent == BehaviorIntent.OBSERVE:
            return "SHARED_REALITY"
        elif intent == BehaviorIntent.RECALL:
            return "RELATIONSHIP_MEMORY"
        elif intent == BehaviorIntent.PROACTIVE_START:
            return "PROACTIVE"
        return "GENERAL"

    @classmethod
    def _build_cognitive_prompt_directive(cls, intent: BehaviorIntent, state: CompanionCognitiveState) -> str:
        lines = [f"[CHARACTER BRAIN INTENT: {intent.value}]"]

        # Temporal Context Note
        if state.temporal_context.time_of_day == TimeOfDay.LATE_NIGHT:
            lines.append("- Temporal Note: It is late at night. Keep voice soothing, quiet, and calm.")
        elif state.temporal_context.time_of_day == TimeOfDay.MORNING:
            lines.append("- Temporal Note: It is morning. Greet the day with refreshing, gentle warmth.")

        # Intent specific directives
        if intent == BehaviorIntent.SILENCE:
            lines.append("- Directive: User is highly occupied or fatigued. Answer with minimal words and do not demand attention.")
        elif intent == BehaviorIntent.RECALL and state.recalled_memories:
            lines.append(f"- Directive: Naturally integrate shared memory '{state.recalled_memories[0].summary}'.")
        elif intent == BehaviorIntent.OBSERVE and state.shared_reality_context:
            target = state.shared_reality_context.target_label or "object"
            lines.append(f"- Directive: Direct attention to shared focus '{target}'.")
        elif intent == BehaviorIntent.LISTEN:
            lines.append("- Directive: Offer deep empathetic listening, validating the user's feelings warmly.")

        return "\n".join(lines) + "\n"
