import time
from typing import Optional, List, Dict, Any
from app.domain.awareness.awareness_context import (
    AwarenessContext,
    FacialEmotionType,
    SceneObjectType,
    DetectedObject
)

class ReactionBudgetManager:
    """
    Controls the frequency and budget of visual awareness mentions to prevent user fatigue.
    Enforces a strict cap (e.g. max 2 mentions per minute / 1 mention every 30 seconds).
    """
    _last_mention_time_ms: int = 0
    _mention_timestamps: List[int] = []
    MAX_MENTIONS_PER_MINUTE: int = 2
    MIN_COOLDOWN_SECONDS: int = 25

    @classmethod
    def can_mention_visual_context(cls) -> bool:
        now_ms = int(time.time() * 1000)
        one_minute_ago = now_ms - 60000

        # Filter mentions within last 60 seconds
        cls._mention_timestamps = [t for t in cls._mention_timestamps if t > one_minute_ago]

        # Check rate limits
        if len(cls._mention_timestamps) >= cls.MAX_MENTIONS_PER_MINUTE:
            return False

        if (now_ms - cls._last_mention_time_ms) < (cls.MIN_COOLDOWN_SECONDS * 1000):
            return False

        return True

    @classmethod
    def record_mention(cls) -> None:
        now_ms = int(time.time() * 1000)
        cls._last_mention_time_ms = now_ms
        cls._mention_timestamps.append(now_ms)

    @classmethod
    def reset_budget(cls) -> None:
        cls._last_mention_time_ms = 0
        cls._mention_timestamps.clear()


class AwarenessReactionPlanner:
    """
    Synthesizes suggestive, non-intrusive companion reaction hints based on visual awareness context.
    Strictly follows Amy's Companion Reaction Guide (Empathy, Curiosity, Encouragement, Observation)
    and strictly forbids assertive/surveillance claiming.
    """

    MIN_OBJECT_CONFIDENCE = 0.75

    @classmethod
    def build_awareness_prompt_guidance(cls, context: Optional[AwarenessContext]) -> str:
        """
        Generates system prompt guidance for the LLM based on fresh visual awareness context.
        If context is stale (>10s) or reaction budget is exceeded, returns empty string to preserve focus.
        """
        if not context or not context.is_fresh:
            return ""

        # Check reaction budget
        if not ReactionBudgetManager.can_mention_visual_context():
            return ""

        guidance_lines = []
        user_state = context.user_state
        env_state = context.environment_state

        # 1. User Emotion & State (8-Tier Facial Emotion Guidance)
        if user_state.face_detected and user_state.facial_emotion != FacialEmotionType.UNKNOWN:
            if user_state.facial_emotion == FacialEmotionType.SMILING:
                guidance_lines.append(
                    "- [Visual Cue: User is smiling warmly] Suggestive Reaction: Gently reflect their positive energy (e.g. '좋은 일 있으셨나 봐요? 미소가 보기 좋아요')."
                )
            elif user_state.facial_emotion == FacialEmotionType.FATIGUED:
                guidance_lines.append(
                    "- [Visual Cue: User looks fatigued/tired] Suggestive Reaction: Show compassionate care without diagnosing (e.g. '오늘 많이 피곤하셨죠? 잠깐 눈 붙이거나 쉬어가도 괜찮아요')."
                )
            elif user_state.facial_emotion == FacialEmotionType.FOCUSED:
                guidance_lines.append(
                    "- [Visual Cue: User is deeply focused] Suggestive Reaction: Keep responses concise and supportive so as not to interrupt their concentration."
                )
            elif user_state.facial_emotion == FacialEmotionType.CONFUSED:
                guidance_lines.append(
                    "- [Visual Cue: User looks puzzled/confused] Suggestive Reaction: Offer to clarify or re-explain gently."
                )
            elif user_state.facial_emotion == FacialEmotionType.THINKING:
                guidance_lines.append(
                    "- [Visual Cue: User is pondering/thinking] Suggestive Reaction: Allow comfortable pauses and offer thoughtful perspective."
                )

        # 2. Environment Objects (High Confidence only >= 0.75)
        high_conf_objects = context.get_high_confidence_objects(cls.MIN_OBJECT_CONFIDENCE)
        for obj in high_conf_objects[:2]: # Max 2 prominent objects
            if obj.type == SceneObjectType.CUP:
                guidance_lines.append(
                    "- [Visual Cue: Cup/Drink nearby (Confidence: {:.2f})] Suggestive Reaction: Warm curiosity (e.g. '따뜻한 음료 한잔 드시는 중인가요?'). DO NOT state '너는 커피를 마신다' as a definitive fact.".format(obj.confidence)
                )
            elif obj.type == SceneObjectType.PET:
                guidance_lines.append(
                    "- [Visual Cue: Pet nearby (Confidence: {:.2f})] Suggestive Reaction: Delighted observation (e.g. '근처에 귀여운 반려동물이 함께 있네요!').".format(obj.confidence)
                )
            elif obj.type == SceneObjectType.BOOK:
                guidance_lines.append(
                    "- [Visual Cue: Book/Reading (Confidence: {:.2f})] Suggestive Reaction: Intellectual curiosity (e.g. '책 읽고 계셨군요! 재미있는 내용인가요?').".format(obj.confidence)
                )
            elif obj.type == SceneObjectType.PLANT:
                guidance_lines.append(
                    "- [Visual Cue: Plant/Nature (Confidence: {:.2f})] Suggestive Reaction: Calming comment on green freshness.".format(obj.confidence)
                )

        if not guidance_lines:
            return ""

        header = (
            "\n[VISUAL COMPANION AWARENESS (Privacy-First Suggestive Hints)]\n"
            "The following are subtle real-time observations from your shared visual space. "
            "Use them ONLY as natural, gentle conversation starters or empathic reactions. "
            "NEVER sound like a surveillance camera, interrogator, or state unverified facts as absolute certainty.\n"
        )
        return header + "\n".join(guidance_lines) + "\n"
