from app.services.personality.models.personality_state import CoreTraits

class TraitEngine:
    """
    Evaluates baseline traits and dynamically modulates warmth, playfulness, curiosity,
    assertiveness, and empathy based on contextual modifiers.
    """

    @staticmethod
    def modulate_traits(
        base_traits: CoreTraits,
        is_user_distressed: bool = False,
        is_user_celebrating: bool = False,
        companion_fatigue: float = 0.0
    ) -> CoreTraits:
        w = base_traits.warmth
        p = base_traits.playfulness
        c = base_traits.curiosity
        a = base_traits.assertiveness
        e = base_traits.empathy

        if is_user_distressed:
            w = min(1.0, w + 0.15)
            e = min(1.0, e + 0.15)
            p = max(0.05, p - 0.50)  # Restrain teasing/playfulness when user struggles
        elif is_user_celebrating:
            w = min(1.0, w + 0.10)
            p = min(1.0, p + 0.20)

        if companion_fatigue > 0.5:
            p = max(0.1, p - (companion_fatigue * 0.3))
            c = max(0.2, c - (companion_fatigue * 0.2))

        return CoreTraits(
            warmth=round(w, 2),
            playfulness=round(p, 2),
            curiosity=round(c, 2),
            assertiveness=round(a, 2),
            empathy=round(e, 2)
        )
