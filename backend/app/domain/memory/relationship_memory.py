from enum import Enum
from typing import List, Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
import time
import uuid

class MemoryType(str, Enum):
    PERSON = "PERSON"
    PET = "PET"
    HOBBY = "HOBBY"
    PROJECT = "PROJECT"
    GOAL = "GOAL"
    PREFERENCE = "PREFERENCE"
    PLACE = "PLACE"
    OBJECT = "OBJECT"
    EVENT = "EVENT"

class MemoryImportance(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RelationshipMemory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    companion_id: str = "default_companion"
    memory_type: MemoryType
    summary: str
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    future_relevance: float = Field(default=0.5, ge=0.0, le=1.0)
    relationship_value: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    visual_tags: List[str] = Field(default_factory=list) # e.g. ['PLANT', 'CUP', 'PET']
    is_pinned: bool = False
    created_at_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    last_referenced_at_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    reference_count: int = 0
    expires_at_ms: Optional[int] = None # TTL in epoch ms

    # Category TTL Constants (in days)
    TTL_DAYS_MAP: ClassVar[Dict[MemoryType, Optional[int]]] = {
        MemoryType.PET: None,          # Long term (no expiry)
        MemoryType.PERSON: None,       # Long term (no expiry)
        MemoryType.GOAL: 365,          # 1 year
        MemoryType.PROJECT: 180,       # 180 days
        MemoryType.HOBBY: 180,         # 180 days
        MemoryType.PLACE: 120,         # 120 days
        MemoryType.OBJECT: 60,         # 60 days
        MemoryType.EVENT: 45,          # 45 days
        MemoryType.PREFERENCE: 180,    # 180 days
    }

    @property
    def final_composite_score(self) -> float:
        """3-Axis Evaluation Score"""
        return round(self.importance_score * self.future_relevance * self.relationship_value, 3)

    @property
    def is_expired(self) -> bool:
        if self.is_pinned or self.expires_at_ms is None:
            return False
        return int(time.time() * 1000) > self.expires_at_ms

    @classmethod
    def calculate_default_expiry(cls, memory_type: MemoryType, created_ms: int) -> Optional[int]:
        ttl_days = cls.TTL_DAYS_MAP.get(memory_type)
        if ttl_days is None:
            return None
        return created_ms + (ttl_days * 24 * 60 * 60 * 1000)
