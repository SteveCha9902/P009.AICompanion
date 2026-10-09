# [SB-15 Audit 5] Database Production & pgvector Optimization

- **작성자**: 🐍 미나리 (Backend Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. PostgreSQL Connection Pool & pgvector Indexing

- **Connection Pool**: `pool_size=20`, `max_overflow=10`, `pool_timeout=30`, `pool_recycle=1800`.
- **pgvector Indexing**:
  ```sql
  CREATE INDEX IF NOT EXISTS idx_memories_embedding_hnsw 
  ON memories USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
  ```
- **Tenant Partitioning**:
  - 모든 쿼리는 반드시 `WHERE user_id = :authenticated_user_id`를 강제하여 타 사용자 데이터 스캔 원천 차단.
