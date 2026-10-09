# P009.AICompanion - Sprint 10: Vision & Camera Interaction Engine (Final)

## 1. Core Architecture Principles

> [!IMPORTANT]
> **Architecture Rule: Vision observes. Emotion interprets. Cognitive Core decides.**
> Vision Engine은 관찰만 수행하며, 감정을 확정하거나 기존 Core Rule을 강제로 덮어쓰지 않습니다.
> 예: `smile_probability=0.81` ➔ `USER_SMILING` (관찰) ➔ Emotion Engine이 긍정적 신호로 해석 ➔ LLM 응답 반영

- **Vision Context Pipeline**: Vision ➔ Observation ➔ VisionContextProvider ➔ ContextBuilder ➔ Cognitive Core ➔ LLM
- Vision과 LLM을 직접 연결하지 않으며, 반드시 기존 인지 파이프라인(ContextBuilder)을 거칩니다.

## 2. Privacy & Frame Processing

- **저장 금지**: 원본 카메라 이미지/비디오/얼굴 데이터는 장기 저장하지 않습니다. 오직 구조화된 관찰 결과(Observation)만 저장합니다.
- **Frame Sampling & Throttling**: 3~5초 고정 주기가 아닌, `Sampling ➔ Throttle ➔ Meaningful Change Detection ➔ Vision Provider` 흐름을 따릅니다.
- **Observation Deduplication**: 의미 없는 중복 데이터(예: `FACE_DETECTED` ➔ `FACE_DETECTED`)는 무시하고, 상태 변화(예: `FACE_DETECTED` ➔ `USER_NOT_VISIBLE`)만 새로운 Observation으로 DB에 저장합니다.

## 3. Database Schema

`vision_observations` 테이블은 향후 확장을 고려해 JSONB 구조를 채택합니다.
- `id`, `session_id`, `type`, `confidence`, `data (JSONB)`, `created_at`
- 데이터 예시: `{"face_count": 1, "gaze": "toward_camera", "expression": "smiling"}`

## 4. Vision Provider

- **Cloud Vision First**: 초기 구현은 `CloudVisionProvider`를 적용하되, `BaseVisionProvider` 추상화를 통해 향후 MediaPipe 등 Local Vision 모델로 쉽게 교체할 수 있도록 합니다.

## 5. Mobile UI & Permissions

- **UI 설계**: 일반 사용자는 Camera Preview, Companion 대답, 마이크 버튼 등 최소한의 자연스러운 화면만 봅니다. Debug 모드에서만 상세 상태(Confidence, Gaze 등)를 텍스트로 노출합니다.
- **Failure Isolation**: Camera Permission Denied, Provider Failure 등의 상황에서도 Vision Context만 생략될 뿐 Text/Voice 기반 대화는 100% 정상 동작해야 합니다.

## 6. Critical Scenarios & Verification

> [!CAUTION]
> **Vision Hallucination Protection**
> 시각 정보 신뢰도(Confidence)가 낮거나 사용자가 화면에 없는 경우(`USER_NOT_VISIBLE`), Companion이 강한 시각적 추측(예: "너 웃고 있네")을 하지 않도록 시스템 프롬프트 및 안전장치를 마련합니다.

- **Full Multimodal Loop 검증**: 
  `Camera + Microphone ➔ Vision + STT ➔ Interaction Input ➔ ContextBuilder ➔ (Persona, Memory, Emotion, Relationship, Presence, Vision) ➔ LLM ➔ TTS ➔ Companion Voice`
- 해당 전체 루프가 작동하는지 E2E 테스트 및 수동 검증으로 확인합니다.
