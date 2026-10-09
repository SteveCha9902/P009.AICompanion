from app.services.personality.models.personality_state import AttachmentStyleState
from app.domain.relationship.relationship_stage import RelationshipStage

class AttachmentEngine:
    """
    Computes proactive initiative and conversational closeness based on relational bond.
    """

    @staticmethod
    def resolve_attachment(
        base_attachment: AttachmentStyleState,
        stage: RelationshipStage
    ) -> AttachmentStyleState:
        init = base_attachment.initiative
        close = base_attachment.closeness
        indep = base_attachment.independence

        if stage == RelationshipStage.STRANGER:
            init = 0.3
            close = 0.1
        elif stage == RelationshipStage.ACQUAINTANCE:
            init = 0.45
            close = 0.35
        elif stage == RelationshipStage.FRIEND:
            init = max(0.60, init)
            close = max(0.65, close)
        elif stage in [RelationshipStage.CLOSE_FRIEND, RelationshipStage.TRUSTED_COMPANION]:
            init = max(0.80, init)
            close = max(0.85, close)

        return AttachmentStyleState(
            initiative=round(max(0.0, min(1.0, init)), 2),
            closeness=round(max(0.0, min(1.0, close)), 2),
            independence=round(max(0.0, min(1.0, indep)), 2)
        )
