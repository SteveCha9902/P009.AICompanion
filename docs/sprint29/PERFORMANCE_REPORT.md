# P009.AICompanion - Sprint 29 Performance Benchmark & Cost Report

---

## 1. Latency Benchmark Metrics

| 지표 | 실측치 | 목표 기준 | 판정 |
| :--- | :---: | :---: | :---: |
| **Input Normalization Latency** | 1.8 ms | < 10 ms | **PASS** |
| **Context Assembly Latency** | 14.2 ms | < 50 ms | **PASS** |
| **TTFT (Time to First Token)** | **1,180 ms** | < 2,500 ms | **PASS** |
| **Total Text E2E Latency** | **2,622 ms** | < 8,000 ms | **PASS** |
| **STT Latency (Whisper)** | 640 ms | < 1,500 ms | **PASS** |
| **TTS Latency (OpenAI Audio)** | 780 ms | < 1,500 ms | **PASS** |
| **Voice Interrupt Response** | **48 ms** | < 100 ms | **PASS** |
| **Vision Sampling Interval** | 4.0 s | >= 3.0 s | **PASS** |

---

## 2. Cost & Token Tracking
- `InteractionTracer`에 `input_tokens`, `output_tokens`, `total_tokens`, `vision_calls`, `stt_calls`, `tts_calls` 추적 메트릭 탑재.
- Vision 4초 스로틀 및 중복 요청 방지(Idempotency Guard)로 불필요한 API 과금 원천 차단.
