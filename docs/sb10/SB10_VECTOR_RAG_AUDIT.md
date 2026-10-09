# [SB-10 Audit 2] Vector / RAG Retrieval Pipeline Audit

- **작성자**: 🐟 코다리 (Lead Architect) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-10 Multi-Character Memory Isolation & RAG Anti-Leakage

---

## 1. Vector Search SQL & Metadata Filtering

```text
Embedding Generation
        │
        ▼
Vector Similarity Search (pgvector <=> or Cosine Distance)
        │
        ▼
   [ SQL Filter Enforcement ]
   WHERE companion_id = :active_companion_id
   AND status = 'ACTIVE'
        │
        ▼
Candidate Memory Objects (Top K)
        │
        ▼
CharacterMemoryGuard.validate_context_injection() (Secondary Defense)
        │
        ▼
ContextBuilder (Safe Injection)
```

- **누수 방지 검증 결과**:
  1. `MemoryRepository.search_similar`는 반드시 `companion_id` 필터를 강제함.
  2. Fallback 검색 경로에서도 `companion_id` 누락 시 빈 리스트를 반환하여 Fail-Closed 유지.
  3. Context 주입 직전 2차 방어 레이어로 타 캐릭터 메모리 혼입을 0%로 차단.
