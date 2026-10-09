from typing import Optional
from app.domain.awareness.awareness_context import SceneObjectType
from app.domain.shared_reality.shared_reality_context import (
    SharedRealityContext,
    JointAttentionState,
    UserConfirmationStatus
)

class SharedRealityPlanner:
    """
    Generates joint attention dialogue directives for the LLM system prompt.
    Adheres strictly to Amy's Shared Reality Dialogue Guide (Observation, Curiosity, Empathy)
    and strictly forbids definitive dogmatic claiming ("그건 100% ○○다").
    """

    @classmethod
    def build_shared_reality_directive(cls, context: Optional[SharedRealityContext]) -> str:
        if not context or context.state == JointAttentionState.NONE or not context.focus_target:
            return ""

        target_name = context.target_label or context.focus_target.value.lower()
        state = context.state

        guidance_body = ""
        if state == JointAttentionState.DISCUSSING_TARGET:
            guidance_body = (
                f"- [ACTIVE JOINT DISCUSSION: {target_name.upper()}]\n"
                f"You and the user are actively sharing attention on this {target_name}. "
                f"Continue the conversation naturally, exploring details or personal thoughts with warm enthusiasm."
            )
        elif state == JointAttentionState.SHARED_FOCUS:
            if context.focus_target == SceneObjectType.CUP:
                guidance_body = (
                    f"- [SHARED ATTENTION: CUP/DRINK (Confidence: {context.target_confidence:.2f})]\n"
                    f"Suggestive Focus: Warm curiosity (e.g. '새로 산 컵이야? 디자인 깔끔하다', '따뜻한 커피 마시는 중이야?'). "
                    f"DO NOT state '그건 100% 커피다' as an absolute certainty."
                )
            elif context.focus_target == SceneObjectType.BOOK:
                guidance_body = (
                    f"- [SHARED ATTENTION: BOOK (Confidence: {context.target_confidence:.2f})]\n"
                    f"Suggestive Focus: Intellectual curiosity (e.g. '어떤 책 읽고 있어? 재미있는 내용이야?')."
                )
            elif context.focus_target == SceneObjectType.PET:
                guidance_body = (
                    f"- [SHARED ATTENTION: PET (Confidence: {context.target_confidence:.2f})]\n"
                    f"Suggestive Focus: Delighted affection (e.g. '정말 귀여운 아이네! 이름이 뭐야?')."
                )
            elif context.focus_target == SceneObjectType.PLANT:
                guidance_body = (
                    f"- [SHARED ATTENTION: PLANT (Confidence: {context.target_confidence:.2f})]\n"
                    f"Suggestive Focus: Calm observation (e.g. '화분이 싱그럽고 예쁘네. 정성 들여 키우나 봐')."
                )
            elif context.focus_target == SceneObjectType.LAPTOP:
                guidance_body = (
                    f"- [SHARED ATTENTION: LAPTOP (Confidence: {context.target_confidence:.2f})]\n"
                    f"Suggestive Focus: Supportive encouragement (e.g. '열심히 작업 중이구나! 힘내')."
                )
            else:
                guidance_body = (
                    f"- [SHARED ATTENTION: {target_name.upper()} (Confidence: {context.target_confidence:.2f})]\n"
                    f"Suggestive Focus: Natural curiosity and friendly engagement."
                )
        elif state == JointAttentionState.USER_FOCUS:
            guidance_body = (
                f"- [USER INTEREST NOTICED: {target_name.upper()}]\n"
                f"Subtly notice what the user is interacting with without interrupting aggressively."
            )

        if not guidance_body:
            return ""

        header = (
            "\n[SHARED REALITY & JOINT ATTENTION DIRECTIVE]\n"
            "You are looking at the exact same physical scene together with the user.\n"
        )
        return header + guidance_body + "\n"
