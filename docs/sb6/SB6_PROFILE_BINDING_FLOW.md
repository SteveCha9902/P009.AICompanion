# [SB-6 Architecture 5] Profile Binding & Runtime Resolution Flow

- **작성자**: 🐍 미나리 (Backend Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-6 Character Presentation Identity & Profile Binding

---

## 1. Character Switching & Presentation Synchronization Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Router as Character Router
    participant Switcher as Switching Runtime
    participant OldPres as Previous Presentation (Genie)
    participant NewPres as New Presentation (Mani)
    participant Resolver as CharacterPresentationResolver

    User->>Router: Switch Character (Genie -> Mani)
    Router->>Switcher: Initiate Switch
    Switcher->>OldPres: Stop Voice TTS & Reset Avatar Animation
    Switcher->>OldPres: Clear Active Presentation Session
    Switcher->>Resolver: Resolve Mani Presentation (user_id, mani_id)
    Resolver-->>Switcher: Return Mani CharacterPresentationContext
    Switcher->>NewPres: Initialize Mani Voice (shimmer) & Avatar (daughter_2d)
    NewPres-->>User: Mani Ready (Expression: happy, Motion: cheerful_bounce)
```

- 이전 캐릭터의 오디오/애니메이션 잔상이 남지 않도록 완벽한 Stop & Reset 후 신규 캐릭터 컨텍스트를 로딩합니다.
