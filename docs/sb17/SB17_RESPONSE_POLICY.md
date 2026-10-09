# [SB-17 Doc 7] Response Policy Object & Prompt Injection Schema

- **작성자**: 🐟 코다리 (Lead Architect) & ✍️ Amy (AI Growth & Persona Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-17 Natural Conversation, Dynamic Cadence & Quiet Empathy

---

## 1. ResponsePolicy Schema

```json
{
  "mode": "QUIET_EMPATHY",
  "max_preferred_sentences": 2,
  "question_allowed": false,
  "empathy_priority": "high",
  "explanation_priority": "low",
  "pressure_level": "none",
  "user_cadence_tier": "short"
}
```
