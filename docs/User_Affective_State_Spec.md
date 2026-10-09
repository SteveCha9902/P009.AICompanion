# User Affective State Specification (Sprint 52)

본 문서는 실시간 감정 및 정서 상태를 표현하는 DTO, 정량 지표 범위 및 계산 공식을 기술합니다.

---

## 📦 1. UserAffectiveState DTO

```typescript
interface UserAffectiveState {
  emotionalValence: number;   // -1.0 (Very Negative) ~ +1.0 (Very Positive)
  energyLevel: number;        // 0.0 (Lethargic/Exhausted) ~ 1.0 (High Energy)
  stressLevel: number;        // 0.0 (Calm/Relaxed) ~ 1.0 (High Stress/Pressure)
  receptiveness: number;      // 0.0 (Unwilling/Closed) ~ 1.0 (Open/Chatty)
  confidence: number;         // 0.0 ~ 1.0 (Estimation reliability)
  adaptiveMode: AdaptiveToneMode;
  voiceParams: AdaptiveVoiceParameters;
  timestampMs: number;
}

interface AdaptiveVoiceParameters {
  rateModifier: number;       // e.g. 1.08 (+8%), 0.90 (-10%)
  pitchModifier: number;      // e.g. 1.05 (+5%), 0.98 (-2%)
  style: string;              // 'cheerful' | 'calm' | 'soothing' | 'empathetic' | 'whisper'
}
```

---

## 📊 2. 정량 차원별 산출 기준

1. **Emotional Valence (-1.0 ~ +1.0)**:
   - 긍정 어휘("좋아", "신나", "최고") 및 `SMILING` 표정 ➔ +0.40 ~ +0.80
   - 부정 어휘("힘들어", "지쳐", "속상해") ➔ -0.45 ~ -0.90
2. **Energy Level (0.0 ~ 1.0)**:
   - 긴 발화 + 빠른 응답 + 활발한 표정 ➔ 0.70 ~ 1.00
   - 단답형 + `FATIGUED` 표정 ➔ 0.10 ~ 0.30
3. **Stress Level (0.0 ~ 1.0)**:
   - 마감/과제/야근/압박 키워드 + `CONFUSED`/혼란 표정 ➔ 0.60 ~ 1.00
4. **Receptiveness (0.0 ~ 1.0)**:
   - 3자 이하 단답형("ㅇㅇ", "응") 및 `FOCUSED` 집중 표정 ➔ 0.10 ~ 0.35
