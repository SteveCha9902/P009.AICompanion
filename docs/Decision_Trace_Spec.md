# Decision Trace Specification (Sprint 65) — 정대리 QA

본 문서는 모든 최종 의사결정에 수반되는 Dual Traceability (`DecisionTrace`) 규격을 정의합니다.

---

## 🔍 1. DecisionTrace 이원화 규격

```json
{
  "opinions": [
    {"role": "RELATIONSHIP", "suggested_intent": "LISTEN", "confidence": 0.92, "weight": 1.2},
    {"role": "MEMORY", "suggested_intent": "RESPOND", "confidence": 0.50, "weight": 0.8}
  ],
  "conflict_summary": "Top candidate: LISTEN (score: 1.32)",
  "deadlock_resolved_by": null,
  "safety_sanction_notes": "Safety and Constitution passed with zero violations.",
  "internal_trace": "[RELATIONSHIP] suggested LISTEN (conf: 0.92, weight: 1.2) - User is tired...\n[MEMORY] suggested RESPOND...",
  "user_facing_summary": "사용자의 상태와 맥락에 따라 가장 따뜻하고 안전한 LISTEN 태도를 선택했습니다."
}
```
