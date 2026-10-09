# [SB-15 Audit 19] Production Deployment Smoke Test Checklist

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps/Security Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. Production Smoke Test Steps

1. `GET /health` ➔ 200 OK (status: ok)
2. `GET /ready` ➔ 200 OK (database: connected)
3. `POST /api/v1/companion/interactions` ➔ SSE Interaction 완료
4. `GET /api/v1/characters` ➔ 사용자 보유 캐릭터 목록 반환
5. Multi-User 격리 검증 ➔ 100% PASS
