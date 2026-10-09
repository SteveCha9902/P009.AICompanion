# [SB-8 Architecture 1] Character Creation Studio & Factory Architecture

- **작성자**: 🐟 코다리 (Lead System Architect) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-8 Character Creation Studio & Character Factory

---

## 1. Creation Pipeline & Transformation Flow

```mermaid
graph TD
    UserReq[CharacterCreationRequest] --> Validator[CharacterCreationValidator]
    Validator --> Compiler[Personality & DNA Compiler]
    Compiler --> Factory[CharacterFactory]
    
    subgraph Preview Pipeline
        Factory --> PreviewDTO[CharacterPreviewResponse (Non-persisted)]
    end

    subgraph Atomic Persistence Transaction
        Factory --> CompanionEntity[Companion Entity]
        Factory --> ProfileEntity[CharacterProfile Entity]
        Factory --> PersonalityEntity[Personality Entity]
        Factory --> ValuesEntity[Values Entity]
        Factory --> RelSeed[Relationship Anchor Entity]
        Factory --> PresProfile[CharacterPresentationProfile Entity]
        Factory --> VersionSnapshot[CharacterVersion 1 INITIAL]
    end

    VersionSnapshot --> Runtime[CharacterRuntimeContext Ready]
    Runtime --> Memory[Memory Scope (Initialized Empty)]
```

---

## 2. Static DNA vs. Dynamic Runtime State 분리 원칙

| 구분 | 포함 항목 | 불변/가변성 |
| :--- | :--- | :--- |
| **Static Character DNA** | Identity, Personality Trait Vector, Values, Speech Profile, Interests, Behavioral Rules, Voice/Avatar Presentation Profile | 생성 시 Version 1으로 스냅샷화되며 변경 시 SB-5 버전 갱신 |
| **Dynamic Runtime State** | Memory (Empty 시작, Genie 기억 복사 금지), Emotion State (Neutral 초기화), Relationship Anchor (Seed 초기화), Growth Level (Lv.1 시작) | 상호작용 및 대화 경험에 따라 동적 진화 |
