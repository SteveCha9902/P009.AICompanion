# P009.AICompanion - Sprint 9: Voice Interaction Engine

Sprint 9의 목표는 P009 AI Companion을 텍스트 기반 인터페이스에서 음성 지원이 가능한 AI Companion으로 확장하는 것입니다. 단순한 STT/TTS 구현을 넘어, Voice Interaction State Machine을 구축하고 이를 기존 Cognitive Core와 통합하는 데 중점을 둡니다.

## User Review Required

이 구현 계획을 검토해 주시기 바랍니다. 승인되면 `task.md`에서 작업을 추적하며 구현을 시작합니다.

> [!IMPORTANT]
> 이번 스프린트에서는 범위를 제한합니다. Wake Word(호출어), 항상 켜진 마이크, 카메라 비전, 아바타, 립싱크, Full Duplex Voice 같은 기능은 Sprint 9 범위에서 명시적으로 제외되며, 향후 스프린트에서 구현됩니다.

## Open Questions

> [!NOTE]
> 1. 초기 구현에서 어떤 STT/TTS Provider를 우선 적용하시겠습니까? (예: OpenAI, Google, Azure, Local 등). 우선은 정의된 대로 Mock Provider와 Adapter 구조부터 시작할 예정입니다.
> 2. Voice Session 로그는 기존 메인 DB에 저장해야 할까요, 아니면 별도의 로깅 백엔드로 분리해야 할까요?

## Proposed Changes

### Database & Domain Models

- `VoiceSession` 도메인 및 데이터베이스 모델을 정의하여 세션을 추적합니다. (원본 오디오는 별도 정책이 없는 한 장기 저장하지 않습니다).

#### [NEW] backend/app/db/models/voice_session.py
#### [MODIFY] backend/app/db/models/__init__.py
#### [NEW] backend/alembic/versions/xxxx_create_voice_sessions_table.py

### API & Services

- STT/TTS 추상화 (Provider Interfaces, Mock Providers) 구현.
- `VoiceService`를 구현하고 기존 `ConversationService`와 연동.
- Voice Session 라이프사이클 처리를 위한 엔드포인트 노출 (생성, 음성인식, 발화, 인터럽트, 종료).

#### [NEW] backend/app/services/voice/provider_interface.py
#### [NEW] backend/app/services/voice/mock_provider.py
#### [NEW] backend/app/services/voice/adapters/...
#### [NEW] backend/app/services/voice_service.py
#### [NEW] backend/app/api/endpoints/voice.py
#### [MODIFY] backend/app/main.py

### Mobile Application

- 다음 상태를 갖는 Voice UI 구현: `IDLE`, `LISTENING`, `TRANSCRIBING`, `THINKING`, `SPEAKING`, `INTERRUPTED`, `ERROR`.
- 모바일 마이크(Microphone) 권한 처리 명시적 구현.
- Phone 및 Tablet 레이아웃 대응 (Adaptive UI).
- 음성 실패 시 텍스트 대화로 자연스럽게 넘어가는 Fallback 매커니즘 적용.

#### [NEW] mobile/lib/features/voice/domain/...
#### [NEW] mobile/lib/features/voice/presentation/...
#### [MODIFY] mobile/lib/features/conversation/presentation/...

### Tests

- 백엔드 Voice Interaction Engine에 대한 Unit Test 및 Integration Test 추가.
- Android 에뮬레이터를 이용해 Voice State Machine 전환을 포괄적으로 테스트하는 E2E UI Test 작성.

#### [NEW] backend/tests/services/test_voice_service.py
#### [NEW] backend/tests/api/test_voice_endpoints.py
#### [NEW] mobile/integration_test/voice_interaction_test.dart

## Verification Plan

### Automated Tests
- `pytest backend/tests/services/test_voice_service.py`
- `pytest backend/tests/api/test_voice_endpoints.py`
- 마이크 권한 및 Voice Session 연동을 위한 Flutter UI 테스트 수행.

### Manual Verification
- Android 에뮬레이터/단말기에 배포하여 마이크 권한 요청, STT 렌더링 속도, 텍스트 Fallback 동작, Phone/Tablet UI 레이아웃 변경을 수동으로 확인.
