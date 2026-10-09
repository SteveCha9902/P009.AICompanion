# [SB-15 Audit 20] Production Operations Runbook

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. Incident Response Runbook

| 상황 (Incident) | 증상 (Symptoms) | 점검 (Check) | 즉각 조치 (Action) |
| :--- | :--- | :--- | :--- |
| **API Down** | HTTP 502 / 504 | `docker logs p009-api` | `docker restart p009-api` |
| **DB Connection Full** | `Too many connections` | `SELECT count(*) FROM pg_stat_activity` | Connection Pool 상향 및 Idle 세션 정리 |
| **Redis Down** | Connection Error | `docker logs p009-redis` | `docker restart p009-redis` (DB Fallback 자동 가동) |
| **High Latency** | Latency > 2s | External AI API 상태 확인 | Fallback 모델 전환 |
