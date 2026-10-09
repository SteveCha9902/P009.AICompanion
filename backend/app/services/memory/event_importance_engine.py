from typing import Dict, Any

class EventImportanceEngine:
    """
    Evaluates the life importance of a conversational episode across 4 dimensions:
    - Novelty: New project, breakthrough, career shift, milestone
    - Emotional Intensity: High joy, deep grief, breakthrough, anxiety
    - Personal Significance: Core life goal, identity, decision
    - Relationship Significance: Deep trust, vulnerability, shared mutual milestone
    """

    @staticmethod
    def calculate_importance(
        summary: str,
        emotional_context: Dict[str, Any],
        user_input: str = ""
    ) -> float:
        text = (summary + " " + user_input).lower()
        base_score = 0.3

        # 1. High Milestone / Novelty Keywords (+0.3 ~ +0.5)
        high_milestone_keywords = [
            "프로젝트 완성", "첫 배포", "런칭", "취업", "합격", "결혼", "시작했어",
            "first prototype", "completed project", "started project", "graduated",
            "promoted", "new career", "won award", "milestone"
        ]
        if any(kw in text for kw in high_milestone_keywords):
            base_score += 0.45

        # 2. Medium Significance Keywords (+0.2)
        med_keywords = [
            "고민", "어려움", "결정", "비밀", "속마음", "문제 해결", "발전",
            "struggling", "decision", "milestone", "breakthrough", "working on"
        ]
        if any(kw in text for kw in med_keywords):
            base_score += 0.20

        # 3. Emotional Intensity Modulation
        arousal = emotional_context.get("arousal", 0.5)
        valence = abs(emotional_context.get("valence", 0.0))
        emotional_boost = (arousal * 0.1) + (valence * 0.1)
        base_score += emotional_boost

        # 4. Low significance routine filter
        trivial_keywords = ["밥 먹었어", "날씨", "졸려", "안녕", "lunch", "weather", "hello"]
        if any(kw in text for kw in trivial_keywords) and base_score < 0.6:
            base_score = min(base_score, 0.15)

        return round(max(0.0, min(1.0, base_score)), 3)
