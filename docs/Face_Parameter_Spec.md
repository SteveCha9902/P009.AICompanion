# Face Parameter Specification (Face_Parameter_Spec.md)

본 문서는 **P009.AICompanion Sprint 41**에서 구축된 실시간 얼굴 엔진(Real-Time Face Engine)의 `FaceParameters` DTO 표준 규격을 정의합니다.

---

## 1. DTO 설계 원칙 (Renderer Independence)

1. **Strict Decoupling (엄격한 분리)**:
   - 렌더러는 `EmotionVector`, `MBTI`, `Memory` 등의 인지적 상태를 직접 참조하지 않습니다.
   - 오직 본 문서에 정의된 `FaceParameters` 수치만을 입력받아 렌더링합니다.
2. **Normalized Numerical Range**:
   - 모든 가중치/강도는 `0.0 ~ 1.0` (또는 `-1.0 ~ 1.0`) 정규화 범위를 가집니다.
   - 각도 파라미터는 degree(도) 단위를 사용합니다.

---

## 2. FaceParameters TypeScript / Pydantic 인터페이스

```typescript
export interface FaceParameters {
  // 1. Eye Parameters
  eyeOpenness: number;    // 0.0 (완전 감음) ~ 1.0 (완전 뜸)
  blinkWeight: number;    // 0.0 (평상시) ~ 1.0 (눈 깜빡임 오버레이)
  eyeDirectionX: number;  // -1.0 (좌측 시선) ~ 1.0 (우측 시선)
  eyeDirectionY: number;  // -1.0 (하단 시선) ~ 1.0 (상단 시선)

  // 2. Mouth Parameters
  mouthOpen: number;      // 0.0 (닫힘) ~ 1.0 (최대 개방)
  smileStrength: number;  // 0.0 (무표정) ~ 1.0 (활짝 웃음)

  // 3. Eyebrow Parameters
  browRaise: number;      // 0.0 (평온) ~ 1.0 (올려짐 / 경청 / 놀람)

  // 4. Head Transform Parameters
  headPitch: number;      // -10.0° ~ +10.0° (상하 끄덕임)
  headYaw: number;        // -10.0° ~ +10.0° (좌우 회전)
  headRoll: number;       // -10.0° ~ +10.0° (좌우 갸우뚱 틸트)

  // 5. Emotional Warmth Overlay
  warmth: number;         // 0.0 ~ 1.0 (볼터치 및 온화한 오라 강도)
}
```

---

## 3. 세부 파라미터 규격 표

| 파라미터명 | 타입 | 허용 범위 | 기본값 | 담당 엔진 |
| :--- | :--- | :--- | :--- | :--- |
| `eyeOpenness` | Float | `0.0 ~ 1.0` | `0.9` | Eye Engine |
| `blinkWeight` | Float | `0.0 ~ 1.0` | `0.0` | Eye Engine (Blink Controller) |
| `eyeDirectionX` | Float | `-1.0 ~ 1.0` | `0.0` | Eye Engine (Gaze Controller) |
| `eyeDirectionY` | Float | `-1.0 ~ 1.0` | `0.0` | Eye Engine (Gaze Controller) |
| `mouthOpen` | Float | `0.0 ~ 1.0` | `0.0` | Mouth Engine |
| `smileStrength` | Float | `0.0 ~ 1.0` | `0.3` | Smile Engine |
| `browRaise` | Float | `0.0 ~ 1.0` | `0.0` | Brow Engine |
| `headPitch` | Float | `-10.0 ~ 10.0` | `0.0` | Head Engine |
| `headYaw` | Float | `-10.0 ~ 10.0` | `0.0` | Head Engine |
| `headRoll` | Float | `-10.0 ~ 10.0` | `0.0` | Head Engine |
| `warmth` | Float | `0.0 ~ 1.0` | `0.5` | Aura / Warmth Layer |
