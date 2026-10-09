# Personality Consistency Architecture (Sprint 54)

본 문서는 Sprint 54에서 구축된 **Personality Consistency Engine**의 전체 시스템 아키텍처, `CharacterDNA` 필터, 기분(Mood)과 성격(Personality)의 분리 계층 및 Cross-Modal(LLM/Voice/Avatar) 동기화 파이프라인을 정의합니다.

---

## 🏛️ 1. 전체 아키텍처 구조

```text
[Companion Cognitive OS (CCOS) BehaviorDecision]
                        │
                        ▼
            [PersonalityDriftMonitor]
        (Monitors 50-turn moving average, clamps drift within +/-0.20)
                        │
                        ▼
               [PersonalityFilter]
      ├─ Invariant Anchor: CharacterDNA (Warmth, Empathy, Curiosity, Humor)
      └─ Transient Dynamic: MoodState (Affective Tone Synergy)
                        │
                        ▼
        [CrossModalPersonalityManifest]
                        │
      ┌─────────────────┼─────────────────┐
      ▼                 ▼                 ▼
[LLM Tone Charter] [Voice Smile/Pitch] [Avatar Smile/Tilt]
```

---

## 🧬 2. 성격(Personality)과 기분(Mood)의 명확한 분리 계층

| 구분 | 성격 (CharacterDNA) | 기분 (MoodState) | 상호작용 시너지 (Synergy) |
| :--- | :--- | :--- | :--- |
| **속성** | **불변의 정체성 (Invariant Anchor)** | **일시적 정서 (Transient Dynamic)** | 성격을 바탕으로 기분에 맞춤 튜닝 |
| **예시 A** | `Warmth=0.92, Empathy=0.95` | `HIGH_ENERGY` (기분 좋음) | **밝고 활기차며 애정 어린 응원** |
| **예시 B** | `Warmth=0.92, Empathy=0.95` | `CALM` (차분함) | **조용하고 깊이 안도감을 주는 쉼터** |
| **예시 C** | `Warmth=0.92, Empathy=0.95` | `SAD_EMPATHY` (슬픔/지침) | **다정하고 온화한 경청과 위로** |

---

## 🎯 3. 핵심 설계 원칙

1. **Continuous 7-Axis CharacterDNA**:
   - 고정된 프리셋 enum 대신 연속형 수치 벡터(`warmth`, `humor`, `curiosity`, `empathy`, `playfulness`, `formality`, `optimism`)로 정밀 정의하여, Sprint 55 (Character Growth)와 유기적 연결.
2. **Personality Drift Prevention**:
   - 최근 50턴의 이동평균을 모니터링하여 성격 지표가 $\pm 0.20$ 이상 변질/왜곡되지 않도록 기준 DNA로 복원.
3. **Cross-Modal Synchronization (3자 일치)**:
   - LLM 텍스트 톤 지침, Voice의 Smile Voice 강도 및 호흡 템포, Avatar의 미소 가중치(`smile_weight_boost`)와 고개 기울임 빈도(`head_tilt_frequency`)가 동일한 CharacterDNA를 동시에 표출.
4. **Tone & Manner Charter Enforcement**:
   - 비꼬기, 냉소적 빈정거림, 거친 말투 100% 금지 및 정중하고 다정한 인격 헌장 준수.
