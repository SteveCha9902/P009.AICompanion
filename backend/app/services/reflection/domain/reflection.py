from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class ReflectionTrigger(str, Enum):
    CONVERSATION_END = "CONVERSATION_END"
    SIGNIFICANT_EMOTION = "SIGNIFICANT_EMOTION"
    IMPORTANT_MEMORY = "IMPORTANT_MEMORY"
    RELATIONSHIP_CHANGE = "RELATIONSHIP_CHANGE"
    DAILY_SUMMARY = "DAILY_SUMMARY"
    MANUAL = "MANUAL"

class ReflectionPriority(str, Enum):
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"

class ReflectionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"

class ReflectionRecord(BaseModel):
    id: str
    companion_id: str
    conversation_id: str
    interaction_id: Optional[str] = None
    trigger_type: ReflectionTrigger
    priority: ReflectionPriority = ReflectionPriority.NORMAL
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    reflection_summary: str = ""
    emotional_pattern: Dict[str, Any] = Field(default_factory=dict)
    relationship_insight: Dict[str, Any] = Field(default_factory=dict)
    behavioral_hints: List[str] = Field(default_factory=list)
    status: ReflectionStatus = ReflectionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
