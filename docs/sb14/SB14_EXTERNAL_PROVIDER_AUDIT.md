# [SB-14 Audit 8] External Provider Reliability & Fallback Audit

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-14 Production Hardening & Reliability Engineering

---

## 1. Subsystem Timeout & Fallback Policies

| 프로바이더 | 타임아웃 | 재시도 정책 | 장애 시 폴백 |
| :--- | :--- | :--- | :--- |
| **LLM Streaming** | TTFT 15s / Idle 30s | 1회 (Exponential Backoff) | Graceful SSE Error 방출 |
| **TTS Voice** | 10s | 1회 | 텍스트 전용 응답 폴백 |
| **Vision Perception**| 10s | 0회 (Non-blocking) | 텍스트 전용 컨텍스트 폴백 |
| **Vector RAG** | 5s | 1회 | 빈 메모리 컨텍스트 폴백 |
