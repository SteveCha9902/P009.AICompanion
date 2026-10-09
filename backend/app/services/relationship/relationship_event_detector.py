from typing import List, Optional
from datetime import datetime, timedelta
from app.domain.relationship.relationship_event import RelationshipEventType

class RelationshipEventDetector:
    """
    Detects relationship events and interaction signals from user dialogue and temporal patterns.
    """

    @staticmethod
    def detect_events(
        user_input: str,
        total_conversations: int,
        last_interacted_at: Optional[datetime] = None
    ) -> List[RelationshipEventType]:
        events: List[RelationshipEventType] = []
        input_lower = user_input.lower().strip()

        # 1. First Meeting Event
        if total_conversations == 0:
            events.append(RelationshipEventType.FIRST_CONVERSATION)

        # 2. Temporal Absence / Return Detection
        if last_interacted_at:
            delta_days = (datetime.utcnow() - last_interacted_at).total_seconds() / 86400.0
            if delta_days >= 7.0:
                events.append(RelationshipEventType.LONG_ABSENCE)
                events.append(RelationshipEventType.RETURN_AFTER_ABSENCE)

        # 3. Personal Story / Vulnerability Sharing
        confession_keywords = [
            "비밀인데", "아무한테도 말 안 했는데", "사실 나", "혼자만 알고 있어",
            "솔직히 말하면", "남들에게 말 못", "my secret", "told nobody else",
            "deep secret", "vulnerable"
        ]
        if any(kw in input_lower for kw in confession_keywords):
            events.append(RelationshipEventType.PERSONAL_STORY_SHARED)

        # 4. Expression of Trust
        trust_keywords = [
            "너만 믿어", "너라서 말하는 거야", "너는 믿을 수 있어", "i trust you",
            "always trust", "reliable"
        ]
        if any(kw in input_lower for kw in trust_keywords):
            events.append(RelationshipEventType.USER_SHOWED_TRUST)

        # 5. Advice / Guidance Seeking
        advice_keywords = [
            "어떻게 해야 할까", "조언 좀 해줘", "너라면 어떻게 할래", "상담하고 싶어",
            "what should i do", "need your advice"
        ]
        if any(kw in input_lower for kw in advice_keywords):
            events.append(RelationshipEventType.USER_REQUESTED_ADVICE)

        # 6. Expression of Gratitude
        gratitude_keywords = [
            "고마워", "감사해", "덕분이야", "힘이 됐어", "위로가 돼",
            "thank you", "thanks to you", "appreciate"
        ]
        if any(kw in input_lower for kw in gratitude_keywords):
            events.append(RelationshipEventType.USER_EXPRESSED_GRATITUDE)

        # 7. Expression of Warmth / Affection
        affection_keywords = [
            "너가 참 좋아", "너랑 이야기하면 편해", "소중해", "너 최고야",
            "like you", "fond of you", "comforting"
        ]
        if any(kw in input_lower for kw in affection_keywords):
            events.append(RelationshipEventType.USER_EXPRESSED_AFFECTION)

        # Fallback to general interaction
        if not events:
            events.append(RelationshipEventType.GENERAL_INTERACTION)

        return events
