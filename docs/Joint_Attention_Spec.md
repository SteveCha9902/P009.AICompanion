# Joint Attention Specification (Sprint 49)

본 문서는 공동 주의(Joint Attention) 및 공유 현실 도메인의 핵심 데이터 모델, 앵커 규격 및 상태 전이 인터페이스를 기술합니다.

---

## 📦 1. Data Transfer Objects (DTO)

### `SharedRealityContext`
```typescript
interface SharedRealityContext {
  state: JointAttentionState;
  focusTarget?: SceneObjectType;
  targetLabel: string;
  targetConfidence: number;      // 0.0 ~ 1.0
  anchor: AttentionAnchor;
  candidateTargets: CandidateFocus[]; // Top 3 Scene Objects
  userIntent: string;
  confirmationStatus: UserConfirmationStatus;
  sharedAttention: boolean;
  timestampMs: number;
  focusLockUntilMs: number;
  lastInteractionTimeMs: number;
  isLocked: boolean;             // Computed: Date.now() < focusLockUntilMs
  isTimedOut: boolean;           // Computed: Date.now() - lastInteractionTimeMs > 15000
}
```

### `JointAttentionState`
- `NONE`: 공유 대상 없음.
- `USER_FOCUS`: 사용자가 특정 대상에 관심을 가짐 (신뢰도 0.45~0.74).
- `SHARED_FOCUS`: 사용자와 캐릭터가 동일 대상에 양방향 공동 주의 형성 (신뢰도 $\ge 0.75$).
- `DISCUSSING_TARGET`: 해당 대상에 대해 본격적으로 대화를 주고받는 중.

### `UserConfirmationStatus`
- `UNKNOWN`: 판별되지 않음.
- `CONFIRMED`: 긍정 확인 ("응", "맞아", "어").
- `REJECTED`: 부정 거절 ("아니", "틀렸어", "그거 말고").

### `AttentionAnchor`
- `USER_FACE`: 사용자 얼굴 정면 응시
- `CENTER`: 화면 중앙
- `LOWER_LEFT`: 화면 좌측 하단 (예: 책, 반려동물)
- `LOWER_CENTER`: 화면 중앙 하단 (예: 노트북, 키보드)
- `LOWER_RIGHT`: 화면 우측 하단 (예: 컵, 음료)
- `UPPER_LEFT`: 화면 좌측 상단 (예: 모니터, TV)
- `UPPER_RIGHT`: 화면 우측 상단 (예: 화분, 창문)
