# Final Embodied Avatar Architecture (Avatar_Architecture_Final.md)

**문서 버전**: v1.0 Final Architecture  
**작성자**: 🐟 코다리 Architect & 🧭 세종이 PM  
**일자**: 2026-08-30

---

## 1. 5-Layer Parameter Composite 아키텍처

```
                       [User Multimodal Input]
                     (Microphone / Vision / Text)
                                 │
                                 ▼
                     [Cognitive Brain Engine]
                (Personality + Memory + Reflection)
                                 │
                                 ▼
                   ⭐ 5-Layer Parameter System
  ┌─────────────────────────────────────────────────────────────┐
  │ Layer 1: FaceParameters       (Eye Open/Blink, Brow, Smile) │
  │ Layer 2: SpeechParameters     (Lip-Sync, Viseme A/E/I/O/U)  │
  │ Layer 3: BehaviorParameters   (Listening Tilt, Nod, Gaze)   │
  │ Layer 4: RelationshipParams   (Familiarity, Trust, Warmth)  │
  │ Layer 5: MotionParameters     (Variety Jitter, 14 Presets)  │
  └─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
              ⭐ RealtimeFaceRenderer (60 FPS Native)
  ┌─────────────────────────────────────────────────────────────┐
  │ • Organic Breathing Loop (4.5s sine curve)                  │
  │ • Random Blink Engine (2~7s Poisson distribution)           │
  │ • EMA Speech Smoothing Filter (α=0.45, No Jitter)           │
  │ • Motion Variety Cooldown (No 3 consecutive repeats)        │
  │ • Relational Warmth Aura Glow                               │
  └─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                   Mobile Screen (iOS / Android)
   "캐릭터가 나를 보고, 듣고, 생각하고, 말하는 살아 숨 쉬는 경험"
```

---

## 2. 렌더러 독립성 원칙 (Renderer Independence Standard)

- **Decoupling**: 모바일 렌더러는 백엔드의 LLM 프롬프트, MBTI, 기억 벡터를 직접 조회하지 않으며, 오직 **정량화된 5대 파라미터 DTO**만을 수신하여 렌더링합니다.
- **Live2D / 3D 호환성**: 모든 DTO 필드는 표준 Live2D Cubism 및 VRM 블렌드셰이프 규격과 1:1로 매핑 가능하도록 정규화되어 향후 Live2D 에셋 도입 시 제로 코드 변경을 보장합니다.
