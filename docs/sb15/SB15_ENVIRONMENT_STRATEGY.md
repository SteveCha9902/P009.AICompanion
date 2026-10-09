# [SB-15 Audit 3] Environment Strategy & Config Separation

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. Environment Matrix

| 환경 | DB 스토리지 | Redis | DEBUG | CORS | 로그 레벨 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Development** | SQLite / Local Postgres | Local Redis / Mock | `True` | `*` (Wildcard) | `DEBUG` |
| **Staging** | Staging Postgres + pgvector | Staging Redis | `False` | 허용 도메인 | `INFO` |
| **Production** | Managed Postgres + pgvector | Managed Redis (Cluster) | `False` | 공식 앱/도메인만 | `INFO` (Masked) |
