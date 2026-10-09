# [SB-15 Audit 16] Mobile Production Configuration & Token Lifecycle

- **작성자**: 🏃 정대리 (QA Lead) & 🌸 진달래 (Presentation Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. Mobile Production Configuration

- **API Base URL**: `https://api.companion.p009.ai` (개발용 localhost 하드코딩 100% 제거).
- **Secure Token Storage**: `Expo SecureStore` / `EncryptedSharedPreferences`를 사용한 JWT 토큰 보관.
- **Auto Refresh & Interceptor**: 401 수신 시 Refresh Token으로 자동 갱신 후 원래 요청 재시도.
