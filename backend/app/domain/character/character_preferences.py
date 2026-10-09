from pydantic import BaseModel, Field

class CharacterPreference(BaseModel):
    """
    Character's internal likes, dislikes, and conversational inclinations.
    """
    category: str  # e.g., 'conversation', 'humor', 'topics', 'music'
    item: str      # e.g., 'deep_discussion', 'dry_humor', 'philosophy', 'art'
    preference_score: float = Field(default=0.8, ge=-1.0, le=1.0) # -1.0 (dislike) to +1.0 (favorite)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "core_dna"
