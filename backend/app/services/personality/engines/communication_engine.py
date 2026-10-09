from app.services.personality.models.personality_state import CommunicationStyleState
from app.domain.relationship.relationship_stage import RelationshipStage

class CommunicationEngine:
    """
    Computes real-time communication dynamics based on relationship stage and emotional mood.
    """

    @staticmethod
    def resolve_communication(
        base_style: CommunicationStyleState,
        stage: RelationshipStage,
        is_serious_topic: bool = False
    ) -> CommunicationStyleState:
        formality = base_style.formality
        humor = base_style.humor
        directness = base_style.directness
        expr = base_style.emotional_expression

        # 1. Modulate by Relationship Stage
        if stage == RelationshipStage.STRANGER:
            formality = max(0.80, formality + 0.5)
            humor = min(0.15, humor * 0.2)
        elif stage == RelationshipStage.ACQUAINTANCE:
            formality = max(0.40, formality)
            humor = min(0.40, humor)
        elif stage == RelationshipStage.FRIEND:
            formality = min(0.25, formality)
        elif stage in [RelationshipStage.CLOSE_FRIEND, RelationshipStage.TRUSTED_COMPANION]:
            formality = 0.05
            expr = min(1.0, expr + 0.15)

        # 2. Modulate by Topic Seriousness
        if is_serious_topic:
            humor = 0.05
            directness = max(0.60, directness)

        return CommunicationStyleState(
            formality=round(max(0.0, min(1.0, formality)), 2),
            humor=round(max(0.0, min(1.0, humor)), 2),
            directness=round(max(0.0, min(1.0, directness)), 2),
            emotional_expression=round(max(0.0, min(1.0, expr)), 2)
        )
