# [SB-11 Audit 5] Agency & Autonomous Decision Isolation Audit

- **작성자**: 🐟 코다리 (Lead Architect) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-02
- **스프린트**: SB-11 Multi-Character Dynamic State Isolation & Concurrency Safety

---

## 1. Agency Action Scope & Anti-Ghost Execution

```text
Genie Plans Proactive Action (Scope: genie_pk)
       │
User Switches to Mani (Active: c_mani)
       │
Background Runner Executes Genie Action
       │
[ Scope Enforcement Check ]
Target Companion ID == 'genie_pk' != Current Active ('c_mani')
       ➔ Delivered to Genie Channel / Safe Background Logging ONLY (No UI Hijack)
```

- **Agency 격리 표준**:
  - `AgencyActionModel`에 `user_id`와 `companion_id`가 필수 기록됨.
  - 실행 엔진은 대상 `companion_id`를 유지하며, 타 캐릭터 대화창에 액션이 노출되는 UI 하이재킹(Ghost Execution)을 원천 차단함.
