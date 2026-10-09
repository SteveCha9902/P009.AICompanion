from typing import Optional, List, Dict, Tuple
import time
from app.domain.identity.identity_state import UserIdentitySnapshot, LifeChapter
from app.services.identity.life_chapter_builder import LifeChapterBuilder

class IdentityContinuityEngine:
    """
    Tracks longitudinal user growth, identity evolution, and provides mature reminiscing guidance.
    Prevents false or unverified narratives.
    """

    _snapshots: Dict[str, UserIdentitySnapshot] = {}

    @classmethod
    def update_identity_snapshot(
        cls,
        user_id: str,
        core_interests: Optional[List[str]] = None,
        life_stage: str = "",
        growth_note: str = ""
    ) -> UserIdentitySnapshot:
        if user_id not in cls._snapshots:
            cls._snapshots[user_id] = UserIdentitySnapshot(user_id=user_id)

        snap = cls._snapshots[user_id]
        if core_interests:
            snap.core_interests = list(set(snap.core_interests + core_interests))
        if life_stage:
            snap.life_stage = life_stage
        if growth_note:
            snap.growth_notes.append(growth_note)
        snap.last_updated_ms = int(time.time() * 1000)
        return snap

    @classmethod
    def get_snapshot(cls, user_id: str) -> UserIdentitySnapshot:
        if user_id not in cls._snapshots:
            cls._snapshots[user_id] = UserIdentitySnapshot(user_id=user_id)
        return cls._snapshots[user_id]

    @classmethod
    def generate_reminiscing_guidance(
        cls,
        user_id: str,
        user_utterance: str
    ) -> Optional[Tuple[str, str, str]]:
        """
        Returns (Intent, ChapterTitle, GuidancePrompt)
        """
        chapters = LifeChapterBuilder.list_chapters(user_id)
        if not chapters:
            return None

        # Find matching chapter
        matched_chapter: Optional[LifeChapter] = None
        for chap in chapters:
            words = chap.title.split()
            if any(w in user_utterance for w in words if len(w) >= 2):
                matched_chapter = chap
                break

        if not matched_chapter:
            return None

        guidance = (
            f"Mature Multi-Year Reminiscing: Reflect upon the ongoing chapter '{matched_chapter.title}' ({matched_chapter.start_date_str}~). "
            f"Recognize the user's growth and time passed warmly (e.g. '처음 이야기를 나누었던 때가 엊그제 같은데, 벌써...'). "
            f"Strictly avoid fabricating events not in the record."
        )

        return ("LIFE_CHAPTER_RECALL", matched_chapter.title, guidance)

    @classmethod
    def clear(cls) -> None:
        cls._snapshots.clear()
