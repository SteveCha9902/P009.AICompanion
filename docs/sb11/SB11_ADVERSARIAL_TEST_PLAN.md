# [SB-11 Audit 8] Dynamic State Adversarial Test Plan

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-02
- **스프린트**: SB-11 Multi-Character Dynamic State Isolation & Concurrency Safety

---

## 1. Dynamic State Adversarial Test Matrix

| Test ID | 테스트 시나리오 | 검증 목표 |
| :--- | :--- | :--- |
| **Test 1** | Emotion Isolation | Genie Emotion(JOY) vs Mani Emotion(CALM) 독립 검증 |
| **Test 2** | Relationship Isolation | Genie Trust 상승 시 Mani Trust 불변 검증 |
| **Test 3** | Growth Isolation | Genie 적응 파라미터가 Mani에 미반영 검증 |
| **Test 4** | Agency Scope Isolation | Genie가 계획한 Proactive Action의 타 캐릭터 실행 방지 |
| **Test 5** | Scope Pinning & Stale Request | 처리 중 캐릭터 스위칭 시에도 원 캐릭터 상태 기록 보장 |
| **Test 6** | Parallel Character Concurrency | 100개 병렬 비동기 요청 시 상호 상태 오염 0건 |
| **Test 7** | Fail-Closed Policy | `companion_id` 누락 시 `CharacterScopeRequiredError` |
| **Test 8** | Ownership Isolation | User A + Genie vs User B + Genie 상태 완전 분리 |
| **Test 9** | State Bundle Consistency | Bundle 내 모든 서브엔티티의 `companion_id` 일치성 검증 |
| **Test 10**| Cache Namespace Invalidation | 캐릭터별 캐시 무효화가 타 캐릭터에 영향 없음 검증 |
