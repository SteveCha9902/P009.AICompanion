from typing import List
from pydantic import BaseModel, Field
from app.services.reflection.domain.reflection import ReflectionTrigger, ReflectionPriority

class ReflectionDecision(BaseModel):
    """
    Evaluated decision by ReflectionPolicy on whether to trigger an autonomous reflection.
    """
    should_reflect: bool
    trigger: ReflectionTrigger
    priority: ReflectionPriority = ReflectionPriority.NORMAL
    reasons: List[str] = Field(default_factory=list)
