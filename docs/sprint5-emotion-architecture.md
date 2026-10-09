# Sprint 5: Emotion Engine Architecture & Final Report

> 이 문서는 Sprint 5 시작 전 최종 확정된 Emotion Engine의 핵심 아키텍처 원칙을 담고 있습니다.

## 1. Context Priority & Trust Boundary
Context의 논리적 우선순위는 다음과 같습니다.
`SYSTEM/SAFETY > PERSONA > MEMORY > EMOTION > HISTORY > CURRENT USER INPUT`

**중요 원칙**: Emotion(현재 상태)이 Current User Request(사용자 의도)를 묵살하거나 거부해서는 안 됩니다. (예: "슬프니까 설명하기 싫어" X) Emotion은 오직 **응답의 표현 방식(Tone/Behavior)**에만 영향을 미칩니다.

## 2. Emotion Extraction과 Transition의 엄격한 분리
LLM이 최종 감정 상태를 직접 결정하지 않습니다.
1. **Emotion Extractor (LLM)**: User Message에서 `Emotion Signal` (유저의 감정, 트리거 등)을 추출.
2. **Transition Engine (Code)**: `Previous State + Emotion Signal + Persona + Memory`를 기반으로 `New Companion State`를 계산 확정.

## 3. User Emotion ≠ Companion Emotion
User의 감정(예: ANGER)이 Companion의 감정(예: EMPATHY, CALM, TENSION 등)과 1:1로 매핑되지 않습니다. User Emotion은 Transition Engine에 들어가는 **입력 신호 중 하나**일 뿐입니다.

## 4. Persona Warmth vs Emotion Warmth
- **Persona Warmth**: Companion의 기본 성향 (Base Personality)
- **Emotion Warmth**: 현재 상황에서의 따뜻함 활성화 정도 (Current Emotional Activation)
-> 최종 표현은 이 두 가지의 결합으로 나타납니다.

## 5. Decay와 Transition의 독립
- **Decay Engine**: 시간 경과에 따라 현재 감정을 Base State로 서서히 낮춥니다.
- **Transition Engine**: 새로운 이벤트가 발생했을 때 Decay된 상태 위에서 새로운 상태로 전이시킵니다.

## 6. Emotion Event Logging
향후 Sprint 6 (Relationship Engine)에서 사용자와의 교감(Shared Experience) 신호로 활용하기 위해, 감정이 변화할 때마다 `emotion_events` DB에 Trigger, Intensity, Source Message 등을 로깅합니다.

## 7. Testing Scenarios
구현 완료 후 다음 5가지 시나리오를 반드시 검증합니다.
- A. Same Emotion + Different Persona
- B. Same Persona + Different Emotion
- C. Emotion must not override Current User Request
- D. Relevant Memory must influence Emotion
- E. 프롬프트 인젝션 방어 (Emotion 임의 조작 불가)
