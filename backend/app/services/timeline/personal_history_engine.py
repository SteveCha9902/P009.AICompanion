from typing import Optional, List, Tuple
from app.domain.timeline.life_event import LifeTimeline, LifeEvent
from app.services.timeline.timeline_builder import TimelineBuilder
from app.services.timeline.event_linker import EventLinker

class PersonalHistoryEngine:
    """
    Searches life event timeline and reconstructs temporal narrative context.
    Synthesizes gentle, non-dogmatic narrative recall statements.
    """

    @classmethod
    def find_relevant_timeline_narrative(
        cls,
        user_id: str,
        user_utterance: str
    ) -> Optional[Tuple[LifeEvent, str]]:
        timeline = TimelineBuilder.get_or_create_timeline(user_id)
        if not timeline.events:
            return None

        # Simple keyword matching against events
        matched_event = None
        for ev in reversed(timeline.events):
            keywords = ev.title.split()
            if any(k in user_utterance for k in keywords if len(k) >= 2):
                matched_event = ev
                break

        if not matched_event:
            return None

        # Reconstruct narrative chain
        chain = EventLinker.get_event_narrative_chain(timeline, matched_event.event_id)
        narrative_lines = []

        if len(chain) > 1:
            first_event = chain[0]
            latest_event = chain[-1]
            if matched_event.confidence >= 0.80:
                narrative_lines.append(
                    f"Timeline Narrative: Journey started with '{first_event.title}' ({first_event.event_date_str}), "
                    f"progressing through to '{latest_event.title}'."
                )
            else:
                narrative_lines.append(
                    f"Timeline Narrative (Tentative): We gently recalled '{first_event.title}' around ({first_event.event_date_str})."
                )
        else:
            if matched_event.confidence >= 0.80:
                narrative_lines.append(f"Life Event Anchor: '{matched_event.title}' ({matched_event.event_date_str}).")
            else:
                narrative_lines.append(f"Life Event Anchor (Gentle Recall): '{matched_event.title}'.")

        return (matched_event, "\n".join(narrative_lines))
