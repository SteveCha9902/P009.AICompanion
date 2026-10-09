from enum import Enum
from typing import List, Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
import time

class BehaviorIntent(str, Enum):
    RESPOND = "RESPOND"                         # 일반적인 자연스러운 응답
    ASK = "ASK"                                 # 호기심이나 관심 질문
    RECALL = "RECALL"                           # 과거 관계 기억 회상 및 연결
    RECALL_TIMELINE = "RECALL_TIMELINE"         # 시간축과 서사를 가진 인생 타임라인 회상
    GENTLE_RECALL = "GENTLE_RECALL"             # 부드럽고 완곡한 자율 회상
    LIFE_CHAPTER_RECALL = "LIFE_CHAPTER_RECALL" # 인생 챕터의 거시적 서사 회상
    REFLECT = "REFLECT"                         # 함께 보낸 시간과 관계에 대한 성찰
    REMINISCE = "REMINISCE"                     # 아련하고 다정한 추억 회상
    PLAN = "PLAN"                               # 미래 목표 및 마일스톤 계획 제안
    GOAL_REVIEW = "GOAL_REVIEW"                 # 부드럽고 비압박적인 목표 안부/진척 확인
    CELEBRATE_PROGRESS = "CELEBRATE_PROGRESS"   # 마일스톤 달성 및 노력 축하/응원
    SOFT_ENCOURAGEMENT = "SOFT_ENCOURAGEMENT"   # 부담 없는 따뜻한 격려와 지지
    ENCOURAGE = "ENCOURAGE"                     # 활기찬 응원과 지지
    OBSERVE = "OBSERVE"                         # 현재 시각/공유 현실 사물 관찰
    PASSIVE_OBSERVE = "PASSIVE_OBSERVE"         # 배경에서 조용히 관찰 (아무 행동 안 함)
    LIGHT_ATTENTION = "LIGHT_ATTENTION"         # 시선만 살짝 반응하며 온화하게 주시
    LISTEN = "LISTEN"                           # 조용히 들어주기 (경청)
    WAIT = "WAIT"                               # 발화 대기 및 차분한 호흡
    SILENT_COMPANION = "SILENT_COMPANION"       # 온화한 미소로 곁을 지키는 침묵의 동반자
    SILENCE = "SILENCE"                         # 말없이 곁을 지키며 온화하게 대기
    PROACTIVE_START = "PROACTIVE_START"         # 먼저 안부나 대화 시작
    UNDERSTAND_CONTEXT = "UNDERSTAND_CONTEXT"   # 현재 사용자의 상황과 환경 맥락 이해
    PREDICT_NEED = "PREDICT_NEED"               # 다가오는 일정/상황에 대한 부드러운 지원 기회 제시
    SITUATION_RECALL = "SITUATION_RECALL"       # 현재 상황과 연결된 과거 패턴 및 사건 회상
    CAUSAL_REFLECTION = "CAUSAL_REFLECTION"     # 상태와 사건 간의 다중 가설 인과 성찰






class CandidateIntent(BaseModel):
    intent: BehaviorIntent
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = ""

class BehaviorDecision(BaseModel):
    selected_intent: BehaviorIntent
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    candidate_intents: List[CandidateIntent] = Field(default_factory=list)
    primary_layer: str = "AFFECTIVE"
    trace_reason: str = ""
    prompt_directive: str = ""
    avatar_expression: str = "neutral"
    voice_rate: float = 1.0
    voice_pitch: float = 1.0
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
