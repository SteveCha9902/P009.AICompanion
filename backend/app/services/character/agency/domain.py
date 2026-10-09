from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AgencyActionType(str, Enum):
    STAY_SILENT = "stay_silent"
    INTERNAL_REFLECTION = "internal_reflection"
    QUIET_PRESENCE = "quiet_presence"
    UI_INITIATIVE = "ui_initiative"
    OUTREACH_CANDIDATE = "outreach_candidate"
    GREETING = "greeting"
    FOLLOW_UP = "follow_up"
    CHECK_IN = "check_in"
    SHARE_MEMORY = "share_memory"
    CELEBRATE = "celebrate"
    OFFER_SUPPORT = "offer_support"

class DeliveryChannel(str, Enum):
    NONE = "none"
    INTERNAL = "internal"
    UI_PRESENCE = "ui_presence"
    PROACTIVE_MESSAGE = "proactive_message"
    NOTIFICATION = "notification"

class DecisionStatus(str, Enum):
    CREATED = "created"
    BLOCKED_BY_POLICY = "blocked_by_policy"
    BLOCKED_BY_BUDGET = "blocked_by_budget"
    BLOCKED_BY_COOLDOWN = "blocked_by_cooldown"
    SCHEDULED = "scheduled"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

class UserInitiativePreference(BaseModel):
    proactive_enabled: bool = True
    notification_enabled: bool = True
    quiet_hours_start: int = 23 # 23:00 (11 PM)
    quiet_hours_end: int = 7    # 07:00 (7 AM)
    max_daily_initiatives: int = 5
    preferred_initiative_level: str = "MEDIUM" # OFF | LOW | MEDIUM | HIGH

class InitiativeDecision(BaseModel):
    """
    Evaluated autonomous action decision by CharacterAgencyEngine.
    """
    should_act: bool = False
    action_type: AgencyActionType = AgencyActionType.STAY_SILENT
    delivery_channel: DeliveryChannel = DeliveryChannel.NONE
    priority_score: float = Field(default=0.0, ge=0.0, le=1.0)
    initiative_strength: float = Field(default=0.0, ge=0.0, le=1.0)
    timing: Optional[datetime] = None
    reason: str = "no_action_needed"
    personality_alignment: float = Field(default=0.8, ge=0.0, le=1.0)
    relationship_alignment: float = Field(default=0.5, ge=0.0, le=1.0)
    budget_cost: float = Field(default=0.0, ge=0.0, le=1.0)
    decision_status: DecisionStatus = DecisionStatus.CREATED
    blocked_reason: Optional[str] = None
