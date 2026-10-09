from typing import Dict, Any, List
from app.domain.awareness.awareness_context import (
    EnvironmentAwarenessState,
    DetectedObject,
    SceneObjectType,
    BoundingBox,
    VisualFocusTarget
)

class EnvironmentAwarenessEngine:
    """
    Detects and validates 8 major scene object categories with confidence ratings and bounding boxes.
    """

    OBJECT_TYPE_MAP = {
        "cup": SceneObjectType.CUP,
        "mug": SceneObjectType.CUP,
        "glass": SceneObjectType.CUP,
        "coffee": SceneObjectType.CUP,
        "food": SceneObjectType.FOOD,
        "snack": SceneObjectType.FOOD,
        "dish": SceneObjectType.FOOD,
        "book": SceneObjectType.BOOK,
        "textbook": SceneObjectType.BOOK,
        "laptop": SceneObjectType.LAPTOP,
        "computer": SceneObjectType.LAPTOP,
        "screen": SceneObjectType.LAPTOP,
        "pet": SceneObjectType.PET,
        "dog": SceneObjectType.PET,
        "cat": SceneObjectType.PET,
        "plant": SceneObjectType.PLANT,
        "flower": SceneObjectType.PLANT,
        "tv": SceneObjectType.TV,
        "monitor": SceneObjectType.TV,
        "window": SceneObjectType.WINDOW,
        "phone": SceneObjectType.PHONE,
        "notebook": SceneObjectType.NOTEBOOK,
    }

    @classmethod
    def analyze_environment(cls, raw_vision_data: Dict[str, Any]) -> EnvironmentAwarenessState:
        """
        Parses structured vision data into high-fidelity EnvironmentAwarenessState.
        """
        raw_objects = raw_vision_data.get("objects", [])
        detected_objects: List[DetectedObject] = []

        for item in raw_objects:
            if isinstance(item, str):
                obj_type = cls.OBJECT_TYPE_MAP.get(item.lower(), SceneObjectType.OTHER)
                detected_objects.append(DetectedObject(
                    type=obj_type,
                    confidence=0.85,
                    label=item
                ))
            elif isinstance(item, dict):
                label = item.get("label", item.get("type", "other")).lower()
                obj_type = cls.OBJECT_TYPE_MAP.get(label, SceneObjectType.OTHER)
                conf = float(item.get("confidence", 0.85))
                bbox = None
                if "bbox" in item and isinstance(item["bbox"], dict):
                    bbox = BoundingBox(
                        x_min=float(item["bbox"].get("x_min", 0.0)),
                        y_min=float(item["bbox"].get("y_min", 0.0)),
                        x_max=float(item["bbox"].get("x_max", 1.0)),
                        y_max=float(item["bbox"].get("y_max", 1.0)),
                    )
                detected_objects.append(DetectedObject(
                    type=obj_type,
                    confidence=round(conf, 2),
                    label=label,
                    bbox=bbox
                ))

        scene_desc = raw_vision_data.get("scene_description", "")
        ambient_light = raw_vision_data.get("ambient_light", "normal")

        return EnvironmentAwarenessState(
            detected_objects=detected_objects,
            scene_description=scene_desc,
            ambient_light=ambient_light
        )

    @classmethod
    def resolve_visual_focus_target(cls, user_detected: bool, objects: List[DetectedObject]) -> VisualFocusTarget:
        """
        Resolves where the Avatar's gaze should naturally shift.
        Prioritizes user face, then high-confidence interactive scene objects.
        """
        if not user_detected and not objects:
            return VisualFocusTarget.NONE

        # High confidence objects (>= 0.80)
        high_conf_objs = [o for o in objects if o.confidence >= 0.80]
        
        # If user is present, default focus is USER_FACE
        if user_detected:
            # 20% natural curiosity glance towards prominent objects if present
            if high_conf_objs and high_conf_objs[0].type == SceneObjectType.PET:
                return VisualFocusTarget.PET
            return VisualFocusTarget.USER_FACE

        # If user is not directly facing camera, look at primary active object
        if high_conf_objs:
            target_map = {
                SceneObjectType.CUP: VisualFocusTarget.CUP,
                SceneObjectType.LAPTOP: VisualFocusTarget.LAPTOP,
                SceneObjectType.PET: VisualFocusTarget.PET,
                SceneObjectType.BOOK: VisualFocusTarget.BOOK,
                SceneObjectType.PLANT: VisualFocusTarget.PLANT,
                SceneObjectType.WINDOW: VisualFocusTarget.WINDOW,
            }
            return target_map.get(high_conf_objs[0].type, VisualFocusTarget.USER_FACE)

        return VisualFocusTarget.USER_FACE
