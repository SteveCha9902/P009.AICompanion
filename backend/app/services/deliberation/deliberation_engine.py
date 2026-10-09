from typing import List, Dict, Any, Optional
from collections import defaultdict
from app.domain.cognitive.decision_types import BehaviorIntent
from app.domain.deliberation.deliberation_types import (
    CouncilRole,
    CouncilOpinion,
    DecisionTrace,
    FinalCompanionDecision,
    UncertaintyLevel
)
from app.services.deliberation.council_interface import (
    MemoryAdvisor,
    RelationshipAdvisor,
    GoalAdvisor,
    WorldModelAdvisor,
    AutonomyAdvisor
)
from app.services.governance.governance_review_engine import GovernanceReviewEngine

class DeliberationEngine:
    """
    Central Deliberation Engine.
    Orchestrates 5 Council Advisors -> Resolves Conflicts (Weighted Voting & TieBreakPolicy) -> Submits to Safety & Constitution Final Arbiters.
    """

    ADVISOR_PRIORITY = [
        CouncilRole.RELATIONSHIP,
        CouncilRole.WORLD_MODEL,
        CouncilRole.MEMORY,
        CouncilRole.GOAL,
        CouncilRole.AUTONOMY
    ]

    @classmethod
    def deliberate(
        cls,
        user_id: str,
        text_input: str,
        context_data: Optional[Dict[str, Any]] = None,
        topic: str = ""
    ) -> FinalCompanionDecision:
        ctx = context_data or {}
        advisors = [
            MemoryAdvisor(),
            RelationshipAdvisor(),
            GoalAdvisor(),
            WorldModelAdvisor(),
            AutonomyAdvisor()
        ]

        # Step 1: Collect Opinions
        opinions: List[CouncilOpinion] = [adv.evaluate(user_id, text_input, ctx) for adv in advisors]

        # Step 2: Confidence-Weighted Voting (Max Confidence + Weighted Support)
        vote_scores: Dict[BehaviorIntent, float] = defaultdict(float)
        opinion_by_role: Dict[CouncilRole, CouncilOpinion] = {}

        for op in opinions:
            opinion_by_role[op.role] = op
            # If intent is default RESPOND, give standard score; specialized intents get full weighted power
            multiplier = 0.4 if op.suggested_intent == BehaviorIntent.RESPOND else 1.2
            vote_scores[op.suggested_intent] += (op.confidence * op.weight * multiplier)

        # Sort candidate intents by weighted score
        sorted_candidates = sorted(vote_scores.items(), key=lambda x: x[1], reverse=True)
        winning_intent, top_score = sorted_candidates[0]


        # Step 3: Deadlock / Tie Resolution
        deadlock_resolver_applied: Optional[str] = None
        if len(sorted_candidates) > 1 and abs(sorted_candidates[0][1] - sorted_candidates[1][1]) < 0.05:
            # Apply TieBreakPolicy: Relationship > WorldModel > Memory > Goal > Autonomy
            for p_role in cls.ADVISOR_PRIORITY:
                if opinion_by_role[p_role].suggested_intent in (sorted_candidates[0][0], sorted_candidates[1][0]):
                    winning_intent = opinion_by_role[p_role].suggested_intent
                    deadlock_resolver_applied = f"Priority TieBreakPolicy ({p_role.value}) selected {winning_intent.value}"
                    break

        # Step 4: Determine Uncertainty Level
        uncertainty = UncertaintyLevel.LOW
        if top_score < 1.0 or ctx.get("information_lacking", False):
            uncertainty = UncertaintyLevel.HIGH
        elif top_score < 1.5:
            uncertainty = UncertaintyLevel.MEDIUM

        # Step 5: Draft Tentative Proposed Utterance based on winning intent
        draft_text = "오늘 하루도 참 고생 많으셨어요. 편안한 마음으로 들려주세요."
        if winning_intent == BehaviorIntent.LISTEN:
            draft_text = "많이 지치고 힘드셨겠어요. 오늘은 조용히 곁에서 이야기 들어드릴게요."
        elif winning_intent == BehaviorIntent.RECALL:
            draft_text = "예전에 이야기하셨던 그 일처럼, 언제나 차근차근 잘 해내실 거라 믿어요."
        elif winning_intent == BehaviorIntent.GOAL_REVIEW:
            draft_text = "전에 말씀하셨던 목표가 생각났어요. 요즘은 어떻게 지내고 계신가요?"
        elif winning_intent == BehaviorIntent.UNDERSTAND_CONTEXT:
            draft_text = "요즘 여러 상황으로 에너지가 많이 쓰이실 수도 있겠어요. 무리하지 마세요."
        elif winning_intent == BehaviorIntent.SILENT_COMPANION:
            draft_text = ""

        # Step 6: Final Arbiters (Safety & Constitution Review)
        review_result = GovernanceReviewEngine.execute_governance_review(
            user_id=user_id,
            proposed_text=draft_text,
            topic=topic
        )

        final_text = review_result.sanitized_text if review_result.is_approved else "언제나 당신의 선택과 편안함을 가장 중요하게 생각해요."
        if not review_result.is_approved:
            winning_intent = BehaviorIntent.RESPOND # Fallback safe intent

        # Step 7: Dual Traceability
        internal_lines = [f"[{op.role.value}] suggested {op.suggested_intent.value} (conf: {op.confidence:.2f}, weight: {op.weight:.1f}) - {op.reason}" for op in opinions]
        if deadlock_resolver_applied:
            internal_lines.append(f"[Deadlock Resolution] {deadlock_resolver_applied}")
        internal_lines.append(f"[Final Arbiter Review] Approved: {review_result.is_approved}, Notes: {review_result.feedback_notes}")
        internal_trace_str = "\n".join(internal_lines)

        user_facing_summary = f"사용자의 상태와 맥락에 따라 가장 따뜻하고 안전한 {winning_intent.value} 태도를 선택했습니다."
        if not review_result.is_approved:
            user_facing_summary = "안전 및 경계 존중 원칙에 따라 가장 온화한 지지형 응답으로 전환했습니다."

        trace = DecisionTrace(
            opinions=opinions,
            conflict_summary=f"Top candidate: {winning_intent.value} (score: {top_score:.2f})",
            deadlock_resolved_by=deadlock_resolver_applied,
            safety_sanction_notes=review_result.feedback_notes,
            internal_trace=internal_trace_str,
            user_facing_summary=user_facing_summary
        )

        return FinalCompanionDecision(
            selected_intent=winning_intent,
            confidence=round(min(1.0, top_score / 3.0), 2),
            uncertainty_level=uncertainty,
            trace=trace,
            proposed_text=final_text,
            avatar_expression="smile" if winning_intent in (BehaviorIntent.RESPOND, BehaviorIntent.GOAL_REVIEW) else "neutral"
        )
