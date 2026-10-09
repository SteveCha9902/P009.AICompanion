# [SB-14 Audit 7] Retry Safety & Idempotency Audit

- **작성자**: 🏃 정대리 (QA Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-14 Production Hardening & Reliability Engineering

---

## 1. Idempotency Execution Model

```text
Request with interaction_id = 'ABC'
       │
InteractionExecutionRegistry Check:
   - Already RUNNING: Return 409 Conflict / SSE Duplicate Error
   - Already COMPLETED: Return cached result (No duplicate mutation!)
   - New: Register -> Execute -> Mark COMPLETED
```

- **중복 성장 및 상태 전이 방어**:
  - 동일 `interaction_id`가 재전송되어도 감정, 친밀도, 성장 마일스톤이 두 번 계산되지 않음.
