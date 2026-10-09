import uuid
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SharePolicy(str, enum.Enum):
    PRIVATE = "private"
    CHARACTER_ONLY = "character_only"
    SHARED = "shared"
    USER_APPROVED = "user_approved"
    SYSTEM_SAFE = "system_safe"


class ShareProposalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class ShareCategory(str, enum.Enum):
    PREFERENCE = "preference"
    PLAN = "plan"
    EVENT = "event"
    FACT = "fact"
    INTEREST = "interest"
    SHARED_ACTIVITY = "shared_activity"
    USER_APPROVED = "user_approved"
    SYSTEM_SAFE = "system_safe"


class SharedExperienceScope(BaseModel):
    """
    Scope identifying a user and the querying companion character.
    """
    user_id: str = Field(..., description="Unique ID of the user")
    current_character_id: str = Field(..., description="Target character requesting shared experiences")


class ShareProposal(BaseModel):
    """
    Candidate proposal to share character-observed information with other companions.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_character_id: str = Field(..., description="Proposing character ID")
    user_id: str = Field(..., description="User ID owner")
    content: str = Field(..., description="The information content proposed for sharing")
    requested_targets: List[str] = Field(default_factory=list, description="Target companion IDs")
    reason: str = Field(default="", description="Reason for sharing")
    category: ShareCategory = Field(default=ShareCategory.FACT)
    status: ShareProposalStatus = Field(default=ShareProposalStatus.PENDING)
    source_interaction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ControlledSharedExperience(BaseModel):
    """
    A policy-approved, independently stored shared experience accessible by designated target companions.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User ID owner")
    source_character_id: Optional[str] = Field(default=None, description="Originating character ID")
    target_character_ids: List[str] = Field(default_factory=list, description="Explicitly allowed character IDs ('*' for all)")
    content: str = Field(..., description="Approved shared content")
    category: ShareCategory = Field(default=ShareCategory.FACT)
    policy: SharePolicy = Field(default=SharePolicy.USER_APPROVED)
    is_revoked: bool = Field(default=False, description="Flag indicating if the user has revoked access")
    source_interaction_id: Optional[str] = None
    source_proposal_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    policy_version: str = "v1.0"

    def is_accessible_by(self, user_id: str, character_id: str) -> bool:
        """Evaluates whether the given character of the user can access this shared experience."""
        if self.user_id != user_id:
            return False
        if self.is_revoked:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        if "*" in self.target_character_ids:
            return True
        return character_id in self.target_character_ids
