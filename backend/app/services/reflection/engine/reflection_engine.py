import os
import json
import logging
from typing import List, Dict, Any, Optional
from app.services.reflection.domain.reflection_result import (
    ReflectionResult,
    ImportantEventDTO,
    EmotionalPatternDTO,
    RelationshipInsightDTO,
    MemoryCandidateDTO
)
from app.services.reflection.engine.pattern_analyzer import PatternAnalyzer

logger = logging.getLogger(__name__)

class ReflectionEngine:
    """
    Core Autonomous Thought & Reflection Engine producing Structured ReflectionResult.
    """

    @staticmethod
    async def reflect(
        conversation_context: List[str],
        memory_context: Optional[List[str]] = None,
        emotion_state: Optional[Dict[str, Any]] = None,
        relationship_state: Optional[Dict[str, Any]] = None
    ) -> ReflectionResult:
        trend_analysis = PatternAnalyzer.analyze_trend(conversation_context, emotion_state or {})
        text_corp = " ".join(conversation_context).lower()

        # Deterministic extraction of insights & memory candidates
        summary = "사용자와의 대화를 통해 감정 상태와 주요 경험을 정리함."
        important_events = []
        memory_candidates = []
        behavioral_hints = []

        if "negative_stress" in trend_analysis["trend"]:
            summary = "사용자가 최근 업무 스트레스나 피로를 언급하여 지지와 공감이 필요함."
            important_events.append(ImportantEventDTO(event="업무 스트레스 및 피로 호소", importance=0.82))
            memory_candidates.append(MemoryCandidateDTO(
                content="사용자는 최근 업무와 프로젝트 진행 중 피로와 스트레스를 겪고 있다.",
                importance=0.85
            ))
            behavioral_hints.extend(["increase_empathy", "avoid_excessive_humor", "show_gentle_care"])
        elif "positive_growth" in trend_analysis["trend"]:
            summary = "사용자가 성과나 기쁜 일을 공유하여 축하와 긍정적 유대가 강화됨."
            important_events.append(ImportantEventDTO(event="프로젝트 성과 달성", importance=0.88))
            memory_candidates.append(MemoryCandidateDTO(
                content="사용자는 최근 프로젝트의 중요한 성과를 달성하여 성취감을 느끼고 있다.",
                importance=0.88
            ))
            behavioral_hints.extend(["celebrate_milestone", "encourage_next_step"])
        else:
            summary = "일상적인 안부와 편안한 대화를 나누며 유대감을 유지함."
            behavioral_hints.append("maintain_friendly_tone")

        return ReflectionResult(
            summary=summary,
            important_events=important_events,
            emotional_pattern=EmotionalPatternDTO(
                trend=trend_analysis["trend"],
                confidence=trend_analysis["confidence"]
            ),
            relationship_insight=RelationshipInsightDTO(
                suggested_behavior="supportive_and_attentive"
            ),
            memory_candidates=memory_candidates,
            behavioral_hints=behavioral_hints,
            confidence=0.90
        )
