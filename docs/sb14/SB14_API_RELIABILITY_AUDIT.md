# [SB-14 Audit 9] API Contract, Rate Limiting & Error Handling Audit

- **작성자**: 🐍 미나리 (Backend Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-14 Production Hardening & Reliability Engineering

---

## 1. Standard Error Contract & Rate Limiter

- **표준 에러 응답**:
  ```json
  {
    "error": {
      "code": "CHARACTER_NOT_FOUND",
      "message": "요청한 캐릭터를 찾을 수 없습니다.",
      "interaction_id": "int_123"
    }
  }
  ```
- **Rate Limiting**:
  - `RateLimiter`: 사용자/IP/캐릭터 단위 초당 최대 요청 수 제한으로 AI 비용 폭주 방어.
