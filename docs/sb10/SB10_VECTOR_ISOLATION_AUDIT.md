# [SB-10 Audit 3] Vector Isolation & Metadata Filtering Audit

- **작성자**: 🐟 코다리 (Lead Architect) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-01
- **스프린트**: SB-10 Multi-Character Memory Isolation & RAG Anti-Leakage

---

## 1. Vector Search Security Rule

- **Vector Metadata Required Fields**:
  - `user_id: string`
  - `companion_id: string`
  - `memory_id: string`
  - `status: string`
- **Similarity Filter Policy**:
  - 아무리 의미적 유사도(Cosine Similarity)가 1.0에 가까운 문장이더라도 `companion_id`가 일치하지 않으면 Vector Search 결과 집합에 포함되지 않음 (`Zero Candidate Leakage`).
