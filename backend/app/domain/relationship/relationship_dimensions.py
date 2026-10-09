from pydantic import BaseModel, Field

class RelationshipDimensions(BaseModel):
    """
    7-Dimensional Social Bond Model.
    All dimensions are normalized in [0.0, 1.0].
    """
    familiarity: float = Field(default=0.1, ge=0.0, le=1.0) # How well acquainted / time together
    trust: float = Field(default=0.1, ge=0.0, le=1.0)       # Belief in reliability and mutual respect
    affection: float = Field(default=0.1, ge=0.0, le=1.0)   # Warmth and fondness
    intimacy: float = Field(default=0.05, ge=0.0, le=1.0)   # Depth of personal vulnerability and confession
    respect: float = Field(default=0.3, ge=0.0, le=1.0)     # Regard for opinions and boundaries
    comfort: float = Field(default=0.1, ge=0.0, le=1.0)     # Naturalness and ease of dialogue
    attachment: float = Field(default=0.05, ge=0.0, le=1.0) # Emotional bond (strictly safe-bounded)
