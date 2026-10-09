# P009.AICompanion - Release Checklist

---

## 🚀 Pre-Release Verification Items

```text
[x] 1. Backend Production Configuration (.env.production 템플릿 검증)
[x] 2. Mobile Production Configuration (EXPO_PUBLIC_API_URL, EXPO_PUBLIC_ENV)
[x] 3. API Key & Secret Isolation (모바일 번들 및 로그 내 키 노출 0건)
[x] 4. Database Migration & PgVector Base Schemas
[x] 5. Provider Factory Dynamic Switching (mock <-> openai)
[x] 6. SSE Reliability & Sequence Numbering (idempotency, ordering)
[x] 7. Retry & Reconnection Policy (7-State Reducer)
[x] 8. Timeout Policy (TTFT 15s, Stream Idle 30s)
[x] 9. Safe Cancellation (Client Disconnect -> aclose() 자원 해제)
[x] 10. Background Privacy Guard (카메라/마이크/오디오 강제 OFF)
[x] 11. Camera & Microphone Permission Isolation (거부 시에도 텍스트 대화 정상)
[x] 12. Session & Conversation Restore (앱 재실행 후 기억/관계 복구)
[x] 13. Memory Continuity & Scoring (Top-K=5, Fact Memory 주입)
[x] 14. Relationship Continuity (L0 STRANGER ~ L5 TRUSTED 단계 보존)
[x] 15. Avatar State Priority & Speaking Sync (Audio onStart/onEnd 일치)
[x] 16. Voice User Interrupt (발화 중 마이크 터치 시 즉각 정지 및 전이)
[x] 17. Vision Frame Sampling Throttle (4초 스로틀, Privacy Raw Media 미저장)
[x] 18. Failure Isolation Matrix (개별 Provider 장애 시 앱 크래시 0건)
[x] 19. Prompt Injection Security Test (4계층 Trust Boundary 100% 방어)
[x] 20. Performance Benchmark Trace (InteractionTracer 지표 분리 로깅)
[x] 21. Android Release Build Profile (app.json Manifest, eas.json)
[x] 22. Full Backend pytest Suite (60/60 PASSED)
[x] 23. Mobile TypeScript Compilation (0 ERRORS)
[x] 24. Production Documentation & Runbook 완비
```
