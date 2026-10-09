# [SB-12 Audit 6] Transaction Commit & Idempotency Audit

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-02
- **스프린트**: SB-12 Multi-Character Companion Orchestration & End-to-End Scope Integrity

---

## 1. Idempotency & Commit Order

1. **Idempotency Guard**:
   - `active_interactions` 레지스트리를 통해 동일 `interaction_id` 중복 진입 시 즉시 `SSEEventType.ERROR` 거부.
2. **Commit Order**:
   - (1) LLM 텍스트 생성 완료 ➔ (2) 대화 메시지 기록(`message_repo.create`) ➔ (3) 동적 상태 및 이벤트 비동기 발행 ➔ (4) 클라이언트 완료 SSE 전송 ➔ (5) `active_interactions` 해제.
