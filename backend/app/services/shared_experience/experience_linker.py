from typing import List, Dict, Any
from app.domain.memory.life_event import LifeEvent

class ExperienceLinker:
    """
    Links related Life Events into a connected episodic narrative chain.
    (e.g., Project Idea -> Difficulty/Struggle -> Breakthrough/Success)
    """

    @staticmethod
    def link_events(events: List[LifeEvent]) -> List[Dict[str, Any]]:
        if not events:
            return []

        # Sort by occurrence date
        sorted_events = sorted(events, key=lambda e: e.occurred_at)

        # Group by thematic category (e.g. PROJECT_MILESTONE, DIFFICULT_PERIOD)
        chains: Dict[str, List[LifeEvent]] = {}
        for ev in sorted_events:
            key = ev.category.value
            if key not in chains:
                chains[key] = []
            chains[key].append(ev)

        narrative_chains = []
        for cat, ev_list in chains.items():
            chain_titles = [e.title for e in ev_list]
            narrative_chains.append({
                "theme": cat,
                "event_count": len(ev_list),
                "progression": " ➔ ".join(chain_titles),
                "events": ev_list
            })

        return narrative_chains
