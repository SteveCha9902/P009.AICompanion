from typing import List, Dict, Any

class PatternAnalyzer:
    """
    Analyzes emotional and thematic trends from recent dialogue and emotion history.
    """

    @staticmethod
    def analyze_trend(recent_messages: List[str], current_emotion: Dict[str, Any]) -> Dict[str, Any]:
        text_corp = " ".join(recent_messages).lower()

        stress_signals = ["힘들어", "스트레스", "지쳤어", "피곤", "exhausted", "stressed", "struggling"]
        positive_signals = ["기뻐", "행복", "성공", "좋아", "happy", "excited", "succeeded"]

        stress_count = sum(text_corp.count(kw) for kw in stress_signals)
        pos_count = sum(text_corp.count(kw) for kw in positive_signals)

        trend = "neutral"
        if stress_count > pos_count:
            trend = "negative_stress"
        elif pos_count > stress_count:
            trend = "positive_growth"

        return {
            "trend": trend,
            "confidence": 0.85,
            "stress_signal_count": stress_count,
            "positive_signal_count": pos_count
        }
