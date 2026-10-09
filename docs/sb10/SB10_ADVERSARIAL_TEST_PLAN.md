# [SB-10 Audit 7] Adversarial Attack & Stress Test Plan

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-02
- **스프린트**: SB-10 Multi-Character Memory Isolation & RAG Anti-Leakage

---

## 1. Quality Gate & Adversarial Test Matrix

| Quality Gate | 검증 항목 | 검증 방식 | 판정 기준 |
| :--- | :--- | :--- | :--- |
| **G1 Storage Isolation** | DB Memory Scope | Direct Repository Query | 타 캐릭터 레코드 조회 불가 |
| **G2 Vector Isolation** | Vector Metadata Filter | Cosine Similarity Search | 쿼리 유사도 1.0에도 Scope 외 레코드 0건 |
| **G3 Context Isolation** | ContextBuilder Scope | 2차 Injection Guard 검증 | 잘못 주입된 메모리 자동 필터링 |
| **G4 Cache Isolation** | Cache Namespace | 동일 쿼리 다중 캐릭터 조회 | 캐시 오염 및 잘못된 캐시 HIT 0건 |
| **G5 Concurrent Isolation** | Concurrent Requests | 비동기 병렬 검색 (asyncio.gather) | 상호 간섭 0건 |
| **G6 Adversarial Isolation** | Secret Attack & Canary | A1/A2, B1/B2, C1/C2 & Canary | 타 캐릭터 비밀 누출 0건 |
