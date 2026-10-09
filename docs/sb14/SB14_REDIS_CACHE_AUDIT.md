# [SB-14 Audit 6] Redis & Cache Hardening Audit

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-14 Production Hardening & Reliability Engineering

---

## 1. Cache Namespacing & Graceful Degradation

```text
p009:emotion:{user_id}:{companion_id}
p009:relationship:{user_id}:{companion_id}
p009:context:{user_id}:{companion_id}
p009:shared_experience:{user_id}:{companion_id}
```

- **Redis 다운 시 Graceful Fallback**:
  - Redis 연결 장애 시 에러를 전파하지 않고 DB Source of Truth로 자동 Fallback하여 대화 서비스가 중단되지 않음.
