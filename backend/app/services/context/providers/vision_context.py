from typing import List, Any
from app.services.context.providers.base import ContextProvider
from app.services.awareness.awareness_coordinator import AwarenessEngineCoordinator

class VisionContextProvider(ContextProvider):
    def __init__(self, db: Any = None):
        self.db = db

    async def build_context(self, conversation_id: str, current_user_message: str) -> List[dict]:
        """
        Build semantic context from DB observation (if available) and AwarenessEngineCoordinator.
        Zero Raw Frame Storage, privacy-first in-memory DTO.
        """
        context_lines = []

        # 1. Try In-Memory Awareness Coordinator (Sprint 48 & 49)
        awareness = AwarenessEngineCoordinator.get_current_awareness_context()
        if awareness and awareness.user_state.user_presence:
            context_lines.append("FACE_DETECTED: 사용자가 스마트폰 전면 카메라 앞에 분명하게 존재함 (User Presence: True)")
            if awareness.user_state.face_detected:
                context_lines.append(f"사용자 표정/감정: {awareness.user_state.facial_emotion.value}, 시선: {awareness.user_state.gaze_direction}")
            if awareness.user_state.user_appearance:
                context_lines.append(f"사용자 외모 특징: {awareness.user_state.user_appearance}")
            if awareness.user_state.clothing:
                context_lines.append(f"사용자 착용 의상/옷차림: {awareness.user_state.clothing}")
            if awareness.environment_state.scene_description:
                context_lines.append(f"주변 배경/환경: {awareness.environment_state.scene_description}")
            if awareness.environment_state.detected_objects:
                objs = [f"{o.label or o.type.value}({o.confidence:.2f})" for o in awareness.environment_state.detected_objects]
                context_lines.append(f"주변 감지 객체: {', '.join(objs)}")

        if not context_lines:
            context_lines.append("CAMERA_STATUS: 카메라 활성화 상태, 현재 세부 시각 관측 정보 없음.")

        semantic_text = (
            "[CURRENT VISUAL CONTEXT]\n"
            + "\n".join(context_lines)
            + "\n\n[CRITICAL MANDATE - REAL-TIME SIGHT]:\n"
            + "1. 당신은 스마트폰 전면 카메라를 통해 전달된 [CURRENT VISUAL CONTEXT]의 시각 관측 정보에만 기반하여 대화해야 합니다.\n"
            + "2. [CURRENT VISUAL CONTEXT]에 명시되지 않은 세부 시각 정보(얼굴 표정, 옷차림, 주변 물건 등)는 임의로 추측하거나 꾸며내지 말고, 현재 화면에서 명확히 확인되지 않는다고 솔직하게 답변하세요.\n"
            + "3. 관측 데이터가 존재하는 경우에만 해당 시각 정보를 자연스럽고 다정하게 대화에 반영하세요."
        )
        
        return [
            {
                "role": "system",
                "content": semantic_text
            }
        ]
