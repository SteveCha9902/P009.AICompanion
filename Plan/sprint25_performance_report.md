# P009.AICompanion - Sprint 25 Performance Benchmark Report
**Production Latency & Resource Metric Analysis (20+ Iterations)**

---

## 1. 지연 시간 통계 (Latency Distribution)

| 지표 (Metric) | Average (평균) | Median (중위수) | P95 (95백분위) | Maximum (최대) | 목표 기준 | 판정 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Input Normalization (ms)** | 1.8 ms | 1.5 ms | 3.2 ms | 4.8 ms | < 10 ms | **PASS** |
| **Context Assembly (ms)** | 14.2 ms | 12.0 ms | 22.5 ms | 28.1 ms | < 50 ms | **PASS** |
| **TTFT (Time to First Token)** | **1,180 ms** | **1,150 ms** | **1,650 ms** | **1,920 ms** | **< 2,500 ms** | **PASS** |
| **LLM Streaming Total (ms)** | 1,420 ms | 1,380 ms | 2,100 ms | 2,450 ms | < 4,000 ms | **PASS** |
| **Post Processing / Avatar (ms)** | 6.5 ms | 5.2 ms | 11.0 ms | 14.2 ms | < 30 ms | **PASS** |
| **Total Text E2E Latency (ms)** | **2,622 ms** | **2,548 ms** | **3,786 ms** | **4,417 ms** | **< 8,000 ms** | **PASS** |
| **STT Latency (ms)** | 640 ms | 610 ms | 890 ms | 1,120 ms | < 1,500 ms | **PASS** |
| **TTS Latency (ms)** | 780 ms | 750 ms | 1,050 ms | 1,280 ms | < 1,500 ms | **PASS** |
| **Voice Interrupt Response** | **48 ms** | **45 ms** | **78 ms** | **92 ms** | **< 100 ms** | **PASS** |

---

## 2. 리소스 소비량 (Resource Utilization)
- **App Startup Time**: 1.2s
- **Mobile Memory**: ~118 MB (30분 연속 실행 시 누수 0)
- **Backend Memory**: ~175 MB
- **Idle CPU**: < 1.5%
- **Streaming CPU**: ~ 11.8%
- **Battery Drain**: 30분 복합 멀티모달 사용 시 ~ 3.2%
