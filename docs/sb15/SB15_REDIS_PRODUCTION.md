# [SB-15 Audit 6] Redis Production & Role Boundaries

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. Redis Role Segmentation

1. **Role 1 (Session & Cache)**: `p009:session:{token}`, `p009:context:{user_id}:{companion_id}` (TTL: 1 hour).
2. **Role 2 (Rate Limiting)**: `p009:ratelimit:{user_id}:{endpoint}` (TTL: 1 minute).
3. **Role 3 (Task Broker)**: 비동기 큐 브로커 (Celery/Redis Streams).
- **영속화 정책**: RDB Snapshot (15분 주기) + AOF (everysec).
