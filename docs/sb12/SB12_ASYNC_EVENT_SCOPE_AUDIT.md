# [SB-12 Audit 5] Async, Event Bus & Background Task Scope Audit

- **작성자**: 🔐 방대장 (DevOps/Security) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-12 Multi-Character Companion Orchestration & End-to-End Scope Integrity

---

## 1. Async & Event Bus Payload Standards

```text
CompanionEvent(
    event_id=UUID,
    interaction_id=interaction_id,
    user_id=user_id,
    companion_id=canonical_companion_id,
    event_type=EventType.LLM_CANDIDATE_GENERATED,
    payload={...}
)
```

- **백그라운드 태스크 스코프**:
  - `asyncio.create_task`로 실행되는 기억 추출 및 감정 처리 백그라운드 태스크는 생성 시점에 Pinned된 `companion_id`와 `interaction_id`를 명시적으로 인자로 전달받아 수행하며, 워커 내부에서 `get_active_character`를 다시 호출하지 않음.
