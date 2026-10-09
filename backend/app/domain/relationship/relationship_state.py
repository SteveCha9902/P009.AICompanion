from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time
from datetime import datetime

from app.domain.relationship.relationship_stage import RelationshipStage
from app.domain.relationship.relationship_dimensions import RelationshipDimensions
from app.domain.relationship.relationship_anchor import RelationshipAnchor

class RelationshipMilestone(BaseModel):
    """
    Key relational events formed between user and companion over time.
    """
    milestone_id: str
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    title: str
    importance: float = Field(ge=0.0, le=1.0, default=0.8)
    memory_refs: List[str] = Field(default_factory=list)
    event_date_str: str = ""

class RelationshipVector(BaseModel):
    """
    5-Axis Continuous Relationship Vector (0.0 ~ 1.0).
    Trust and Familiarity are strictly decoupled.
    """
    trust: float = Field(default=0.30, ge=0.0, le=1.0)          # 신뢰도 (일관성, 도움의 질, 약속 이행)
    familiarity: float = Field(default=0.10, ge=0.0, le=1.0)    # 친숙도 (상호작용 빈도, 누적 세션)
    comfort: float = Field(default=0.20, ge=0.0, le=1.0)        # 편안함 (대화의 자연스러움, 침묵의 편안함)
    shared_history_score: float = Field(default=0.10, ge=0.0, le=1.0)
    engagement: float = Field(default=0.50, ge=0.0, le=1.0)     # 상호작용 몰입도

    # Cumulative stats
    total_interaction_turns: int = 0
    total_shared_memories_count: int = 0
    consecutive_days_met: int = 1
    last_interaction_timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

class RelationshipState(BaseModel):
    user_id: str
    companion_id: str = "default_companion"
    stage: RelationshipStage = RelationshipStage.STAGE_1_NEW
    dimensions: RelationshipDimensions = Field(default_factory=RelationshipDimensions)
    anchors: List[RelationshipAnchor] = Field(default_factory=list)
    total_conversations: int = 0
    recent_presence: float = 0.0
    last_interaction: Optional[datetime] = None

    # Sprint 55 Enhanced Vector & Milestones
    vector: RelationshipVector = Field(default_factory=RelationshipVector)
    milestones: List[RelationshipMilestone] = Field(default_factory=list)
    last_daily_growth_timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    today_accumulated_growth: float = 0.0 # Daily growth cap tracker

    def compute_stage(self) -> RelationshipStage:
        # Composite intimacy score
        composite = (self.vector.trust * 0.40) + (self.vector.familiarity * 0.30) + (self.vector.comfort * 0.30)
        if composite >= 0.80 and len(self.milestones) >= 3:
            return RelationshipStage.STAGE_4_DEEP
        elif composite >= 0.55:
            return RelationshipStage.STAGE_3_TRUSTED
        elif composite >= 0.30:
            return RelationshipStage.STAGE_2_FAMILIAR
        return RelationshipStage.STAGE_1_NEW
