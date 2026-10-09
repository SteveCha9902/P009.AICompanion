# [SB-14 Audit 5] Concurrency & Race Condition Audit

- **작성자**: 🏃 정대리 (QA Lead) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-14 Production Hardening & Reliability Engineering

---

## 1. Concurrency Matrix & Race Condition Defenses

1. **Same User + Same Character**:
   - `active_interactions` Set 기반의 중복 요청 차단 및 요청별 고유 `interaction_id` 부여.
2. **Same User + Rapid Switching**:
   - `CompanionInteractionContext`의 Pinned Scope 덕분에 전환 전후 요청 간 상태 오염 0건 보장.
3. **Optimistic Locking & Unique Constraints**:
   - `(user_id, companion_id)` 유니크 제약 조건을 통한 중복 생성 원천 차단.
