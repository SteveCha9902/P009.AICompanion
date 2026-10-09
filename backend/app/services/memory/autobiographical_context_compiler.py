from typing import List, Optional
from app.domain.memory.story_chapter import StoryChapter
from app.domain.memory.shared_experience import SharedExperience
from app.domain.memory.life_event import LifeEvent

class AutobiographicalContextCompiler:
    """
    Compiles Autobiographical Memory and Shared Experience context for ContextBuilder.
    Strictly preserves Truth Boundaries:
    - If companion actively participated -> 'We experienced/discussed this together'
    - If user private event -> 'The user previously mentioned that...'
    """

    @staticmethod
    def compile(
        chapters: List[StoryChapter],
        shared_experiences: List[SharedExperience],
        recent_life_events: List[LifeEvent]
    ) -> str:
        lines: List[str] = []
        lines.append("[SHARED HISTORY & AUTOBIOGRAPHICAL MEMORY]")

        # 1. Active Story Chapters
        if chapters:
            lines.append("Current Life Chapters:")
            for ch in chapters[:2]:
                lines.append(f"- Chapter {ch.chapter_number}: '{ch.title}' ({ch.summary})")

        # 2. Shared Experiences (Truth-bounded)
        if shared_experiences:
            lines.append("\nShared Experiences (Our Mutual Journey):")
            for exp in shared_experiences[:3]:
                if exp.is_co_experienced:
                    lines.append(f"- Together: {exp.summary}")
                else:
                    lines.append(f"- User's Personal Event (You listened): {exp.summary}")

        # 3. Recent Significant Life Events
        if recent_life_events:
            lines.append("\nRecent Life Milestones:")
            for ev in recent_life_events[:2]:
                lines.append(f"- Milestone [{ev.category.value}]: {ev.summary}")

        # 4. Truth Boundary Instruction
        lines.append("\n[MEMORY TRUTH BOUNDARY]")
        lines.append("1. Only refer to events as 'our shared memory' if you actively participated in discussing or solving them with the user.")
        lines.append("2. Never fabricate false joint experiences that the user never mentioned.")

        return "\n".join(lines)
