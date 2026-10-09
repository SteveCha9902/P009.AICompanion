from typing import List, Tuple, Optional
from app.domain.awareness.awareness_context import SceneObjectType, DetectedObject
from app.domain.shared_reality.shared_reality_context import (
    CandidateFocus,
    UserConfirmationStatus,
    AttentionAnchor
)
from app.services.shared_reality.deictic_resolver import DeicticResolutionEngine

class UserIntentEstimator:
    """
    Estimates user focus intent and confirmation status by synthesizing
    verbal deictic cues with candidate visual objects.
    """

    @classmethod
    def estimate_focus_candidates(
        cls,
        user_utterance: str,
        detected_objects: List[DetectedObject]
    ) -> Tuple[Optional[CandidateFocus], List[CandidateFocus], UserConfirmationStatus, str]:
        """
        Returns (Primary Selected Candidate, Top 3 Candidates, Confirmation Status, Intent Description)
        """
        confirmation_status = UserConfirmationStatus.UNKNOWN
        if DeicticResolutionEngine.is_user_confirming(user_utterance):
            confirmation_status = UserConfirmationStatus.CONFIRMED
        elif DeicticResolutionEngine.is_user_rejecting(user_utterance):
            confirmation_status = UserConfirmationStatus.REJECTED

        # Build candidate focus list
        candidates: List[CandidateFocus] = []
        for obj in detected_objects:
            anchor = cls._resolve_anchor_from_bbox(obj)
            candidates.append(CandidateFocus(
                object_type=obj.type,
                label=obj.label or obj.type.value,
                confidence=obj.confidence,
                anchor=anchor,
                bbox=obj.bbox
            ))

        # Sort by confidence descending
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        top_candidates = candidates[:3]

        # 1. Check for explicit keyword mention (e.g. "이 책 봐봐")
        explicit_type = DeicticResolutionEngine.detect_explicit_object_mention(user_utterance)
        if explicit_type:
            matching = next((c for c in top_candidates if c.object_type == explicit_type), None)
            if matching:
                return (matching, top_candidates, confirmation_status, f"Explicit mention of {explicit_type.value}")
            else:
                # User mentions object even if confidence was slightly lower
                explicit_cand = CandidateFocus(
                    object_type=explicit_type,
                    label=explicit_type.value.lower(),
                    confidence=0.88,
                    anchor=AttentionAnchor.CENTER
                )
                return (explicit_cand, [explicit_cand] + top_candidates[:2], confirmation_status, f"Explicit mention of {explicit_type.value}")

        # 2. Deictic intent ("이거 봐", "어때?") -> Select top confidence candidate
        if DeicticResolutionEngine.has_deictic_intent(user_utterance) and top_candidates:
            primary = top_candidates[0]
            return (primary, top_candidates, confirmation_status, f"Deictic pointer matching top object {primary.object_type.value}")

        # 3. Default fallback
        primary = top_candidates[0] if top_candidates else None
        intent_desc = "Passive scene presence" if primary else "No active focus"
        return (primary, top_candidates, confirmation_status, intent_desc)

    @classmethod
    def _resolve_anchor_from_bbox(cls, obj: DetectedObject) -> AttentionAnchor:
        if not obj.bbox:
            # Fallback based on object type
            type_anchor_map = {
                SceneObjectType.CUP: AttentionAnchor.LOWER_RIGHT,
                SceneObjectType.LAPTOP: AttentionAnchor.LOWER_CENTER,
                SceneObjectType.BOOK: AttentionAnchor.LOWER_LEFT,
                SceneObjectType.PET: AttentionAnchor.LOWER_LEFT,
                SceneObjectType.PLANT: AttentionAnchor.UPPER_RIGHT,
                SceneObjectType.TV: AttentionAnchor.UPPER_LEFT,
            }
            return type_anchor_map.get(obj.type, AttentionAnchor.CENTER)

        center_x = (obj.bbox.x_min + obj.bbox.x_max) / 2.0
        center_y = (obj.bbox.y_min + obj.bbox.y_max) / 2.0

        if center_y > 0.6:
            if center_x < 0.35:
                return AttentionAnchor.LOWER_LEFT
            elif center_x > 0.65:
                return AttentionAnchor.LOWER_RIGHT
            return AttentionAnchor.LOWER_CENTER
        elif center_y < 0.4:
            if center_x < 0.5:
                return AttentionAnchor.UPPER_LEFT
            return AttentionAnchor.UPPER_RIGHT

        return AttentionAnchor.CENTER
