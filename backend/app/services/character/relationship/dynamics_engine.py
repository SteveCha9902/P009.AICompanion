from app.services.character.relationship.domain import RelationshipVector

class RelationshipDynamicsEngine:
    """
    Analyzes the qualitative nature and primary dynamic archetype of an 8D Relationship Vector.
    """

    @staticmethod
    def classify_dynamic_archetype(v: RelationshipVector) -> str:
        # A. Playful & High Closeness
        if v.closeness >= 0.60 and v.playfulness >= 0.60:
            return "PLAYFUL_FRIENDSHIP"
        
        # B. Deep Trust & Emotional Safety
        if v.trust >= 0.70 and v.comfort >= 0.70 and v.emotional_safety >= 0.70:
            return "DEEP_CONFIDANT_BOND"

        # C. Respect & Mutual Distance
        if v.respect >= 0.60 and v.closeness < 0.50:
            return "RESPECTFUL_PROFESSIONAL"

        # Default
        return "BALANCED_COMPANIONSHIP"
