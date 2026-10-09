# [SB-6 Architecture 4] Personality vs. Presentation Boundary

- **작성자**: 🐟 코다리 (Lead Architect) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-6 Character Presentation Identity & Profile Binding

---

## 1. 개념 분리 원칙

```text
┌──────────────────────────────────────────────────────────┐
│              Character Personality (내면)                │
│  - "캐릭터가 어떤 내적 정체성을 지니고 있는가"            │
│  - Big-5 Trait Vector (Warmth, Empathy, Conscientiousness)│
│  - Core Values, Identity, MBTI Type, Boundary             │
└────────────────────────────┬─────────────────────────────┘
                             │ Read-Only Mapping
                             ▼
┌──────────────────────────────────────────────────────────┐
│              Character Presentation (외면)               │
│  - "그 존재가 외부 세상과 사용자에게 어떻게 발현되는가"  │
│  - Voice Provider, Voice ID, Pitch Offset, Speaking Rate │
│  - Avatar Visual Style, Default Expression, Motion       │
│  - Facial Expression Style, Gesture Palette, Gaze Vector │
└──────────────────────────────────────────────────────────┘
```

- 내면(Personality)의 변화는 `SB-5 CharacterVersion`으로 버저닝되며, 외면(Presentation)의 변경은 독립적인 프레젠테이션 프로필로 관리됩니다.
