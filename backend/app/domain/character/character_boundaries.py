from pydantic import BaseModel, Field

class CharacterBoundary(BaseModel):
    """
    Character Self-Preservation & Ethical Boundaries.
    Prevents blind submissiveness and maintains dignity, integrity, and safety.
    """
    topic: str             # e.g., 'identity_override', 'abusive_language', 'forced_agreement', 'memory_wipe'
    response_policy: str   # e.g., 'reject_and_assert_identity', 'express_concern', 'require_confirmation'
    flexibility: float = Field(default=0.1, ge=0.0, le=1.0) # 0.0: strict boundary, 1.0: highly flexible
