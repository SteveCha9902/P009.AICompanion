import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.relationship import RelationshipState as RelationshipStateModel, RelationshipEvent as RelationshipEventModel
from app.domain.relationship.relationship_dimensions import RelationshipDimensions
from app.domain.relationship.relationship_stage import RelationshipStage
from app.domain.relationship.relationship_state import RelationshipState
from app.domain.relationship.relationship_anchor import RelationshipAnchorType

from app.services.relationship.relationship_event_detector import RelationshipEventDetector
from app.services.relationship.relationship_change_calculator import RelationshipChangeCalculator
from app.services.relationship.relationship_stage_resolver import RelationshipStageResolver
from app.services.relationship.relationship_anchor_service import RelationshipAnchorService
from app.services.relationship.relationship_context_compiler import RelationshipContextCompiler

logger = logging.getLogger(__name__)

class RelationshipEngine:
    """
    Core Social Bond Engine orchestrating multi-dimensional relationship states,
    events, anchors, and ContextBuilder integration.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.anchor_service = RelationshipAnchorService(db)

    async def get_or_create_state(
        self,
        user_id: str = "default_user",
        companion_id: str = "default_companion"
    ) -> RelationshipState:
        stmt = select(RelationshipStateModel).where(
            RelationshipStateModel.companion_id == companion_id
        )
        res = await self.db.execute(stmt)
        model = res.scalars().first()

        if not model:
            model = RelationshipStateModel(
                companion_id=companion_id,
                user_id=user_id,
                stage="stranger",
                familiarity=0.1,
                trust=0.1,
                affection=0.1,
                intimacy=0.05,
                respect=0.3,
                comfort=0.1,
                attachment=0.05,
                recent_presence=1.0,
                total_conversations=0,
                last_interacted_at=datetime.utcnow()
            )
            self.db.add(model)
            await self.db.commit()
            await self.db.refresh(model)

            # Record First Meeting Anchor
            char_name = "지니"
            cid_lower = companion_id.lower()
            if "mani" in cid_lower or "마니" in companion_id:
                char_name = "마니"
            elif "hana" in cid_lower or "하나" in companion_id:
                char_name = "하나"

            await self.anchor_service.create_anchor(
                user_id=user_id,
                companion_id=companion_id,
                anchor_type=RelationshipAnchorType.FIRST_MEETING,
                summary=f"처음 만난 날. {char_name}와의 소중한 첫 대화가 시작되었습니다.",
                importance=0.9
            )

        stage_enum = RelationshipStage(model.stage) if model.stage in [s.value for s in RelationshipStage] else RelationshipStage.STRANGER
        dims = RelationshipDimensions(
            familiarity=model.familiarity,
            trust=model.trust,
            affection=model.affection,
            intimacy=model.intimacy,
            respect=model.respect,
            comfort=model.comfort,
            attachment=model.attachment
        )

        return RelationshipState(
            user_id=model.user_id,
            companion_id=model.companion_id,
            stage=stage_enum,
            dimensions=dims,
            recent_presence=getattr(model, "recent_presence", 1.0) or 1.0,
            total_conversations=getattr(model, "total_conversations", 0) or 0,
            last_interaction=getattr(model, "last_interacted_at", getattr(model, "updated_at", None))
        )


    async def process_interaction(
        self,
        user_id: str,
        companion_id: str,
        user_input: str
    ) -> RelationshipState:
        """
        Detects events, calculates bounded deltas, updates DB state, and evaluates stage promotions.
        """
        current_state = await self.get_or_create_state(user_id, companion_id)

        # 1. Detect Events
        events = RelationshipEventDetector.detect_events(
            user_input=user_input,
            total_conversations=current_state.total_conversations,
            last_interacted_at=current_state.last_interaction
        )


        # 2. Calculate Bounded Deltas (Rate Limit <= 0.03)
        deltas = RelationshipChangeCalculator.calculate_deltas(
            events=events,
            current_dimensions=current_state.dimensions
        )

        # 3. Apply Deltas to DB model
        stmt = select(RelationshipStateModel).where(
            RelationshipStateModel.companion_id == companion_id
        )
        res = await self.db.execute(stmt)
        model = res.scalars().first()
        if not model:
            return current_state

        new_f = max(0.0, min(1.0, model.familiarity + deltas.get("familiarity", 0.0)))
        new_t = max(0.0, min(1.0, model.trust + deltas.get("trust", 0.0)))
        new_a = max(0.0, min(1.0, model.affection + deltas.get("affection", 0.0)))
        new_i = max(0.0, min(1.0, model.intimacy + deltas.get("intimacy", 0.0)))
        new_r = max(0.0, min(1.0, model.respect + deltas.get("respect", 0.0)))
        new_c = max(0.0, min(1.0, model.comfort + deltas.get("comfort", 0.0)))
        new_att = max(0.0, min(1.0, model.attachment + deltas.get("attachment", 0.0)))

        model.familiarity = round(new_f, 4)
        model.trust = round(new_t, 4)
        model.affection = round(new_a, 4)
        model.intimacy = round(new_i, 4)
        model.respect = round(new_r, 4)
        model.comfort = round(new_c, 4)
        model.attachment = round(new_att, 4)
        model.total_conversations += 1
        model.last_interacted_at = datetime.utcnow()
        model.recent_presence = 1.0

        # 4. Resolve Stage
        updated_dims = RelationshipDimensions(
            familiarity=model.familiarity,
            trust=model.trust,
            affection=model.affection,
            intimacy=model.intimacy,
            respect=model.respect,
            comfort=model.comfort,
            attachment=model.attachment
        )
        new_stage = RelationshipStageResolver.resolve_stage(updated_dims, model.total_conversations)
        old_stage = model.stage

        if new_stage.value != old_stage:
            model.stage = new_stage.value
            # Record Milestone Anchor
            await self.anchor_service.create_anchor(
                user_id=user_id,
                companion_id=companion_id,
                anchor_type=RelationshipAnchorType.STAGE_UPGRADE,
                summary=f"관계가 '{new_stage.value.upper()}' 단계로 성숙해졌습니다.",
                importance=0.85
            )

        # 5. Persist Events
        for ev in events:
            ev_model = RelationshipEventModel(
                companion_id=companion_id,
                signal_type=ev.value,
                dimension_changed=", ".join(deltas.keys()),
                delta_applied=str(deltas),
                reason=f"Event {ev.value} triggered by user interaction"
            )
            self.db.add(ev_model)

        await self.db.commit()
        await self.db.refresh(model)

        return RelationshipState(
            user_id=model.user_id,
            companion_id=model.companion_id,
            stage=new_stage,
            dimensions=updated_dims,
            recent_presence=getattr(model, "recent_presence", 1.0) or 1.0,
            total_conversations=getattr(model, "total_conversations", 0) or 0,
            last_interaction=getattr(model, "last_interacted_at", getattr(model, "updated_at", None))
        )

