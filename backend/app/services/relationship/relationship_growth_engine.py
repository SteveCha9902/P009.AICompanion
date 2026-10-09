import time
from typing import Optional, Dict
from app.domain.relationship.relationship_state import RelationshipState, RelationshipVector, RelationshipStage, RelationshipMilestone
from app.domain.adaptive.affective_state import UserAffectiveState
from app.domain.awareness.awareness_context import AwarenessContext
from app.domain.memory.relationship_memory import RelationshipMemory
from app.services.relationship.interaction_quality_analyzer import InteractionQualityAnalyzer
from app.services.relationship.trust_calculator import TrustCalculator

class RelationshipGrowthEngine:
    """
    Main engine for slow, authentic relationship progression.
    Enforces Daily Growth Rate Limits and manages Milestones.
    """

    DAILY_MAX_GROWTH = 0.05 # Strict rate limiter (prevents overnight intimacy inflation)
    _user_states: Dict[str, RelationshipState] = {}

    @classmethod
    def get_or_create_state(cls, user_id: str) -> RelationshipState:
        if user_id not in cls._user_states:
            cls._user_states[user_id] = RelationshipState(user_id=user_id)
        return cls._user_states[user_id]

    @classmethod
    def process_turn(
        cls,
        user_id: str,
        user_utterance: str,
        affective_state: Optional[UserAffectiveState] = None,
        awareness_context: Optional[AwarenessContext] = None,
        recalled_memories_count: int = 0
    ) -> RelationshipState:
        state = cls.get_or_create_state(user_id)
        now_ms = int(time.time() * 1000)

        # 1. Reset daily growth accumulator if 24 hours passed
        if (now_ms - state.last_daily_growth_timestamp_ms) > (24 * 3600 * 1000):
            state.today_accumulated_growth = 0.0
            state.last_daily_growth_timestamp_ms = now_ms

        # 2. Analyze turn quality
        quality = InteractionQualityAnalyzer.analyze_turn_quality(user_utterance, affective_state, awareness_context)

        # 3. Update Familiarity (Grows steadily with interactions)
        state.vector.total_interaction_turns += 1
        raw_fam_inc = 0.005 * quality
        fam_inc = min(raw_fam_inc, max(0.0, cls.DAILY_MAX_GROWTH - state.today_accumulated_growth))
        state.vector.familiarity = min(1.0, state.vector.familiarity + fam_inc)

        # 4. Calculate Trust increment (Decoupled from familiarity)
        raw_trust_inc = TrustCalculator.calculate_trust_increment(state.vector, quality, recalled_memories_count)
        if raw_trust_inc > 0:
            trust_inc = min(raw_trust_inc, max(0.0, cls.DAILY_MAX_GROWTH - state.today_accumulated_growth))
        else:
            trust_inc = raw_trust_inc # Negative drops are never capped

        state.vector.trust = max(0.05, min(1.0, state.vector.trust + trust_inc))
        state.vector.comfort = max(0.05, min(1.0, state.vector.comfort + (fam_inc * 0.8)))

        # Track daily growth usage
        if fam_inc > 0 or (trust_inc > 0):
            state.today_accumulated_growth += max(fam_inc, trust_inc if trust_inc > 0 else 0)

        # 5. Milestone Checking (e.g. 50 turns or deep trust)
        if state.vector.total_interaction_turns == 10 and not any(m.milestone_id == "m_10_turns" for m in state.milestones):
            state.milestones.append(RelationshipMilestone(
                milestone_id="m_10_turns",
                title="첫 10번의 소중한 대화 완성",
                importance=0.6,
                event_date_str=time.strftime("%Y-%m-%d")
            ))

        # 6. Update Stage
        state.stage = state.compute_stage()
        state.vector.last_interaction_timestamp_ms = now_ms
        return state

    @classmethod
    def record_custom_milestone(cls, user_id: str, title: str, memory_refs: list) -> RelationshipMilestone:
        state = cls.get_or_create_state(user_id)
        ms = RelationshipMilestone(
            milestone_id=f"ms_{int(time.time()*1000)}",
            title=title,
            importance=0.85,
            memory_refs=memory_refs,
            event_date_str=time.strftime("%Y-%m-%d")
        )
        state.milestones.append(ms)
        state.stage = state.compute_stage()
        return ms

    @classmethod
    def clear(cls) -> None:
        cls._user_states.clear()
