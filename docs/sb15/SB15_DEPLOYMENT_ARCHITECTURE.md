# [SB-15 Audit 2] Deployment Architecture & Container Topography

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. Container Separation Topography

1. **`reverse-proxy` (Nginx/Caddy)**: 포트 80/443 처리, TLS 종단, 보안 헤더, 요청 크기 제한(Body 10MB, Audio 50MB).
2. **`api` (FastAPI + Gunicorn)**: 4 Uvicorn Workers, REST API 및 SSE Interaction 처리.
3. **`worker` (Async Celery/Background Worker)**: 비동기 기억 추출, 감정 분석, 긴급 알림 처리.
4. **`postgres` (PostgreSQL 16 + pgvector)**: 주 영속화 스토리지 및 벡터 검색.
5. **`redis` (Redis 7 Alpine)**: 세션/캐시/레이트 리미터 및 큐.
