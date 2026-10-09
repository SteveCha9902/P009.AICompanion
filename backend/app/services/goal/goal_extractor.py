import time
from typing import Optional, List
from app.domain.goal.goal import GoalCandidate, GoalType

class GoalExtractor:
    """
    Extracts potential goal candidates from conversational intentions and desires without forced creation.
    """

    @classmethod
    def extract_goal_candidate(cls, user_id: str, utterance: str) -> Optional[GoalCandidate]:
        text = utterance.strip()

        # Check for goal-oriented intent markers
        is_goal_phrase = any(kw in text for kw in ("싶어", "갈 거야", "계획", "시작했어", "목표", "준비", "도전", "배우"))
        if not is_goal_phrase:
            return None


        # Determine type
        gtype = GoalType.CUSTOM
        if any(w in text for w in ("운동", "체력", "다이어트", "건강", "수면", "걷기")):
            gtype = GoalType.HEALTH
        elif any(w in text for w in ("여행", "일본", "제주도", "휴가", "캠핑")):
            gtype = GoalType.TRAVEL
        elif any(w in text for w in ("공부", "자격증", "합격", "시험", "배우")):
            gtype = GoalType.LEARNING
        elif any(w in text for w in ("아들", "가족", "부모님", "외박")):
            gtype = GoalType.FAMILY
        elif any(w in text for w in ("프로젝트", "개발", "작업")):
            gtype = GoalType.PROJECT
        elif any(w in text for w in ("식물", "화분", "가구", "인테리어")):
            gtype = GoalType.HOME

        title = text
        conf = 0.85 if "시작했어" in text or "목표야" in text else 0.65
        prompt = f"'{title}'에 대해 이야기하셨는데, 앞으로 함께 응원할 목표로 기억해둘까요?"

        return GoalCandidate(
            candidate_id=f"cand_{int(time.time()*1000)}",
            user_id=user_id,
            title=title,
            goal_type=gtype,
            confidence=conf,
            suggested_confirmation_prompt=prompt
        )
