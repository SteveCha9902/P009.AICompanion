# [SB-15 Audit 15] Production Rollback Procedure

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. Zero-Downtime Rollback

- **Application Rollback**: Nginx 업스트림 포인터를 이전 버전 컨테이너로 원복 (소요 시간 < 5초).
- **Database Migration Rollback**: `alembic downgrade -1` 또는 마이그레이션 전 백업 복구.
