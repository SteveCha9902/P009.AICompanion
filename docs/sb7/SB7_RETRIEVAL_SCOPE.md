# [SB-7 Architecture 4] Memory Retrieval Scope & Vector Filter Policy

- **작성자**: 🐍 미나리 (Backend Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-01
- **스프린트**: SB-7 Character Memory Isolation & Independent Experience System

---

## 1. Vector Search Query Filter 강제

모든 pgvector 유사도 검색은 반드시 `companion_id` 필터를 선행 적용합니다:

```sql
SELECT id, content, type, importance,
       (1.0 - (embedding <=> :query_embedding)) AS similarity
FROM memories
WHERE companion_id = :companion_id
  AND status = 'ACTIVE'
  AND (1.0 - (embedding <=> :query_embedding)) >= :threshold
ORDER BY embedding <=> :query_embedding ASC
LIMIT :limit;
```
