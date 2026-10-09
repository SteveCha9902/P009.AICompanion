from typing import List
from app.domain.world_model.situation_model import SituationHypothesis

class CausalReasoningEngine:
    """
    Generates multiple explanatory hypotheses for observed user states.
    Strictly avoids dogmatic single-cause determinations (Alternative Explanation Coverage).
    """

    @classmethod
    def generate_hypotheses(cls, observed_state: str) -> List[SituationHypothesis]:
        hypotheses: List[SituationHypothesis] = []
        state_lower = observed_state.lower()

        if any(kw in state_lower for kw in ("어지러", "어지럽", "dizzy", "headache", "두통")):
            hypotheses.append(SituationHypothesis(

                hypothesis_id="hyp_sleep_fatigue",
                explanation="수면 부족 또는 누적된 피로로 인한 일시적 어지러움 가능성",
                confidence=0.65,
                supporting_evidence=["최근 늦은 취침 언급", "피로 호소"],
                conflicting_evidence=[]
            ))
            hypotheses.append(SituationHypothesis(
                hypothesis_id="hyp_hydration_meal",
                explanation="수분 섭취 부족 또는 식사 간격 지연으로 인한 혈당/혈압 변화 가능성",
                confidence=0.55,
                supporting_evidence=["식사 언급 없음"],
                conflicting_evidence=[]
            ))
            hypotheses.append(SituationHypothesis(
                hypothesis_id="hyp_screen_strain",
                explanation="장시간 모니터 응시 또는 실내 환기 부족 가능성",
                confidence=0.45,
                supporting_evidence=["작업 지속"],
                conflicting_evidence=[]
            ))

        elif any(kw in state_lower for kw in ("피곤", "지치", "tired", "exhausted")):
            hypotheses.append(SituationHypothesis(
                hypothesis_id="hyp_heavy_workload",
                explanation="프로젝트 및 집중 업무량 증가에 따른 자연스러운 신체적 피로",
                confidence=0.70,
                supporting_evidence=["집중 세션 지속"],
                conflicting_evidence=[]
            ))
            hypotheses.append(SituationHypothesis(
                hypothesis_id="hyp_poor_rest",
                explanation="휴식의 질 저하 또는 수면 패턴의 일시적 불균형",
                confidence=0.60,
                supporting_evidence=["피로 회복 지연 호소"],
                conflicting_evidence=[]
            ))

        else:
            hypotheses.append(SituationHypothesis(
                hypothesis_id="hyp_general_context",
                explanation="일상적인 활동 및 환경적 변화에 따른 상태",
                confidence=0.50,
                supporting_evidence=[observed_state],
                conflicting_evidence=[]
            ))
            hypotheses.append(SituationHypothesis(
                hypothesis_id="hyp_mild_variance",
                explanation="계절 또는 시간대에 따른 자연스러운 신체 리듬 변화",
                confidence=0.40,
                supporting_evidence=["시간대 변화"],
                conflicting_evidence=[]
            ))

        return hypotheses
