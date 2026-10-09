import re
from typing import Optional, List
from app.domain.memory.relationship_memory import RelationshipMemory, MemoryType
from app.domain.awareness.awareness_context import AwarenessContext, SceneObjectType
from app.services.memory.relationship.privacy_filter import PrivacyFilterEngine
from app.services.memory.relationship.importance_scorer import ImportanceScoringEngine

class CandidateExtractor:
    """
    Extracts high-value relationship memory candidates from user utterance
    and links visual signature tags from Visual Awareness / Shared Reality.
    """

    PATTERNS = [
        (r"(강아지|고양이|반려견|반려묘|키우게 됐어|입양|데려왔어)", MemoryType.PET, "반려동물 입양 및 양육"),
        (r"(식물|화분|몬스테라|다육이|선인장|키우기 시작|새로 산 식물)", MemoryType.OBJECT, "반려식물 키우기"),
        (r"(프로젝트|개발 시작|론칭|창업|출시 준비|마감|작업 중)", MemoryType.PROJECT, "진행 중인 주요 프로젝트"),
        (r"(취미|배우기 시작|운동 시작|헬스|수영|기타|그림|요가)", MemoryType.HOBBY, "새로운 취미 및 여가 활동"),
        (r"(목표|다이어트|자격증|합격|목표로|결심했어)", MemoryType.GOAL, "달성하고자 하는 개인 목표"),
        (r"(엄마|아빠|가족|친구|동생|형|누나|언니|남편|아내|여친|남친)", MemoryType.PERSON, "소중한 사람들과의 관계"),
        (r"(제주도|여행 가|이사|새 동네|자주 가는 카페)", MemoryType.PLACE, "의미 있는 장소 및 여행"),
        (r"(좋아해|싫어해|라떼만 마셔|민트초코|최애)", MemoryType.PREFERENCE, "취향 및 기호"),
    ]

    @classmethod
    def extract_candidate_memory(
        cls,
        user_id: str,
        companion_id: str,
        user_utterance: str,
        awareness_context: Optional[AwarenessContext] = None
    ) -> Optional[RelationshipMemory]:
        # 1. Privacy Safety Filter
        is_safe, _ = PrivacyFilterEngine.is_safe_to_store(user_utterance)
        if not is_safe:
            return None

        # 2. Extract Memory Type & Base Summary
        matched_type: Optional[MemoryType] = None
        matched_summary: str = ""

        for pat, mem_type, desc in cls.PATTERNS:
            if re.search(pat, user_utterance):
                matched_type = mem_type
                matched_summary = f"{desc}: {user_utterance.strip()}"
                break

        if not matched_type:
            return None

        # 3. Visual Signature Tags Linking (No raw images, tags only)
        visual_tags: List[str] = []
        if awareness_context and awareness_context.is_fresh:
            for obj in awareness_context.environment_state.detected_objects:
                if obj.confidence >= 0.75:
                    tag = obj.type.value
                    if obj.label:
                        tag += f":{obj.label}"
                    visual_tags.append(tag)

        # 4. 3-Axis Importance Evaluation
        imp, fut, rel, composite = ImportanceScoringEngine.evaluate_3_axis_scores(
            memory_type=matched_type,
            summary=user_utterance
        )

        if not ImportanceScoringEngine.should_persist(composite):
            return None

        created_ms = int(RelationshipMemory.calculate_default_expiry(matched_type, 0) or 0)
        # Calculate real expiry ms
        from time import time
        now_ms = int(time() * 1000)
        expiry_ms = RelationshipMemory.calculate_default_expiry(matched_type, now_ms)

        return RelationshipMemory(
            user_id=user_id,
            companion_id=companion_id,
            memory_type=matched_type,
            summary=matched_summary,
            importance_score=imp,
            future_relevance=fut,
            relationship_value=rel,
            confidence=0.90,
            visual_tags=visual_tags,
            created_at_ms=now_ms,
            last_referenced_at_ms=now_ms,
            expires_at_ms=expiry_ms
        )
