from typing import List, Tuple, Optional
from app.domain.cognitive.decision_types import BehaviorIntent, CandidateIntent
from app.domain.cognitive.cognitive_state import CompanionCognitiveState, TimeOfDay
from app.domain.adaptive.affective_state import AdaptiveToneMode
from app.domain.shared_reality.shared_reality_context import JointAttentionState
from app.services.cognitive.balance_monitor import ConversationBalanceMonitor

class ConflictResolver:
    """
    Cognitive Priority Policy Engine:
    Priority 1 (Emotion / Receptiveness) > Priority 2 (Awareness / Shared Reality)
    > Priority 3 (Relationship Memory) > Priority 4 (Proactive Initiation)
    """

    MAX_CONTEXT_ITEMS = 2 # Cognitive Load Budget (Prevents overwhelming prompt stuffing)

    @classmethod
    def resolve_candidates(
        cls,
        state: CompanionCognitiveState,
        user_utterance: str
    ) -> Tuple[BehaviorIntent, float, List[CandidateIntent], str]:
        candidates: List[CandidateIntent] = []
        trace_steps: List[str] = []

        affective = state.affective_state
        shared_reality = state.shared_reality_context
        recalled_mems = state.recalled_memories
        proactive = state.proactive_opportunity
        temporal = state.temporal_context

        # =========================================================================
        # PRIORITY 1: AFFECTIVE & RECEPTIVENESS (User Internal State)
        # =========================================================================
        if affective:
            if affective.receptiveness < 0.25 or affective.adaptive_mode == AdaptiveToneMode.FOCUSED_SILENCE:
                # Extreme low receptiveness overrides everything else
                candidates.append(CandidateIntent(
                    intent=BehaviorIntent.SILENCE,
                    confidence=0.95,
                    reason=f"User Receptiveness is critically low ({affective.receptiveness:.2f})"
                ))
                trace_steps.append("P1 OVERRIDE: Low receptiveness (<0.25) -> SILENCE selected, suppressing Memory & Proactive")
                return (BehaviorIntent.SILENCE, 0.95, candidates, " -> ".join(trace_steps))

            if affective.adaptive_mode == AdaptiveToneMode.SAD_EMPATHY or affective.emotional_valence < -0.30:
                candidates.append(CandidateIntent(
                    intent=BehaviorIntent.LISTEN,
                    confidence=0.90,
                    reason="User has low emotional valence, prioritizing gentle listening and empathy"
                ))
            elif affective.adaptive_mode == AdaptiveToneMode.HIGH_ENERGY or (affective.emotional_valence > 0.35 and affective.energy_level > 0.60):
                candidates.append(CandidateIntent(
                    intent=BehaviorIntent.ENCOURAGE,
                    confidence=0.88,
                    reason="User is in high spirits and energetic"
                ))


        # =========================================================================
        # PRIORITY 2: CURRENT REALITY & AWARENESS (Physical Present)
        # =========================================================================
        if shared_reality and shared_reality.state in (JointAttentionState.SHARED_FOCUS, JointAttentionState.DISCUSSING_TARGET):
            target_name = shared_reality.target_label or (shared_reality.focus_target.value if shared_reality.focus_target else "object")
            candidates.append(CandidateIntent(
                intent=BehaviorIntent.OBSERVE,
                confidence=0.86,
                reason=f"Active Joint Attention formed on {target_name} (Conf: {shared_reality.target_confidence:.2f})"
            ))

        # =========================================================================
        # PRIORITY 3: RELATIONSHIP MEMORY (Past Life Connection)
        # =========================================================================
        if recalled_mems:
            top_mem = recalled_mems[0]
            candidates.append(CandidateIntent(
                intent=BehaviorIntent.RECALL,
                confidence=0.82,
                reason=f"Relevant relationship memory matched: {top_mem.summary}"
            ))

        # =========================================================================
        # PRIORITY 4: PROACTIVE INITIATION (Autonomous Agency)
        # =========================================================================
        if proactive:
            candidates.append(CandidateIntent(
                intent=BehaviorIntent.PROACTIVE_START,
                confidence=proactive.priority_score,
                reason=f"Proactive follow-up due for topic: {proactive.topic}"
            ))

        # Default fallback candidate
        if not candidates:
            candidates.append(CandidateIntent(
                intent=BehaviorIntent.RESPOND,
                confidence=0.75,
                reason="Standard harmonious conversation turn"
            ))

        # Meta-Cognition Check: Prevent question spamming
        if ConversationBalanceMonitor.should_suppress_questioning():
            trace_steps.append("META-COGNITION: Questioning suppressed due to consecutive ASK turns -> favoring LISTEN/RESPOND")
            for c in candidates:
                if c.intent in (BehaviorIntent.ASK, BehaviorIntent.PROACTIVE_START):
                    c.confidence = max(0.20, c.confidence - 0.35)

        # Sort candidates by confidence descending
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        winner = candidates[0]

        trace_steps.append(f"WINNER: {winner.intent.value} (Conf: {winner.confidence:.2f}) based on {winner.reason}")
        return (winner.intent, winner.confidence, candidates, " | ".join(trace_steps))
