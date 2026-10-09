# [SB-14 Audit 15] Failure Recovery Matrix & Graceful Degradation Plan

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-14 Production Hardening & Reliability Engineering

---

## 1. Production Failure Matrix

| 컴포넌트 | 장애 유형 | 기대 동작 |
| :--- | :--- | :--- |
| **PostgreSQL DB** | 일시적 연결 실패 | Safe Fail (트랜잭션 롤백 및 에러 반환) |
| **Redis Cache** | 서비스 다운 | Graceful DB Fallback (대화 서비스 계속 동작) |
| **LLM Provider** | 타임아웃 / Rate Limit | 지수 백오프 1회 재시도 후 안내 메시지 반환 |
| **TTS Provider** | 장애 / 타임아웃 | 텍스트 전용 응답 폴백 |
| **Vision Provider** | 서비스 불가 | 텍스트 대화로 Graceful Degradation |
| **Worker Process** | 비정상 종료 | 메시지 큐 재시도 및 멱등성 보호 |
| **Mobile Network** | 접속 끊김 | 클라이언트 재시도 및 중복 방어 |
| **Character Scope** | 권한 불일치 / 보관 | 즉시 403 차단 (Fail Closed) |
| **Duplicate Interaction** | 동일 ID 재전송 | Idempotency Guard에 의해 중복 실행 차단 |
