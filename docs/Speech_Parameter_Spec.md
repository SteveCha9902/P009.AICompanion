# Speech Parameter Specification (Speech_Parameter_Spec.md)

본 문서는 **P009.AICompanion Sprint 42**의 `SpeechParameters` DTO 표준 규격을 정의합니다.

---

## 1. SpeechParameters TypeScript / Pydantic 인터페이스

```typescript
export interface SpeechParameters {
  isSpeaking: boolean;        // 현재 오디오 음성 출력 중 여부
  mouthOpen: number;          // 0.0 (완전 닫힘) ~ 1.0 (최대 개방)
  viseme: 'closed' | 'viseme_a' | 'viseme_e' | 'viseme_i' | 'viseme_o' | 'viseme_u';
  speechIntensity: number;    // 0.0 (속삭임/조용함) ~ 1.0 (강조/활기참)
  speechProgress: number;     // 0.0 (문장 시작) ~ 1.0 (문장 종료)
}
```

---

## 2. 세부 파라미터 규격 표

| 파라미터명 | 타입 | 허용 범위 | 기본값 | 설명 |
| :--- | :--- | :--- | :--- | :--- |
| `isSpeaking` | Boolean | `true / false` | `false` | TTS 오디오 음성 재생 활성 플래그 |
| `mouthOpen` | Float | `0.0 ~ 1.0` | `0.0` | 오디오 진폭 및 Viseme 연동 입 벌림 크기 |
| `viseme` | Enum / String | `closed`, `viseme_a/e/i/o/u` | `closed` | 실시간 발화 음소의 시각적 형태 |
| `speechIntensity` | Float | `0.0 ~ 1.0` | `0.5` | 발화 에너지 및 입모양/헤드 액센트 강도 |
| `speechProgress` | Float | `0.0 ~ 1.0` | `0.0` | 발화 진행률 (종료 시 0으로 부드러운 감쇠) |

---

## 3. 레이어 독립성 원칙 (Decoupling)

- `SpeechParameters`는 표정(`FaceParameters`)이나 전신 동작(`MotionParameters`)과 상호 간섭 없이 독립적으로 수신되며, 렌더러에서 합성(Composited)됩니다.
