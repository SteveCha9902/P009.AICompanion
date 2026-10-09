# Real-Time Face Engine Architecture (Face_Engine_Architecture.md)

본 문서는 **P009.AICompanion Sprint 41**의 실시간 얼굴 엔진(Face Engine) 4대 모듈 구조 및 렌더링 파이프라인을 정의합니다.

---

## 1. 4대 독립 엔진 모듈 (Core Engine Modules)

```
                       [FaceParameters Ingestion]
                                    │
       ┌────────────────┬───────────┴────┬────────────────┐
       ▼                ▼                ▼                ▼
  [Eye Engine]    [Mouth Engine]   [Brow Engine]    [Smile Engine]
 (Blink & Gaze)   (4-Tier Open)    (Elevation)     (Curvature/Warm)
       │                │                │                │
       └────────────────┬────────────────┴────────────────┘
                                    ▼
                      [RealtimeFaceRenderer]
            (Reanimated 60fps Native Layered Compositor)
```

### (1) Eye Engine (`EyeEngine.ts`)
- **Blink Controller**: 2.0초 ~ 7.0초 무작위 간격으로 120ms 고속 눈 깜빡임 생성 (`blinkWeight 0 ➔ 1 ➔ 0`).
- **Eye Openness**: 졸림/평온(0.7), 경청/집중(1.0), 생각(0.85) 실시간 조절.
- **Eye Direction (Gaze)**: X(-1.0 ~ 1.0), Y(-1.0 ~ 1.0) 시선 이동으로 사용자 바라보기/생각할 때 시선 분산 구현.

### (2) Mouth Engine (`MouthEngine.ts`)
- `mouthOpen` 4단계 제어:
  - `Closed` (0.0 ~ 0.1)
  - `Small Open` (0.1 ~ 0.35)
  - `Medium Open` (0.35 ~ 0.65)
  - `Wide Open` (0.65 ~ 1.0)
- 발화 시 오디오 진폭에 맞춰 자연스러운 개폐 펄스 합성.

### (3) Brow Engine (`BrowEngine.ts`)
- `browRaise` (0.0 ~ 1.0): 질문 수신 시 0.3 올려짐, 놀람 시 0.8 올려짐을 Spring 애니메이션으로 보간.

### (4) Smile Engine (`SmileEngine.ts`)
- `smileStrength` (0.0 ~ 1.0): 은은한 미소(0.3) ➔ 따뜻한 미소(0.6) ➔ 환한 미소(0.9)로 Ease-In-Out 보간.

---

## 2. 상태 ➔ FaceParameters 실시간 매핑 규칙

1. **`LISTENING` 상태**:
   - `eyeOpenness`: 1.0, `browRaise`: 0.35, `headPitch`: 2.0°, `headRoll`: 2.5° (경청 틸트).
2. **`THINKING` 상태**:
   - `eyeOpenness`: 0.8, `eyeDirectionY`: -0.4 (하단/측면 시선), `headRoll`: -4.0°, `headPitch`: -2.0°.
3. **`PRE_EXPRESSION` 상태**:
   - `smileStrength`: 0.75 (말하기 200ms 전 미소 피어남), `eyeOpenness`: 0.95.
4. **`SPEAKING` 상태**:
   - `mouthOpen`: 0.2~0.7 (오디오 연동 펄스), `smileStrength`: 0.6.
