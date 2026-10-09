# [SB-13 Audit 3] Memory & RAG Boundary Audit

- **작성자**: 🐍 미나리 (Backend Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-13 Controlled Shared Experience & Character-to-Character Information Sharing

---

## 1. Zero Direct Cross-Character Memory Retrieval

```text
Mani Retrieval Path:
   Mani Private Memory (companion_id='c_mani')  [ALLOWED]
   +
   Shared Experience (user_id='u1', target='c_mani', is_revoked=False) [ALLOWED]
   -
   Genie Private Memory (companion_id='genie_pk') [STRICTLY FORBIDDEN / BLOCKED]
```

- **RAG 메타데이터 분리**:
  - `memory_type: shared_experience`와 `memory_type: private_memory`가 철저히 분리되어 색인/검색됨.
