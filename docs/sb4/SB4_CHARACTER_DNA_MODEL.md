# [SB-4 Architecture 2] Character DNA Specification & Domain Model

- **작성자**: 🐟 코다리 (Lead System Architect) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-4 Character Creation Engine & Personality DNA Factory

---

## 1. CharacterDNA 도메인 모델 정의

`CharacterDNA`는 캐릭터의 불변(Immutable) 성격 및 정체성의 근본 구조를 정의합니다.

```python
@dataclass(frozen=True)
class CharacterDNA:
    """
    Immutable Core DNA representing fundamental character nature.
    Decoupled from dynamic mutable state (emotion, current relationship, etc.).
    """
    identity: CharacterIdentity
    personality: PersonalityProfile
    values: CharacterValues
    speech_style: str
    avatar_preset: str
    voice_id: str
    emotion_baseline: Dict[str, float]
    relationship_defaults: Dict[str, Any]
```

---

## 2. DNA vs Dynamic State 분리

| 구분 | 성격 | 구성 요소 | 영속화 주기 |
| :--- | :--- | :--- | :--- |
| **Character DNA** | 불변 (Immutable) | Identity, Personality Traits, Core Values, Speech Style, Voice/Avatar ID | 생성 시 1회 고정 |
| **Dynamic State** | 가변 (Mutable) | EmotionState (Valence/Arousal), RelationshipState (Closeness), Growth XP | 대화 중 실시간 갱신 |
