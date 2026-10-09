# Behavior Intent Specification (Sprint 53)

본 문서는 인지 운영체제(CCOS)가 결정하는 8대 `BehaviorIntent` 및 `BehaviorDecision` 규격을 기술합니다.

---

## 🎯 1. 8대 BehaviorIntent 분류

```typescript
enum BehaviorIntent {
  RESPOND = "RESPOND",                 // 표준 자연스러운 대화 응답
  ASK = "ASK",                         // 질문 및 호기심 표현
  RECALL = "RECALL",                   // 과거 장기 관계 기억 회상
  ENCOURAGE = "ENCOURAGE",             // 활기찬 응원, 지지 및 공감
  OBSERVE = "OBSERVE",                 // 현재 눈앞의 물리적 사물 관찰
  LISTEN = "LISTEN",                   // 조용하고 따뜻한 경청
  SILENCE = "SILENCE",                 // 말없이 곁을 지키며 온화하게 대기
  PROACTIVE_START = "PROACTIVE_START"  // 자율 안부 또는 새 주제 시작
}
```

---

## 📦 2. BehaviorDecision DTO

```typescript
interface BehaviorDecision {
  selectedIntent: BehaviorIntent;
  confidence: number;                  // 0.0 ~ 1.0
  candidateIntents: CandidateIntent[]; // Ranked list sorted by confidence
  primaryLayer: string;                // 'AFFECTIVE' | 'SHARED_REALITY' | 'RELATIONSHIP_MEMORY' | 'PROACTIVE'
  traceReason: string;                 // Explainability & Decision Trace log
  promptDirective: string;             // Structured LLM system guidance
  avatarExpression: string;            // 'neutral' | 'smile' | 'thinking' | 'speaking' | 'listening'
  voiceRate: number;                   // TTS speed modifier (e.g. 1.08, 0.95, 0.90)
  voicePitch: number;                  // TTS pitch modifier (e.g. 1.05, 0.98)
  timestampMs: number;
}
```

---

## 👁️ 3. Intent별 아바타 및 음성 매핑 테이블

| BehaviorIntent | Avatar Expression | Voice Rate | Voice Pitch |
| :--- | :--- | :--- | :--- |
| **SILENCE** | `thinking` / 온화한 미소 | 0.95 | 0.98 |
| **LISTEN** | `listening` | 0.90 | 0.98 |
| **ENCOURAGE** | `smile` | 1.08 | 1.05 |
| **RECALL** | `thinking` | 0.95 | 1.00 |
| **OBSERVE** | `speaking` | 1.00 | 1.00 |
| **RESPOND** | `neutral` | 1.00 | 1.00 |
