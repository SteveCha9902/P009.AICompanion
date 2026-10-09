# Emotion Adaptation Architecture (Sprint 52)

본 문서는 Sprint 52에서 구축된 **Emotionally Adaptive Companion Engine**의 전체 시스템 아키텍처, 6번째 인지 계층(Emotion Adaptation Layer), 감정 스무딩 및 적응형 음성/행동 조절 데이터 흐름을 정의합니다.

---

## 🏛️ 1. 전체 아키텍처 구조

```text
[User Utterance + Length/Latency] + [Visual Awareness: Emotion & Gaze]
                                    │
                                    ▼
                      [AffectiveStateEstimator]
          (Valence: -1.0~1.0, Energy: 0~1.0, Stress: 0~1.0, Receptiveness: 0~1.0)
                                    │
                                    ▼
                       [AffectiveStateSmoother]
          (5~10s EMA Filter, alpha=0.35: Eliminates Rapid Jitter)
                                    │
                                    ▼
                      [AdaptiveBehaviorPlanner]
          ├─ Confidence-First Guard (Conf < 0.70 ➔ CALM Safe Fallback)
          ├─ Adaptive Silence Guard (Receptiveness < 0.25 ➔ FOCUSED_SILENCE)
          └─ Mode & Voice Modulation Mapping
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         ▼                                                     ▼
[LLM Adaptive Prompt Directive]                      [Adaptive TTS Parameters]
 (ContextBuilder ➔ Tone, Word Choice)                  (Rate: 0.90~1.08, Pitch: 0.98~1.05)
```

---

## 🎭 2. 5대 Adaptive Tone Modes & Voice Modulation

| Mode | 발동 조건 | 톤앤매너 | TTS Rate / Pitch |
| :--- | :--- | :--- | :--- |
| **HIGH_ENERGY** | Valence > 0.35 & Energy > 0.60 | 밝고 활기차며 생동감 넘치는 반응 | **Rate: +8% (1.08) / Pitch: +5% (1.05)** |
| **CALM** | 중립 상태 또는 Confidence < 0.70 | 부드럽고 편안한 동반자적 태도 | **Rate: -5% (0.95) / Pitch: 1.00** |
| **STRESSED** | Stress > 0.50 | 압박감 없는 여유롭고 진정시키는 태도 | **Rate: -5% (0.95) / Pitch: 0.98** |
| **SAD_EMPATHY** | Valence < -0.30 | 따뜻하고 깊은 공감 및 경청 (단정 배제) | **Rate: -10% (0.90) / Pitch: 0.98** |
| **FOCUSED_SILENCE** | Receptiveness < 0.25 | 말없이 온화한 미소로 대기 (능동 억제) | **Rate: -5% (0.95) / Pitch: 0.98** |

---

## 🎯 3. 핵심 설계 원칙

1. **Confidence-First Policy**:
   - 감정 추정 신뢰도가 0.70 미만인 불확실한 상황에서는 섣부른 감정 개입을 하지 않고 안전한 `CALM` 모드를 유지.
2. **No Clinical Inference Policy (임상/정신건강 진단 절대 금지)**:
   - "우울증", "불안장애", "번아웃" 등 의학적/정신건강 상태를 추론하거나 진단하는 표현 100% 금지.
   - 단정적 주장("너 우울하네") 대신 완곡한 배려("조금 피곤해 보이는 것 같기도 해")를 일관되게 적용.
3. **Emotional Drift Smoothing (EMA Filter)**:
   - 5~10초 지수이동평균(EMA, $\alpha=0.35$) 필터를 적용하여 1초 단위 표정 깜빡임으로 인한 말투 요동을 원천 방지.
4. **Adaptive Silence Mode**:
   - 사용자의 대화 수용도(`Receptiveness`)가 0.25 미만일 때 능동 발화를 완전 억제하고 미소로 차분히 대기.
5. **Adaptive Voice Modulation**:
   - 감정 톤에 맞춰 TTS 발화 속도와 피치를 동적으로 변조하여 극적인 사용자 체감 향상.
