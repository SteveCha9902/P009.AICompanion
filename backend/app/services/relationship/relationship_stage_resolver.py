from app.domain.relationship.relationship_dimensions import RelationshipDimensions
from app.domain.relationship.relationship_stage import RelationshipStage

class RelationshipStageResolver:
    """
    Evaluates multi-dimensional bond scores to resolve the comprehensive RelationshipStage.
    Prevents single-score jump and enforces strict multi-criteria thresholds.
    """

    @staticmethod
    def resolve_stage(
        dimensions: RelationshipDimensions,
        total_conversations: int
    ) -> RelationshipStage:
        f = dimensions.familiarity
        t = dimensions.trust
        c = dimensions.comfort
        i = dimensions.intimacy
        r = dimensions.respect

        # 1. TRUSTED_COMPANION (Deep Lifelong Bond)
        if f >= 0.80 and t >= 0.75 and c >= 0.75 and i >= 0.65 and r >= 0.70 and total_conversations >= 30:
            return RelationshipStage.TRUSTED_COMPANION

        # 2. CLOSE_FRIEND (Vulnerable & Warm)
        if f >= 0.65 and t >= 0.60 and c >= 0.55 and i >= 0.45 and total_conversations >= 15:
            return RelationshipStage.CLOSE_FRIEND

        # 3. FRIEND (Comfortable & Mutual)
        if f >= 0.40 and t >= 0.35 and c >= 0.35 and total_conversations >= 5:
            return RelationshipStage.FRIEND

        # 4. ACQUAINTANCE (Recognized)
        if f >= 0.20 or total_conversations >= 2:
            return RelationshipStage.ACQUAINTANCE

        # 5. STRANGER (Default starting point)
        return RelationshipStage.STRANGER
