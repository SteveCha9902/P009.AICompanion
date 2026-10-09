# P009.AICompanion - Sprint 30 Cost Simulation & Analysis Report

---

## 1. 1인 일일 사용 시나리오 (Daily User Persona)
- **Text 대화**: 30회 (평균 250 Input Tokens / 120 Output Tokens ➔ `gpt-4o-mini`)
- **Voice 대화**: 10회 (Whisper STT ~15초 / OpenAI TTS ~120자)
- **Vision 관찰**: 10회 (4초 스로틀 1회 관찰 ➔ `gpt-4o-mini Vision`)
- **Memory Embedding**: 5회 (`text-embedding-3-small`)

---

## 2. 단위 비용 및 사용자 규모별 시뮬레이션 (Cost Projections)

| 모달리티 / 모델 | 1인 일일 비용 (USD) | 1인 월간 비용 (30일) |
| :--- | :---: | :---: |
| **LLM (gpt-4o-mini)** | $0.0028 | $0.084 |
| **STT (Whisper Audio)** | $0.0015 | $0.045 |
| **TTS (OpenAI Audio)** | $0.0036 | $0.108 |
| **Vision (Multimodal)**| $0.0042 | $0.126 |
| **Embedding & Vector** | $0.0001 | $0.003 |
| **총계 (Total Per User)**| **$0.0122 / 일** | **$0.366 / 월 (~490원)** |

---

## 3. 사용자 규모별 월간 비용 추정 (Scalability Matrix)

- **100 Active Users**: **$36.60 / 월**
- **1,000 Active Users**: **$366.00 / 월**
- **10,000 Active Users**: **$3,660.00 / 월**

> **결론**: Vision 4초 스로틀 샘플링 및 중복 요청 방지(Idempotency Guard)를 통해 1인당 월 500원 미만의 극도로 효율적인 프로덕션 운영 비용 구조 달성.
