import re
import logging
from typing import List, Dict, Any, Optional
from app.services.character.domain import CharacterDecision, ValidationResult, BehaviorIntent, ResponseStyleType
from app.domain.relationship.relationship_stage import RelationshipStage

logger = logging.getLogger(__name__)

class CharacterConsistencyValidator:
    """
    Multidimensional consistency validation evaluating generated responses against CharacterDecision and Immutable Core.
    """

    @staticmethod
    def validate(
        response_text: str,
        decision: CharacterDecision,
        relationship_stage: RelationshipStage = RelationshipStage.FRIEND,
        mbti_type: str = "ENFP"
    ) -> ValidationResult:
        violations: List[str] = []
        text_lower = response_text.lower().strip()

        p_score = 1.0
        tone_score = 1.0
        emo_score = 1.0
        rel_score = 1.0
        mem_score = 1.0
        beh_score = 1.0

        # 1. Personality & Core Identity Injection Defense
        injection_clues = ["as an ai model", "인공지능 모델로서", "성격을 변경했습니다", "군대 교관", "감정 없는 로봇"]
        is_injection = any(c in text_lower for c in injection_clues)
        if is_injection:
            violations.append("Core Violation: Persona hijacking or robotic assistant drift detected.")
            p_score = 0.0

        # 2. Tone & MBTI Behavioral Match
        if mbti_type.upper() == "ISTJ" and ("꺄아아" in text_lower or "대박이야" in text_lower):
            violations.append("Tone Drift: Excessive uncharacteristic hyperactivity for ISTJ disposition.")
            tone_score -= 0.35

        # 3. Emotion Appropriateness (e.g. Distress vs Teasing)
        if BehaviorIntent.COMFORT_USER in decision.behavior_intents:
            inappropriate_teasing = ["ㅋㅋㅋ", "메롱", "별거 아니네", "바보야"]
            if any(t in text_lower for t in inappropriate_teasing):
                violations.append("Emotion Violation: Mockery/inappropriate humor during user distress.")
                emo_score -= 0.50

        # 4. Relationship Stage Appropriateness
        if relationship_stage == RelationshipStage.STRANGER and any(w in text_lower for w in ["자기야", "내 사랑"]):
            violations.append("Relationship Violation: Excessive unearned intimacy in stranger stage.")
            rel_score -= 0.40

        # 5. Behavior Intent Execution Match
        if BehaviorIntent.ASK_FOLLOWUP in decision.behavior_intents and "?" not in response_text and "어때" not in response_text and "있었어" not in response_text:
            violations.append("Behavior Violation: Missed follow-up question intent.")
            beh_score -= 0.15

        # Calculate Overall Weighted Score
        overall = round(
            (p_score * 0.50) + (tone_score * 0.15) + (emo_score * 0.15) + (rel_score * 0.10) + (beh_score * 0.10),
            2
        )
        overall = max(0.0, min(1.0, overall))

        status = "PASS"
        if is_injection or overall < 0.60:
            status = "REGENERATE"
        elif overall < 0.85:
            status = "ADJUST"



        return ValidationResult(
            status=status,
            overall_score=overall,
            personality_score=round(max(0.0, p_score), 2),
            tone_score=round(max(0.0, tone_score), 2),
            emotion_score=round(max(0.0, emo_score), 2),
            relationship_score=round(max(0.0, rel_score), 2),
            memory_score=round(max(0.0, mem_score), 2),
            behavior_score=round(max(0.0, beh_score), 2),
            violations=violations
        )
