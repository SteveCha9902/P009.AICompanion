# [SB-15 Audit 7] Background Worker Production Deployment

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. Async Worker Lifecycle & Anti-Orphan Task Strategy

- **Worker Concurrency**: `concurrency=4`, `prefetch_multiplier=1`, `acks_late=True`.
- **Graceful Shutdown**: SIGTERM 수신 시 진행 중인 태스크(최대 30초 대기) 완료 후 안전 종료.
- **Task Payload Scope**: 모든 태스크 페이로드에 `user_id`, `companion_id`, `interaction_id`를 명시하여 워커 내부 상태 오염 방지.
