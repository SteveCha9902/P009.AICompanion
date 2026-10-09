from typing import Dict, Any, Optional
from app.domain.awareness.awareness_context import AwarenessContext, VisualFocusTarget
from app.services.awareness.user_awareness_engine import UserAwarenessEngine
from app.services.awareness.environment_awareness_engine import EnvironmentAwarenessEngine

class AwarenessEngineCoordinator:
    """
    Central Coordinator for Sprint 48 Visual Awareness & Companion Perception Engine.
    Converts raw vision analyzer structured outputs into validated AwarenessContext DTOs.
    """

    _cached_awareness_context: Optional[AwarenessContext] = None

    @classmethod
    def process_vision_observation(cls, raw_vision_data: Dict[str, Any]) -> AwarenessContext:
        """
        Processes vision output with Ephemeral In-Memory pipeline (No Raw Image Storage).
        """
        user_state = UserAwarenessEngine.analyze_user_presence(raw_vision_data)
        env_state = EnvironmentAwarenessEngine.analyze_environment(raw_vision_data)
        
        focus_target = EnvironmentAwarenessEngine.resolve_visual_focus_target(
            user_detected=user_state.face_detected,
            objects=env_state.detected_objects
        )

        context = AwarenessContext(
            user_state=user_state,
            environment_state=env_state,
            focus_target=focus_target,
            confidence=float(raw_vision_data.get("confidence", 0.90))
        )

        cls._cached_awareness_context = context
        return context

    @classmethod
    def get_current_awareness_context(cls) -> Optional[AwarenessContext]:
        """
        Returns cached awareness context if fresh (<= 10 seconds), otherwise None.
        """
        if cls._cached_awareness_context and cls._cached_awareness_context.is_fresh:
            return cls._cached_awareness_context
        return None

    @classmethod
    def clear_cache(cls) -> None:
        cls._cached_awareness_context = None
