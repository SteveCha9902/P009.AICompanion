from typing import List, Optional
from app.domain.timeline.life_event import LifeEvent, LifeTimeline

class EventLinker:
    """
    Builds causal and temporal graphs across life events (e.g. Purchase -> Growth -> Repotting).
    """

    @classmethod
    def link_events(cls, parent_event: LifeEvent, child_event: LifeEvent) -> None:
        child_event.parent_event_id = parent_event.event_id
        if child_event.event_id not in parent_event.child_event_ids:
            parent_event.child_event_ids.append(child_event.event_id)

    @classmethod
    def get_event_narrative_chain(cls, timeline: LifeTimeline, event_id: str) -> List[LifeEvent]:
        """
        Traverses parent and children to reconstruct the full chronological story chain.
        """
        event_map = {e.event_id: e for e in timeline.events}
        if event_id not in event_map:
            return []

        # Find root
        curr = event_map[event_id]
        while curr.parent_event_id and curr.parent_event_id in event_map:
            curr = event_map[curr.parent_event_id]

        # Traverse downstream chain
        chain = [curr]
        queue = list(curr.child_event_ids)
        while queue:
            cid = queue.pop(0)
            if cid in event_map and event_map[cid] not in chain:
                chain.append(event_map[cid])
                queue.extend(event_map[cid].child_event_ids)

        return sorted(chain, key=lambda e: e.timestamp_ms)
