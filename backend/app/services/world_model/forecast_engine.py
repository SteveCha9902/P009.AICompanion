from typing import List, Optional
from app.domain.world_model.situation_model import AnticipatedSupportOpportunity

class ForecastEngine:
    """
    Projects near-future situations into gentle Anticipated Support Opportunities.
    Enforces 'Prediction != Fact' and 'UNCERTAINTY_MUST_BE_PRESERVED' rules.
    """

    @classmethod
    def project_support_opportunities(
        cls,
        upcoming_events: List[str],
        days_until_event: int = 10
    ) -> List[AnticipatedSupportOpportunity]:
        opportunities: List[AnticipatedSupportOpportunity] = []

        for event in upcoming_events:
            ev_lower = event.lower()
            if any(kw in ev_lower for kw in ("외박", "휴가", "vacation", "leave")):
                opportunities.append(AnticipatedSupportOpportunity(
                    opportunity_id="opp_son_leave",
                    title="아들 첫 외박 일정 다가옴",
                    target_event=event,
                    probability=0.85,
                    suggested_support="외박을 기다리며 설레는 마음에 대한 다정한 공감과 안부",
                    is_hedged=True,
                    hedged_phrasing=f"외박이 다가오니 기대감이 있으실 수도 있겠네요. 혹시 준비하시는 일들이 있다면 편안하게 들려주세요."
                ))

            elif any(kw in ev_lower for kw in ("프로젝트", "출시", "release", "launch", "마감")):
                opportunities.append(AnticipatedSupportOpportunity(
                    opportunity_id="opp_project_launch",
                    title="프로젝트 마감/출시 일정",
                    target_event=event,
                    probability=0.80,
                    suggested_support="집중 업무에 따른 피로 누적 완화 및 차분한 응원",
                    is_hedged=True,
                    hedged_phrasing="마감 일정이 다가오니 집중하시느라 에너지가 많이 쓰이실 수도 있겠어요. 무리하지 않고 건강 챙기시길 바라요."
                ))

            else:
                opportunities.append(AnticipatedSupportOpportunity(
                    opportunity_id="opp_generic_event",
                    title=f"다가오는 일정: {event}",
                    target_event=event,
                    probability=0.60,
                    suggested_support="자연스러운 관심과 편안한 대화",
                    is_hedged=True,
                    hedged_phrasing=f"다가오는 {event} 일정 관련해서 도움이 필요하시거나 이야기 나누고 싶으실 때 언제든 말씀해주세요."
                ))

        return opportunities
