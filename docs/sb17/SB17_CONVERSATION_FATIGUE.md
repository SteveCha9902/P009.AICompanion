# [SB-17 Doc 6] Conversation Fatigue Tracker & Scoring Model

- **작성자**: 🐍 미나리 (Backend Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-17 Natural Conversation, Dynamic Cadence & Quiet Empathy

---

## 1. Deterministic Fatigue Scoring Formula

$$\text{Fatigue} = 0.3 \times \text{ShortReplyRatio} + 0.3 \times \text{NegativeEmotionWeight} + 0.4 \times \text{TurnDurationDecay}$$

- `Fatigue >= 0.7`: 피로도 높음 ➔ 응답 길이 단축 및 질문 전면 차단.
