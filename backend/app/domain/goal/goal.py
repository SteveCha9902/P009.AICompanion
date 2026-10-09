from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time
from datetime import datetime, date

class GoalType(str, Enum):
    HEALTH = "HEALTH"
    PROJECT = "PROJECT"
    LEARNING = "LEARNING"
    TRAVEL = "TRAVEL"
    FAMILY = "FAMILY"
    PET = "PET"
    HOBBY = "HOBBY"
    CAREER = "CAREER"
    HOME = "HOME"
    CUSTOM = "CUSTOM"

class GoalStatus(str, Enum):
    IDEA = "IDEA"
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED" # Replaces ABANDONED (No guilt, gentle archiving)

class GoalMilestone(BaseModel):
    milestone_id: str
    title: str
    is_completed: bool = False
    target_date_str: str = "" # "YYYY-MM-DD"
    completed_at_ms: Optional[int] = None

class GoalCandidate(BaseModel):
    candidate_id: str
    user_id: str
    title: str
    goal_type: GoalType = GoalType.CUSTOM
    confidence: float = Field(ge=0.0, le=1.0, default=0.75)
    suggested_confirmation_prompt: str = ""
    created_at_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

class Goal(BaseModel):
    goal_id: str
    user_id: str
    title: str
    goal_type: GoalType
    status: GoalStatus = GoalStatus.ACTIVE
    confidence: float = Field(ge=0.0, le=1.0, default=0.90)       # 추정 신뢰도
    commitment_level: float = Field(ge=0.0, le=1.0, default=0.50) # 실천/몰입 수준
    milestones: List[GoalMilestone] = Field(default_factory=list)
    target_date_str: str = "" # "YYYY-MM-DD"
    created_at_ms: int = Field(default_factory=lambda: int(time.time() * 1000))
    updated_at_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

class DDayInfo(BaseModel):
    title: str
    target_date_str: str
    days_remaining: int
    dday_tag: str # "D-Day", "D-1", "D-7", "D-30", "D+3"
