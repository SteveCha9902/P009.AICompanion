# Awareness Context Specification (Sprint 48)

본 문서는 시각 인지 도메인의 핵심 데이터 모델 및 DTO 명세를 기술합니다.

---

## 📦 1. Data Transfer Objects (DTO)

### `AwarenessContext`
```typescript
interface AwarenessContext {
  userState: UserAwarenessState;
  environmentState: EnvironmentAwarenessState;
  focusTarget: VisualFocusTarget;
  confidence: number;            // 0.0 ~ 1.0
  awarenessTimestampMs: number;  // Epoch millisecond
  ageMs: number;                 // Computed: Date.now() - awarenessTimestampMs
  isFresh: boolean;              // Computed: ageMs <= 10000 (10 seconds)
}
```

### `UserAwarenessState`
```typescript
interface UserAwarenessState {
  userPresence: boolean;
  faceDetected: boolean;
  gazeDirection: "toward_camera" | "away" | "screen" | "looking_down";
  attentionLevel: number;        // 0.0 ~ 1.0
  facialEmotion: FacialEmotionType;
  emotionConfidence: number;     // 0.0 ~ 1.0
}
```

### `FacialEmotionType` (8-Tier)
- `SMILING`: 따뜻하고 긍정적인 미소
- `NEUTRAL`: 차분한 기본 상태
- `FOCUSED`: 작업이나 화면에 깊이 몰입한 상태
- `CONFUSED`: 의아해하거나 질문이 생겼을 때의 표정
- `THINKING`: 깊이 고민하거나 생각에 잠긴 상태
- `FATIGUED`: 피로하거나 지쳐 보이는 상태
- `SURPRISED`: 놀람이나 예기치 못한 반응
- `UNKNOWN`: 판별 불가

### `DetectedObject`
```typescript
interface DetectedObject {
  type: SceneObjectType;         // CUP, FOOD, BOOK, LAPTOP, PET, PLANT, TV, WINDOW, PHONE, NOTEBOOK, OTHER
  confidence: number;            // 0.0 ~ 1.0 (>= 0.70 to react)
  label: string;
  bbox?: {
    xMin: number;
    yMin: number;
    xMax: number;
    yMax: number;
  };
}
```

### `VisualFocusTarget`
- `USER_FACE` | `CUP` | `LAPTOP` | `PET` | `BOOK` | `PLANT` | `WINDOW` | `NONE`
