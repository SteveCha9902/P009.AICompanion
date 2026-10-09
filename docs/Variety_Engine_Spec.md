# Behavioral Variety Engine Specification (Variety_Engine_Spec.md)

본 문서는 **P009.AICompanion Sprint 45**의 행동 다양성 엔진(Behavioral Variety Engine) 및 모션 쿨다운(Motion Cooldown) 알고리즘을 정의합니다.

---

## 1. 행동 다양성 확보 원칙 (Core Variety Principles)

1. **상태/감정별 다중 후보군 (Multiple Candidates per State)**:
   - 동일한 `LISTENING` 상태라도 4가지 후보 모션 중 최적 모션을 동적 선별합니다.
2. **최근 모션 쿨다운 페널티 (Motion Cooldown Penalty)**:
   - 최근 3회 이내에 사용된 모션은 가중치를 대폭 감소시켜 연속 반복을 엄격히 차단합니다:
     $$P(\text{Motion}_i) = \text{BaseWeight}_i \times (1.0 - 0.4 \times \text{RecentUsageCount}_i)$$
3. **미세 난수 지터 (Randomization Jitter $\pm10\%$)**:
   - 동일 모션이 선택되더라도 각도(`headTilt`), 끄덕임 진폭(`nodIntensity`)에 $\pm10\%$ 미세 편차를 부여하여 기계적 느낌을 완전히 배제합니다.

---

## 2. 모션 선택 파이프라인 (Selection Dataflow)

```
[State, Emotion, Relationship, Context]
                   │
                   ▼
       [Filter Valid Candidates]
                   │
                   ▼
       [Apply Cooldown Penalty]
                   │
                   ▼
     [Weighted Stochastic Selection]
                   │
                   ▼
       [Apply ±10% Jitter Scale]
                   │
                   ▼
           [Realtime Renderer]
```
