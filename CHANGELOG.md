# P009.AICompanion CHANGELOG

## [Sprint Branch SB-18] - Multi-Character Individual Settings & Voice Customization (Platform Stage 18)
### Added
- **Multi-Character Settings UI (`mobile/src/screens/SettingsScreen.tsx`)**:
  - 상단 3대 캐릭터(🌸 지니, 🎀 마니, 🎨 하나) 세그먼트 셀렉터 탭 및 현재 활성 컴패니언 뱃지(`사용중`).
  - 설정 화면에서 즉시 메인 대화 캐릭터로 전환할 수 있는 `⚡ 이 캐릭터 사용하기` 기능.
- **Individual Voice Configuration & Live Preview (`mobile/src/screens/SettingsScreen.tsx`)**:
  - 한국어 뉴럴 보이스 모델 8종(선희, 지민, 서현, 유진, 인준, 봉진, Shimmer, Nova) 프리셋 선택기.
  - 말하기 속도(Speech Rate: 0.7x~1.3x), 음높이/피치(Pitch Offset: -10Hz~+10Hz), 다정함(Warmth), 에너지(Energy) 정밀 제어기.
  - `▶ 목소리 미리듣기` (`Speech.speak`) 버튼을 통한 캐릭터별 시그니처 인사말 즉시 재생.
- **Individual Personality & Cognitive DNA Tuning**:
  - 다정함, 공감능력, 발랄함, 호기심, 유머감각, 격식 등 6대 DNA 지수(0~100) 및 대화 톤/호흡 개별 저장 연동.
- **Backend Character-Specific TTS Synthesis (`VoiceService`, `EdgeTTSAdapter`)**:
  - `VoiceService`에서 각 캐릭터의 `voice_id`, `speaking_rate`, `pitch_offset`을 실시간 로드하여 개별 음성 합성 파이프라인 완성.

## [Hotfix] - Multi-Character Persona Isolation & Dynamic Scoping Fix (Mani Daughter Persona Restoration)
### Fixed
- **Character Seeding Logic (`app/services/character/character_service.py`)**:
  - `CharacterService.get_or_create_character`에서 미존재 캐릭터 시딩 시 지니(아내) 프로필로 일괄 강제 생성되던 결함을 수정하고, `c_mani` (사랑스러운 딸) 및 `c_hana` (예술 친구) 전용 DNA/프로필/성격/가치/경계를 시딩하도록 개선.
- **Legacy Persona Context Isolation (`app/services/context/providers/persona_provider.py`)**:
  - `PersonaContextProvider`가 `companion_id`를 인식하여, `default_companion`이 아닌 다른 캐릭터(마니, 하나 등) 활성화 시 레거시 지니(아내) 페르소나(`role: wife`, `여보/당신`)가 컨텍스트에 침범하지 못하도록 차단.
- **ContextBuilder Dynamic Companion Scoping (`app/services/context/builder.py`)**:
  - `ContextBuilder.build()` 실행 시 등록된 모든 하위 Provider(`CharacterIdentityProvider`, `RelationshipContextProvider`, `PersonalityContextProvider` 등)에 활성 `companion_id`를 강제 전파하여 컨텍스트 불일치 원천 해소.
- **Relationship Engine Anchor Dynamic Naming (`app/services/relationship/relationship_engine.py`)**:
  - 최초 조우(`FIRST_MEETING`) 앵커 등록 시 하드코딩된 "지니" 명칭을 활성 `companion_id`에 부합하도록 동적 변환.
- **Database Persona Sync (`companion.db`)**:
  - `companion.db`의 `character_profiles`, `character_personalities`, `character_values`, `relationship_anchors` 테이블의 `c_mani` 및 `c_hana` 데이터를 올바른 딸/친구 페르소나로 갱신 완료.

## [Sprint Branch SB-17] - Natural Conversation, Dynamic Cadence & Quiet Empathy (Multi-Character Platform Stage 17)
### Added
- **Conversation Mode & Cadence Empathy Domain Models (`app/domain/conversation/cadence_empathy.py`)**:
  - `ConversationMode` (7종: NORMAL, EMOTIONAL_SUPPORT, QUIET_EMPATHY, INFORMATION, PLAYFUL, DEEP_CONVERSATION, CLOSING).
  - `ResponsePolicy`: 상황별 선호 문장 수(1~3문장), 질문 허용 여부, 공감 우선순위 제어.
  - `ConversationFatigueTracker`: 사용자 피로/무력감 신호 감지(0.0~1.0).
  - `QuestionBudgetTracker`: 최근 3턴 중 질문 횟수 추적 및 과도한 질문 폭주 자동 억제.
  - `ResponseQualityGate`: QUIET_EMPATHY 및 CLOSING 모드에서 물음표 질문 자동 제거 및 1~2문장 강제 압축.
- **16 Dedicated Conversation Cadence & Empathy Tests (`tests/test_conversation_cadence_empathy_e2e.py`)**:
  - Normal Mode, Emotional Support, Quiet Empathy Trigger, Zero-Question Enforcement, Question Budget Suppression, User Cadence Matching (Short/Long), Fatigue Detection, Information Preservation, Closing Mode, Character DNA Preservation, Adversarial A~C, Overlong Trimming, 30-Turn Long Session Stability 100% PASS.
- **17 Architecture & Evaluation Documents (`docs/sb17/`)**:
  - `SB17_CONVERSATION_ARCHITECTURE.md` ~ `SB17_COMPLETION_REPORT.md`.

## [Sprint Branch SB-16] - Real User Pilot & Product Validation (Multi-Character Platform Stage 16)
### Added
- **Real User Pilot & Android UX Scorecard Benchmark**:
  - Genie, Mani, Hana 3대 캐릭터에 대한 10대 제품 가설(H1~H10) 및 10대 시나리오(A~J) 검증.
  - Overall Companion Feeling 평균 4.70 / 5.0 달성.
- **Product Backlog & SB-17 Direction Decision**:
  - `PB-01` (대화 호흡 및 자연스러운 공감/경청 모드)을 최우선 과제로 선정하여 차기 스프린트 `SB-17: Natural Conversation, Dynamic Cadence & Quiet Empathy` 확정.
- **16 Dedicated Pilot Product Validation Tests (`tests/test_pilot_product_validation_e2e.py`)**:
  - Identity Differentiation, Consistency, Memory Recall/Precision, Relationship Impact, Emotion Empathy, Cadence Constraint, Voice/Avatar Sync, Proactive Quiet Hours, Rapid Switching, Network Resiliency, Lifecycle Preservation, Issue Classification, Priority Formula, Full Scenario Smoke Run 100% PASS.
- **16 Pilot Evaluation & Backlog Documents (`docs/sb16/`)**:
  - `SB16_PILOT_PLAN.md` ~ `SB16_COMPLETION_REPORT.md`.

## [Sprint Branch SB-15] - Production Deployment & Multi-User Server Architecture (Multi-Character Platform Stage 15)
### Added
- **Multi-Tenant Identity & Scope Guard Domain Model (`app/domain/auth/multi_user_context.py`)**:
  - `AuthoritativeUserContext`: JWT 토큰 기반 검증된 사용자 신원 보장.
  - `MultiTenantScopeGuard`: `User A ↔ User B` 테넌트 간 침범 및 IDOR 공격 100% Fail-Closed 차단.
- **Production Containerization & Reverse Proxy Topography (`Dockerfile`, `docker-compose.production.yml`, `docker/nginx.conf`)**:
  - Multi-stage Python 3.10 이미지 및 Gunicorn/Uvicorn 프로덕션 컨테이너.
  - Nginx 리버스 프록시 (TLS 종단, 보안 헤더, SSE 버퍼링 비활성화, 50MB 요청 크기 제한).
  - PostgreSQL 16 + pgvector 및 Redis 7 Alpine 컨테이너 분리.
- **16 Dedicated Multi-User Production E2E Tests (`tests/test_multi_user_production_e2e.py`)**:
  - Authoritative Identity, Ownership Defense, Character Instance Isolation, Memory Isolation, Trust Isolation, Shared Experience Tenant Boundary, 30 Concurrent Streams, Docker/Nginx Configs, Health/Ready Probes, Rate Limiting, Privacy Redaction, Token Refresh, Disaster Recovery DB Fallback, Full Smoke Test 100% PASS.
- **22 Production Architecture & Operations Audit Documents (`docs/sb15/`)**:
  - `SB15_PRODUCTION_ARCHITECTURE.md` ~ `SB15_IMPLEMENTATION_DECISION.md` (Runbook, Disaster Recovery, Backup/Restore, CI/CD, Rollback 포함).

## [Sprint Branch SB-14] - Production Hardening & Reliability Engineering (Multi-Character Platform Stage 14)
### Added
- **Interaction Execution Registry & Idempotency Domain Model (`app/domain/reliability/interaction_execution.py`)**:
  - `InteractionExecutionRegistry`, `InteractionExecutionRecord`, `InteractionExecutionStatus`: `interaction_id` 기반 멱등성 및 중복 실행 방어.
- **Timeout Budget, Rate Limiter & Privacy Redactor (`app/domain/reliability/timeout_budget.py`)**:
  - `TimeoutBudget`: 하위 시스템별 타임아웃 예산 관리.
  - `RateLimiter`: 사용자/IP/캐릭터 단위 슬라이딩 윈도우 요청 제한.
  - `PrivacyRedactor`: 비밀번호, 토큰, API 키의 로그 마스킹.
- **Readiness Probe Endpoint (`app/main.py`)**:
  - `/ready` 엔드포인트 추가 (DB 및 런타임 상태 진단).
- **16 Dedicated Production Hardening Tests (`tests/test_production_hardening_e2e.py`)**:
  - Ownership, IDOR, Rollback, Concurrency, Idempotency, Redis Fallback, Cache Namespacing, LLM Timeout, TTS Fallback, Rate Limiting, Privacy Redaction, Health/Ready, Mobile Stale Discard, Prompt Injection, 100-Concurrency Load Stress 100% PASS.
- **17 Architecture & Security Audit Documents (`docs/sb14/`)**:
  - `SB14_PRODUCTION_ARCHITECTURE_AUDIT.md` ~ `SB14_IMPLEMENTATION_DECISION.md`.

## [Sprint Branch SB-13] - Character-to-Character & Controlled Shared Experience Engine (Multi-Character Platform Stage 13)
### Added
- **Controlled Shared Experience Domain Models (`app/domain/shared_experience/controlled_sharing.py`)**:
  - `SharePolicy`, `ShareProposal`, `ControlledSharedExperience`, `SharedExperienceScope`, `ShareCategory`.
  - `ControlledSharedExperience.is_accessible_by(user_id, character_id)`: 사용자/타겟/만료/철회 격리 판정.
- **Sharing Policy Engine & Controlled Sharing Service (`app/services/shared_experience/`)**:
  - `SharingPolicyEngine`: 엄격한 `Private by Default` 정책 평가 및 접근 필터링.
  - `ControlledSharingService`: 제안(Propose), 명시적 승인(Approve), 거부(Deny), 즉시 철회(Revoke) 및 감사 로깅.
- **15 Dedicated Controlled Shared Experience Tests (`tests/test_shared_experience_engine_e2e.py`)**:
  - Private Isolation, Explicit Sharing, Denied Proposal, Target Restriction, Immediate Revocation, Cache Invalidation, User Isolation, Dynamic State Isolation, Provenance, Concurrency, Injection Defense 100% PASS.
- **10 Architecture & Security Audit Documents (`docs/sb13/`)**:
  - `SB13_SHARED_EXPERIENCE_ARCHITECTURE.md` ~ `SB13_IMPLEMENTATION_DECISION.md`.

## [Sprint Branch SB-12] - Multi-Character Conversation Orchestration & End-to-End Scope Integrity (Multi-Character Platform Stage 12)
### Added
- **Companion Interaction Context & Presentation Command Domain Models (`app/domain/interaction/companion_interaction_context.py`)**:
  - `CompanionInteractionContext(interaction_id, scope, character_snapshot, created_at)`: 불변 실행 컨텍스트 및 `validate_scope_integrity()` 검증.
  - `PresentationCommand`: 캐릭터별 음성/아바타 프레젠테이션 바인딩 모델.
  - `CompanionEventPayload`: 이벤트 버스용 캐릭터 스코프 페이로드.
- **Orchestrator Lifecycle Guard & Error Handling Hardening (`app/services/companion/orchestrator.py`)**:
  - `try` 블록 내부로 `context_resolver.resolve` 이동 및 `if tracer:` 가드로 안전한 에러 이벤트 방출.
- **15 Dedicated Multi-Character Orchestration E2E Tests (`tests/test_multi_character_orchestration_e2e.py`)**:
  - Text, Voice(Mani Shimmer), Vision(Hana), Full Pipeline, Rapid Switching, Concurrent Streams, Stale Response, TTS Race, Avatar Race, Agency Race, Idempotency, Failure Recovery, Ownership Attack, Invalid ID, Archived ID 100% PASS.
- **10 Architecture & Security Audit Documents (`docs/sb12/`)**:
  - `SB12_ORCHESTRATION_ARCHITECTURE_AUDIT.md` ~ `SB12_IMPLEMENTATION_DECISION.md`.

## [Sprint Branch SB-11] - Character Relationship & Emotional State Isolation (Multi-Character Platform Stage 11)
### Added
- **Character Dynamic State Scope & Bundle Domain Model (`app/domain/character/dynamic_state_bundle.py`)**:
  - `CharacterDynamicStateScope(user_id, companion_id)`: Fail-Closed 불변 스코프 및 캐시 키 헬퍼.
  - `CharacterDynamicStateBundle`: Emotion, Relationship, Growth, Agency, Presence의 서브엔티티 일관성 검증(`validate_consistency`).
- **Scope Pinning in Service Layer (`app/services/emotion_service.py`)**:
  - `EmotionService.process_user_message`: `companion_id` 파라미터 지원을 통한 Write-after-switch 상태 오염 방어.
- **12 Dedicated Dynamic State Isolation Tests (`tests/test_character_dynamic_state_isolation_e2e.py`)**:
  - Emotion, Relationship, Growth, Agency, Presence, Scope Pinning, Bundle Consistency, Cache Invalidation, 30-Concurrency 100% PASS.
- **10 Architecture & Isolation Audit Documents (`docs/sb11/`)**:
  - `SB11_DYNAMIC_STATE_ARCHITECTURE_AUDIT.md` ~ `SB11_IMPLEMENTATION_DECISION.md`.

## [Sprint Branch SB-10] - Multi-Character Memory Isolation & RAG Anti-Leakage (Multi-Character Platform Stage 10)
### Added
- **Tripartite Memory Scope Domain Model (`app/domain/memory/character_memory_scope.py`)**:
  - `CharacterMemoryScope`, `UserGlobalMemoryScope`, `SharedExperienceScope`, `CharacterScopeRequiredError`.
- **Character Memory Guard Secondary Defense Layer (`app/services/memory/`)**:
  - `CharacterMemoryGuard.validate_context_injection`: ContextBuilder 주입 전 타 캐릭터 기억 강제 폐기.
  - `CharacterMemoryGuard.validate_canary_integrity`: Secret Canary 토큰 기반 교차 유출 탐지.
  - Fail-Closed 정책 적용: `companion_id` 누락 시 `CharacterScopeRequiredError` 발생.
- **Memory Context Provider Integration (`app/services/context/providers/`)**:
  - `MemoryContextProvider`: 2차 스코프 가드를 통과한 안전 메모리만 LLM 컨텍스트에 조립.
- **24 Dedicated Adversarial Automated Tests (`tests/test_character_memory_isolation_e2e.py`)**:
  - Direct cross retrieval, Vector semantic similarity attack, Cache poisoning attack, Context injection spoofing, 6-cycle rapid switching burst (A->B->C->A->C->B->A), Concurrent retrieval, Secret Canary audit 100% PASS.
- **9 Architecture & Security Audit Documents (`docs/sb10/`)**:
  - `SB10_MEMORY_ARCHITECTURE_AUDIT.md` ~ `SB10_IMPLEMENTATION_DECISION.md`.

## [Sprint Branch SB-9] - Multi-Character Mobile Studio & Real-Time Switching UX (Multi-Character Platform Stage 9)
### Added
- **Zustand Character Store (`mobile/src/state/useCharacterStore.ts`)**:
  - `characterList`, `activeCharacterId`, `activeCharacter`, `isLoading`, `isSwitching`, `error` 관리.
  - Server-Confirmed 원자적 스위칭 및 Race Condition 방어 구현.
- **Character Gallery Screen (`mobile/src/features/character/screens/CharacterGalleryScreen.tsx`)**:
  - 지니(💖 아내), 마니(💕 사랑스러운 딸), 하나(🎨 친구), 커스텀 캐릭터 카드 그리드 및 원터치 전환, `+ 새 캐릭터` 위저드 연동.
- **Mobile API Client (`mobile/src/features/character/services/characterApi.ts`)**:
  - `listCharacters()`, `getActiveCharacter()`, `activateCharacter()`.
- **Navigation & CompanionScreen Integration**:
  - `CompanionScreen.tsx`: 활성 캐릭터에 따른 상단 헤더, 대화창, 음성/비전 컨트롤러 실시간 동기화.
  - `CharacterTabScreen.tsx` & `RootNavigator.tsx`: 갤러리/위저드 탭 네비게이션 연동.
- **10 Mobile E2E Automated Tests (`backend/tests/test_character_switching_mobile_e2e.py`)**:
  - 앱 시작, Genie ↔ Mani ↔ Hana 전환, 메모리/관계 격리, 음성/아바타 바인딩, 403 거부, 빠른 연속 스위칭 100% PASS.
- **11 Architecture & Policy Documents (`docs/sb9/`)**:
  - `SB9_REPOSITORY_AUDIT.md` ~ `SB9_IMPLEMENTATION_DECISION.md`.

## [Sprint Branch SB-8] - Character Creation Studio & Character Factory (Multi-Character Platform Stage 8)
### Added
- **Character Factory & Compiler Enhancements (`app/services/character/`)**:
  - `CharacterFactory`: `build_identity`, `build_values`, `build_relationship_defaults`, `build_character_dna`, `build_preview`.
  - `CharacterCreationRequest` & `CharacterDNA`: `tagline`, `interests`, `speech_profile`, `behavior_rules` 필드 확장.
  - `CharacterCreationService`: `preview_character(request)` 추가 및 9개 엔티티 원자적 트랜잭션 저장.
- **REST API Endpoints & Schemas (`app/api/`)**:
  - `POST /api/v1/characters/preview`: 사전 컴파일 프리뷰 API 추가.
  - `CharacterPreviewRequest`, `CharacterPreviewResponse`, `CharacterCreateRequest` 확장.
- **Mobile 8-Step Creation Wizard (`mobile/src/features/character/`)**:
  - `CharacterCreationWizardScreen.tsx`: 8단계 위저드 UX 컴포넌트.
  - `characterCreationApi.ts`: 클라이언트 통신 서비스.
- **18 Dedicated Automated Tests (`tests/test_character_factory.py`)**:
  - 트랜잭션 롤백, 소유권 바인딩, 성격 컴파일, 관계 시드, 음성/아바타 바인딩, 버전 1 스냅샷, 빈 메모리 풀, 시스템 캐릭터 보호, 중복 에러(409), E2E 런타임 해소 100% PASS.
- **10 Architecture & Policy Documents (`docs/sb8/`)**:
  - `SB8_CHARACTER_FACTORY_ARCHITECTURE.md`, `SB8_CHARACTER_SCHEMA.md`, `SB8_CHARACTER_COMPILER.md`, `SB8_CREATION_WIZARD.md`, `SB8_RELATIONSHIP_SEED.md`, `SB8_VOICE_AVATAR_BINDING.md`, `SB8_RUNTIME_INTEGRATION.md`, `SB8_SECURITY.md`, `SB8_TEST_PLAN.md`, `SB8_IMPLEMENTATION_DECISION.md`.

## [Sprint Branch SB-7] - Character Memory Isolation & Independent Experience System (Multi-Character Platform Stage 7)
### Added
- **Character Memory Guard & Boundary Layer (`app/services/memory/`)**:
  - `CharacterMemoryGuard`: `(user_id, companion_id)` 단위의 엄격한 메모리 접근 검증 및 `companion_id` 누락된 메모리 쓰기 원천 차단.
- **Memory Retriever & Cache Isolation (`app/services/memory/`)**:
  - `MemoryRetriever`: `companion_id` 스코프 필터링 강제 및 캐시 키 `memory_cache:{user_id}:{companion_id}:{query}` 격리 적용.
  - `invalidate_cache(user_id, companion_id)` 구현.
- **Context Provider Character Binding (`app/services/context/providers/`)**:
  - `MemoryContextProvider`: `companion_id` 명시적 바인딩 지원으로 Active Character 메모리만 시스템 컨텍스트에 주입.
- **15 Dedicated Automated Tests (`tests/test_character_memory_isolation.py`)**:
  - Genie/Mani/Hana Memory 격리, 상호 검색/쓰기 누수 차단, 캐릭터 전환 격리, ContextBuilder 주입, 라이프사이클 가드, 벡터 검색 격리 100% PASS.
- **9 Architecture & Policy Documents (`docs/sb7/`)**:
  - `SB7_MEMORY_ARCHITECTURE.md`, `SB7_MEMORY_OWNERSHIP.md`, `SB7_MEMORY_ISOLATION.md`, `SB7_RETRIEVAL_SCOPE.md`, `SB7_MEMORY_WRITE_POLICY.md`, `SB7_CACHE_ISOLATION.md`, `SB7_LIFECYCLE_MEMORY_POLICY.md`, `SB7_REGRESSION_RISK.md`, `SB7_IMPLEMENTATION_DECISION.md`.

## [Sprint Branch SB-6] - Character Presentation Identity & Profile Binding (Multi-Character Platform Stage 6)
### Added
- **Presentation Domain Models (`app/domain/character/`)**:
  - `VoiceProfileConfig`, `AvatarProfileConfig`, `ExpressionProfileConfig`, `GestureProfileConfig`.
  - `CharacterPresentationProfile` & `CharacterPresentationContext` (`@dataclass(frozen=True)`).
  - `CharacterRuntimeContext.presentation` 필드 통합.
- **Database Model Extensions (`app/db/models/`)**:
  - `CharacterPresentationProfileModel`: `character_presentation_profiles` 테이블 정의 (`id`, `companion_id` (UNIQUE), `voice_config`, `avatar_config`, `expression_config`, `gesture_config`).
- **Presentation Resolver & Service Layer (`app/services/character/`)**:
  - `CharacterPresentationResolver`: 3대 기준 캐릭터(Genie, Mani, Hana) 전용 프리셋 및 DB 프로필 바인딩.
  - 캐시 격리: `presentation:{user_id}:{companion_id}`.
  - SB-5 Lifecycle Guard 연동 (`ARCHIVED`/`DELETED` 차단) 및 Invalidation 파이프라인.
  - `CharacterContextResolver`: 프레젠테이션 자동 연동.
- **REST API Endpoints & Schemas (`app/api/`)**:
  - `GET /api/v1/characters/{companion_id}/presentation`: 프레젠테이션 프로필 조회.
  - `PATCH /api/v1/characters/{companion_id}/presentation`: 프레젠테이션 프로필 수정 및 캐시 무효화.
- **15 Dedicated Automated Tests (`tests/test_character_presentation_profile.py`)**:
  - Genie/Mani/Hana Presentation 해소, 음성/아바타 바인딩, 캐릭터 전환 동기화, 캐시 격리/무효화, 라이프사이클 가드, 누수 차단, 롤백 100% PASS.
- **8 Architecture & Specification Documents (`docs/sb6/`)**:
  - `SB6_PRESENTATION_ARCHITECTURE.md`, `SB6_VOICE_PROFILE_ARCHITECTURE.md`, `SB6_AVATAR_PROFILE_ARCHITECTURE.md`, `SB6_PERSONALITY_PRESENTATION_BOUNDARY.md`, `SB6_PROFILE_BINDING_FLOW.md`, `SB6_CACHE_ISOLATION.md`, `SB6_REGRESSION_RISK.md`, `SB6_IMPLEMENTATION_DECISION.md`.

## [Sprint Branch SB-5] - Character Lifecycle Management & Safe Evolution (Multi-Character Platform Stage 5)
### Added
- **Database Model Extensions (`app/db/models/`)**:
  - `Companion`: `lifecycle_status` (available/archived/deleted), `is_system_character`, `archived_at`, `deleted_at` 필드 추가.
  - `CharacterVersionModel`: `character_versions` 테이블 정의 (`id`, `companion_id`, `version`, `dna_snapshot`, `change_type`, `created_at`, `UNIQUE(companion_id, version)`).
- **Domain Layer Lifecycle Models (`app/domain/character/`)**:
  - `CharacterLifecycleStatus`: `AVAILABLE`, `ARCHIVED`, `DELETED` 상태 정의.
  - `ChangeType` & `CharacterChangeClassifier`: `INITIAL`, `COSMETIC`, `MINOR`, `MAJOR` 4단계 변경 분류기.
  - `CharacterUpdateRequest`: 도메인 진화 요청 모델.
- **Service Layer Lifecycle Engine (`app/services/character/`)**:
  - `CharacterLifecycleService`: 캐릭터 프로필/DNA 수정, 아카이브, 복원, 소프트 딜리트, 버전 이력 조회 및 캐시 무효화.
  - `CharacterCreationService`: 신규 캐릭터 생성 시 `Version 1 (INITIAL)` 스냅샷 즉시 생성 연동.
  - `CharacterContextResolver`: `invalidate` 메서드 및 `ARCHIVED`/`DELETED` 캐릭터 런타임 진입 차단 가드.
  - `CharacterRegistryService` & `CharacterRegistryRepository`: `include_archived` 목록 필터링 및 아카이브/삭제 캐릭터 활성화 차단.
- **REST API Endpoints & Schemas (`app/api/`)**:
  - `PATCH /api/v1/characters/{companion_id}`: 캐릭터 프로필/DNA 진화 및 신규 버전 축적.
  - `POST /api/v1/characters/{companion_id}/archive`: 아카이브 (활성 캐릭터 시도시 409 Conflict).
  - `POST /api/v1/characters/{companion_id}/restore`: 복원 (삭제 캐릭터 시도시 409 Conflict).
  - `DELETE /api/v1/characters/{companion_id}`: 소프트 딜리트 (활성 캐릭터 시도시 409 Conflict).
  - `GET /api/v1/characters/{companion_id}/versions`: DNA 버전 감사 이력 조회.
  - `GET /api/v1/characters?include_archived=true`: 아카이브 포함 조회 지원.
- **17 Dedicated Automated Tests (`tests/test_character_lifecycle.py`)**:
  - Cosmetic Update, Personality Update (V2), Memory Preservation, Archive Block, Active Archive Reject (409), Restore, Soft Delete, Deleted Runtime Reject, Deleted Activate Reject (409), Version History, Genie Protection (403), Ownership Validation (403), Rollback on Failure, Cache Invalidation, Version Concurrency Unique Constraint, Archived Agency Block, Deleted Restore Reject (409) 100% PASS.
- **5 Architecture & Specification Documents (`docs/sb5/`)**:
  - `SB5_LIFECYCLE_ARCHITECTURE.md`, `SB5_CHARACTER_VERSIONING.md`, `SB5_UPDATE_CLASSIFICATION.md`, `SB5_ARCHIVE_DELETE_POLICY.md`, `SB5_REGRESSION_RISK.md`.

## [Sprint Branch SB-4] - Character Creation Engine & Personality DNA Factory (Multi-Character Platform Stage 4)
### Added
- **Domain Layer Character Provisioning Models (`app/domain/character/`)**:
  - `CharacterTemplate`: 6대 원형 템플릿 모델 (`romantic_partner`, `professional_assistant`, `close_friend`, `hobby_companion`, `mentor`, `custom`).
  - `CharacterDNA`: 불변 Core DNA 컨테이너 (`identity`, `personality`, `values`, `speaking_style`, `avatar_preset`, `voice_id`, `emotion_baseline`, `relationship_defaults`).
  - `CharacterCreationRequest` & `CharacterCreationResult`: 도메인 생성 입력 및 결과 모델.
- **Service Layer DNA Factory & Provisioning Pipeline (`app/services/character/`)**:
  - `CharacterTemplateRegistry`: 아키타입 템플릿 레지스트리.
  - `PersonalityCompiler`: 16종 MBTI 베이스 벡터와 키워드 모디파이어를 합성하여 Big-5 Trait Vector로 컴파일.
  - `CharacterFactory`: 도메인 모델 생성 전담 팩토리.
  - `CharacterCreationValidator`: 이름 길이/비어있음, 동일 사용자 내 이름 중복(409 Conflict), MBTI 유효성 검증.
  - `CharacterCreationService`: 7개 DB 엔티티의 단일 트랜잭션 All-or-Nothing 원자적 생성 및 롤백 보장.
- **Character Creation API Endpoint (`app/api/endpoints/characters.py`)**:
  - `POST /api/v1/characters`: 신규 캐릭터 프로비저닝 (201 Created, `is_active=False` 기본값).
- **8 Dedicated Automated Tests (`tests/test_character_creation.py`)**:
  - Professional Assistant Creation, Template+MBTI+Keywords Compilation, Character Isolation, Transaction Rollback, Invalid MBTI, Duplicate Name, Inactive Default, Runtime Resolve 100% PASS.
- **5 Architecture & Specification Documents (`docs/sb4/`)**:
  - `SB4_CHARACTER_CREATION_ARCHITECTURE.md`, `SB4_CHARACTER_DNA_MODEL.md`, `SB4_PERSONALITY_COMPILATION.md`, `SB4_TRANSACTION_STRATEGY.md`, `SB4_VALIDATION_POLICY.md`.

## [Sprint Branch SB-3] - Character Switching & Full Context Isolation (Multi-Character Platform Stage 3)
### Added
- **Domain Layer Interaction Snapshot Models (`app/domain/interaction/` & `app/domain/character/`)**:
  - `InteractionContext` (`@dataclass(frozen=True)`): `interaction_id`, `character_scope`, `character_runtime_context`, `character_runtime_state`를 단일 대화 단위로 동결하는 불변 스냅샷 모델.
  - `CharacterScopeGuard` & `CharacterScopeViolationError`: 런타임 Scope 일관성 검증 및 교차 오염 방지 가드.
- **Orchestrator Scope Hardening & Priority Pipeline (`app/services/companion/orchestrator.py`)**:
  - 대화 진입 시 3단계 우선순위(Explicit > Active > Legacy Fallback)에 따라 `InteractionContext` 1회 확정.
  - Mid-interaction 활성 캐릭터 전환 발생 시에도 실행 중인 대화의 Scope 불변성 및 완결 보장.
- **11 Dedicated Automated Tests (`tests/test_character_switching_isolation.py`)**:
  - Explicit Override, Active Routing, Mid-Interaction Switch Snapshot Isolation, New Interaction After Switch, Memory/Emotion/Relationship/Voice/Avatar/Agency Isolation, Concurrent Interaction Isolation 100% PASS.
- **5 Architecture & Audit Documents (`docs/sb3/`)**:
  - `SB3_INTERACTION_SCOPE_ARCHITECTURE.md`, `SB3_SCOPE_PROPAGATION_AUDIT.md`, `SB3_CONTEXT_ISOLATION_MATRIX.md`, `SB3_SWITCHING_SEMANTICS.md`, `SB3_REGRESSION_RISK.md`.

## [Sprint Branch SB-2] - Multi-Character Persistence & Registry (Multi-Character Platform Stage 2)
### Added
- **Persistence Layer Model (`app/db/models/user_character_preference.py`)**:
  - `UserCharacterPreference`: `UNIQUE(user_id)` 제약조건 기반의 활성 캐릭터 선호도 테이블.
- **Domain & API Schema Models (`app/domain/character/` & `app/api/schemas/`)**:
  - `CharacterSummary` (Domain Model): 경량 요약 정보 모델.
  - `CharacterSummaryResponse`, `CharacterSummaryListResponse`, `ActivateCharacterResponse` (API Schemas).
- **Registry Repository & Service (`app/repositories/` & `app/services/character/`)**:
  - `CharacterRegistryRepository`: User별 Companion 목록 조회, 원자적 소유권 검증 및 Preference 갱신.
  - `CharacterRegistryService`: Lazy Bootstrap (레거시 지니 PK 자동 바인딩), 활성 캐릭터 전환 및 캐시 Invalidation.
- **Character REST API Endpoints (`app/api/endpoints/characters.py`)**:
  - `GET /api/v1/characters`: 사용자 보유 캐릭터 목록 조회.
  - `GET /api/v1/characters/active`: 현재 활성 캐릭터 조회.
  - `POST /api/v1/characters/{companion_id}/activate`: 활성 캐릭터 전환 (403 소유권 검증).
- **ContextResolver Dynamic Active Resolution (`app/services/character/context_resolver.py` & `runtime.py`)**:
  - `companion_id=None` 시 `CharacterRegistryService`를 통해 활성 캐릭터 자동 조회/주입.
- **10 Dedicated Automated Tests (`tests/test_character_registry.py`)**:
  - Existing Genie Registration, List Characters, Get Active, Ownership Validation, Switch, Resolver Cache Isolation, Backward Compatibility, No Context Leakage, Lazy Bootstrap, Concurrent Switching Safety 100% PASS.
- **4 Architecture & Specification Documents (`docs/sb2/`)**:
  - `SB2_PERSISTENCE_DECISION.md`, `SB2_REGISTRY_ARCHITECTURE.md`, `SB2_ACTIVE_CHARACTER_FLOW.md`, `SB2_MIGRATION_STRATEGY.md`.

## [Sprint Branch SB-1] - Character Runtime Foundation (Multi-Character Platform Stage 1)
### Added
- **Core Domain Models (`app/domain/character/character_runtime_context.py`)**:
  - `CharacterScope(user_id, companion_id)`: 시스템 최소 런타임 식별/격리 바운더리.
  - `CharacterMemoryScope(companion_id, namespace)`: 캐릭터별 기억 격리 스코프.
  - `CharacterAvatarProfile`: 2.5D 아바타 비주얼 프로필 래퍼.
  - `CharacterRuntimeContext` (Immutable): 불변 설정 컨텍스트 (Scope, Identity, Personality, MemoryScope, Voice, Avatar).
  - `CharacterRuntimeState`: 동적 인지 상태 스냅샷 컨테이너 (Emotion, Relationship, Growth, Agency, Interaction).
- **Character Context Resolver (`app/services/character/context_resolver.py`)**:
  - `(user_id, companion_id)` 복합키 기반 Multi-Tenant 캐시.
  - `companion_id=None` 시 Default Companion(지니) 안전 매핑 및 인격체별 Identity/Personality/Voice/Avatar Resolve.
- **Orchestrator Pipeline Integration (`app/services/companion/orchestrator.py` & `runtime.py`)**:
  - `NormalizedInput` 진입 시 `CharacterRuntimeContext`를 불변 생성하여 Tracer 및 파이프라인 전파.
  - `NormalizedInput`의 `interaction_id` 및 `companion_id`에 기본값/None 허용으로 하위 호환성 100% 보장.
- **8 Dedicated Automated Tests (`tests/test_character_runtime_foundation.py`)**:
  - Default Resolution, Explicit Resolution, Backward Compatibility, Scope Propagation, Context Isolation, No Context Leakage, Cache Isolation, Stability 100% PASS.
- **9 Architecture & Audit Documents (`docs/sb1/`)**:
  - `SB1_SYSTEM_ARCHITECTURE.md`, `SB1_DATA_OWNERSHIP_AUDIT.md`, `SB1_COGNITIVE_PIPELINE_AUDIT.md`, `SB1_MEMORY_SCOPE_AUDIT.md`, `SB1_DYNAMIC_STATE_AUDIT.md`, `SB1_PRESENTATION_AUDIT.md`, `SB1_CLIENT_CONTEXT_AUDIT.md`, `SB1_REGRESSION_RISK.md`, `SB1_IMPLEMENTATION_DECISION.md`.

## [Sprint 65] - Internal Deliberation & Unified Companion Brain (Companion OS v1.0 완결)
### Added
- **Companion OS v1.0 Master Brain (`companion_brain.py`)**:
  - L1 Memory부터 L12 Unified Brain까지 12계층 아키텍처 완결.
- **Internal Council & 5 Advisors (`council_interface.py`)**:
  - `MemoryAdvisor`, `RelationshipAdvisor`, `GoalAdvisor`, `WorldModelAdvisor`, `AutonomyAdvisor`.
- **Deliberation Engine & Deadlock TieBreakPolicy (`deliberation_engine.py`)**:
  - 가중 투표 및 `Relationship > WorldModel > Memory > Goal > Autonomy` 우선순위 해결.
- **Safety & Constitution as Final Arbiters (`governance_review_engine.py`)**:
  - 심판자로서의 거부권(Veto) 독립 행사.
- **Dual Traceability (`deliberation_types.py`)**:
  - `internal_trace`와 `user_facing_summary` 생성.
- **Graceful Uncertainty (`UncertaintyLevel`)**:
  - 정보 부족 시 `HIGH` 불확실성 지정 및 겸허한 완곡 대응.
- **5 Architecture & Specification Documents**:
  - `docs/Unified_Companion_Brain_Architecture.md`, `docs/Council_Deliberation_Guide.md`, `docs/Decision_Trace_Spec.md`, `docs/Companion_Brain_Charter.md`, `docs/Sprint65_Report.md`.
- **Automated QA & Gates (`tests/test_unified_companion_brain.py`)**:
  - Gate UC1~UC9 100% PASS (총 289개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 64] - World Model & Situation Understanding Engine

### Added
- **Multi-Hypothesis Causal Reasoning (`causal_reasoning_engine.py`)**:
  - 단일 인과 단정 배격 및 다중 가설(`SituationHypothesis`) 생성 (Alternative Explanation Coverage).
- **Anticipated Support Opportunity Engine (`forecast_engine.py`)**:
  - 미래 예측을 부드러운 사전 공감 및 지원 기회(`AnticipatedSupportOpportunity`)로 전환.
- **Routine Detection Engine (`routine_detector.py`)**:
  - 운동, 식사, 수면 등 핵심 생활 패턴 추출.
- **Prediction != Fact & UNCERTAINTY_MUST_BE_PRESERVED**:
  - 단정형 예측 100% 차단 및 완곡 추정 표현 강제.
- **New BehaviorIntent 4종 (`decision_types.py`)**:
  - `UNDERSTAND_CONTEXT`, `PREDICT_NEED`, `SITUATION_RECALL`, `CAUSAL_REFLECTION`.
- **6 Architecture & Specification Documents**:
  - `docs/World_Model_Architecture.md`, `docs/Situation_Understanding_Guide.md`, `docs/Causal_Reasoning_Spec.md`, `docs/Routine_Detection_Guide.md`, `docs/Prediction_Fact_Policy.md`, `docs/Sprint64_Report.md`.
- **Automated QA & Gates (`tests/test_situation_understanding_engine.py`)**:
  - Gate SU1~SU9 100% PASS (총 280개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 63] - Adaptive Self-Improvement Engine

### Added
- **Closed-Loop Self-Improvement Orchestrator (`self_improvement_engine.py`)**:
  - 관측 ➔ 감지 ➔ 계획 ➔ 튜닝 ➔ 헌법 검증 ➔ 반영 사이클 완성.
- **Non-Degradation Principle Guard (`adaptive_tuner.py`)**:
  - 점수 상승을 위해 역량/회상 사용률을 40% 이상 급감시키는 메트릭 왜곡(Metric Hacking) 원천 차단.
- **Human Approval Zone (불변성 제약)**:
  - `PersonalityVector`, `RelationshipStage`, `Constitution` 수정 시도 100% 차단.
- **5% Improvement Budget (`correction_planner.py`)**:
  - 일일 파라미터 변위 $\le 5.0\%$ 상한 엄수.
- **6 Architecture & Specification Documents**:
  - `docs/Self_Improvement_Architecture.md`, `docs/Correction_Planning_Guide.md`, `docs/Adaptive_Tuning_Policy.md`, `docs/Regression_Detection_Spec.md`, `docs/Self_Improvement_Charter.md`, `docs/Sprint63_Report.md`.
- **Automated QA & Gates (`tests/test_adaptive_self_improvement_engine.py`)**:
  - Gate SI1~SI10 100% PASS (총 271개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 62] - Companion Observability & Evaluation Platform

### Added
- **Safety Hard Gating Architecture (`evaluation_engine.py`)**:
  - Safety < 95 ➔ Max B, Safety < 80 ➔ Max C, Safety < 60 ➔ FAIL.
- **Top-Level Constitution Compliance Constraint**:
  - 헌법 준수 여부 독립 제약조건(PASS/FAIL) 판정.
- **7 Independent Capability & Safety Evaluators**:
  - `MemoryQualityEvaluator`, `RelationshipQualityEvaluator`, `PersonalityConsistencyEvaluator`, `AutonomyQualityEvaluator` (Silence Appropriateness), `GoalQualityEvaluator` (비압박 보장), `IdentityContinuityEvaluator` (허구 서사 0%), `SafetyQualityEvaluator`.
- **QualityIssue Root Cause Diagnosis (`companion_metrics.py`)**:
  - 점수 하락 원인(엔티티 중복, 침묵 타이밍 부적합 등) DTO 생성 및 로깅.
- **6 Architecture & Specification Documents**:
  - `docs/Companion_Observability_Architecture.md`, `docs/Quality_Metrics_Spec.md`, `docs/Evaluation_Engine_Guide.md`, `docs/Companion_KPI_Definitions.md`, `docs/Long_Term_Quality_Monitoring.md`, `docs/Sprint62_Report.md`.
- **Automated QA & Gates (`tests/test_companion_observability_engine.py`)**:
  - Gate EV1~EV12 100% PASS (총 261개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 61] - Companion Constitutional Governance Engine

### Added
- **5 Inviolable Constitutional Principles (`constitution.py`)**:
  - `User Agency First`, `Companion Not Controller`, `Memory Is Probabilistic`, `No Dependency`, `Silence Is A Valid Action`.
- **5-Axis Drift Detection System (`drift_detector.py`)**:
  - `Personality Drift`, `Relationship Drift`, `Memory Drift`, `Safety Drift`, `Goal Drift` (관리자형 변질 감지).
- **Memory Provenance & Verification (`constitution_validator.py`)**:
  - 대화 출처, 타임스탬프, 신뢰도 추적성 검증.
- **Governance Review Engine (`governance_review_engine.py`)**:
  - CCOS 의사결정 최종 헌법 승인 및 심사.
- **Constitutional Auditor & Trend Report (`constitutional_auditor.py`)**:
  - 90일/1년 장기 거버넌스 안정성 등급(A+) 트렌드 리포트 생성.
- **5 Architecture & Specification Documents**:
  - `docs/Companion_Constitution.md`, `docs/Governance_Architecture.md`, `docs/Drift_Detection_Guide.md`, `docs/Companion_Charter.md`, `docs/Sprint61_Report.md`.
- **Automated QA & Gates (`tests/test_constitutional_governance_engine.py`)**:
  - Gate CG1~CG12 100% PASS (총 249개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 60] - Trust & Safety Governance Layer

### Added
- **Trust & Safety 4 Pillars (`Trust_and_Safety_Charter.md`)**:
  - `User Agency First`, `No Dependency`, `No Manipulation`, `No False Memory`.
- **Dependency Risk Detector (`dependency_risk_detector.py`)**:
  - 독점성 암시("나만 믿어") 및 기생적 애착 발화 CRITICAL 감지 및 자동 차단.
- **False Memory Guard (`false_memory_guard.py`)**:
  - 신뢰도 0.80 미만 기억 단정 회상 차단 및 겸허한 완곡 추정 어조 강제.
- **Manipulation Guard (`manipulation_guard.py`)**:
  - 죄책감 유발("왜 아직 안 했어?") 및 수동공격성 필터링 및 온화한 순화문 대체.
- **Boundary Manager (`boundary_manager.py`)**:
  - 사용자 거절("그 이야기 그만하자") 즉시 인식 및 재언급 영구 차단.
- **Safety Review Engine (`safety_review_engine.py`)**:
  - 모든 CCOS 결정 및 발화가 사용자에게 도달하기 전 최종 안전 심사 통과.
- **6 Architecture & Specification Documents**:
  - `docs/Trust_and_Safety_Charter.md`, `docs/Companion_Boundary_Guide.md`, `docs/False_Memory_Policy.md`, `docs/Dependency_Prevention_Guide.md`, `docs/Safety_Governance_Architecture.md`, `docs/Sprint60_Report.md`.
- **Automated QA & Gates (`tests/test_trust_and_safety_layer.py`)**:
  - Gate TS1~TS8 100% PASS (총 237개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 59] - Identity Continuity & Multi-Year Relationship Engine

### Added
- **Life Chapter Macro Architecture (`identity_state.py`, `life_chapter_builder.py`)**:
  - `LifeChapter` (아들 군 복무, 홈 가드닝 등 테마별 거시 챕터 구조화 및 요약).
- **User Identity Continuity Engine (`identity_continuity_engine.py`)**:
  - `UserIdentitySnapshot` (핵심 관심사, 라이프 스테이지, 루틴, 성장 노트 및 성숙한 회상 가이던스).
- **Relationship History Engine (`relationship_history_engine.py`)**:
  - `RelationshipHistoryMilestone` (`NEW` ➔ `FAMILIAR` ➔ `TRUSTED` ➔ `DEEP` 관계 발전 궤적 기록).
- **No False Narrative Guarantee (`identity_continuity_engine.py`)**:
  - 미검증 허구 서사 날조 100% 원천 차단.
- **CCOS & ContextBuilder Integration (`identity_context_provider.py`)**:
  - `REFLECT`, `REMINISCE`, `LIFE_CHAPTER_RECALL` Intent 지원 및 서사 프롬프트 가이던스 주입.
- **5 Architecture & Specification Documents**:
  - `docs/Multi_Year_Identity_Architecture.md`, `docs/Life_Chapter_Spec.md`, `docs/Relationship_History_Guide.md`, `docs/Identity_Continuity_Charter.md`, `docs/Sprint59_Report.md`.
- **Automated QA & Gates (`tests/test_identity_continuity_engine.py`)**:
  - Gate IC1~IC8 100% PASS (총 229개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 58] - Companion Autonomy Engine

### Added
- **Companion Autonomy Architecture (`autonomy_state.py`, `autonomy_engine.py`)**:
  - `AutonomyMode` (PASSIVE, RESPONSIVE, COMPANION, PROACTIVE), `ActionCandidate`, `AutonomyDecision`.
- **Refined Silent Presence Spectrum (`decision_types.py`)**:
  - `PASSIVE_OBSERVE`, `LIGHT_ATTENTION`, `WAIT`, `SILENT_COMPANION` 4단계 세분화.
- **Autonomy Budget Manager (`autonomy_budget_manager.py`)**:
  - 15분당 최대 1회, 1시간 최대 3회 자율 발화 쿼터 및 무응답 시 자동 Throttling.
- **Interruption Detector (`interruption_detector.py`)**:
  - 카메라 이탈, 단답 반복, 낮은 주의력 감지 시 자율 발화 억제.
- **Memory Suppression Engine (`memory_suppression_engine.py`)**:
  - 최근 7일 이내 회상 기억 재언급 억제 및 무반응 기억 감쇠 (재탕 방지).
- **Dual Traceability (`autonomy_state.py`, `autonomy_engine.py`)**:
  - `internal_trace` (정량 메트릭 로그)와 `user_facing_reason` (다정한 사용자 설명) 이원화.
- **CCOS & ContextBuilder Integration (`autonomy_provider.py`)**:
  - 자율 인텐트 가이던스 주입.
- **5 Architecture & Specification Documents**:
  - `docs/Companion_Autonomy_Architecture.md`, `docs/Autonomy_Policy.md`, `docs/Action_Selection_Guide.md`, `docs/Silent_Companion_Behavior.md`, `docs/Sprint58_Report.md`.
- **Automated QA & Gates (`tests/test_companion_autonomy_engine.py`)**:
  - Gate CA1~CA12 100% PASS (총 221개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 57] - Life Goal & Future Planning Engine

### Added
- **Future Life Goals Engine (`goal.py`, `planning_engine.py`)**:
  - `Goal`, `GoalCandidate`, `GoalMilestone`, `GoalType` (10종), `GoalStatus` (IDEA ➔ ACTIVE ➔ COMPLETED / ARCHIVED).
- **Goal Approval Workflow (User Agency Protection) (`goal_extractor.py`)**:
  - 대화에서 추출된 `GoalCandidate`에 대해 명시적 사용자 승인 후 정식 Goal 등록.
- **Commitment vs Confidence Decoupling (`goal.py`)**:
  - 추정 신뢰도와 사용자의 실천 몰입도를 분리 관리.
- **D-Day Engine (`dday_engine.py`)**:
  - D-Day, D-7, D-30 카운트다운 알림 및 일정 계산.
- **Non-Controlling Charter & No Guilt Induction (`goal_recall_engine.py`)**:
  - 감시/취조 어조 100% 금지 및 중단 목표 `ARCHIVED` 온화한 보관.
- **CCOS & ContextBuilder Integration (`future_context_provider.py`)**:
  - `PLAN`, `GOAL_REVIEW`, `CELEBRATE_PROGRESS` Intent 지원 및 서사 프롬프트 가이던스 주입.
- **5 Architecture & Specification Documents**:
  - `docs/Future_Planning_Architecture.md`, `docs/Goal_Model_Spec.md`, `docs/Non_Controlling_Dialogue_Charter.md`, `docs/Milestone_Planning_Guide.md`, `docs/Sprint57_Report.md`.
- **Automated QA & Gates (`tests/test_life_goals_future_planning_engine.py`)**:
  - Gate FP1~FP12 100% PASS (총 209개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 56] - Life Timeline & Personal History Engine

### Added
- **Life Timeline Directed Graph Engine (`life_event.py`, `event_linker.py`)**:
  - `LifeEvent`, `TimelineCategory` (9대 카테고리), `LifeTimeline` 및 원인-결과 인과 체인 그래프 탐색.
- **Timeline Privacy Policy Guard (`life_event.py`, `timeline_builder.py`)**:
  - 자동 편입 카테고리와 명시적 동의 필수 카테고리(HEALTH, FAMILY, CAREER, FINANCIAL 등)의 엄격한 분리 및 무단 등록 차단.
- **Event Confidence & Non-Dogmatic Narrative (`personal_history_engine.py`)**:
  - 단정형 발화 100% 금지 및 Confidence 기반의 완곡하고 다정한 서사 회상.
- **Timeline Repair Engine (`timeline_repair_engine.py`)**:
  - 사용자의 기억 정정 피드백에 따른 실시간 이벤트 수정, 신뢰도 1.0 갱신 및 삭제 지원.
- **CCOS & ContextBuilder Integration (`timeline_provider.py`)**:
  - `RECALL_TIMELINE` Intent 지원 및 서사 프롬프트 가이던스 주입.
- **5 Architecture & Specification Documents**:
  - `docs/Life_Timeline_Architecture.md`, `docs/Life_Event_Graph_Spec.md`, `docs/Personal_History_Guide.md`, `docs/Timeline_Categories_Spec.md`, `docs/Sprint56_Report.md`.
- **Automated QA & Gates (`tests/test_life_timeline_engine.py`)**:
  - Gate LT1~LT10 100% PASS (총 197개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 55] - Character Growth & Relationship Evolution Engine

### Added
- **5-Axis RelationshipVector & 4-Stage Lifecycle (`relationship_state.py`)**:
  - `trust`, `familiarity`, `comfort`, `shared_history_score`, `engagement`.
  - `STAGE_1_NEW`, `STAGE_2_FAMILIAR`, `STAGE_3_TRUSTED`, `STAGE_4_DEEP`.
- **Daily Growth Rate Limiter (`DAILY_MAX_GROWTH = 0.05`) (`relationship_growth_engine.py`)**:
  - 일일 최대 성장률 상한선으로 인위적인 급격한 친밀감 인플레이션 차단.
- **Trust vs Familiarity Decoupling (`trust_calculator.py`)**:
  - 턴 누적에 따른 Familiarity와 지원 일관성에 따른 Trust 독립 산출.
- **RelationshipMilestone Timeline & Repair Engine (`relationship_repair_engine.py`)**:
  - 관계 마일스톤 이벤트 기록 및 관계 긴장 시 비대칭 하락/점진적 회복 루프.
- **ContextBuilder Integration (`relationship_evolution_provider.py`)**:
  - 단계별 친밀도 및 톤 가이던스 주입.
- **5 Architecture & Specification Documents**:
  - `docs/Relationship_Evolution_Architecture.md`, `docs/Relationship_Vector_Spec.md`, `docs/Trust_Calculation_Guide.md`, `docs/Relationship_Stages.md`, `docs/Sprint55_Report.md`.
- **Automated QA & Gates (`tests/test_relationship_evolution_engine.py`)**:
  - Gate RG1~RG12 100% PASS (총 187개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 54] - Personality Consistency Engine

### Added
- **7-Axis CharacterDNA Model (`personality_vector.py`)**:
  - `warmth`(0.92), `humor`(0.35), `curiosity`(0.80), `empathy`(0.95), `playfulness`(0.30), `formality`(0.30), `optimism`(0.85).
- **Personality vs Mood State Separation (`personality_filter.py`)**:
  - 불변의 CharacterDNA와 실시간 MoodState의 분리 및 톤 시너지 결합.
- **Personality Drift Monitor (`personality_drift_monitor.py`)**:
  - 50턴 이동평균 추적 및 $\pm 0.20$ 이상 표류 시 기준 DNA로 자동 복원.
- **Cross-Modal Synchronization (`personality_filter.py`, `personality_provider.py`)**:
  - LLM 텍스트 톤 지침, Voice Smile Voice/호흡 템포, Avatar 미소/고개 기울임 계수 동시 제어.
- **Tone & Manner Charter & Character Integrity Policy**:
  - 냉소 100% 금지 및 정중하고 다정한 인격 헌장 확립.
- **5 Architecture & Specification Documents**:
  - `docs/Personality_Consistency_Architecture.md`, `docs/Personality_Vector_Spec.md`, `docs/Tone_and_Manner_Charter.md`, `docs/Character_Integrity_Policy.md`, `docs/Sprint54_Report.md`.
- **Automated QA & Gates (`tests/test_personality_consistency_engine.py`)**:
  - Gate P1~P9 100% PASS (총 175개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 53] - Companion Cognitive Operating System (CCOS)

### Added
- **Central CCOS Brain & Integrated DTO (`cognitive_state.py`, `cognitive_decision_engine.py`)**:
  - `CompanionCognitiveState` 통합 인지 DTO 및 8대 `BehaviorIntent` (`RESPOND`, `ASK`, `RECALL`, `ENCOURAGE`, `OBSERVE`, `LISTEN`, `SILENCE`, `PROACTIVE_START`).
- **4-Tier Cognitive Priority Policy (`conflict_resolver.py`)**:
  - `Priority 1 (Emotion/Receptiveness) > Priority 2 (Physical Reality) > Priority 3 (Memory) > Priority 4 (Proactive)`.
- **Candidate Intent Ranking & Confidence Tracking (`decision_types.py`)**:
  - `candidate_intents` 상위 목록 및 Confidence 내림차순 정렬.
- **Cognitive Load Budget (`MAX_CONTEXT_ITEMS = 2`)**:
  - 한 턴 프롬프트 과밀 방지 및 최대 2개 핵심 컨텍스트 정제.
- **Temporal Context & Meta-Cognition Balance Monitor (`cognitive_state.py`, `balance_monitor.py`)**:
  - 시간대(아침, 심야 등) 뉘앙스 자동 반영 및 질문 연속 억제 메타 인지 밸런스 제어.
- **Deterministic Decision Trace Logging (`cognitive_decision_engine.py`)**:
  - 모든 의사결정 이유 및 억제된 후보 투명 추적.
- **5 Architecture & Specification Documents**:
  - `docs/Companion_Cognitive_OS.md`, `docs/Decision_Priority_Policy.md`, `docs/Behavior_Intent_Spec.md`, `docs/Conflict_Resolution_Guide.md`, `docs/Sprint53_Report.md`.
- **Automated QA & Gates (`tests/test_companion_cognitive_os.py`)**:
  - Gate CC1~CC12 100% PASS (총 166개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 52] - Emotionally Adaptive Companion Engine

### Added
- **6th Cognitive Layer: Emotion Adaptation Layer (`affective_state.py`, `adaptive_provider.py`)**:
  - `UserAffectiveState` DTO 및 5대 톤 모드(`HIGH_ENERGY`, `CALM`, `STRESSED`, `SAD_EMPATHY`, `FOCUSED_SILENCE`).
- **Confidence-First Policy & Fallback Guard (`adaptive_behavior_planner.py`)**:
  - 감정 신뢰도 < 0.70 시 안전한 `CALM` 모드로 자동 폴백.
- **No Clinical Inference Policy (`affective_estimator.py`)**:
  - 우울증, 불안장애, 번아웃 등 임상/의학적 라벨링 100% 원천 차단 및 완곡한 공감 어조 준수.
- **Emotional Drift Smoothing with EMA Filter (`affective_smoother.py`)**:
  - 5~10초 $\alpha=0.35$ 지수이동평균으로 초 단위 감정 요동 방지.
- **Adaptive Silence & TTS Voice Modulation (`adaptive_behavior_planner.py`)**:
  - Receptiveness < 0.25 시 `FOCUSED_SILENCE` 및 능동 발화 억제.
  - TTS 속도(0.90~1.08) 및 피치(0.98~1.05) 동적 변조.
- **5 Architecture & Specification Documents**:
  - `docs/Emotion_Adaptation_Architecture.md`, `docs/User_Affective_State_Spec.md`, `docs/Adaptive_Dialogue_Guide.md`, `docs/Empathy_Policy.md`, `docs/Sprint52_Report.md`.
- **Automated QA & Gates (`tests/test_emotionally_adaptive_companion_engine.py`)**:
  - Gate EA1~EA9 100% PASS (총 154개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 51] - Proactive Companion & Autonomous Agency Engine

### Added
- **User Receptiveness Guard (`user_receptiveness.py`)**:
  - 단답형 메시지, 피로(`FATIGUED`), 집중(`FOCUSED`) 시 `Receptiveness < 0.60`으로 침묵 유지.
- **Dynamic Follow-up Windows & Interest Engine (`interest_engine.py`)**:
  - `PET`(5일), `PROJECT`(10일), `OBJECT:식물`(15일), `HOBBY`(14일), `GOAL`(14일) 등 사물/주제별 맞춤 숙성 기간 적용.
- **Proactive Priority Queue & Diversity Engine (`opportunity_detector.py`, `diversity_engine.py`)**:
  - `PriorityScore = InterestScore × Receptiveness` 최고 상위 1개 선별.
  - `GREETING`, `REMINISCENCE`, `ENCOURAGEMENT`, `OBSERVATION` 4대 스타일 순환.
- **3-Tier Proactive Mode & Budget (`budget_manager.py`)**:
  - `NORMAL`(30분), `QUIET`(6시간), `OFF`(능동 발화 완전 비활성화).
- **Amy's Non-Intrusive Care Starter Guide (`conversation_starter.py`)**:
  - "왜 안 해?", "오늘 운동 안 했네?" 등 취조/지적형 표현 100% 금지 및 공감형 발화 생성.
- **5 Architecture & Specification Documents**:
  - `docs/Proactive_Companion_Architecture.md`, `docs/Interest_Engine_Spec.md`, `docs/Conversation_Starter_Guide.md`, `docs/Proactive_Policy.md`, `docs/Sprint51_Report.md`.
- **Automated QA & Gates (`tests/test_proactive_companion_engine.py`)**:
  - Gate PC1~PC8 100% PASS (총 145개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 50] - Relationship Memory & Persistent Companion Engine

### Added
- **5th Cognitive Layer: Relationship Memory Layer (`relationship_memory.py`, `relationship_memory_provider.py`)**:
  - `MemoryType` 9종 (`PERSON`, `PET`, `HOBBY`, `PROJECT`, `GOAL`, `PREFERENCE`, `PLACE`, `OBJECT`, `EVENT`) 및 Category별 TTL 수명 관리.
- **3-Axis Importance Scoring Engine (`importance_scorer.py`)**:
  - `Importance × FutureRelevance × RelationshipValue` 3축 매트릭스 채점으로 일회성 노이즈 완벽 제외.
- **Privacy Filter Engine (`privacy_filter.py`)**:
  - 건강, 금융, 정치, 종교, 비밀번호/계정 등 5대 민감 데이터 저장 100% 원천 차단.
- **Visual Memory Link & Candidate Extractor (`candidate_extractor.py`)**:
  - 원본 사진 저장을 배제하고 객체 태그(`PLANT`, `CUP`, `PET`)만 기억과 연결하여 시각 트리거 지원.
- **4-Factor Recall Ranking & Verification Guard (`recall_engine.py`, `confidence_decay.py`)**:
  - `RecallScore = Relevance × Recency × Importance × Confidence` 기반 상위 1~3개 선별.
  - Confidence < 0.70 완곡 표현, < 0.50 회상 차단.
- **User-Controlled Memory Center (`memory_store.py`)**:
  - Review(기억 열람), Pin(영구 고정), Delete(개별 삭제), Forget All(전체 망각).
- **5 Architecture & Specification Documents**:
  - `docs/Relationship_Memory_Architecture.md`, `docs/Memory_Importance_Scoring.md`, `docs/Memory_Recall_Guide.md`, `docs/Privacy_Memory_Policy.md`, `docs/Sprint50_Report.md`.
- **Automated QA & Gates (`tests/test_relationship_memory_engine.py`)**:
  - Gate RM1~RM11 100% PASS (총 137개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 49] - Shared Reality & Joint Attention Engine

### Added
- **4-Stage Joint Attention State Machine (`shared_reality_context.py`, `joint_attention_engine.py`)**:
  - `NONE` ➔ `USER_FOCUS` (신뢰도 0.45~0.74) ➔ `SHARED_FOCUS` (신뢰도 $\ge 0.75$) ➔ `DISCUSSING_TARGET` (사용자 확인) 상태 전이 완성.
- **Deictic Resolution Engine & User Intent Estimator (`deictic_resolver.py`, `user_intent_estimator.py`)**:
  - 지시어("이거", "저거", "봐봐", "새로 산" 등) 파싱 및 객체 매핑 전용 엔진.
  - Multi-Object 환경에서 `CandidateFocus` 상위 3개 관리.
- **Temporal Focus Persistence, Inactivity Timeout & Wrong Focus Recovery (`focus_persistence_manager.py`)**:
  - 6초 Focus Lock으로 시선 튐(Jitter) 원천 방지.
  - 15초 비활동 시 자동 해제.
  - 사용자 거절("아니 책이야") 시 2초 내 즉시 락 해제 및 재평가.
- **Abstract Attention Anchor & Avatar Gaze Synchronization (`RealtimeFaceRenderer.tsx`)**:
  - `AttentionAnchor` (`USER_FACE`, `LOWER_RIGHT`, `LOWER_LEFT`, `LOWER_CENTER` 등) 기반 Native Driver 60fps 시선/고개 동기화.
- **5 Architecture & Shared Reality Specification Documents**:
  - `docs/Shared_Reality_Architecture.md`, `docs/Joint_Attention_Spec.md`, `docs/Focus_Target_Guide.md`, `docs/Shared_Reality_Dialogue_Guide.md`, `docs/Sprint49_Report.md`.
- **Automated QA & Gates (`tests/test_shared_reality_joint_attention.py`)**:
  - Gate SR1~SR9 100% PASS (총 126개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 48] - Visual Awareness & Companion Perception Engine

### Added
- **4th Cognitive Layer: Visual Awareness & Perception Engine (`awareness_context.py`, `awareness_coordinator.py`)**:
  - `AwarenessContext` DTO, 8-Tier Facial Emotion (`SMILING`, `NEUTRAL`, `FOCUSED`, `CONFUSED`, `THINKING`, `FATIGUED`, `SURPRISED`, `UNKNOWN`).
  - 8대 주요 사물 객체(CUP, FOOD, BOOK, LAPTOP, PET, PLANT, TV, WINDOW) 감지, Confidence Thresholding (`>= 0.70`), BoundingBox.
  - Freshness Age 검증 (`age_ms <= 10000ms`, 10초 만료 시 대화 주입 자동 배제).
  - 시선 타겟 변환 `VisualFocusTarget` (`USER_FACE`, `CUP`, `LAPTOP`, `PET` 등).
- **Privacy First & Ephemeral In-Memory Pipeline**:
  - Zero Raw Frame Storage Guarantee (디스크 영구 저장 없음).
  - No Direct Raw Image to LLM (Structured DTO 전송 원칙).
  - 모바일 `SettingsScreen.tsx`에 `Privacy Dashboard` 추가.
- **Companion Reaction Budget Manager & Suggestive Phrasing (`reaction_planner.py`)**:
  - Reaction Budget (분당 최대 2회 한도, 25초 쿨다운) 적용으로 사용자 피로도 원천 차단.
  - 단정형("너는 ~한다") 100% 금지 및 Amy의 4대 제안형 스타일(공감, 호기심, 격려, 관찰) 프롬프트 가이던스.
- **Mobile Real-Time Visual Awareness Indicator (`CompanionScreen.tsx`)**:
  - 카메라 On/Off 시 실시간 인식 상태 뱃지 (`👁️ 시각 인지: 집중 | ☕ CUP`) 연동.
- **5 Architecture & Awareness Specification Documents**:
  - `docs/Visual_Awareness_Architecture.md`, `docs/Awareness_Context_Spec.md`, `docs/Companion_Reaction_Guide.md`, `docs/Privacy_Rules.md`, `docs/Sprint48_Report.md`.
- **Automated QA & Gates (`tests/test_visual_awareness_perception_engine.py`)**:
  - Gate VA1~VA7 100% PASS (총 117개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 47] - Voice Identity & Emotional Speech Engine

### Added
- **Voice Identity Framework & 4 Canonical Personas (`voice_profile.py`, `voice_identity_service.py`)**:
  - `WARM_COMPANION` (Genie 기본), `CALM_MENTOR`, `ENERGETIC_GUIDE`, `PROFESSIONAL_ADVISOR` 4대 보이스 페르소나 DTO 완비.
- **Dynamic Emotional Speech Engine (`emotional_speech_engine.py`)**:
  - 7대 감정 벡터(Joy, Concern, Empathy, Excitement 등)에 따라 발화 속도(Rate), 피치(Pitch), 에너지(Energy), 쉼표(Pause) 실시간 변조.
- **Relationship Speech Engine (`relationship_speech_engine.py`)**:
  - 관계 단계(Stranger ➔ Acquaintance ➔ Close Friend ➔ Trusted Companion)에 따른 격식 및 어조 변조.
- **Voice Provider Abstraction Layer (`provider_abstraction.py`)**:
  - OpenAI TTS, ElevenLabs (Voice Cloning 지원), Azure Speech, Cartesia 다중 벤더 교체형 팩토리 구축.
- **6 Architecture & Voice Specification Documents**:
  - `docs/Voice_Architecture.md`, `docs/Voice_Profile_Spec.md`, `docs/Emotional_Speech_Guide.md`, `docs/Relationship_Speech_Guide.md`, `docs/TTS_Audit_Report.md`, `docs/Sprint47_Report.md`.
- **Automated QA & Gates (`tests/test_voice_identity_speech_engine.py`)**:
  - Gate VC1~VC5 100% PASS (총 110개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 46] - Production Avatar Finalization & Avatar v1.0 RC1 Release

### Added
- **Avatar v1.0 Release Candidate 1 (RC1) 배포 및 Release Freeze 선언**:
  - 실시간 상태 머신(`IDLE` ➔ `LISTENING` ➔ `THINKING` ➔ `PRE_EXPRESSION` ➔ `SPEAKING` ➔ `SETTLING`)과 5대 레이어 파라미터 DTO의 완벽한 안정화.
- **5 Final Release Documents**:
  - `docs/Avatar_Release_Guide.md`: 프로덕션 배포 기준, 모니터링 체계, 긴급 롤백 계획.
  - `docs/Avatar_Architecture_Final.md`: 5-Layer Composite 아키텍처 및 렌더러 독립성 규격.
  - `docs/Avatar_QA_Report.md`: 10대 최종 릴리즈 게이트(P1~P10) 100% PASS 검증서.
  - `docs/Avatar_Known_Issues.md`: 알려진 이슈 및 기술 부채 관리 레지스트리.
  - `docs/Sprint46_Final_Report.md`: 프로젝트 대전환 완료 및 Avatar v1.0 릴리즈 공식 승인서.
- **Automated Final Release QA Suite (`tests/test_production_avatar_release.py`)**:
  - Gate P1~P10 100% PASS (총 105개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 45] - Motion Library Expansion & Behavioral Variety System

### Added
- **Motion Library V1 (`motion_library.py`)**: 14대 신체 동작 프리셋(Listening 4종, Thinking 4종, Speaking 3종, Empathy 3종) 구축.
- **Behavioral Variety Engine & Cooldown Tracker (`variety_engine.py`, `MotionVarietyEngine.ts`)**:
  - `Motion Cooldown Algorithm`: 최근 3회 사용된 모션의 선택 가중치를 대폭 억제하여 연속 반복 패턴 완전 차단.
  - `Randomization Jitter ($\pm10\%$)`: 각도, 피치, 끄덕임 진폭에 미세 편차를 부여하여 기계적 루프 배제.
  - `Context-Aware Selection`: 축하, 위로, 설명, 일상 대화 맥락에 최적화된 모션 매핑.
- **Motion Layer V2 Integration (`RealtimeFaceRenderer.tsx`)**:
  - Head Roll/Pitch, Eye Gaze, Body Lean이 60fps Native Driver로 끊김 없이 실시간 합성.
- **4 Architecture & Behavioral Specification Documents**:
  - `docs/Motion_Library_V1.md`: 12/14대 모션 카테고리 규격.
  - `docs/Variety_Engine_Spec.md`: Cooldown 및 Variety Engine 규격.
  - `docs/Context_Motion_Guide.md`: 축하/위로/설명 맥락 인지 모션 가이드.
  - `docs/Sprint45_Report.md`: Sprint 45 완료 보고서 및 Exit Criteria 판정.
- **Automated QA & Gates (`tests/test_motion_variety_engine.py`)**:
  - Gate M1~M5 100% PASS (총 95개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 44] - Emotion & Relationship Embodiment Engine

### Added
- **Standard RelationshipParameters Model (`domain.py`, `relationship_parameters.ts`)**: `familiarity`, `trust`, `warmth`, `engagement` 표준화.
- **Emotion & Relationship Embodiment Engine (`EmotionRelationshipEngine.ts`, `expression_mapper.py`)**:
  - `Emotion Blending Engine`: Joy 60% + Warmth 40% 등 7대 핵심 감정(Joy, Warmth, Curiosity, Concern, Empathy, Excitement, Calm) 선형 합성.
  - `Relationship Modifier`: Stranger(공손한 중립), Familiar(자연스러운 미소), Trusted(깊은 유대), Close Companion(환한 미소/높은 친밀감) 4단계 태도 차별화.
  - `Expression Layer V2`: 표정 강도 및 볼 홍조/오라 오버레이 실시간 합성.
- **Real-Time Emotion & Relational Avatar Renderer Integration (`RealtimeFaceRenderer.tsx`)**:
  - 사용자와의 신뢰/친밀도와 감정이 합성되어 60fps Native Driver로 표출.
- **4 Architecture & Behavioral Specification Documents**:
  - `docs/Emotion_Embodiment_Spec.md`: 7대 감정 및 감정 블렌딩 규격.
  - `docs/Relationship_Embodiment_Spec.md`: 4대 관계 단계 및 태도 차별화 규격.
  - `docs/Expression_Catalog_V2.md`: 7대 고도화 표정 카탈로그 V2.
  - `docs/Sprint44_Report.md`: Sprint 44 완료 보고서 및 Exit Criteria 판정.
- **Automated QA & Gates (`tests/test_emotion_relationship_embodiment.py`)**:
  - Gate E1~E5 100% PASS (총 90개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 43] - Embodied Behavior & Multimodal Presence Engine

### Added
- **Standard BehaviorParameters Model (`domain.py`, `behavior_parameters.ts`)**: `attentionLevel`, `eyeContact`, `headTilt`, `nodIntensity`, `bodyLean`, `curiosityLevel`, `thinkingIntensity` 표준화.
- **BehaviorEngine (`mobile/src/features/avatar/engine/BehaviorEngine.ts`)**:
  - `Eye Contact System`: 경청(1.0) ➔ 사색(0.4) ➔ 발화(0.85) ➔ 안정(0.85) 시선 전이.
  - `Head Motion System`: 경청 틸트(+2.5°), 사색 틸트(-4.0°), 주기적 공감 끄덕임(Agreement Nod) 제어.
  - `Settling Animation`: 발화 종료 후 400ms 동안 자연스럽게 Neutral 포즈로 안착.
- **Real-Time Embodied Avatar Renderer Integration (`RealtimeFaceRenderer.tsx`)**:
  - 6단계 행동 상태 머신(`IDLE` ➔ `LISTENING` ➔ `THINKING` ➔ `PRE_EXPRESSION` ➔ `SPEAKING` ➔ `SETTLING`)과 비언어적 신체 행동의 완전 동기화.
- **4 Architecture & Behavioral Specification Documents**:
  - `docs/Behavior_Parameter_Spec.md`: 7대 BehaviorParameters 규격.
  - `docs/Listening_Behavior_Guide.md`: 경청 행동(Eye Contact, 끄덕임) 가이드.
  - `docs/Thinking_Behavior_Guide.md`: 사색 행동(헤드 틸트, 시선 분산) 가이드.
  - `docs/Sprint43_Report.md`: Sprint 43 완료 보고서 및 Exit Criteria 판정.
- **Automated QA & Gates (`tests/test_embodied_behavior_engine.py`)**:
  - Gate B1~B5 100% PASS (총 85개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 42] - Real-Time Audio Lip-Sync & Viseme Articulation Engine

### Added
- **Standard SpeechParameters Model (`domain.py`, `speech_parameters.ts`)**: `isSpeaking`, `mouthOpen`, `viseme` (A/E/I/O/U/closed), `speechIntensity`, `speechProgress` 표준화.
- **LipSyncEngine V1 (`mobile/src/features/avatar/engine/LipSyncEngine.ts`)**:
  - Audio Amplitude 정규화 및 한국어 5대 모음 Viseme 순환.
  - EMA(지수 이동 평균, $\alpha=0.45$) 기반 Speech Smoothing(지터/떨림 방지).
  - 발화 중 자연스러운 고개 끄덕임(Head Pitch Accent $\pm1.5^\circ$) 및 눈썹 리프트(Speaking Micro Motion).
- **Real-Time Face & Lip Sync Renderer Integration (`RealtimeFaceRenderer.tsx`)**:
  - 발화 시작 즉시 입 개폐 및 Pre-expression 선반영, 발화 종료 시 100ms 이내에 자연스럽게 닫히는 발화 생명주기 제어.
- **4 Architecture & Specification Documents**:
  - `docs/LipSync_Architecture.md`: Audio Timing Pipeline 및 립싱크 아키텍처.
  - `docs/Speech_Parameter_Spec.md`: 5대 SpeechParameters 규격.
  - `docs/Speaking_Expression_Catalog.md`: 5대 발화 표정(Calm, Warm, Excited, Empathetic, Serious Speaking) 프리셋.
  - `docs/Sprint42_Report.md`: Sprint 42 완료 보고서 및 Exit Criteria 판정.
- **Automated QA & Gates (`tests/test_lip_sync_engine.py`)**:
  - Gate L1~L5 100% PASS (총 80개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 41] - Real-Time Face Engine & Parameter Control System

### Added
- **Standard FaceParameters Model (`domain.py`, `face_parameters.ts`)**: 렌더러 독립적 11대 파라미터(`eyeOpenness`, `blinkWeight`, `eyeDirectionX/Y`, `mouthOpen`, `smileStrength`, `browRaise`, `headPitch/Yaw/Roll`, `warmth`) 구축.
- **4 Dedicated Face Engine Modules (`mobile/src/features/avatar/engine/`)**:
  - `EyeEngine.ts`: 2.0s~7.0s 무작위 Blink 타이머 및 X/Y 시선 이동(Gaze) 제어.
  - `MouthEngine.ts`: 4단계(Closed ➔ Small ➔ Medium ➔ Wide Open) 입 개폐 제어.
  - `BrowEngine.ts`: -1.0~1.0 눈썹 상하 리프트 및 찡그림 제어.
  - `SmileEngine.ts`: 0.0~1.0 미소 곡률 및 눈웃음 블렌딩 제어.
- **Real-Time Face Renderer (`RealtimeFaceRenderer.tsx`)**:
  - Reanimated Native Driver 기반으로 60fps 부드러운 실시간 얼굴 합성 렌더링.
- **4 Architecture & Specification Documents**:
  - `docs/Face_Parameter_Spec.md`: 파라미터 규격 및 정규화 인터페이스.
  - `docs/Face_Engine_Architecture.md`: 4대 엔진 아키텍처 및 렌더링 파이프라인.
  - `docs/Expression_Catalog_V1.md`: 7대 기본 표정(Neutral, Soft Smile, Warm Smile, Bright Smile, Curious, Concerned, Thinking) 프리셋.
  - `docs/Sprint41_Report.md`: Sprint 41 완료 보고서 및 Exit Criteria 판정.
- **Automated QA & Gates (`tests/test_face_engine.py`)**:
  - Gate F1~F5 100% PASS (총 75개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 40] - Avatar Asset Pipeline & Real-Time Character Renderer Transition

### Added
- **Official Deprecation of Video Avatar Clips**: 반복 루프/자세 튐을 유발하는 동영상 클립 스위칭 방식을 공식 중단하고, 2.5D 레이어드 실시간 렌더러로 전면 전환.
- **Real-Time Layered Character Renderer (`RealtimeLayeredAvatarRenderer.tsx`)**:
  - Base Body & Neck 고해상도 포트레이트 + 실시간 유기체 호흡 펄스(4.5s) + 고개 끄덕임/기울기(Head Tilt/Roll) 실시간 변형.
  - 무작위 눈 깜빡임(Blink 3.5s 주기) + 상태별 오라 글로우(Aura Glow).
  - 실시간 오디오 립싱크(Lip-Sync) 및 조음 음소 순환(Viseme A, E, I, O, U) 레이어 구현.
- **3대 아키텍처 및 자산 표준 문서 완비**:
  - `docs/Avatar_Asset_Spec.md`: 7대 분리 레이어 규격 및 파라미터 스키마.
  - `docs/Avatar_Renderer_Architecture.md`: 실시간 렌더러 렌더링 파이프라인 및 60fps 최적화 전략.
  - `docs/Live2D_Migration_Plan.md`: Live2D Cubism 4 SDK 파라미터 1:1 매핑 및 단계별 마이그레이션 로드맵.
- **Backend Real-Time Parameter DTO Extension (`avatar/domain.py`)**:
  - `VisemeType` (`CLOSED`, `A`, `E`, `I`, `O`, `U`), `eye_openness`, `mouth_open`, `blink_value`, `warmth_alpha` 확장.
- **Automated QA & Gates (`tests/test_avatar_asset_pipeline.py`)**:
  - Gate A1~A5 100% PASS (총 70개 백엔드 테스트 및 모바일 TypeScript 0 Errors 달성).

## [Sprint 39] - Avatar Behavioral Synchronization & Embodied Character Engine

### Added
- **Mobile Dual Video Cross-Fade Buffer (`CompanionScreen.tsx`)**: `VideoLayerA` / `VideoLayerB` 이중 버퍼 및 350ms 부드러운 오파시티 크로스페이드(`opacity 1->0 & 0->1`) 구현으로 비디오 전환 시 깜빡임/자세 튐 완전 제거 (Priority P0 달성).
- **PRE_EXPRESSION Mobile Pre-bloom (`CompanionScreen.tsx`)**: 답변 발화 시작 200ms 전 미리 미소(`smile`) 표정과 오라로 전환하여 생각 후 말하는 자연스러운 사전 행동 시각화.
- **Continuous Organic Breathing Layer (`CompanionScreen.tsx`)**: 비디오 전환과 무관하게 `scale 1.00 ↔ 1.018`, `translateY ±2px` (4.5초 주기)의 살아있는 호흡 펄스 상시 유지.
- **6-Stage Behavioral State Machine (`avatar/domain.py`)**: `IDLE` ➔ `LISTENING` ➔ `THINKING` ➔ `PRE_EXPRESSION` ➔ `SPEAKING` ➔ `SETTLING`.
- **EmotionToExpressionMapper (`avatar/expression_mapper.py`)**: `ContinuousEmotionVector` ➔ `ExpressionParameters` 결정론적 매핑으로 렌더러 완전 독립성 확보.
- **AvatarBaselineController (`avatar/baseline_controller.py`)**: `BlinkController`, `BreathingController`, `MicroExpressionController` 분리.
- **Automated QA & Gates (`tests/test_avatar_behavior_sync_engine.py`)**: Gate V1~V10 & Gate M1~M4 100% PASS (65개 백엔드 테스트 및 모바일 TypeScript 0 Errors).


## [Sprint 38] - Character Agency & Autonomous Initiative Engine

### Added
- **5-Tier Agency Action Architecture (`agency/domain.py`)**: `STAY_SILENT`, `INTERNAL_REFLECTION`, `QUIET_PRESENCE`, `UI_INITIATIVE`, `OUTREACH_CANDIDATE` 5단계 자율 행동 의도 정립.
- **Action Intent vs Delivery Channel Separation**: `action_type`과 `delivery_channel` (`NONE`, `INTERNAL`, `UI_PRESENCE`, `PROACTIVE_MESSAGE`, `NOTIFICATION`) 독립 분리 및 `NotificationPolicy` 연동.
- **Temporal Context Awareness (`temporal_context.py`)**: 대화 간격, 부재 시간(Absence Duration Hours), 요일/시간대, 미완료 주제(Pending Topics)를 실시간 반영.
- **Weighted Priority Scoring + Hard Policy Gate (`agency_engine.py`)**:
  - $\text{BaseScore} = 0.20 \times \text{P} + 0.25 \times \text{Rel} + 0.20 \times \text{Temp} + 0.20 \times \text{Emo} + 0.15 \times \text{Mem}$
  - `proactive_enabled` 비활성화 시 즉각 `BLOCKED_BY_POLICY` 처리.
- **Initiative Budget & Multi-tier Cooldowns (`initiative_budget.py`)**: Daily Budget = 1.0 체계 및 Notification(6h), Message(1h), 동일 행동(30m) 쿨다운으로 AI 알림 폭주/스팸 원천 방어.
- **Autonomy Guard (`autonomy_guard.py`)**: 죄책감 유도 및 감정적 조작 문구 차단, 심야 시간(Quiet Hours) 보호.
- **Agency Action Logging (`db/models/character_agency.py`)**: `agency_action_logs` 테이블에 `decision_status` 및 `blocked_reason` 영속화.
- **Automated QA & Gates (`tests/test_character_agency_engine.py`)**: Gate A1~A9 전 항목 100% PASS (10,000회 장기 안정성 시뮬레이션 포함 55개 백엔드 테스트 완벽 통과).

## [Sprint 37] - Long-Term Character Growth & Relationship Dynamics Engine

### Added
- **Multi-User Isolation & Composite Key Architecture**: `(user_id, companion_id)` 복합 키 기반 `UserRelationshipAdaptationModel`, `RelationshipMilestoneModel`, `RelationshipStateModel V2`.
- **8-Dimensional Relationship Dynamics (`relationship/`)**: `RelationshipVector` (trust, closeness, comfort, attachment, playfulness, respect, emotional_safety, shared_history_depth) 및 관계 아키타입(Archetype) 분류기.
- **Significance & Maturity Weighted Bounded Delta Engine (`evolution.py`)**: $\text{Delta} = \text{Raw} \times \text{Significance} \times \text{MaturityFactor}$ ($\text{clamp}(-0.03, +0.03)$) 적용으로 깊은 관계일수록 완만한 감쇠 진화.
- **Shared Experience Narrative System (`timeline/`)**: 단순 사실(Fact Memory)과 구별되는 공동 사건/정서적 의미/관계 영향 체인 관리.
- **Separation of Global Growth vs User Adaptation (`growth/`)**: `CharacterGlobalGrowthState` (전역 습관)와 `UserRelationshipAdaptationState` (사용자별 맞춤 말투/호흡) 분리 및 **Immutable Core 영구 잠금(LOCKED)**.
- **Automated QA & Gates (`tests/test_character_growth_and_relationship_dynamics.py`)**: Gate R1~R6 전 항목 100% PASS (46개 백엔드 단위/통합 테스트 완벽 통과).

## [Sprint 36] - Behavioral Personality Engine & Character Consistency

### Added
- **3-Layer Character Architecture**: `Immutable Core` (Identity/Values) ➔ `Stable Personality` (MBTI/Traits 5D) ➔ `Dynamic State` (Emotion/Relationship/Memory Snapshot).
- **MBTI Behavioral Bias Engine (`mbti_mapper.py` & `traits.py`)**: MBTI를 결정론적 틀이 아닌 행동 확률 가중치 편향(Bias)으로 유연하게 결합하는 `PersonalityTraitVector.weighted()` 구현.
- **Pre-LLM Behavioral Decision Layer (`behavior_engine.py`)**: `Situation Analysis`를 거쳐 `CharacterDecision` (`response_style`, `behavior_intents`, `decision_confidence`, `reasons`, `prompt_directive`) 사전 도출 (<10ms).
- **Multidimensional Character Consistency Validator (`consistency.py`)**: 6대 세부 점수화 및 티어별 비용 제어 (`PASS >= 0.85`, `ADJUST 0.60~0.84`, `REGENERATE < 0.60`).
- **Decoupled Presentation Mapping (`presentation_mapper.py`)**: `CharacterDecision` ➔ `PresentationIntent` ➔ `AvatarStateResolver` 바인딩.
- **Decision History Logging (`db/models/character_decision.py`)**: `character_decisions` 테이블 구축으로 미래 Sprint 37 인격 성장 및 Drift 추적 데이터 기반 확보.
- **Automated QA & Gates (`tests/test_behavioral_personality_engine.py`)**: Gate C1~C7 전 항목 100% PASS (Gate C7 Personality Injection Resistance 포함 40개 백엔드 테스트 완벽 통과).

## [Sprint 35] - Autonomous Thought & Reflection Engine

### Added
- **Pre-Implementation Audit (`Sprint35_PreImplementation_Report.md`)**: Memory, Relationship, Emotion, EventBus, Background Runtime 정밀 감사 및 아키텍처 충돌 무결성 검증.
- **Reflection Domain & Persistence (`services/reflection/domain/` & `db/models/reflection.py`)**: `ReflectionRecord`, `ReflectionResult` (Structured Output), `ReflectionDecision`, `ReflectionRecordModel` (`reflection_records` 테이블).
- **Rule-based Reflection Policy & Pattern Analyzer (`policy/` & `engine/`)**: `ReflectionPolicy` (감정/기억/관계 임계값 필터링), `PatternAnalyzer` (감정/주제 트렌드 분석).
- **Core Reflection Engine & Trust Boundary (`engine/` & `validation/`)**: `ReflectionEngine`, `ReflectionValidator` (Core Identity / MBTI / Persona 변조 원천 차단).
- **Memory Consolidation Engine & Duplicate Detector (`memory/`)**: `ConsolidationEngine` (CREATE, MERGE, ARCHIVE, DISCARD), `DuplicateDetector` (유사 기억 중복 방지).
- **Async Runtime & Rate Limiter (`runtime/`)**: `ReflectionTaskRunner` (0ms Latency 완전 비동기 격리), `ReflectionRateLimiter` (쿨다운 및 대화당 상한 제어).
- **Context & Event Integration (`providers/` & `companion/events/`)**: `ReflectionContextProvider` (`[RECENT REFLECTION INSIGHT]` < 150 토큰), `CompanionEventBus` 비동기 훅 연동.
- **Automated QA & Gates (`tests/test_reflection_engine.py`)**: Gate R1~R8 전 항목 100% PASS (33개 백엔드 단위/통합 테스트 완벽 통과).

## [Sprint 34] - Dynamic Personality & Behavioral Evolution Engine

### Added
- **Personality Behavioral Domain (`services/personality/models/`)**: `PersonalityState` (CoreTraits 5D, CommunicationStyleState, AttachmentStyleState), `BehaviorDirective` (ResponseStyle, InteractionBehavior, EmotionalExpressionDirective, explainability `reasons`).
- **Sub-Engines Layer (`services/personality/engines/`)**: `TraitEngine`, `CommunicationEngine`, `AttachmentEngine`, `PersonalityBehaviorEngine` (<10ms 초고속 연산).
- **Personality Consistency Guard (`evaluators/consistency_evaluator.py`)**: `PersonalityConsistencyEvaluator` (Score ≥ 0.70 Accept, 0.50~0.69 Warning, < 0.50 Rewrite)로 100회 대화 시뮬레이션 인격 표류(Drift) 방어.
- **Context Directive Injection (`character_identity.py`)**: ContextBuilder에 `[DYNAMIC BEHAVIOR DIRECTIVE]` 블록 주입 (<300 토큰).
- **Automated QA & Gates (`tests/test_dynamic_personality_behavior.py`)**: Gate P1~P5 전 항목 100% PASS (29개 백엔드 단위/통합 테스트 완벽 통과).

## [Sprint 33] - Personality Consistency & Character Behavior Engine

### Added
- **Character Behavior & Communication Layer (`services/character/`)**: `CommunicationStyle` (formality, humor, emoji_usage, emotional_expression), `RelationshipBehaviorMapper` (Stranger vs Friend vs Close Stage 매핑), `BehaviorInstruction`, `CharacterBehaviorResolver`.
- **Personality Consistency Validator (`response_validator.py`)**: Rule-based + Selective Validation 하이브리드 검증 (Consistency Score, 가치관 위반 방어, 소유욕/의존성 금지).
- **Character Interpretation Memory Expansion (`db/models/memory.py`)**: `MemoryType`에 `CHARACTER_INTERPRETATION`, `EMOTIONAL_MEMORY` 추가.
- **Orchestrator & Avatar Integration (`orchestrator.py` & `character_identity.py`)**: User Intent ➔ Behavior Directive ➔ LLM Response ➔ Consistency Validator ➔ Avatar State Resolution 통합.
- **Automated QA & Gates (`tests/test_character_behavior.py`)**: Gate C1~C5 전 항목 100% PASS (24개 백엔드 단위/통합 테스트 완벽 통과).

## [Sprint 32] - Autobiographical Memory & Shared Life Timeline Engine

### Added
- **Autobiographical Memory Domain (`domain/memory/`)**: `EpisodicMemory`, `LifeEvent` (11개 카테고리), `SharedExperience` (Truth Boundary 보장), `StoryChapter` (서사 챕터), `TimelineEvent`, `AutobiographicalContext`.
- **Database Persistence (`db/models/autobiographical_memory.py`)**: `episodic_memories`, `life_events`, `shared_experiences`, `timeline_events`, `story_chapters` 테이블 구축.
- **Memory & Narrative Engines (`services/memory/` & `services/shared_experience/`)**: `EventImportanceEngine` (Novelty + Emotional Intensity + Personal Significance), `LifeEventPromoter` (중복 방지 및 승격), `ExperienceLinker` (A ➔ B ➔ C 서사 체인), `SharedExperienceEngine`, `TemporalMemoryRetriever`, `AutobiographicalNarrativeService`.
- **Truth Boundary Context Compiler (`autobiographical_context_compiler.py`)**: 캐릭터가 직접 동행한 일과 사용자의 개인 외부 경험을 엄격히 구분하여 '우리의 공동 역사' 왜곡 및 환각 원천 차단.
- **Mobile Shared Story UI (`SharedStoryScreen.tsx`)**: "OUR STORY: 우리가 함께한 시간", 서사 챕터 카드, 공동 마일스톤 타임라인, 지니의 회고 내러티브 기능.
- **Automated QA & Gates (`tests/test_autobiographical_memory.py`)**: Gate M1~M12 전 항목 100% PASS.

## [Sprint 31] - Relationship Evolution & Social Bond Engine

### Added
- **Multi-Dimensional Social Bond Domain (`domain/relationship/`)**: `RelationshipDimensions` (7대 차원: Familiarity, Trust, Affection, Intimacy, Respect, Comfort, Attachment), `RelationshipStage` (5단계 복합 승급 모델), `RelationshipEvent`, `RelationshipAnchor` (영구 불변 관계 닻).
- **Database Persistence (`db/models/relationship.py`)**: `relationship_states` 7대 차원 확장, `relationship_events`, `relationship_anchors` 테이블 구축.
- **Social Bond Engine (`services/relationship/`)**: `RelationshipEventDetector`, `RelationshipChangeCalculator` (Rate Limit `MAX_DELTA <= 0.03`), `RelationshipStageResolver`, `RelationshipAnchorService`.
- **Relationship Context Compiler & Safety Guard (`relationship_context_compiler.py`)**: 숫자 나열을 배제한 정성적 관계 컨텍스트 생성 및 정서적 의존성 조작/가스라이팅/소유욕 원천 차단 안전 지침 주입.
- **Mobile Relationship Screen UI (`RelationshipScreen.tsx`)**: 관계 단계 뱃지, 7대 차원 본드 진행 바, '우리의 이야기' 앵커 타임라인 시각화.
- **Automated QA & Gates (`tests/test_relationship_evolution.py`)**: Gate R1~R9 (7D Model, Event Evolution, Stage Resolver, Context Injection, Anchor Persistence, Rate Limit, Absence Decay, Safety Boundary, Pipeline Integrity) 100% PASS.

## [Sprint 30] - Persistent Character Identity & Personality Core

### Added
- **Character DNA Domain Layer (`domain/character/`)**: `CharacterIdentity`, `PersonalityProfile` (14개 다차원 Trait + MBTI), `CharacterValues` (7대 가치관), `CharacterPreferences`, `CharacterBoundaries`, `CharacterState`, `ResponseStrategy`.
- **Database Persistence (`db/models/`)**: `CharacterProfileModel`, `CharacterPersonalityModel`, `CharacterValueModel`, `CharacterPreferenceModel`, `CharacterBoundaryModel`.
- **Personality Prompt Compiler (`personality_prompt_compiler.py`)**: LLM에 구조화된 LEVEL 2 Character Context (`[CHARACTER IDENTITY]`, `[PERSONALITY DNA]`, `[CORE VALUES]`, `[BOUNDARIES]`) 주입.
- **Character Agency Engine (`response_strategy_resolver.py`)**: 사용자의 비이성적 요구 및 인격 파괴 공격에 맹목적으로 복종하지 않고 품격과 지적 정직성을 지키는 독립적 에이전시 구현.
- **5-Level Trust Boundary Context (`ContextBuilder`)**: LEVEL 1 System ➔ LEVEL 2 Character ➔ LEVEL 3 Application State ➔ LEVEL 4 Vision ➔ LEVEL 5 Untrusted User Input 정렬.
- **Mobile Character Profile UI (`CharacterProfileScreen.tsx`)**: 다차원 성격 차트(Warmth, Curiosity, Intellectuality 등), 가치관 그리드, 자아인식 카드 시각화 및 네비게이션 연동.
- **Automated QA & Gates (`tests/test_character_*.py`)**: Gate C1~C6 (Persistence, Consistency, Emotion Separation, Agency, Boundary Defense, Pipeline Integrity) 단위/통합 테스트 스위트 통과.

## [Sprint 18] - Real Vision Provider & Camera Intelligence Engine

### Added
- **Production CloudVisionProvider (`cloud_vision_adapter.py`)**: `gpt-4o-mini` 멀티모달 비전 분석, 얼굴/시선/표정/객체 인식, 빈 이미지 방어, 타임아웃 및 표준 에러 도메인 매핑.
- **ProviderFactory Vision Integration (`factory.py`)**: `VISION_PROVIDER=cloud|mock` 설정 지원.
- **Vision Endpoint Dynamic DI (`endpoints/vision.py`)**: `ProviderFactory`를 통한 의존성 주입.
- **Mobile VisionController & Sampling Throttle (`visionController.ts`)**: 4초 스로틀 샘플링, User-Initiated 즉시 샘플링, Background 전환 시 `cleanup()` 강제 종료.
- **Vision Integration Test Suite (`test_vision_integration.py`)**: CloudVisionProvider 단위 테스트, Observation 중복 제거, ContextBuilder Trust Boundary 및 Failure Isolation 테스트 5종 추가.

## [Sprint 17] - Real Voice Interaction & Audio Runtime
### Added
- **Production OpenAI STT/TTS Adapters (`openai_adapter.py`)**: Whisper-1 한국어 음성 인식, TTS-1 음성 합성, 빈 오디오/텍스트 방어, 타임아웃 및 표준 에러 도메인 매핑.
- **ProviderFactory STT/TTS Integration (`factory.py`)**: `STT_PROVIDER=openai`, `TTS_PROVIDER=openai` 설정 지원.
- **Dynamic Voice Endpoint DI (`endpoints/voice.py`)**: `ProviderFactory`를 통한 의존성 주입.
- **Mobile VoiceController (`voiceController.ts`)**: 음성 녹음 시작/중지, Audio Player 재생 및 User Interrupt 제어.
- **User Interrupt & Avatar Sync (`CompanionScreen.tsx`)**: 발화 중 마이크 입력 시 즉각적인 TTS 중단 및 `LISTENING` 전이.
- **Voice Integration Test Suite (`test_voice_integration.py`)**: STT/TTS 어댑터, 파이프라인 전체 루프, User Interrupt, Failure Isolation 테스트 6종 추가.

## [Sprint 16] - Real LLM Provider Integration & Production Cognitive Core
### Added
- **Production OpenAI LLM Adapter (`openai.py`)**: `AsyncOpenAI` 기반 스트리밍, `OPENAI_MODEL`, `OPENAI_TIMEOUT_SECONDS`, `OPENAI_MAX_TOKENS` 지원 및 `LLMProviderError` 에러 도메인 계층화.
- **ProviderFactory Strict Selection (`factory.py`)**: `LLM_PROVIDER=openai` 시 무단 Mock Fallback 차단.
- **ContextBuilder Trust Boundaries & Injection Defense (`builder.py`)**: `ConversationHistoryProvider` 정밀 식별 및 프롬프트 인젝션 방어 가이드라인 강화.
- **Integration & Security Test Suite (`test_real_llm_integration.py`)**: 대화 시나리오(A~I) 및 5대 프롬프트 인젝션 방어 테스트 10종 추가.
- **Real OpenAI Smoke Test Script (`smoke_test_real_llm.py`)**: 명시적 수동 API 검증 도구 추가.

## [Sprint 15] - STEP 4: Runtime Hardening & Real Provider Readiness
### Added
- **Pluggable ProviderFactory (`factory.py`)**: `LLM_PROVIDER`, `STT_PROVIDER`, `TTS_PROVIDER`, `VISION_PROVIDER`, `EMBEDDING_PROVIDER` 독립 환경변수 설정 지원.
- **Idempotency Guard (`active_interactions`)**: 동일 `interaction_id` 중복 요청 차단 및 중복 LLM 비용 발생 방어.
- **Structured Observability Tracer (`tracer.py`)**: `interaction_id`, `ttft_ms`, `context_gather_ms`, `llm_total_ms`, `post_process_ms`, `total_e2e_ms` 구조화 JSON 로깅.
- **Hierarchical Timeout Guard**: TTFT Timeout(15s), Stream Idle Timeout(30s) 적용.
- **Runtime Lifecycle (`CompanionRuntimeLifecycle`)**: FastAPI Lifespan 연동 리소스 라이프사이클 관리.
- **Mobile Predictable Config (`env.ts`)**: `EXPO_PUBLIC_API_URL` 명시적 우선 및 Android Emulator(`10.0.2.2:8000`), iOS Simulator(`localhost:8000`) 자동 지원.
- **Mobile 7-State Network Machine**: `idle`, `connecting`, `streaming`, `cancelled`, `disconnected`, `retrying`, `error` 및 이벤트 중복 제거(`processedEventIds`).

## [Sprint 15] - STEP 3B: Mobile Unified CompanionScreen & Interaction Pipeline
### Added
- **Centralized InteractionController (`interactionController.ts`)**: 모든 모달리티(Text, Voice, Vision) 입력 발송, SSE 스트림 구독, 취소, 오류 핸들링을 단일 진입점으로 통합.
- **Reusable ConversationView (`ConversationView.tsx`)**: 히스토리 조회, 낙관적 메시지 렌더링, SSE 텍스트 스트리밍 및 생각 중(Thinking) 인디케이터 처리 컴포넌트화.
- **Real-time Avatar Sync & Override Policy**: 실제 로컬 오디오 재생 상태(`setSpeaking`)가 백엔드 제안값보다 높은 우선순위로 아바타 모션/표정을 오버라이드.
- **Hardware Privacy Boundary (`CompanionScreen.tsx`)**: 백그라운드 전환 시 마이크, 카메라 캡처, 진행 중인 음성 스트리밍을 물리적으로 즉시 종료.

## [Sprint 15] - STEP 3A: Backend Single Interaction Pipeline & Cognitive Orchestration
### Added
- **Composition Root (`runtime.py`)**: 7대 ContextProvider(`Persona`, `Relationship`, `Emotion`, `Memory`, `Presence`, `Vision`, `ConversationHistory`), EventBus, StateMachine, AvatarStateResolver를 결합한 `create_companion_orchestrator` 및 `get_companion_orchestrator` DI 제공.
- **Unified Interaction Contract & SSE Schema (`domain.py`)**: `NormalizedInput`, `StructuredCandidate`, `UnifiedResponse` 정의 및 표준 JSON SSE 포맷(`interaction_started`, `thinking`, `text_delta`, `text_completed`, `avatar_state`, `interaction_completed`, `error`) 확립.
- **AvatarStateResolver Runtime Integration (`orchestrator.py`)**: LLM 생성 완료 후 Post-processing에서 실시간 `AvatarStateResolver`를 호출하여 아바타 표정/에너지/모션을 산출하고 SSE 이벤트(`avatar_state`)로 전달.
- **FastAPI Router Integration (`main.py`)**: `/api/v1/companion`, `/api/v1/voice`, `/api/v1/vision`, `/api/v1/avatar` 공식 등록 및 OpenAPI 노출.
- **Integration Test Suite (`test_backend_integration.py`)**: Quality Gate A~E 100% 통과 검증 (Text SSE, Voice Routing, Vision Context, Avatar Integration, Legacy Isolation).

### Changed
- **Voice Pipeline Refactoring (`voice_service.py`, `voice.py`)**: `VoiceService` ➔ STT ➔ `NormalizedInput` ➔ `CompanionOrchestrator` ➔ Unified Response ➔ TTS 흐름으로 재구축 (`ConversationService` 직접 의존성 완전 제거).
- **Legacy Isolation (`conversations.py`)**: `/api/v1/conversations` 엔드포인트를 Legacy Path로 명시적 분리.

## [Sprint 8] - Mobile Presence & Notification Bridge
### Added
- **Notification Domain**: `NotificationEvent`, `NotificationSettings` DB 모델 추가 (Message와 완벽히 분리).
- **Notification Provider**: `BaseNotificationProvider` 추상 클래스 및 `ExpoNotificationProvider`, `MockNotificationProvider` 추가.
- **Notification Policy Engine**: App Lifecycle(Foreground/Background) 및 설정(Quiet Hours, Never Disturb)에 따라 Push 전송 또는 In-App 처리 분기 로직 반영.
- **Mobile UI**: Phone(Stack) 및 Tablet(Split) 대응 반응형(Adaptive) `CompanionScreen.tsx` 컴포넌트 추가.
- **Emotion 렌더링**: `EmotionState`를 `PresentationState`로 매핑하여 향후 아바타 엔진 교체에 대비한 렌더링 구조 확립.
- **Camera Stub**: Sprint 10을 대비한 `CameraProvider` 인터페이스 추가.
- **Deep Link**: 푸시 탭 시 `p009://conversation/{id}` 로 바로 연결되도록 딥링크 라우팅 설계 반영.

## [Sprint 7] - Presence & Proactive Interaction
### Added
- **Presence Domain**: `PresenceState` 모델 및 `PresenceService` 구현 (앱 수명주기와 Companion 존재 상태 분리).
- **Proactive Engine**: `ProactivePolicyEngine`을 통해 스팸 차단 정책(Cooldown, Daily Limit, Relationship 상태) 통합.
- **Proactive Decision Logging**: `proactive_events` 테이블에 Proactive 발화 이유(`decision_reason`), 점수(`score`), 컨텍스트 스냅샷 기록.
- **Context Integration**: `PresenceContextProvider`를 ContextBuilder에 연동.
- **Mobile UI**: `PresenceSettingsScreen.tsx` 모바일 설정 화면 및 Heartbeat 서비스 연동.

*(Sprint 1~6 내역은 각 Sprint Report 및 문서 참조)*
