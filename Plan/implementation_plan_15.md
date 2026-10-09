# P009.AICompanion - Sprint 15: Real Device Validation Pre-Implementation Report

## 1. Sprint 14 Gap Analysis (현재 구현 상태 평가)

Sprint 14의 "문서상 기획"과 "실제 코드 구현 상태"를 비교한 Gap Report입니다.

### Backend (Orchestration Engine)
- **완료된 부분**: `CompanionOrchestrator`, `CompanionEventBus` (Sync/Async), `ContextBuilder` (우선순위 강제 적용), `InteractionStateMachine` 등 Orchestration 기본 구조는 코드로 구현되었습니다.
- **Gap (미구현 / 더미 상태)**: 
  - `LLM Provider`가 여전히 Raw Text를 반환하거나 임시로 파싱하고 있습니다 (Strict JSON/Function Calling 미적용).
  - API Endpoint (`POST /api/v1/companion/interactions`)가 실제로 Orchestrator와 완전히 연결되지 않은 상태입니다.

### Mobile Frontend
- **완료된 부분**: `AvatarService`, `IAvatarRenderer`, `AvatarView` 등 Presentation 추상화 뼈대가 작성되었습니다.
- **Gap (미구현 / 더미 상태)**:
  - `CompanionScreen.tsx`가 여전히 Sprint 12 수준의 Dummy UI(`faceText: {face}`)로 하드코딩되어 있습니다. Sprint 13에서 만든 `AvatarView`를 연동하지 않았습니다.
  - **Camera Sampling 로직**: Vision 처리를 위한 모바일 측 카메라 샘플링(Background 전송) 로직이 없습니다.
  - **Audio & TTS Sync**: `AudioPlayer.onStart` ➔ `AvatarService.setSpeaking(true)` 흐름 및 Interrupt 로직이 실제 모바일 코드로 짜여있지 않습니다.
  - Background 전환 시 Camera/Mic 권한 강제 해제(Stop) 로직이 없습니다.

---

## 2. Sprint 15 핵심 과제 (Implementation Plan)

새로운 엔진 추가 없이, 위 Gap을 채우고 **실제 스마트폰 기기에서 하루 종일(Day-in-the-Life) 동작하는 E2E 파이프라인 완성**에 집중합니다.

### STEP 1: Mobile UI & Avatar 연동 완료
- `CompanionScreen.tsx`에 `AvatarView`, `ConversationView` (Chat), `VoiceController` (Mic), `VisionController` (Camera)를 최종 통합합니다.
- Phone (Avatar 위주) / Tablet (Split View) 레이아웃을 실제 동작 코드로 구현합니다.

### STEP 2: Mobile Hardware Control & Privacy
- **Vision Sampling**: 매 프레임이 아닌 특정 주기(예: 3초)로 캡처하여 Backend 전송.
- **Privacy Boundary**: 앱이 Background로 전환 시 React Native `AppState`를 감지하여 Camera/Mic 스트림 즉시 차단(Stop).
- **TTS Sync & Interrupt**: 오디오 재생 중 사용자가 마이크를 켜면(Interrupt), 진행 중인 TTS를 즉시 Stop하고 `AvatarState`를 LISTENING으로 강제 전환.

### STEP 3: API & Orchestrator 연결 
- `POST /api/v1/companion/interactions` 엔드포인트 구현.
- 텍스트/음성/비전 입력을 `NormalizedInput`으로 변환하여 `CompanionOrchestrator` 파이프라인(Input ➔ Context ➔ LLM ➔ Validation ➔ Avatar) 태우기.

### STEP 4: 5대 Continuity E2E 검증 시나리오
1. **Memory**: 어제 한 말(메모리)을 오늘 대화에서 LLM이 Context로 끌어와서 대답하는지 확인.
2. **Relationship**: 여러 번의 상호작용 후 친밀도가 오르면, LLM 어투와 Avatar의 `expression`이 변화하는지 확인.
3. **Vision -> Emotion**: 웃는 얼굴(FACE_DETECTED, smile)이 감정을 긍정(JOY)으로 변화시키는지 확인.
4. **Failure Isolation**: Vision 모듈 에러 시 텍스트 채팅은 멀쩡하게 진행되는지 확인.
5. **Background Restore**: 앱 종료 후 푸시 알림(Proactive) 탭 시, 끊긴 시점부터 대화가 이어지는지 확인.

### STEP 5: Latency & Performance 로깅
- `TTFT` (Time To First Token), `TTS Start Latency`, `STT Latency` 측정용 로거 부착.

---

## User Review Required

실제 코드 상태 분석 결과, **모바일 프론트엔드의 하드웨어 제어(Mic/Camera/TTS)**와 **Backend Orchestrator API 연결** 영역에서 큰 Gap이 남아 있습니다. 

보고서를 확인해주시고 승인(Approve)해주시면, Task 리스트를 정리하고 STEP 1(Mobile 통합 및 하드웨어 제어 로직 구현)부터 맹렬하게 E2E 통합을 시작하겠습니다! (마지막에 Real Device Validation Report도 자동 생성하겠습니다.)
