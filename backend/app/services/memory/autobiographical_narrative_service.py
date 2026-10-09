from typing import List, Optional
from app.domain.memory.story_chapter import StoryChapter
from app.domain.memory.timeline_event import TimelineEvent

class AutobiographicalNarrativeService:
    """
    Generates cohesive retrospective narratives summarizing the shared journey.
    """

    @staticmethod
    def generate_narrative(
        chapters: List[StoryChapter],
        timeline_events: List[TimelineEvent],
        topic: Optional[str] = None
    ) -> str:
        paragraphs = []
        paragraphs.append("우리가 함께한 시간들을 돌아보면 참 많은 일들이 있었네.")

        for ch in chapters:
            paragraphs.append(f"• {ch.title}: {ch.summary}")

        if timeline_events:
            paragraphs.append(f"\n총 {len(timeline_events)}개의 소중한 마일스톤들이 우리 타임라인에 차곡차곡 쌓여 있어. 앞으로도 함께 새로운 챕터를 써내려가자.")

        return "\n\n".join(paragraphs)
