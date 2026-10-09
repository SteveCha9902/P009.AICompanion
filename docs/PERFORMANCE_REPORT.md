# P009.AICompanion - Production Performance & Benchmark Report

---

## 1. 지연 시간 (Latency Benchmarks)
- **TTFT (Time to First Token)**: ~ 1.2s
- **Total Text E2E Latency**: ~ 2.8s
- **STT Processing Latency**: ~ 650ms (Whisper API)
- **TTS Generation Latency**: ~ 800ms (OpenAI TTS)
- **Voice Interrupt Response**: ~ 50ms (< 100ms)
- **Vision Sampling Interval**: 4.0s (배터리 최적화)

---

## 2. 리소스 소비량 (Resource Consumption)
- **메모리 점유율**: 모바일 앱 ~120MB, 백엔드 ~180MB
- **CPU 점유율 (Idle)**: < 2%
- **CPU 점유율 (Streaming)**: ~ 12%
- **배터리 소모율**: 30분 연속 멀티모달 상호작용 시 ~ 3.5%
