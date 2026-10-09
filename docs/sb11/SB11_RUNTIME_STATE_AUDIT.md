# [SB-11 Audit 6] Runtime State & Scope Pinning Audit

- **작성자**: 🐟 코다리 (Lead Architect) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-11 Multi-Character Dynamic State Isolation & Concurrency Safety

---

## 1. Request Scope Pinning Pattern

```text
Request Arrives (Target: Genie)
       │
Scope Pinning: request_scope = CharacterDynamicStateScope(user_id, 'genie_pk')
       │
LLM / Cognitive Engine Processing (Takes 1.5s)
       │ (User simultaneously switches to Mani in background)
       │
State Persistence: Uses request_scope.companion_id ('genie_pk')
       ➔ Writes to Genie State (NOT Mani!)
```

- **Race Condition 방어**:
  - `write` 시점에 현재 활성 캐릭터를 재조회하지 않고, 요청 진입 시 고정된 `request_scope`를 사용함으로써 Write-after-switch 상태 오염을 원천 방어함.
