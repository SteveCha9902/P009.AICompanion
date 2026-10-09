# Live2D Migration Plan (Live2D_Migration_Plan.md)

본 문서는 **P009.AICompanion** 아바타를 2.5D 레이어드 렌더러에서 **Live2D Cubism 4 SDK 기반의 완전 실시간 인터랙티브 모델**로 전환하기 위한 로드맵 및 어댑터 설계를 정의합니다.

---

## 1. 전환 배경 및 목표

- **목표**: 2.5D 레이어드 합성 단계를 거쳐, 파츠별 자연스러운 메쉬 디포메이션(Mesh Deformation)과 60fps 물리 연산(Physics)을 지원하는 Live2D 모델로 마이그레이션.
- **아키텍처 호환성**: Sprint 39~40에서 구축한 `ExpressionParameters` 및 `AvatarBehaviorPlan`은 Live2D Core 파라미터와 1:1로 직접 매핑되도록 설계되었습니다.

---

## 2. Parameter 1:1 Mapping Table

| P009 Engine Parameter | Live2D Cubism Parameter ID | 설명 |
| :--- | :--- | :--- |
| `eye_openness` / `blink` | `PARAM_EYE_L_OPEN`, `PARAM_EYE_R_OPEN` | 좌/우 눈 개폐 (0.0 ~ 1.0) |
| `smile_strength` | `PARAM_EYE_L_SMILE`, `PARAM_MOUTH_FORM` | 눈웃음 및 입꼬리 미소 형태 |
| `brow_raise` | `PARAM_BROW_L_Y`, `PARAM_BROW_R_Y` | 좌/우 눈썹 상하 위치 (-1.0 ~ 1.0) |
| `mouth_open` | `PARAM_MOUTH_OPEN_Y` | 입 벌림 크기 (0.0 ~ 1.0) |
| `head_pitch` | `PARAM_ANGLE_Y` | 고개 상하 각도 (-30° ~ +30°) |
| `head_yaw` | `PARAM_ANGLE_X` | 고개 좌우 회전 (-30° ~ +30°) |
| `head_roll` | `PARAM_ANGLE_Z` | 고개 좌우 기울기 (-30° ~ +30°) |
| `breathing_scale` | `PARAM_BREATH` | 호흡 펄스 (0.0 ~ 1.0) |

---

## 3. 단계별 마이그레이션 로드맵

1. **Phase 1 (Sprint 40 - 현재 완료)**:
   - 2.5D 레이어드 렌더러 구축 (Base + Eye/Brow/Mouth Viseme + Breathing + Head Pose).
   - Parameter DTO 및 음소 기반 립싱크 파이프라인 확립.
2. **Phase 2 (Sprint 41 - Live2D SDK 연동)**:
   - React Native Live2D 래퍼 (`react-native-live2d` / WebGL Canvas 뷰) 추가.
   - Genie 캐릭터 Cubism `.model3.json` 자산 번들링.
3. **Phase 3 (Sprint 42 - 물리 연산 및 시선 추적 연동)**:
   - 카메라 시선 추적(Gaze Tracking)과 Live2D 헤드 앵글 실시간 바인딩.
   - 머리칼 및 의상 실시간 물리 진동(Physics Simulation) 활성화.

---

## 4. Live2D Adapter Interface Spec
```typescript
export interface ILive2DAdapter {
  loadModel(modelPath: string): Promise<void>;
  setParameter(paramId: string, value: number, weight?: number): void;
  updateExpression(expression: ExpressionParameters): void;
  updateLipSync(mouthOpen: number, viseme: string): void;
  renderFrame(): void;
}
```
