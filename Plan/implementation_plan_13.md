# P009.AICompanion - Sprint 13 Pre-Implementation Report
**Avatar & Multimodal Presentation Engine**

## 1. Existing Reusable Components & Integration Points

- **Avatar / Presentation Engine**: Sprint 11에서 구축된 `PresentationEngine`(`backend/app/services/presentation_engine.py`)이 이미 존재합니다. 이를 **`AvatarStateResolver`** 의 역할로 확장하여 요구사항에 맞는 `AvatarState` (expression, animation, gaze, speaking, listening, intensity, energy) JSON을 반환하도록 리팩토링합니다.
- **Voice Integration**: `VoiceSession` 모델 및 `VoiceService`가 존재하며 `LISTENING`, `THINKING`, `SPEAKING` 상태를 제공합니다.
- **Vision Integration**: `VisionSession` 및 `VisionObservation` (USER_DETECTED, FACE_DETECTED) 데이터가 존재합니다.
- **Emotion & Relationship**: `EmotionState` 및 `RelationshipState` 구조가 이미 마련되어 있으며, PresentationEngine에서 이를 매핑하고 있습니다.

## 2. Modified & Created Files

### Backend (Python)
- **[MODIFY]** `backend/app/services/presentation_engine.py`: 기존 로직을 `AvatarStateResolver` 역할에 맞게 정교화 (`speaking`, `listening`, `energy` 필드 추가, 리팩토링).
- **[MODIFY]** `backend/app/api/endpoints/avatar.py`: 모바일에서 Avatar State를 Polling 하거나 SSE로 받을 수 있도록 개선.

### Mobile (React Native / TypeScript)
- **[NEW]** `mobile/src/features/avatar/domain/avatar_state.ts`: `AvatarState` 인터페이스 정의.
- **[NEW]** `mobile/src/features/avatar/services/avatar_service.ts`: Backend API 연동 및 상태 관리.
- **[NEW]** `mobile/src/features/avatar/components/AvatarView.tsx`: Avatar 렌더링 최상위 컴포넌트.
- **[NEW]** `mobile/src/features/avatar/components/AvatarExpression.tsx`
- **[NEW]** `mobile/src/features/avatar/components/AvatarAnimation.tsx`
- **[NEW]** `mobile/src/features/avatar/components/AvatarSpeakingIndicator.tsx`
- **[NEW/MODIFY]** `mobile/src/screens/CompanionScreen.tsx`: Phone/Tablet Adaptive Layout을 지원하는 메인 통합 화면.

## 3. Potential Architectural Conflicts

> [!WARNING]
> **Real-time Synchronization (Lip Sync & Animation)**
> LLM ➔ TTS ➔ Audio 재생 시점과 Avatar의 `SPEAKING` 애니메이션 시점을 모바일 프론트엔드에서 정확히 맞추기 위한 동기화(Synchronization) 로직이 필요합니다. 
> - **해결 방안**: Audio Player의 이벤트(OnStart, OnEnd)를 기반으로 클라이언트 단에서 `speaking = true/false`를 오버라이드 하거나, Backend `AvatarState`와 결합하여 하이브리드로 처리해야 합니다.

## 4. Mobile Adaptive Layout Strategy

**Phone Layout (Avatar-Centric)**
- 화면 중앙에 AvatarView 배치. 하단에 Voice/Vision/Chat 컨트롤 바.
- 대화 내역은 Overlay 하거나 별도 패널로 숨김 처리.

**Tablet Layout (Split View)**
- 좌측: Conversation History
- 중앙: Companion (AvatarView)
- 우측/하단: Vision Camera Debug & Tools

## 5. Failure Isolation
- React Native Error Boundary를 `AvatarView`에 적용하여, 렌더링 실패 시 해당 컴포넌트만 다운되고 나머지 Conversation / Voice / Vision UI는 정상 동작하도록 격리(Isolation)합니다.

---
## User Review Required

위 Pre-Implementation Report에 대한 검토를 부탁드립니다. 
승인해주시면, Sprint 11에서 만든 `PresentationEngine`을 `AvatarStateResolver` 규격으로 고도화하고, 바로 모바일(React Native) `CompanionScreen.tsx` 및 `AvatarView` 구현으로 진입하겠습니다.
