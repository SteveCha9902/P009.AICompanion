# P009.AICompanion - Sprint 19 Pre-Implementation Audit Report
**Real Avatar Presentation & Multimodal Synchronization Engine**

---

## 1. 개요 및 핵심 아키텍처 원칙

Sprint 19의 목표는 **LLM 의미 ➔ Emotion ➔ AvatarState ➔ Audio ➔ Expression/Animation** 흐름을 단일 Presentation Pipeline으로 통합하는 것입니다.

```text
Companion Core
      ↓
AvatarStateResolver (Backend)
      ↓ (Unified JSON SSE: avatar_state)
AvatarService (Mobile State Hub) ◄─── Audio Player / VoiceController (Real-time Speaking)
      ↓
AvatarRenderer Interface
      ├── StaticImageRenderer (2D Baseline)
      └── Live2D / 3D Renderer Adapter (Extensible)
```

---

## 2. Phase 1 — 현재 Avatar 코드 Audit (8대 질문 답변)

### Q1. 현재 AvatarState 구조
[avatar_state.ts](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/features/avatar/domain/avatar_state.ts) 및 [presentation_engine.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/presentation_engine.py):
- `state_version`: number (상태 버전 증가 추적)
- `timestamp`: ISO 8601 string
- `expression`: string ("neutral", "smile", "warm_smile", "curious", "surprised", "soft", "restrained", "sleeping")
- `animation`: string ("idle", "thinking", "speaking", "attentive", "relaxed", "breathing", "reduced", "hidden")
- `gaze`: string ("user", "away", "closed", "searching")
- `speaking`: boolean (실제 모바일 오디오 재생과 연동)
- `listening`: boolean (마이크 캡처 중 활성화)
- `intensity`: float 0.0~1.0 (감정/모션 강도)
- `energy`: float 0.0~1.0 (각성도)

### Q2. 실제 Avatar 렌더링 경로
```text
CompanionOrchestrator.process_interaction()
       │
       ▼ Post Processing
AvatarStateResolver.resolve(companion_id)
       │
       ▼ SSE Event: avatar_state (id: {id}:{seq})
Mobile InteractionController
       │
       ▼ updateSemanticState(avatar_state)
AvatarService (State Merging & Preserving Real-time Speaking)
       │
       ▼ subscribe()
AvatarView (Wrapped with AvatarErrorBoundary)
       │
       ▼ render({ state })
IAvatarRenderer (StaticImageRenderer)
```

### Q3. Audio 재생 이벤트 위치
- [voiceController.ts](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/services/voiceController.ts)의 `stopListeningAndSend()`:
  - 오디오 수신 및 재생 시작: `this.isSpeaking = true; avatarService.setSpeaking(true);`
  - 오디오 재생 종료: `this.isSpeaking = false; avatarService.setSpeaking(false);`
  - 오디오 에러 발생: `this.isSpeaking = false; avatarService.setSpeaking(false);`

### Q4. Speaking 상태 관리 위치
- **모바일 클라이언트 `avatarService.ts`가 Speaking 상태의 최종 진실 출처(Single Source of Truth)**.
- 백엔드 `AvatarStateResolver`는 발화 의도(Semantic Intention)만 전달하며, `avatarService.updateSemanticState()`는 백엔드 값으로 로컬 `speaking`을 덮어쓰지 않고 실제 Audio Player 상태를 최우선 유지.

### Q5. Emotion → Avatar 변환 위치
- 백엔드 [presentation_engine.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/presentation_engine.py)의 `AvatarStateResolver.resolve()`:
  - `EmotionState.primary_emotion` (JOY, EMPATHY, CURIOSITY, SURPRISE, FRUSTRATION) + `intensity`
  - `RelationshipState.current_stage` (STRANGER는 0.5x restrained, CLOSE는 1.2x relaxed)
  - ➔ `expression`, `intensity`, `animation`으로 규칙 매핑.

### Q6. 기존 코드 중 재사용 가능한 부분
- `AvatarStateResolver` ([presentation_engine.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/presentation_engine.py))
- `AvatarState` ([avatar_state.ts](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/features/avatar/domain/avatar_state.ts))
- `IAvatarRenderer` 인터페이스 및 `StaticImageRenderer` ([AvatarRenderer.tsx](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/features/avatar/presentation/AvatarRenderer.tsx))
- `AvatarErrorBoundary` 및 `AvatarView` ([AvatarView.tsx](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/features/avatar/presentation/AvatarView.tsx))
- `avatarService` ([avatar_service.ts](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/features/avatar/services/avatar_service.ts))
- `voiceController`의 `interrupt()` 및 `cleanup()` ([voiceController.ts](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/services/voiceController.ts))

### Q7. 현재 Stub/Mock 상태
- `StaticImageRenderer`: 이모지 및 텍스트 기반 2D Baseline Renderer.
- Live2D / 3D Renderer는 추상 인터페이스(`IAvatarRenderer`)를 통해 확장 가능한 상태.

### Q8. 실제 구현 시 충돌 가능성 및 해결 방안
1. **Presentation 상태 우선순위 충돌**:
   - 동시에 여러 상태(Thinking, Speaking, Listening, Error)가 발생할 수 있음.
   - **우선순위 계층 정의**: `ERROR > INTERRUPTED > SPEAKING > LISTENING > THINKING > EMOTION > IDLE`.
2. **Audio Callback Race Condition**:
   - 이전 Interaction의 오디오 종료 콜백이 새 Interaction의 Speaking 상태를 덮어쓰는 문제.
   - **해결 방안**: `playbackId` 기반 일치 여부 검증 및 `interrupt()` 호출 시 이전 `playbackId` 즉각 무효화.

---

## 3. Sprint 19 구현 계획 (Phases 2 ~ 8)

1. **Phase 2 (AvatarState Contract 확정)**:
   - `AvatarState` 스키마 동결 (`expression`, `animation`, `gaze`, `speaking`, `listening`, `intensity`, `energy`).
2. **Phase 3 (Emotion → Avatar Mapping 규칙 강화)**:
   - `AvatarStateResolver`의 감정/관계별 매핑 룰 명확화 (JOY ➔ warm_smile/smile, EMPATHY ➔ soft, CURIOSITY ➔ curious, SURPRISE ➔ surprised, FRUSTRATION ➔ restrained).
3. **Phase 4 (AvatarRenderer Interface & Baseline Renderer)**:
   - `IAvatarRenderer` 인터페이스 및 반응형 2D Renderer 고도화.
4. **Phase 5 & 6 (Audio & Interrupt Synchronization)**:
   - Audio `onStart` ➔ `speaking = true`, Audio `onEnd`/`onError` ➔ `speaking = false`.
   - 발화 중 마이크 입력 시 `interrupt()` ➔ `speaking = false` ➔ `LISTENING` 전이.
5. **Phase 7 (Presentation State Priority Layer)**:
   - `avatarService` 내 우선순위 상태 머신 정립.
6. **Phase 8 (Phone & Tablet Adaptive Layout)**:
   - `CompanionScreen.tsx`에서 반응형 아바타/대화/컨트롤 레이아웃 검증.

---

## 4. Quality Gates (Gate A ~ H)

| Gate | 검증 항목 | 검증 방식 |
| :--- | :--- | :---: |
| **Gate A** | AvatarState Contract Test | 필수 필드 누락 없는지 단위 테스트 |
| **Gate B** | Emotion → Avatar Mapping Test | 감정/관계 조합별 표현식 매핑 테스트 |
| **Gate C** | Audio Start → Speaking Test | 오디오 시작 시 `speaking = true` 동기화 |
| **Gate D** | Audio End → Idle/Emotion Test | 오디오 종료/에러 시 `speaking = false` 복구 |
| **Gate E** | User Interrupt Test | 발화 중 마이크 토글 시 즉각 발화 중단 및 `LISTENING` 전이 |
| **Gate F** | Failure Isolation Test | 아바타 렌더링 에러 시 ErrorBoundary로 격리, 대화 지속 |
| **Gate G** | Backend Regression Test | 기존 58개 테스트 100% PASS |
| **Gate H** | Mobile TypeScript Build | `npx tsc --noEmit` 에러 0개 |
