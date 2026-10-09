import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.models.reflection import ReflectionRecordModel
from app.services.reflection.domain.reflection import (
    ReflectionTrigger,
    ReflectionPriority,
    ReflectionStatus,
    ReflectionRecord
)
from app.services.reflection.policy.reflection_policy import ReflectionPolicy
from app.services.reflection.engine.reflection_engine import ReflectionEngine
from app.services.reflection.validation.reflection_validator import ReflectionValidator
from app.services.reflection.memory.consolidation_engine import MemoryConsolidationEngine
from app.services.reflection.runtime.rate_limiter import ReflectionRateLimiter

logger = logging.getLogger(__name__)

# Global rate limiter instance
_global_rate_limiter = ReflectionRateLimiter(cooldown_seconds=10.0, max_reflections_per_conversation=10)

class ReflectionService:
    """
    Facade orchestrating the entire Autonomous Thought & Reflection Pipeline.
    """

    def __init__(self, db: AsyncSession, rate_limiter: Optional[ReflectionRateLimiter] = None):
        self.db = db
        self.rate_limiter = rate_limiter or _global_rate_limiter

    async def evaluate_and_reflect(
        self,
        companion_id: str,
        conversation_id: str,
        interaction_id: Optional[str] = None,
        recent_messages: Optional[List[str]] = None,
        emotion_state: Optional[Dict[str, Any]] = None,
        relationship_state: Optional[Dict[str, Any]] = None,
        emotion_intensity: float = 0.0,
        memory_importance: float = 0.0,
        relationship_delta: float = 0.0,
        is_manual: bool = False
    ) -> Optional[ReflectionRecord]:
        # 1. Evaluate Policy
        decision = ReflectionPolicy.evaluate(
            emotion_intensity=emotion_intensity,
            memory_importance=memory_importance,
            relationship_delta=relationship_delta,
            is_manual=is_manual
        )
        if not decision.should_reflect:
            return None

        # 2. Rate Limit Check
        allowed, msg = self.rate_limiter.is_allowed(conversation_id, decision.trigger.value)
        if not allowed:
            logger.info(f"[ReflectionService] Reflection skipped for {conversation_id}: {msg}")
            return None

        self.rate_limiter.record_execution(conversation_id, decision.trigger.value)

        # 3. Create Pending Record
        record_id = str(uuid.uuid4())
        rec_model = ReflectionRecordModel(
            id=record_id,
            companion_id=companion_id,
            conversation_id=conversation_id,
            interaction_id=interaction_id,
            trigger_type=decision.trigger.value,
            priority=decision.priority.value,
            importance_score=max(emotion_intensity, memory_importance, 0.5),
            status=ReflectionStatus.RUNNING.value
        )
        self.db.add(rec_model)
        await self.db.commit()

        # 4. Execute Reflection Engine
        try:
            result = await ReflectionEngine.reflect(
                conversation_context=recent_messages or [],
                emotion_state=emotion_state,
                relationship_state=relationship_state
            )

            # 5. Validation Layer (Trust Boundary)
            is_valid, validation_reasons = ReflectionValidator.validate(result)
            if not is_valid:
                rec_model.status = ReflectionStatus.REJECTED.value
                rec_model.reflection_summary = f"Rejected: {', '.join(validation_reasons)}"
                await self.db.commit()
                return None

            # 6. Memory Consolidation
            if result.memory_candidates:
                await MemoryConsolidationEngine.consolidate(self.db, companion_id, result.memory_candidates)

            # 7. Update Record to Completed
            rec_model.reflection_summary = result.summary
            rec_model.emotional_pattern = result.emotional_pattern.model_dump()
            rec_model.relationship_insight = result.relationship_insight.model_dump()
            rec_model.behavioral_hints = result.behavioral_hints
            rec_model.status = ReflectionStatus.COMPLETED.value
            rec_model.completed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(rec_model)

            logger.info(f"[ReflectionService] Reflection {record_id} COMPLETED successfully.")

            return ReflectionRecord(
                id=rec_model.id,
                companion_id=rec_model.companion_id,
                conversation_id=rec_model.conversation_id,
                interaction_id=rec_model.interaction_id,
                trigger_type=decision.trigger,
                priority=decision.priority,
                importance_score=rec_model.importance_score,
                reflection_summary=rec_model.reflection_summary,
                emotional_pattern=rec_model.emotional_pattern,
                relationship_insight=rec_model.relationship_insight,
                behavioral_hints=rec_model.behavioral_hints,
                status=ReflectionStatus.COMPLETED,
                created_at=rec_model.created_at,
                completed_at=rec_model.completed_at
            )

        except Exception as e:
            logger.error(f"[ReflectionService] Reflection {record_id} failed: {e}", exc_info=True)
            rec_model.status = ReflectionStatus.FAILED.value
            rec_model.reflection_summary = f"Failed: {str(e)}"
            await self.db.commit()
            return None

    async def get_recent_insights(
        self,
        companion_id: str,
        limit: int = 1
    ) -> List[ReflectionRecord]:
        stmt = (
            select(ReflectionRecordModel)
            .where(
                ReflectionRecordModel.companion_id == companion_id,
                ReflectionRecordModel.status == ReflectionStatus.COMPLETED.value
            )
            .order_by(desc(ReflectionRecordModel.created_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        models = res.scalars().all()

        return [
            ReflectionRecord(
                id=m.id,
                companion_id=m.companion_id,
                conversation_id=m.conversation_id,
                interaction_id=m.interaction_id,
                trigger_type=ReflectionTrigger(m.trigger_type),
                priority=ReflectionPriority(m.priority),
                importance_score=m.importance_score,
                reflection_summary=m.reflection_summary,
                emotional_pattern=m.emotional_pattern,
                relationship_insight=m.relationship_insight,
                behavioral_hints=m.behavioral_hints,
                status=ReflectionStatus(m.status),
                created_at=m.created_at,
                completed_at=m.completed_at
            )
            for m in models
        ]
