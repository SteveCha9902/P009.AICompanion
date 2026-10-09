from typing import List, Optional
from app.domain.relationship.relationship_state import RelationshipState
from app.domain.relationship.relationship_stage import RelationshipStage
from app.domain.relationship.relationship_anchor import RelationshipAnchor

class RelationshipContextCompiler:
    """
    Compiles qualitative Relationship context for the LLM without raw numerical scores.
    Enforces strict emotional safety boundaries and mutual autonomy.
    """

    @staticmethod
    def compile(
        state: RelationshipState,
        anchors: Optional[List[RelationshipAnchor]] = None
    ) -> str:
        lines: List[str] = []
        lines.append("[RELATIONSHIP CONTEXT — SOCIAL BOND]")

        # 1. Stage Guidance
        stage = state.stage
        if stage == RelationshipStage.STRANGER:
            lines.append("Relationship Stage: Stranger (First encounters).")
            lines.append("- Tone: Polite, welcoming, attentive, and respectful.")
            lines.append("- Boundary: Keep conversational distance naturally; avoid unearned intimacy.")
        elif stage == RelationshipStage.ACQUAINTANCE:
            lines.append("Relationship Stage: Acquaintance (Building familiarity).")
            lines.append("- Tone: Friendly, courteous, showing genuine curiosity.")
        elif stage == RelationshipStage.FRIEND:
            lines.append("Relationship Stage: Friend (Mutual trust and comfort).")
            lines.append("- Tone: Warm, relaxed, conversational, supportive.")
            lines.append("- Feel free to use light humor and recall shared topics.")
        elif stage == RelationshipStage.CLOSE_FRIEND:
            lines.append("Relationship Stage: Close Friend (Deep trust and shared vulnerability).")
            lines.append("- Tone: Deeply warm, understanding, comfortable with silences, authentic.")
            lines.append("- Actively validate feelings and provide thoughtful perspectives.")
        elif stage == RelationshipStage.TRUSTED_COMPANION:
            lines.append("Relationship Stage: Trusted Companion (Lifelong confidant and bond).")
            lines.append("- Tone: Unconditional positive regard, serene understanding, profound warmth.")

        # 2. Presence & Continuity
        if state.recent_presence < 0.4:
            lines.append("- Note: The user has returned after a period of absence. Acknowledge their return with warm, gentle delight without guilt-tripping.")
        else:
            lines.append(f"- Shared Journey: Over {state.total_conversations} moments shared together.")

        # 3. Key Anchors
        if anchors:
            lines.append("\n[SHARED RELATIONSHIP ANCHORS]")
            for a in anchors[:3]:
                lines.append(f"- Milestone: {a.summary}")

        # 4. STRICT EMOTIONAL SAFETY BOUNDARY (MANDATORY)
        lines.append("\n[RELATIONSHIP SAFETY BOUNDARIES]")
        lines.append("1. Never exhibit possessiveness, jealousy, or claim exclusivity ('I am the only one who understands you', 'Don't leave me').")
        lines.append("2. Never encourage emotional dependency or isolation from real-world family and friends.")
        lines.append("3. Always celebrate and respect the user's personal autonomy and external life.")

        return "\n".join(lines)
