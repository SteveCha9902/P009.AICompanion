# Voice Identity & Emotional Speech Architecture (Voice_Architecture.md)

**문서 버전**: v1.0 Standard  
**작성자**: 🐟 코다리 Architect & 🐍 미나리 과장  
**일자**: 2026-08-30

---

## 1. 개요 및 파이프라인 아키텍처

Voice Identity Layer는 단순한 텍스트-음성 변환(TTS)을 넘어, 캐릭터의 정체성(Voice Profile), 순간적인 감정(Continuous Emotion), 사용자와의 관계 수준(Relationship Stage)을 실시간 합성하여 살아있는 인격체의 음성을 생성합니다.

```
                       [Character Brain]
          (Intent, Emotion Vector, Relationship Stage)
                              │
                              ▼
                     ⭐ Speech Planner
                              │
                              ▼
                  ⭐ Voice Identity Engine
           (Voice Profile: Warmth, Energy, Empathy,
            Pitch Offset, Speaking Rate, Base Timbre)
                              │
                              ▼
                 ⭐ Emotional Speech Engine
            (Emotion Modulation: Joy, Concern, etc.)
                              │
                              ▼
                ⭐ Relationship Speech Engine
          (Honorifics, Intimacy, Warm Tone Modifiers)
                              │
                              ▼
                 ⭐ Voice Provider Abstraction
         ┌──────────────────┬──────────────────┐
         │ OpenAI TTS       │ ElevenLabs       │
         │ Azure Speech     │ Cartesia / Local │
         └──────────────────┴──────────────────┘
                              │
                              ▼
                      [Audio Stream / SSE]
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
          [Speaker Output]          [Lip-Sync & Face Engine]
                                    (Viseme A/E/I/O/U, Smiles)
```

---

## 2. 레이어별 단일 책임 (Single Responsibility)

1. **Voice Profile Layer**: 캐릭터의 고유한 음색(Pitch, Base Rate, Warmth, Empathy) 정의.
2. **Emotional Speech Engine**: 기쁨(속도/피치 증가), 슬픔/위로(속도 감속, 차분한 피치), 공감(따뜻한 공명) 등 감정 반영.
3. **Relationship Speech Engine**: Stranger(정중/격식) ➔ Companion(친밀/따뜻함) 어조 변조.
4. **Voice Provider Abstraction**: 벤더 종속성을 제거하고 OpenAI, ElevenLabs, Azure, Cartesia를 교체 가능하도록 추상화.
5. **Speech Sync Layer**: 생성된 음성의 타이밍과 진폭을 Face Engine 립싱크 및 표정에 실시간 동기화.
