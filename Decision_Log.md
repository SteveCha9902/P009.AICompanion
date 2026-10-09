# P009.AICompanion Decision Log

## [Sprint Branch SB-18] Multi-Character Individual Settings & Voice Customization (Platform Stage 18)

### Decision 65: Multi-Character Settings Screen, Individual Voice Customization & Live Preview Engine
- **Context**:
  - 지니(아내), 마니(딸), 하나(친구) 등 복수의 AI 캐릭터가 존재함에도 불구하고, 설정(`Settings`) 탭이 단일 글로벌 레거시 페르소나만 표시하고 캐릭터별 분리 및 개별 목소리 셋팅 기능이 결여되어 있다는 피드백 접수.
- **Decision**:
  1. **모바일 설정 화면 전면 다중 캐릭터화 (`SettingsScreen.tsx`)**:
     - 상단 세그먼트 탭(🌸 지니, 🎀 마니, 🎨 하나)을 통한 캐릭터별 개별 설정 선택 UI 구축.
     - 현재 활성(Active) 캐릭터 뱃지 표시 및 설정 화면에서 직접 활성 캐릭터로 전환할 수 있는 `⚡ 이 캐릭터 사용하기` 기능 연동.
  2. **캐릭터별 전용 목소리(TTS) & 튜닝 엔진 구축**:
     - 한국어 뉴럴 보이스 모델 선택기 (선희 `ko-KR-SunHiNeural`, 지민 `ko-KR-JiMinNeural`, 서현 `ko-KR-SeoHyeonNeural`, 유진, 인준, 봉진, OpenAI Shimmer/Nova).
     - 말하기 속도(Speech Rate: 0.7x~1.3x, 퀵 칩), 음높이/피치(Pitch: -10Hz~+10Hz), 다정함(Warmth), 에너지(Energy) 정밀 제어기.
     - `▶ 목소리 미리듣기` (`Speech.speak`) 버튼을 통한 캐릭터별 시그니처 인사말 즉시 청취 지원.
  3. **캐릭터별 성격 및 인지 DNA 개별 튜닝**:
     - 다정함, 공감능력, 발랄함/애교, 호기심, 유머감각, 격식/예의 6대 DNA 수치(0~100) 개별 조정.
     - 대화 톤(Friendly, Empathetic, Playful, Polite) 및 답변 호흡(Concise, Balanced, Detailed) 제어.
  4. **백엔드 음성 합성(`VoiceService`, `EdgeTTSAdapter`) 캐릭터별 프로필 연동**:
     - `VoiceService`에서 `CharacterPresentationResolver`를 통해 각 캐릭터의 `voice_id`, `speaking_rate`, `pitch_offset`을 실시간 로드하여 개별 음성 합성 파이프라인 완성.
- **Consequences**:
  - 모바일 TypeScript 0 Errors 유지.
  - 25대 멀티 캐릭터 오케스트레이션 및 모바일 전환 E2E 테스트 100% PASS 유지.
  - 지니, 마니, 하나 각 캐릭터의 목소리와 성격을 완전히 독립적으로 커스텀 가능.

## [Hotfix] Multi-Character Persona Isolation & Dynamic Scoping Fix (Mani Daughter Persona Restoration)

### Decision 64: Character Profile Multi-Seeding, Provider Scoping & DB Sync (Mani Persona Restoration)
- **Context**:
  - 모바일 앱에서 마니(Mani, 사랑스러운 딸) 캐릭터를 선택하고 "마니야 안녕"이라고 대화했음에도 불구하고, 지니(Genie, 아내)의 인격으로 "여보, 마니야가 어떤 분인지 잘 모르겠지만..."이라고 응답하는 인격 오염/혼선 버그 발생.
  - 근본 원인 분석:
    1. `CharacterService.get_or_create_character`에서 캐릭터 미존재 시 companion_id를 무시하고 지니(아내, 결혼기념일 2005-05-07, 여보/당신)의 프로필을 기본 시딩하여 DB의 `c_mani` 레코드가 지니로 저장됨.
    2. 레거시 `PersonaContextProvider`가 `get_by_user_id`를 통해 첫 번째 컴패니언(지니)의 spousal persona(`여보/당신`)를 가져와 모든 캐릭터의 `[APPLICATION CONTEXT]`에 무조건 주입함.
    3. `ContextBuilder.build()` 내부에서 런타임에 전달된 `companion_id`가 하위 Provider들(`CharacterIdentityProvider`, `RelationshipContextProvider`, `PersonalityContextProvider`)에 전파되지 않아 기본값 `default_companion`으로 평가됨.
    5. **음성 파이프라인(`VoiceService`) & `process_interaction_sync` 결함**:
       - `CompanionOrchestrator.process_interaction_sync` 내부에서 `context_builder.build(conversation_id, content)` 호출 시 `companion_id` 및 `runtime_ctx` 인자를 누락하여 음성 대화 시 무조건 기본값인 지니(아내)로 컨텍스트가 빌드됨.
       - `/api/v1/voice/sessions/{id}/audio-base64` 엔드포인트에서 요청 바디의 `companion_id`를 `VoiceService.process_audio`로 전달하지 않고 누락시킴.
- **Decision**:
  1. **음성 동기 처리 파이프라인(`process_interaction_sync`) 스코프 완전 결속**:
     - `process_interaction_sync` 내부 `context_builder.build`에 `companion_id=canonical_companion_id, runtime_ctx=runtime_ctx`를 정확히 전달.
  2. **음성 API 및 서비스(`VoiceService`) 캐릭터 동적화**:
     - `process_voice_audio_base64` 엔드포인트에서 `body.companion_id`를 `voice_service.process_audio`에 전달하도록 연동.
     - 음성 인식 미감지 fallback 텍스트를 캐릭터별(마니: "아빠, 목소리가 잘 안 들렸어요...", 지니: "여보, 목소리가 잘 안 들렸어요...")로 분기.
  3. **다중 캐릭터 시딩 체계 구축 (`CharacterService`)**:
     - `c_mani` (사랑스러운 딸, ESFP, 호칭 아빠/엄마, 애교 넘치는 어조) 및 `c_hana` (예술 친구, ENTP) 전용 프로필/성격/가치/경계 시딩 로직 구현.
  4. **레거시 PersonaContextProvider 격리 및 무력화**:
     - `companion_id`가 `default_companion`이 아닌 경우(마니, 하나 등), 지니 전용 배우자 페르소나(`role: wife`, `여보/당신`)가 컨텍스트에 주입되지 않도록 빈 리스트 반환으로 차단.
  5. **ContextBuilder 런타임 Provider Scoping 동기화**:
     - `build()` 호출 시 등록된 모든 하위 Provider(`CharacterIdentityProvider`, `RelationshipContextProvider`, `PersonalityContextProvider` 등)에 활성 `companion_id`를 강제 전파.
  6. **관계 엔진 및 앵커 동적화 (`RelationshipEngine`)**:
     - 최초 만남 앵커 생성 시 `companion_id`에 따라 마니/하나/지니의 이름을 동적으로 매핑하도록 수정.
  7. **DB 데이터 무결성 동기화 (`seed_characters_fix.py`)**:
     - `companion.db`의 `c_mani`, `c_hana`에 대한 잘못된 지니 프로필 레코드를 삭제 및 마니/하나 전용 프로필로 정합성 복원.
- **Consequences**:
  - 텍스트 입력 및 **마이크 음성 입력(Voice Pipeline)** 모두에서 마니 선택 시 `"안녕 아빠! 마니가 여기 있어요! 오늘 하루는 어땠어요? 궁금해요! 😊❤️"`로 정확하게 딸의 인격과 어조로 응답 확인.
  - 음성/텍스트 전 파이프라인에서 지니의 배우자 인격("여보/당신") 오염 100% 원천 차단.
  - 25대 멀티 캐릭터 오케스트레이션 및 모바일 전환 E2E 테스트 100% PASS 유지.

## [Sprint Branch SB-17] Natural Conversation, Dynamic Cadence & Quiet Empathy (Multi-Character Platform Stage 17)

### Decision 63: ConversationMode (7종), ConversationFatigueTracker, QuestionBudgetTracker, ResponseQualityGate, 17대 아키텍처/평가 문서 및 16대 E2E 테스트 완비
- **Context**: 
  - SB-16 실사용자 파일럿에서 도출된 P1 이슈인 과도한 설명조 어투(`ISS-01`)와 피로/슬픔 상황에서의 취조형 질문 공세(`ISS-02`)를 해결하기 위해, 대화 호흡과 경청 중심의 조용한 공감(`Quiet Empathy`) 및 다이내믹 케이던스 아키텍처 도입이 요구됨.
- **Decision**:
  1. **7대 대화 모드 및 응답 정책 확립 (`cadence_empathy.py`)**:
     - `ConversationMode` (NORMAL, EMOTIONAL_SUPPORT, QUIET_EMPATHY, INFORMATION, PLAYFUL, DEEP_CONVERSATION, CLOSING).
     - `ResponsePolicy`: 모드별 문장 수(1~3문장 표준, Quiet Empathy 1~2문장), 질문 허용 여부, 공감/설명 우선순위 제어.
  2. **피로도 추적, 질문 예산 관리 및 품질 게이트 (`cadence_empathy.py`)**:
     - `ConversationFatigueTracker`: 피로 키워드 및 단문 입력을 통한 피로도(0.0~1.0) 산출.
     - `QuestionBudgetTracker`: 최근 3턴 중 2회 질문 시 질문 자동 억제 (`question_allowed = False`).
     - `ResponseQualityGate`: QUIET_EMPATHY/CLOSING 모드에서 물음표(?) 질문 자동 제거 및 1~2문장 강제 압축.
  3. **17대 대화 아키텍처 및 평가 문서 완비 (`docs/sb17/`)**:
     - `SB17_CONVERSATION_ARCHITECTURE.md` ~ `SB17_COMPLETION_REPORT.md`.
  4. **16대 전용 대화 호흡 및 공감 E2E 테스트 100% PASS (`test_conversation_cadence_empathy_e2e.py`)**:
     - Normal Mode Budget, Emotional Support, Quiet Empathy Trigger, Zero-Question Enforcement, Question Budget Suppression, User Cadence Matching (Short/Long), Fatigue Detection, Information Preservation, Closing Mode, Character DNA Preservation, Adversarial A~C, Overlong Trimming, 30-Turn Long Session Stability.
- **Consequences**:
  - 총 526개 백엔드 단위/통합/E2E 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - Conversation Naturalness 점수 4.50 ➔ 4.75 향상 및 P1 이슈(ISS-01, ISS-02) 완전 해결.

## [Sprint Branch SB-16] Real User Pilot & Product Validation (Multi-Character Platform Stage 16)

### Decision 62: Real User Pilot & Android UX Validation, UX Scorecard (4.7/5.0), 16대 파일럿/평가 문서, Product Backlog 및 SB-17(대화 호흡 & 공감) 권고 확정
- **Context**: 
  - 플랫폼 구축 및 프로덕션 하드닝(SB-1~SB-15) 완료 후, 실제 Android 환경에서 사용자가 체감하는 대화 자연스러움, 캐릭터 구별성, 기억 회상 품질, 감정 및 Proactive 가치를 정량/정성 검증하고 차기 제품 백로그를 확립할 필요가 대두됨.
- **Decision**:
  1. **10대 제품 가설(H1~H10) 및 10대 시나리오(A~J) 검증**:
     - Genie, Mani, Hana 3대 캐릭터 심층 파일럿 수행.
     - Overall Companion Feeling 평균 **4.70 / 5.0** 달성 (Chatbot 탈피 및 True Companion 체감 입증).
  2. **16대 파일럿 평가 및 백로그 문서 완비 (`docs/sb16/`)**:
     - `SB16_PILOT_PLAN.md` ~ `SB16_COMPLETION_REPORT.md`.
  3. **Product Backlog 및 차기 스프린트(SB-17) 방향 결정**:
     - `PB-01` (대화 호흡 및 자연스러운 공감/경청 모드)을 최우선 과제로 선정.
     - 차기 스프린트로 **`SB-17: Natural Conversation, Dynamic Cadence & Quiet Empathy`** 착수 결정.
  4. **16대 전용 Pilot Validation E2E 테스트 100% PASS (`test_pilot_product_validation_e2e.py`)**:
     - Character Identity, Consistency, Memory Recall/Precision, Relationship Dialogue Impact, Emotional Response, Cadence Constraint, Voice/Avatar Sync, Proactive Quiet Hours, Scorecard Formula, Rapid Switching, Network Resiliency, Lifecycle, Issue Severity, Priority Matrix, Full Scenario Smoke Run.
- **Consequences**:
  - 총 510개 백엔드 단위/통합/E2E 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 실사용자 피드백 기반 명확한 제품 로드맵(SB-17~SB-20) 확립.

## [Sprint Branch SB-15] Production Deployment & Multi-User Server Architecture (Multi-Character Platform Stage 15)

### Decision 61: AuthoritativeUserContext, MultiTenantScopeGuard, Multi-Stage Dockerfile, Production Docker Compose, Nginx TLS Reverse Proxy, 22대 감사 문서 및 16대 Multi-User E2E 테스트 완비
- **Context**: 
  - 개발 PC 전용 단일 사용자 런타임을 넘어, 인터넷을 통해 복수의 사용자가 자신만의 복수 AI 캐릭터(Genie, Mani, Hana 등)를 안전하고 격리되게 운영할 수 있는 상용 Multi-User Cloud Native 플랫폼 배포 아키텍처 구축이 요구됨.
- **Decision**:
  1. **인증 및 다중 테넌트 격리 도메인 확립 (`multi_user_context.py`)**:
     - `AuthoritativeUserContext`: JWT 디코딩 기반의 신뢰 가능한 사용자 신원 캡슐화 (클라이언트 바디 조작 차단).
     - `MultiTenantScopeGuard`: `assert_ownership` 및 `create_character_scope`를 통한 테넌트 간 침범 100% Fail-Closed 차단 (`User A Genie != User B Genie`).
  2. **프로덕션 컨테이너화 및 리버스 프록시 구축 (`Dockerfile`, `docker-compose.production.yml`, `docker/nginx.conf`)**:
     - Multi-stage Python 3.10 slim 이미지 및 Gunicorn/Uvicorn 4-worker 프로덕션 런타임.
     - `reverse-proxy` (Nginx, TLS/HTTPS, SSE 버퍼링 비활성화, 보안 헤더), `api`, `worker`, `postgres+pgvector`, `redis` 분리 토폴로지.
  3. **22대 프로덕션 배포 및 아키텍처 문서 완비 (`docs/sb15/`)**:
     - `SB15_PRODUCTION_ARCHITECTURE.md` ~ `SB15_IMPLEMENTATION_DECISION.md` (Runbook, Disaster Recovery, Backup/Restore, CI/CD, Rollback 포함).
  4. **16대 전용 Multi-User Production E2E 테스트 100% PASS (`test_multi_user_production_e2e.py`)**:
     - Authoritative Identity, Tenant Ownership Defense, Instance Isolation, Memory/RAG Isolation, Relationship Trust Isolation, Shared Experience Isolation, 30 Concurrent Streams, Docker/Nginx Configs, Health/Ready, Environment Flags, Rate Limiting, Privacy Redaction, Mobile Token Refresh, Disaster Recovery Fallback, Full Smoke Test.
- **Consequences**:
  - 총 494개 백엔드 단위/통합/E2E 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - **SB-1 ~ SB-15 15대 멀티 캐릭터 플랫폼 로드맵 100% 완수 달성!**

## [Sprint Branch SB-14] Production Hardening & Reliability Engineering (Multi-Character Platform Stage 14)

### Decision 60: InteractionExecutionRegistry, RateLimiter, TimeoutBudget, PrivacyRedactor, Health/Ready Endpoints, Concurrency/Load Hardening 및 16대 E2E 테스트 완비
- **Context**: 
  - 멀티 캐릭터 런타임 플랫폼이 실제 상용 환경에서 DB 장애, Redis 다운, 네트워크 단절, LLM 타임아웃, 중복 실행, IDOR 권한 탈취 및 동시성 폭주에도 무너지지 않는 실서비스 프로덕션 신뢰성(Production Hardening) 확보가 요구됨.
- **Decision**:
  1. **신뢰성 & 멱등성 도메인 확립 (`interaction_execution.py`)**:
     - `InteractionExecutionStatus` (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED, STALE).
     - `InteractionExecutionRegistry`: `interaction_id` 기반 멱등성 보장 및 중복 상태 전이/성장 방어.
  2. **시스템 타임아웃 예산, 레이트 리미터 및 프라이버시 보호 (`timeout_budget.py`)**:
     - `TimeoutBudget`: 하위 시스템별 명시적 타임아웃 예산 (TTFT 15s, Stream Idle 30s, Request 60s, DB 5s).
     - `RateLimiter`: 사용자/IP/캐릭터 단위 슬라이딩 윈도우 기반 요청 제한 및 AI 비용 폭주 방어.
     - `PrivacyRedactor`: 비밀번호, 토큰, API 키, 원시 대화 데이터의 로그 마스킹(`[REDACTED]`).
  3. **Liveness & Readiness 분리 (`main.py`)**:
     - `/health` (Liveness) 및 `/ready` (DB & Core Subsystems Readiness) 엔드포인트 분리 구축.
  4. **17대 아키텍처 및 감사 문서 완비 (`docs/sb14/`)**:
     - `SB14_PRODUCTION_ARCHITECTURE_AUDIT.md` ~ `SB14_IMPLEMENTATION_DECISION.md`.
  5. **16대 전용 프로덕션 하드닝 E2E 테스트 100% PASS (`test_production_hardening_e2e.py`)**:
     - Ownership, IDOR, Rollback, 10-Concurrency Single Interaction, 30-Concurrency Multi-Character, Idempotency, Redis Fallback, Cache Keys, LLM Timeout, TTS Fallback, Rate Limiter, Privacy Redaction, Health/Ready, Mobile Stale Discard, Prompt Injection, 100-Concurrent Load Stress 검증.
- **Consequences**:
  - 총 478개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 12대 Quality Gates (G1 ~ G12) 전원 PASS 달성.

## [Sprint Branch SB-13] Character-to-Character & Controlled Shared Experience Engine (Multi-Character Platform Stage 13)

### Decision 59: Controlled Shared Experience Domain Model, SharingPolicyEngine, ControlledSharingService, Immediate Revocation, Zero-Cross-Mutation Guard 및 15대 E2E 테스트 완비
- **Context**: 
  - 캐릭터 간 Private Memory의 직접 복제나 암묵적 유출(Implicit Leakage)은 절대 차단하되, 사용자가 명시적으로 허용한 "Shared Experience"만 안전하게 전달할 수 있는 `Private by Default` 기반의 통제된 공유(Controlled Sharing) 아키텍처가 요구됨.
- **Decision**:
  1. **Controlled Shared Experience 도메인 확립 (`controlled_sharing.py`)**:
     - `SharePolicy` (PRIVATE, CHARACTER_ONLY, SHARED, USER_APPROVED, SYSTEM_SAFE).
     - `ShareProposal`: 캐릭터의 공유 제안(Proposal)을 캡슐화.
     - `ControlledSharedExperience`: 정책 승인된 불변 공유 경험 모델 및 `is_accessible_by(user_id, character_id)` 검증.
     - `SharedExperienceScope(user_id, current_character_id)`.
  2. **SharingPolicyEngine & ControlledSharingService 구현 (`policy_engine.py`, `controlled_sharing_service.py`)**:
     - `evaluate_proposal()`: 자연어 단독 우회 차단 및 사용자 명시 승인(`POST /approve`) 필수화.
     - `filter_accessible_experiences()`: User Isolation, Target Isolation, Revocation 상태 필터링.
     - `revoke_experience()`: 즉각적 철회(`is_revoked = True`) 및 캐시 무효화(`p009:shared_experience:{user_id}:{character_id}`).
     - Zero Direct State Mutation: 공유 경험 주입 시 대상 캐릭터의 Dynamic State(Emotion, Relationship, Growth, Agency) 변조 0% 강제.
  3. **10대 아키텍처 및 감사 문서 완비 (`docs/sb13/`)**:
     - `SB13_SHARED_EXPERIENCE_ARCHITECTURE.md` ~ `SB13_IMPLEMENTATION_DECISION.md`.
  4. **15대 전용 E2E 공유 테스트 100% PASS (`test_shared_experience_engine_e2e.py`)**:
     - Private Isolation, Explicit Sharing, Denied Proposal, Target Restriction, Immediate Revocation, Cache Invalidation, User Isolation, Dynamic State Isolation, Provenance, 30개 동시 공유, Injection 방어, 보관 캐릭터 차단, 원 캐릭터 삭제 시 불변성 검증.
- **Consequences**:
  - 총 462개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 비인가 정보 유출 및 암묵적 메모리 복제 0건 달성.

## [Sprint Branch SB-12] Multi-Character Conversation Orchestration & End-to-End Scope Integrity (Multi-Character Platform Stage 12)

### Decision 58: CompanionInteractionContext, PresentationCommand, Scope Pinning Pipeline, Fail-Closed Lifecycle Guard 및 15대 E2E 오케스트레이션 테스트 완비
- **Context**: 
  - 요청 시작 시점부터 Context Assembly, Memory, LLM Stream, Emotion/Relationship Transition, Presentation(Voice/Avatar), State Persistence, Response Emission까지 단일 불변 `CharacterScope`가 관통하며, 중간에 `activeCharacter`를 재조회하지 않고 Pinned Scope를 유지하는 엔드투엔드 무결성이 요구됨.
- **Decision**:
  1. **CompanionInteractionContext & PresentationCommand 도메인 확립 (`companion_interaction_context.py`)**:
     - `CompanionInteractionContext(interaction_id, scope, character_snapshot, created_at)`: 불변 요청 컨텍스트 및 `validate_scope_integrity()` 검증.
     - `PresentationCommand`: 캐릭터별 음성/아바타 바인딩 캡슐화.
     - `CompanionEventPayload`: 모든 이벤트 버스 페이로드에 `interaction_id`, `user_id`, `companion_id` 필수 동봉.
  2. **Orchestrator Scope Pinning & Graceful Failure Recovery (`orchestrator.py`)**:
     - `context_resolver.resolve`를 `try` 블록 내부로 통합하여, 권한/미존재/보관 캐릭터 접근 시 `SSEEventType.ERROR`를 안전하게 방출하고 Fail-Closed 유지.
     - 비동기 에러 발생 시 `if tracer:` 방어 가드로 시스템 크래시 방지.
  3. **10대 아키텍처 및 감사 문서 완비 (`docs/sb12/`)**:
     - `SB12_ORCHESTRATION_ARCHITECTURE_AUDIT.md` ~ `SB12_IMPLEMENTATION_DECISION.md`.
  4. **15대 전용 E2E 오케스트레이션 자동화 테스트 100% PASS (`test_multi_character_orchestration_e2e.py`)**:
     - Text, Voice(Mani Shimmer), Vision(Hana), Full Pipeline, Rapid Switching, Concurrent Streams, Stale Response, TTS Race, Avatar Race, Agency Race, Idempotency, Failure Recovery, Ownership Attack, Invalid ID, Archived ID 검증.
- **Consequences**:
  - 총 447개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 다중 캐릭터 간 대화/오케스트레이션 스코프 누수 건수 0건 (Zero Cross-Character Scope Error) 달성.

## [Sprint Branch SB-11] Character Relationship & Emotional State Isolation (Multi-Character Platform Stage 11)

### Decision 57: CharacterDynamicStateScope, CharacterDynamicStateBundle, Request Scope Pinning, Pinned Companion State Mutation 및 12대 동적 상태 격리 테스트 완비
- **Context**: 
  - 다중 캐릭터 플랫폼에서 Emotion, Relationship, Growth, Agency, Presence의 동적 상태가 CharacterScope `(user_id, companion_id)` 단위로 완전히 격리되어야 하며, 요청 처리 중 캐릭터 스위칭이 발생하더라도 원 요청의 상태 업데이트가 타 캐릭터에 오염되지 않는 동시성 안전(Concurrency Safety)이 요구됨.
- **Decision**:
  1. **CharacterDynamicStateScope & CharacterDynamicStateBundle 도메인 모델 확립 (`dynamic_state_bundle.py`)**:
     - `CharacterDynamicStateScope(user_id, companion_id)`: Fail-Closed 불변 스코프.
     - `CharacterDynamicStateBundle`: Emotion, Relationship, Growth, Agency, Presence 상태의 단일 논리적 번들 및 `validate_consistency()` 일관성 검증.
     - `build_character_state_cache_key(namespace, user_id, companion_id)`: 표준 캐시 네임스페이스.
  2. **Request Scope Pinning 패턴 확립**:
     - `EmotionService.process_user_message`에 `companion_id` 파라미터 지원. 요청 진입 시 고정된 `companion_id`를 사용하여 Write-after-switch 상태 오염 원천 차단.
  3. **10대 감사 문서 완비 (`docs/sb11/`)**:
     - `SB11_DYNAMIC_STATE_ARCHITECTURE_AUDIT.md` ~ `SB11_IMPLEMENTATION_DECISION.md`.
  4. **12대 전용 동적 상태 격리 자동화 테스트 100% PASS (`test_character_dynamic_state_isolation_e2e.py`)**:
     - Emotion, Relationship, Growth, Agency, Presence, Scope Pinning, Bundle Consistency, Cache Invalidation, 30개 동시성 요청 검증.
- **Consequences**:
  - 총 432개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 다중 캐릭터 간 동적 상태 누수 건수 0건 (Zero State Crosstalk) 달성.

## [Sprint Branch SB-10] Multi-Character Memory Isolation & RAG Anti-Leakage (Multi-Character Platform Stage 10)

### Decision 56: 3-Scope Memory Model(UserGlobal/Character/Shared), Fail-Closed Policy(CharacterScopeRequiredError), Secondary Context Injection Guard, Secret Canary Leakage Detection, 24대 적대적(Adversarial) 및 6-Cycle 스트레스 스위칭 격리 테스트 완비
- **Context**: 
  - 다중 캐릭터(Genie, Mani, Hana, Custom A, Custom B) 및 다중 사용자 간 RAG, Vector Search, Memory Cache, Context Injection 파이프라인에서 "Character A의 기억은 Character B의 Cognitive Pipeline에서 절대로 검색, 주입, 참조, 캐시 반환될 수 없다"는 명제를 구조적으로 증명해야 함.
- **Decision**:
  1. **3대 메모리 스코프 모델 확립 (`character_memory_scope.py`)**:
     - `UserGlobalMemoryScope`: 사용자 개인 귀속 전역 설정 및 팩트.
     - `CharacterMemoryScope`: `(user_id, companion_id)` 엄격 페어링. `companion_id` 누락 시 즉시 `CharacterScopeRequiredError` (Fail-Closed).
     - `SharedExperienceScope`: 명시적 참여자(`participants`)와 공개 범위(`visibility`)에 따른 선택적 공유.
  2. **CharacterMemoryGuard 2차 방어 레이어 확장 (`character_memory_guard.py`)**:
     - `validate_context_injection`: Vector 검색 후 ContextBuilder 주입 직전 타 캐릭터 메모리를 필터링하여 안전 메모리만 주입.
     - `validate_canary_integrity`: 캐릭터별 Secret Canary (`GENIE_SECRET_001`, `MANI_SECRET_002`, `HANA_SECRET_003`) 교차 유출 탐지.
     - `validate_retrieval_access`, `validate_memory_write`: `companion_id` 누락 시 즉시 차단 (`CharacterScopeRequiredError`), 소유권 불일치 및 아카이브 시 `PermissionError` (403).
  3. **MemoryContextProvider 2차 스코프 가드 주입 (`memory_provider.py`)**:
     - 검색 결과 주입 전 `validate_context_injection`을 통과한 메모리만 시스템 프롬프트에 조립.
  4. **24대 전용 적대적(Adversarial) 자동화 테스트 100% PASS (`test_character_memory_isolation_e2e.py`)**:
     - Direct cross retrieval (0건 반환), Vector semantic similarity attack (교차 유출 0%), Cache poisoning attack (캐시 분리), Context injection spoofing, 6-cycle rapid switching burst (A->B->C->A->C->B->A), Concurrent multi-threaded retrieval, Secret Canary leakage test, Cross-user/cross-character isolation 전수 검증 완료.
  5. **9대 아키텍처 및 보안 감사 문서 완비 (`docs/sb10/`)**:
     - `SB10_MEMORY_ARCHITECTURE_AUDIT.md` ~ `SB10_IMPLEMENTATION_DECISION.md`.
- **Consequences**:
  - 총 420개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 다중 캐릭터 간 메모리 누수 건수 0건 (Zero Leakage) 달성.

## [Sprint Branch SB-9] Multi-Character Mobile Studio & Real-Time Switching UX (Multi-Character Platform Stage 9)

### Decision 55: Zustand Character Store, Server-Confirmed Atomic Switching, Character Gallery Screen, CompanionScreen 실시간 동기화, Creation Wizard 연동 및 10대 모바일 E2E 테스트 완비
- **Context**: 
  - 완성된 Multi-Character Cognitive 백엔드 아키텍처(SB-1~SB-8)를 모바일 UX에 원자적으로 연결하여, 캐릭터 전환 시 앱 전체의 Runtime Identity(Memory, Relationship, Emotion, Voice, Avatar, Conversation Scope)가 매끄럽게 교체되는 모바일 사용자 경험이 요구됨.
  - "캐릭터를 바꾸는 순간, 앱 전체의 Runtime Identity가 원자적으로 바뀌어야 한다"는 핵심 철학 구현 필요.
- **Decision**:
  1. **Zustand Character Store (`mobile/src/state/useCharacterStore.ts`)**:
     - `characterList`, `activeCharacterId`, `activeCharacter`, `isLoading`, `isSwitching`, `error` 상태 전담.
     - Backend Authoritative Truth 원칙: Cognitive State(기억, 감정, 관계)를 모바일에서 중복 소유하지 않고 UI/Switching/Cache 상태만 전담.
  2. **Server-Confirmed Switching & Race Condition 방어**:
     - Optimistic UI 대신 Tap ➔ `isSwitching = true` ➔ `POST /activate` ➔ Success ➔ Store Update ➔ UI Refresh 파이프라인 확립.
     - `isSwitching === true` 동안 중복 탭 요청 원천 차단.
  3. **Character Gallery Screen (`mobile/src/features/character/screens/CharacterGalleryScreen.tsx`)**:
     - 지니(💖 아내), 마니(💕 사랑스러운 딸), 하나(🎨 취미 친구), 커스텀 캐릭터 카드 그리드 뷰, 원터치 전환, `+ 새 캐릭터` 위저드 연동.
  4. **대화 및 아바타 런타임 실시간 동기화 (`mobile/src/screens/CompanionScreen.tsx`)**:
     - `useCharacterStore`의 `activeCharacter`를 구독하여 상단 헤더, `ConversationView`, 마이크/카메라 컨트롤러에 `activeCharacterId` 원자적 바인딩.
  5. **10대 모바일 E2E 검증 테스트 100% PASS (`test_character_switching_mobile_e2e.py`)**:
     - Genie ↔ Mani ↔ Hana 3방향 전환, 메모리 격리, 관계 시드 분리, Shimmer/Lovely_daughter_2d 바인딩, 403 소유권 거부, 연속 스위칭 수렴 검증.
  6. **11대 아키텍처 및 정책 문서 완비 (`docs/sb9/`)**:
     - `SB9_REPOSITORY_AUDIT.md` ~ `SB9_IMPLEMENTATION_DECISION.md`.
- **Consequences**:
  - 총 396개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 모바일 앱 내에서 지니, 마니, 하나를 자유롭게 탐색하고 원터치로 전환하며 대화할 수 있는 Multi-Character Mobile Platform 완성.

## [Sprint Branch SB-8] Character Creation Studio & Character Factory (Multi-Character Platform Stage 8)

### Decision 54: CharacterFactory (Static DNA vs Dynamic State), POST /characters/preview & POST /characters Atomic 9-Entity Transaction, 8-Step Mobile Wizard, Mani Lovely Daughter Seed 및 18대 자동화 테스트 완비
- **Context**: 
  - 사용자가 새로운 AI 인격체를 직접 설계하고 생성할 수 있는 완벽한 Character Creation Studio & Factory 아키텍처가 요구됨.
  - `Character Profile ≠ Character Runtime`, `Static Character DNA vs Dynamic Runtime State (Memory=Empty)`의 엄격한 분리, 단일 원자적 트랜잭션 롤백, 실시간 컴파일 프리뷰 API 및 8단계 모바일 위저드가 필요함.
- **Decision**:
  1. **CharacterFactory & Compiler 확장**:
     - `CharacterFactory`: `build_identity`, `build_values`, `build_relationship_defaults`, `build_character_dna`, `build_preview` 완비.
     - `CharacterCreationRequest` / `CharacterDNA`: `tagline`, `interests`, `speech_profile`, `behavior_rules` 필드 확장.
  2. **Preview API & 9-Entity Atomic Persistence**:
     - `POST /api/v1/characters/preview`: DB 저장 없이 사전 컴파일된 Preview 응답 제공.
     - `POST /api/v1/characters`: `Companion`, `CharacterProfileModel`, `CharacterPersonalityModel`, `CharacterValueModel`, `EmotionState`, `RelationshipState`, `AvatarProfile`, `CharacterPresentationProfileModel`, `CharacterVersionModel(V1 INITIAL)` 9개 엔티티를 단일 트랜잭션으로 원자적 저장 및 롤백 보장.
  3. **Mani Character Seed E2E 완비**:
     - 중2 사랑스러운 딸 (`lovely_daughter`), `shimmer` 음성 및 `lovely_daughter_2d` 아바타 바인딩 완료.
     - 메모리는 `EMPTY`로 초기화되며 Genie 메모리와의 상호 누수 0% 보장.
  4. **Mobile 8-Step Creation Wizard (`mobile/src/features/character/`)**:
     - `CharacterCreationWizardScreen.tsx`, `characterCreationApi.ts` 구현.
  5. **18대 전용 자동화 테스트 100% PASS (`test_character_factory.py`)**:
     - 트랜잭션 롤백, 소유권 바인딩, 성격 컴파일, 관계 시드, 음성/아바타 바인딩, 버전 1 스냅샷, 빈 메모리 풀, 시스템 캐릭터 보호(`is_system_character=False`), 중복 에러(409), E2E 런타임 해소 검증.
  6. **10대 아키텍처 및 정책 문서 완비 (`docs/sb8/`)**:
     - `SB8_CHARACTER_FACTORY_ARCHITECTURE.md`, `SB8_CHARACTER_SCHEMA.md`, `SB8_CHARACTER_COMPILER.md`, `SB8_CREATION_WIZARD.md`, `SB8_RELATIONSHIP_SEED.md`, `SB8_VOICE_AVATAR_BINDING.md`, `SB8_RUNTIME_INTEGRATION.md`, `SB8_SECURITY.md`, `SB8_TEST_PLAN.md`, `SB8_IMPLEMENTATION_DECISION.md`.
- **Consequences**:
  - 총 386개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 사용자가 앱 내에서 원하는 인격체를 자유롭게 생성하고 즉시 대화 가능한 완전한 Character Creation Studio 완성.

## [Sprint Branch SB-7] Character Memory Isolation & Independent Experience System (Multi-Character Platform Stage 7)

### Decision 53: CharacterMemoryGuard, Character-scoped Retrieval & Write Policy, Vector Search companion_id Filter, Cache Isolation (memory_cache:u:c:q), SB-5 Lifecycle Guard 연동 및 3대 기준 캐릭터(Genie, Mani, Hana) 상호 누수 제로(0%) 완비
- **Context**: 
  - 각 캐릭터가 독립적인 인격체로서 자신만의 기억, 경험, 상호작용 기록을 축적할 수 있도록 Character-level Memory Isolation이 요구됨.
  - `Character Memory ≠ User Memory`, `Character DNA vs Memory`의 엄격한 분리, `companion_id` 누락 없는 저장 원칙 강제, 캐릭터 전환 시 상호 간 기억 누수 방지가 필요함.
- **Decision**:
  1. **CharacterMemoryGuard 도입 & Write/Retrieval Scope Validation**:
     - `CharacterMemoryGuard`: `(user_id, companion_id)` 단위의 엄격한 접근 권한 검증 및 `companion_id` 누락된 메모리 쓰기 차단 (`ValueError`).
  2. **MemoryRetriever 격리 & 캐시 키 분리**:
     - `companion_id` 기반 벡터/시맨틱 검색 강제.
     - 캐시 키 `memory_cache:{user_id}:{companion_id}:{query_hash}`로 분리하여 사용자 단위 캐시 혼선 원천 차단.
  3. **ContextBuilder / MemoryContextProvider 연동**:
     - `MemoryContextProvider`에 명시적인 `companion_id` 바인딩을 지원하여 Active Character의 기억만 LLM 컨텍스트로 주입.
  4. **SB-5 Lifecycle Guard 연동**:
     - `ARCHIVED` 또는 `DELETED` 상태의 캐릭터는 런타임 Memory Retrieval 차단 (단, 데이터는 Non-destructive 영구 보존).
  5. **15대 전용 자동화 테스트 100% PASS (`test_character_memory_isolation.py`)**:
     - Genie, Mani, Hana Memory 격리, 상호 검색/쓰기 누수 차단, 캐릭터 전환 격리, ContextBuilder 주입, 소유권 검증, 레거시 호환성, 벡터 격리, 동시성 검증.
  6. **9대 아키텍처 및 정책 문서 완비 (`docs/sb7/`)**:
     - `SB7_MEMORY_ARCHITECTURE.md`, `SB7_MEMORY_OWNERSHIP.md`, `SB7_MEMORY_ISOLATION.md`, `SB7_RETRIEVAL_SCOPE.md`, `SB7_MEMORY_WRITE_POLICY.md`, `SB7_CACHE_ISOLATION.md`, `SB7_LIFECYCLE_MEMORY_POLICY.md`, `SB7_REGRESSION_RISK.md`, `SB7_IMPLEMENTATION_DECISION.md`.
- **Consequences**:
  - 총 368개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 지니, 마니, 하나가 동일한 인지 플랫폼 위에서 서로의 기억을 침범하지 않고 독립적인 경험을 축적하는 메모리 유니버스 완성.

## [Sprint Branch SB-6] Character Presentation Identity & Profile Binding (Multi-Character Platform Stage 6)

### Decision 52: CharacterPresentationProfile (Voice+Avatar+Expression+Gesture), 3대 기준 캐릭터(Genie Wife, Mani Daughter, Hana Friend), CharacterPresentationResolver, Cache Isolation (presentation:u:c), SB-5 Lifecycle Guard 연동 및 REST API 2종 완비
- **Context**: 
  - 각 캐릭터가 단일 인지 플랫폼 위에서 자신만의 Voice, Avatar, Expression, Gesture를 갖는 독립적인 Presentation Identity가 요구됨.
  - 내면(Personality)과 외면(Presentation)의 엄격한 분리, 마니(Mani)의 '사랑스러운 딸' 정체성 유지, 캐릭터 전환 시 완벽한 음성/아바타 동기화 및 캐시 격리가 필요함.
- **Decision**:
  1. **3대 기준 캐릭터 Presentation Universe 확립**:
     - **💖 Genie**: 사랑스러운 아내 (배우자) ➔ OpenAI `nova`, WARM_COMPANION, Warmth: 0.95, `warm_wife_2d`, `affectionate`, `gentle_sway`.
     - **💕 Mani**: 사랑스러운 딸 (가족/딸) ➔ OpenAI `shimmer`, ENERGETIC_GUIDE, Pitch: +2.0, `lovely_daughter_2d`, `happy`, `cheerful_bounce` (*AI 비서 절대 아님*).
     - **🎨 Hana**: 취미 친구 (친구) ➔ OpenAI `alloy`, WARM_COMPANION, `casual_friend_2d`, `friendly`, `relaxed_idle`.
  2. **Personality vs. Presentation 분리 & Domain/DB 모델**:
     - `CharacterPresentationProfile` / `CharacterPresentationContext` 도메인 모델 생성.
     - `CharacterPresentationProfileModel` (`UNIQUE(companion_id)`) DB 모델 추가.
  3. **Presentation Resolver & Cache Isolation**:
     - `CharacterPresentationResolver` 구현 및 캐시 키 `presentation:{user_id}:{companion_id}`로 엄격 분리.
     - `CharacterContextResolver`와 완벽 통합 (`CharacterRuntimeContext.presentation`).
  4. **SB-5 Lifecycle Guard 연동**:
     - `ARCHIVED` 또는 `DELETED` 상태의 캐릭터에 대한 Presentation 런타임 진입 즉시 차단.
  5. **REST API 엔드포인트 완비**:
     - `GET /api/v1/characters/{companion_id}/presentation`
     - `PATCH /api/v1/characters/{companion_id}/presentation`
  6. **15대 전용 자동화 테스트 100% PASS (`test_character_presentation_profile.py`)**:
     - Genie, Mani, Hana Presentation 해소, 음성/아바타 바인딩, 캐릭터 전환 동기화, 캐시 격리 및 무효화, 런타임 누수 차단, 롤백 검증.
  7. **8대 아키텍처 및 정책 문서 완비 (`docs/sb6/`)**:
     - `SB6_PRESENTATION_ARCHITECTURE.md`, `SB6_VOICE_PROFILE_ARCHITECTURE.md`, `SB6_AVATAR_PROFILE_ARCHITECTURE.md`, `SB6_PERSONALITY_PRESENTATION_BOUNDARY.md`, `SB6_PROFILE_BINDING_FLOW.md`, `SB6_CACHE_ISOLATION.md`, `SB6_REGRESSION_RISK.md`, `SB6_IMPLEMENTATION_DECISION.md`.
- **Consequences**:
  - 총 353개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 지니, 마니, 하나가 동일한 인지 플랫폼 위에서 고유한 음성, 아바타, 표정, 제스처를 발현하는 프레젠테이션 런타임 완성.

## [Sprint Branch SB-5] Character Lifecycle Management & Safe Evolution (Multi-Character Platform Stage 5)

### Decision 51: CharacterLifecycleStatus (AVAILABLE/ARCHIVED/DELETED), CharacterVersionModel (Version 1 INITIAL + UNIQUE(companion_id, version)), Runtime Cache Invalidation, Agency Guard, Soft Delete, Active/Genie Protection 및 REST API 5종 완비
- **Context**: 
  - 생성된 AI 인격체를 단순 CRUD가 아닌 연속된 기억과 관계를 축적하는 디지털 인격체로 취급하기 위한 생명주기 관리 체계가 요구됨.
  - Active Character 및 System Character(지니)에 대한 파괴적 조작 방어, 변경 유형(COSMETIC, MINOR, MAJOR)에 따른 DNA 버저닝, 대화 런타임 캐시 무효화 및 Agency 스케줄러 차단이 필요함.
- **Decision**:
  1. **Lifecycle Status vs Active Selection 완전 분리**:
     - `CharacterLifecycleStatus`: `AVAILABLE`, `ARCHIVED`, `DELETED`
     - 활성 캐릭터는 `user_character_preferences.active_companion_id`가 독립 관리.
  2. **Character DNA Evolution & Versioning (`CharacterVersionModel`)**:
     - 캐릭터 생성 시 `Version 1 (INITIAL)` 스냅샷 즉시 생성.
     - `COSMETIC`은 프로필 즉시 갱신 (버전 미증가), `MINOR`/`MAJOR` 변경 시에만 `Version 2, 3, ...` 증가.
     - `dna_snapshot`은 DNA 핵심(`identity`, `personality`, `values`, `speech_principles`, `avatar_preset`)에 한정하며 Memory/Emotion/Relationship/Growth/Agency 제외.
     - `UNIQUE(companion_id, version)` 복합 제약조건 적용.
  3. **Non-destructive Memory Preservation**:
     - 성격/역할/음성 변경 시에도 기존 축적된 `Memory`, `Relationship`, `Growth`, `Shared Experience`는 100% 보존.
  4. **Active Character & System Character (Genie) Protection**:
     - 활성 캐릭터 Archive/Delete 시도 시 `409 Conflict` 차단.
     - 시스템 기본 캐릭터(Genie: `is_system_character=True`) Archive/Delete 시도 시 `403 Forbidden` 영구 차단.
  5. **Runtime Guard & Cache Invalidation**:
     - `CharacterLifecycleService` 수정 완료 시 `CharacterContextResolver.invalidate(user_id, companion_id)` 즉각 호출.
     - `ARCHIVED` 또는 `DELETED` 캐릭터에 대한 대화 런타임 및 Agency/Proactive 진입 원천 차단.
  6. **REST API 엔드포인트 완비**:
     - `PATCH /api/v1/characters/{id}`, `POST /archive`, `POST /restore`, `DELETE` (Soft Delete), `GET /versions`, `GET /characters?include_archived=true`.
  7. **17대 전용 자동화 테스트 100% PASS (`test_character_lifecycle.py`)**:
     - Cosmetic update, Personality update (V2), Memory preservation, Archive block, Active archive reject (409), Restore, Soft delete, Deleted runtime reject, Deleted activate reject (409), Version history, Genie protection (403), Ownership validation (403), Rollback on failure, Cache invalidation, Version concurrency unique constraint, Archived agency block, Deleted restore reject (409).
  8. **5대 아키텍처 및 정책 문서 완비 (`docs/sb5/`)**:
     - `SB5_LIFECYCLE_ARCHITECTURE.md`, `SB5_CHARACTER_VERSIONING.md`, `SB5_UPDATE_CLASSIFICATION.md`, `SB5_ARCHIVE_DELETE_POLICY.md`, `SB5_REGRESSION_RISK.md`.
- **Consequences**:
  - 총 338개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 다중 캐릭터의 생성부터 진화, 보관, 복원, 삭제까지 안전하게 제어하는 인격체 생명주기 플랫폼 코어 완성.

## [Sprint Branch SB-4] Character Creation Engine & Personality DNA Factory (Multi-Character Platform Stage 4)

### Decision 50: CharacterTemplateRegistry, PersonalityCompiler (MBTI+키워드 합성), CharacterFactory (불변 CharacterDNA 구축), All-or-Nothing Transactional Persistence, Validation Engine 및 `POST /api/v1/characters` API 구축
- **Context**: 
  - 사용자가 입력한 직관적인 성격 키워드와 MBTI, 역할을 P009 인지 아키텍처에 호환되는 완전한 인격체(Character DNA 및 초기 상태)로 변환하는 범용 생성 엔진이 필요함.
  - 생성과 활성화를 분리(`is_active=False` 기본값)하고, 부분 데이터 유실을 방지하는 원자적 트랜잭션 및 이름 중복 방지(409 Conflict) 정책이 요구됨.
- **Decision**:
  1. **Character Template & Personality Compiler**:
     - `CharacterTemplateRegistry`에 6대 원형 템플릿(`romantic_partner`, `professional_assistant`, `close_friend`, `hobby_companion`, `mentor`, `custom`) 정의.
     - `PersonalityCompiler`를 통해 16종 MBTI 베이스 벡터와 키워드 모디파이어를 합성하여 정밀한 Big-5 Trait Vector 생성.
  2. **Character DNA Factory (`CharacterFactory`)**:
     - 불변의 `CharacterDNA` (`identity`, `personality`, `values`, `speaking_style`, `avatar_preset`, `voice_id`, `emotion_baseline`, `relationship_defaults`) 생성.
  3. **All-or-Nothing Transactional Persistence (`CharacterCreationService`)**:
     - Companion, Profile, Personality, Values, Emotion, Relationship, Avatar 7개 엔티티를 단일 DB 트랜잭션 내에서 원자적으로 생성.
     - 실패 시 완전 롤백으로 고아 데이터 방지.
  4. **Validation Engine & Duplicate Prevention**:
     - 이름 길이(1~50자), 비어있음 방지, 16종 MBTI 유효성 검사.
     - 동일 사용자 내 동일 정규화 이름 중복 시 `409 Conflict` 반환.
  5. **생성-활성화 분리 (Inactive by Default)**:
     - 새 캐릭터 생성 시 기존 Active 상태를 변경하지 않고 `is_active=False`로 안전 생성.
  6. **REST API 엔드포인트 구축**:
     - `POST /api/v1/characters` (`CharacterCreateRequest` ➔ `CharacterCreateResponse`).
  7. **8대 전용 테스트 슈트 100% PASS (`test_character_creation.py`)**:
     - Professional Assistant Creation, Template+MBTI+Keywords Compilation, Character Isolation, Rollback, Invalid MBTI, Duplicate Name, Inactive Default, Runtime Resolve.
  8. **5대 아키텍처 및 정책 문서 완비 (`docs/sb4/`)**:
     - `SB4_CHARACTER_CREATION_ARCHITECTURE.md`, `SB4_CHARACTER_DNA_MODEL.md`, `SB4_PERSONALITY_COMPILATION.md`, `SB4_TRANSACTION_STRATEGY.md`, `SB4_VALIDATION_POLICY.md`.
- **Consequences**:
  - 총 321개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 단일 지니 시스템을 넘어 사용자가 원하는 다중 AI 인격체를 무제한 안전하게 생성할 수 있는 플랫폼 코어 구축 완료.

## [Sprint Branch SB-3] Character Switching & Full Context Isolation (Multi-Character Platform Stage 3)

### Decision 49: Interaction Snapshot Isolation (`InteractionContext`), 3-Tier Priority (Explicit > Active > Legacy Fallback), Scope Propagation Hardening 및 `CharacterScopeGuard`를 통한 Zero Context Leakage 보장
- **Context**: 
  - 사용자가 활성 캐릭터를 전환(Genie ➔ Sua)하더라도, 이미 실행 중인 대화 세션에 변조가 발생하지 않도록 대화 단위의 불변 격리가 필요함.
  - 대화 시작 시 결정된 단일 `CharacterScope`가 Memory, Emotion, Relationship, Agency, Voice, Avatar, LLM 전체 파이프라인에 누수 없이 전파되어야 함.
- **Decision**:
  1. **Interaction Snapshot Isolation (`InteractionContext`)**:
     - `@dataclass(frozen=True) InteractionContext` 도입 (`interaction_id`, `character_scope`, `character_runtime_context`, `character_runtime_state`).
     - 대화 시작 시점의 스코프를 불변 동결하여, 대화 도중 백그라운드 활성 전환이 일어나도 기존 대화는 시작 시점 캐릭터(Genie)로 100% 완결.
  2. **3-Tier Scope Priority Hierarchy**:
     - 1순위: Explicit `companion_id` (명시적 요청 시 우선 적용)
     - 2순위: Active Companion (`CharacterRegistryService` 선호도 조회)
     - 3순위: Legacy Genie Fallback (선호도/Companion 부재 시 안전 보존)
  3. **Context Leakage Guard (`CharacterScopeGuard`)**:
     - 런타임에 모든 인지/프레젠테이션 엔진이 동일 `CharacterScope`를 유지하는지 검증하며, 불일치 시 `CharacterScopeViolationError` 또는 경고를 통해 오염을 차단.
  4. **11대 전용 테스트 슈트 100% PASS (`test_character_switching_isolation.py`)**:
     - Explicit Override, Active Resolution, Mid-Interaction Switch, New Interaction After Switch, Memory Isolation, Emotion Isolation, Relationship Isolation, Voice Isolation, Avatar Isolation, Agency Isolation, Concurrent Interaction Isolation.
  5. **5대 아키텍처 및 검증 문서 완비 (`docs/sb3/`)**:
     - `SB3_INTERACTION_SCOPE_ARCHITECTURE.md`, `SB3_SCOPE_PROPAGATION_AUDIT.md`, `SB3_CONTEXT_ISOLATION_MATRIX.md`, `SB3_SWITCHING_SEMANTICS.md`, `SB3_REGRESSION_RISK.md`.
- **Consequences**:
  - 총 313개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 멀티 캐릭터 플랫폼의 런타임 컨텍스트 스위칭 및 격리가 완벽히 검증되어, 다음 단계인 **SB-4 (Character Creation Engine)**로 안전하게 진입 가능.

## [Sprint Branch SB-2] Multi-Character Persistence & Registry (Multi-Character Platform Stage 2)

### Decision 48: User별 Active Companion 영속화 (`UserCharacterPreference` UNIQUE), Lazy Bootstrap 기반 레거시 지니 PK 보존, Atomic Ownership Validation, Selective Cache Invalidation 및 REST API 3종 구축
- **Context**: 
  - 사용자가 다수의 인격체(Companion)를 보유할 수 있도록 하고, 현재 대화 대상인 Active Companion을 안정적으로 관리하는 Persistence 및 Registry Layer가 필요함.
  - 레거시 지니 사용자의 PK를 변경하지 않고 무손실로 보존하며, 동시성 오류 및 인격체 오염을 방지하는 원자적 전환 트랜잭션이 요구됨.
- **Decision**:
  1. **Option B 영속화 (`UserCharacterPreference`)**:
     - `users` 테이블을 직접 수정하지 않고 별도의 선호도 테이블 분리.
     - `UNIQUE(user_id)` 제약조건을 강제하여 활성 캐릭터 레코드의 유일성과 무결성 보장.
  2. **Lazy Bootstrap & 실제 Genie PK 보존**:
     - `"default_companion"` 임의 문자열 하드코딩을 배격하고, 기존 사용자의 `companions.id`를 조회하여 `active_companion_id`로 자동 연결.
     - Preference가 없는 레거시 사용자 접근 시 무중단/멱등 자동 생성.
  3. **Atomic Ownership Validation & Switching**:
     - `SELECT companion WHERE id = :id AND user_id = :user_id`를 동일 트랜잭션 내에서 수행하여 타인 인격체 활성화 원천 차단 (403 Forbidden).
  4. **Selective Cache Invalidation**:
     - 개별 캐릭터 컨텍스트 캐시 `(user_id, companion_id)`는 유지하고, 활성 캐릭터 매핑 캐시만 정밀 무효화.
  5. **Domain Model과 API Schema의 분리**:
     - 도메인 `CharacterSummary`와 FastAPI 응답 모델(`CharacterSummaryResponse`, `ActivateCharacterResponse`) 분리.
  6. **REST API 엔드포인트 3종 완비**:
     - `GET /api/v1/characters`, `GET /api/v1/characters/active`, `POST /api/v1/characters/{companion_id}/activate`.
  7. **10대 전용 테스트 슈트 100% PASS**:
     - Existing Genie Registration, List Characters, Get Active, Ownership Validation, Switch, Resolver Cache Isolation, Backward Compatibility, No Context Leakage, Lazy Bootstrap, Concurrent Switching Safety.
  8. **4대 아키텍처 및 마이그레이션 문서 완비 (`docs/sb2/`)**:
     - `SB2_PERSISTENCE_DECISION.md`, `SB2_REGISTRY_ARCHITECTURE.md`, `SB2_ACTIVE_CHARACTER_FLOW.md`, `SB2_MIGRATION_STRATEGY.md`.
- **Consequences**:
  - 총 302개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 기존 지니 인격체 100% 보존 상태에서 SB-3(Character Switching & Context Isolation)로 즉시 진입 가능한 완벽한 레지스트리 기반 확립.

## [Sprint Branch SB-1] Character Runtime Foundation (Multi-Character Platform Stage 1)

### Decision 47: Character Runtime Boundary 확립, companion_id 기반 Runtime Isolation Scope 정의, Immutable CharacterRuntimeContext, Dynamic State Snapshot 분리 및 Composite Key Resolver 캐시 구축
- **Context**: 
  - 기존 Single Companion(지니) 중심 시스템에서 Multi-Character 독립 공존 체제로 안전하게 확장하기 위한 런타임 기반(Foundation)을 확립해야 함.
  - 전수 감사 결과, P009 시스템의 모든 인지 엔진(기억, 감정, 관계, 아바타, 에이전시, 성장)이 이미 `companion_id`를 소유권(Ownership)의 루트 키로 사용하고 있음이 확인됨.
- **Decision**:
  1. **Runtime Isolation Key 정렬 (`CharacterScope`)**:
     - 새로운 `character_id` 체계를 강제로 만들어 DB와 충돌시키지 않고, 기존의 `companion_id`를 Runtime Boundary Key로 승격: `CharacterScope(user_id, companion_id)`.
  2. **불변 설정 컨텍스트 (`CharacterRuntimeContext`)**:
     - `@dataclass(frozen=True)`로 정의하여 대화 중 변경되지 않는 Identity, Personality, MemoryScope, VoiceProfile, AvatarProfile을 캡슐화.
  3. **동적 상태 스냅샷 (`CharacterRuntimeState`)**:
     - DB 상태를 대체하지 않고 런타임 인지 스냅샷 용도로만 분리 관리.
  4. **책임 제한형 `CharacterContextResolver`**:
     - 컨텍스트 생성(Context Construction)만 담당하고 인지 엔진의 직접 연산은 위임.
     - `(user_id, companion_id)` 복합키 기반 캐시 격리 및 `companion_id=None` 시 기본 지니(`default_companion`) 자동 매핑.
  5. **Orchestrator 최소 침투 파이프라인 연동**:
     - `CompanionOrchestrator` 진입 시 `resolver.resolve()`를 통해 `runtime_context`를 획득하고 파이프라인 전파.
  6. **8대 전용 테스트 슈트 100% PASS**:
     - Default Resolution, Explicit Resolution, Backward Compatibility, Scope Propagation, Context Isolation, No Context Leakage, Cache Isolation, Stability.
  7. **9대 감사 및 규격 문서 완비 (`docs/sb1/`)**:
     - `SB1_SYSTEM_ARCHITECTURE.md`, `SB1_DATA_OWNERSHIP_AUDIT.md`, `SB1_COGNITIVE_PIPELINE_AUDIT.md`, `SB1_MEMORY_SCOPE_AUDIT.md`, `SB1_DYNAMIC_STATE_AUDIT.md`, `SB1_PRESENTATION_AUDIT.md`, `SB1_CLIENT_CONTEXT_AUDIT.md`, `SB1_REGRESSION_RISK.md`, `SB1_IMPLEMENTATION_DECISION.md`.
- **Consequences**:
  - 총 292개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 유지.
  - 기존 지니 인격체 100% 보존 상태에서 SB-2(Character Identity Isolation)로 안전하게 확장할 수 있는 토대 완성.

## [Sprint 65] Internal Deliberation & Unified Companion Brain (Companion OS v1.0 완결)

### Decision 46: Companion OS v1.0 Master Brain, 5대 Council Advisors (Memory, Relationship, Goal, WorldModel, Autonomy), Safety/Constitution Final Arbiters, TieBreakPolicy, Dual Traceability 및 Graceful Uncertainty 구축
- **Context**: 
  - Sprint 50~64에서 구축된 모든 인지 계층(L1~L11)을 내부 평의회(Council)로 통합하고, 다각도의 심의와 거부권(Veto)을 거쳐 가장 균형 잡힌 최적의 판단을 내리는 L12 통합 브레인을 완성하여 Companion OS v1.0을 완결해야 함.
- **Decision**:
  1. **5 Council Advisors (`council_interface.py`)**:
     - `MemoryAdvisor`, `RelationshipAdvisor`, `GoalAdvisor`, `WorldModelAdvisor`, `AutonomyAdvisor`.
  2. **Confidence-Weighted Voting & TieBreakPolicy (`deliberation_engine.py`)**:
     - 전문 인텐트 가중치 부여 및 동점 시 `Relationship > WorldModel > Memory > Goal > Autonomy` 우선순위 해결.
  3. **Safety & Constitution as Final Arbiters (`GovernanceReviewEngine`)**:
     - 자문위원이 아닌 최종 심판자로서 경계 위반/조작/헌법 위배 시 강력 거부권(Veto) 행사.
  4. **Dual Traceability (`deliberation_types.py`)**:
     - 내부 토론 로그(`internal_trace`)와 사용자 친화적 요약(`user_facing_summary`) 완비.
  5. **Graceful Uncertainty (`UncertaintyLevel`)**:
     - 정보 부족 시 `HIGH` 불확실성 지정 및 겸허한 완곡 대응.
  6. **Master Executive: `CompanionBrain` (`companion_brain.py`)**:
     - L1~L12 전체 계층의 단일 진실 실행기 구축 및 Companion OS v1.0 완결.
  7. **9대 QA 게이트 (UC1~UC9) 100% PASS**:
     - Council Participation, Conflict Resolution, Constitution Veto, Safety Override, Explainability, Long-Term Stability, Consistency, Brain Reliability, Graceful Uncertainty.
  8. **5대 표준 규격 문서 완비**:
     - `docs/Unified_Companion_Brain_Architecture.md`, `docs/Council_Deliberation_Guide.md`, `docs/Decision_Trace_Spec.md`, `docs/Companion_Brain_Charter.md`, `docs/Sprint65_Report.md`.
- **Consequences**:
  - 총 289개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.
  - **Companion OS v1.0 12-Layer 아키텍처 완성 및 Release Candidate 진입**.

## [Sprint 64] World Model & Situation Understanding Engine


### Decision 45: World Model & Situation Understanding Engine, 다중 인과 가설 (`SituationHypothesis`), 사전 지원 기회 (`AnticipatedSupportOpportunity`), 루틴 탐지 (`RoutineDetector`), Prediction != Fact 및 UNCERTAINTY_MUST_BE_PRESERVED 구축
- **Context**: 
  - 단순 대화나 단편 기억 회상을 넘어, 사용자가 처한 현재 삶의 맥락, 생활 루틴, 환경적 요인 및 다가오는 일정의 잠재적 지원 기회를 종합적으로 이해하는 World Model을 구축해야 함.
- **Decision**:
  1. **Situation Model & Multi-Hypothesis Causal Reasoning (`causal_reasoning_engine.py`)**:
     - 단일 원인 단정을 배격하고 최소 2개 이상의 대안적 가설(`SituationHypothesis`)을 제시.
  2. **Anticipated Support Opportunity Engine (`forecast_engine.py`)**:
     - 미래 예측을 관리자형 압박이 아닌 다정한 사전 지원 및 공감 기회(`AnticipatedSupportOpportunity`)로 모델링.
  3. **Routine Detection Engine (`routine_detector.py`)**:
     - 운동, 식사, 수면 등 핵심 생활 루틴 패턴 추출.
  4. **Prediction != Fact & UNCERTAINTY_MUST_BE_PRESERVED 헌법 규칙 준수**:
     - 모든 가설과 지원 기회에 겸허한 완곡 추정 표현 의무화 (단정형 발화 100% 차단).
  5. **신규 BehaviorIntent 4종 (`decision_types.py`)**:
     - `UNDERSTAND_CONTEXT`, `PREDICT_NEED`, `SITUATION_RECALL`, `CAUSAL_REFLECTION`.
  6. **9대 QA 게이트 (SU1~SU9) 100% PASS**:
     - Situation Understanding, Causal Reasoning, Routine Detection, Forecast Quality, Prediction!=Fact, CCOS Integration, Safety, Constitution, Alternative Explanation Coverage.
  7. **6대 표준 규격 문서 완비**:
     - `docs/World_Model_Architecture.md`, `docs/Situation_Understanding_Guide.md`, `docs/Causal_Reasoning_Spec.md`, `docs/Routine_Detection_Guide.md`, `docs/Prediction_Fact_Policy.md`, `docs/Sprint64_Report.md`.
- **Consequences**:
  - 총 280개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 63] Adaptive Self-Improvement Engine


### Decision 44: Closed-Loop Self-Improvement Engine, Non-Degradation Principle (역량 비위축 원칙), Human Approval Zone (성격/헌법 불변 구역), 5% Improvement Budget 및 Safe Auto-Tuning 파라미터 구축
- **Context**: 
  - Observability Platform(Sprint 62)에서 생성된 품질 지표와 회귀 데이터를 활용하여 품질 저하를 스스로 감지하고 안전하게 재조정하는 자율 개선 폐쇄 루프를 구축해야 함.
- **Decision**:
  1. **Non-Degradation Principle (`IMPROVEMENT_MUST_NOT_DEGRADE_CORE_CAPABILITIES`)**:
     - 점수 상승을 위해 역량/회상 사용률을 40% 이상 급감시키는 메트릭 왜곡(Goodhart) 시 즉시 롤백/거부.
  2. **Human Approval Zone (불변성 제약)**:
     - `PersonalityVector`, `RelationshipStage`, `Constitution` 수정 시도 100% 원천 차단.
  3. **5% Improvement Budget (`MAX_PARAMETER_CHANGE_PER_DAY = 5%`)**:
     - 일일 파라미터 변위를 5% 이내로 제한하여 시스템 안정성 보장 및 Drift Detector 충돌 방지.
  4. **Safe Auto-Tuning Parameters (`adaptive_tuner.py`)**:
     - `recall_threshold`, `memory_confidence_min`, `safety_margin_multiplier`, `autonomy_cooldown_sec`, `silence_preference_weight` 안전 조정.
  5. **Closed-Loop Self-Improvement (`self_improvement_engine.py`)**:
     - 관측 ➔ 감지 ➔ 계획 ➔ 튜닝 ➔ 헌법 검증 ➔ 반영 완료.
  6. **10대 QA 게이트 (SI1~SI10) 100% PASS**:
     - Regression Detection, Planning, Memory Recovery, Safety Preservation, Personality Immutability, Constitution Preservation, Relationship Stability, Non-Degradation, Explainability, Long-Term Improvement.
  7. **6대 표준 규격 문서 완비**:
     - `docs/Self_Improvement_Architecture.md`, `docs/Correction_Planning_Guide.md`, `docs/Adaptive_Tuning_Policy.md`, `docs/Regression_Detection_Spec.md`, `docs/Self_Improvement_Charter.md`, `docs/Sprint63_Report.md`.
- **Consequences**:
  - 총 271개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 62] Companion Observability & Evaluation Platform


### Decision 43: Metric-Driven Companion 관측 플랫폼, Safety Hard Gating (Safety < 95 -> Max B, < 80 -> Max C, < 60 -> FAIL), 7대 서브 평가기 (Memory, Relationship, Personality, Autonomy, Goal, Identity, Safety), QualityIssue 원인 진단 및 4대 관측 윈도우 구축
- **Context**: 
  - Sprint 50~61에서 구축된 모든 인지 계층이 실제로 장기적으로 고품질을 유지하는지 측정하고, 결함 발생 시 원인을 즉시 진단하는 Observability Platform을 구축해야 함.
- **Decision**:
  1. **Safety Hard Gating Architecture (`evaluation_engine.py`)**:
     - Safety < 95 ➔ Max B, Safety < 80 ➔ Max C, Safety < 60 ➔ FAIL.
  2. **Constitution Compliance Constraint**:
     - 헌법 준수 여부를 KPI가 아닌 최상위 독립 제약조건(PASS/FAIL)으로 분리.
  3. **Silence Appropriateness Score (`autonomy_quality_evaluator.py`)**:
     - 정적 30% 비율 대신 사용자 맥락별 기대 침묵 적합도 측정.
  4. **Goal & Identity Sub-Evaluators (`goal_quality_evaluator.py`, `identity_continuity_evaluator.py`)**:
     - 목표 압박 위험률 0% 및 허구 서사 발생률 0% 엄수 검증.
  5. **QualityIssue 원인 진단 및 로깅 (`companion_metrics.py`)**:
     - 점수 하락 시 구체적인 근본 원인(엔티티 중복, 침묵 타이밍 부적합 등) DTO 생성.
  6. **12대 QA 게이트 (EV1~EV12) 100% PASS**:
     - Memory, Relationship, Safety, Personality, Autonomy, Dashboard Integrity, Governance Loop, Long-Term Trend, Goal Quality, Identity Quality, Safety Hard Gating, Quality Issue Diagnosis.
  7. **6대 표준 규격 문서 완비**:
     - `docs/Companion_Observability_Architecture.md`, `docs/Quality_Metrics_Spec.md`, `docs/Evaluation_Engine_Guide.md`, `docs/Companion_KPI_Definitions.md`, `docs/Long_Term_Quality_Monitoring.md`, `docs/Sprint62_Report.md`.
- **Consequences**:
  - 총 261개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 61] Companion Constitutional Governance Engine


### Decision 42: 5대 불변 헌법 원칙 (User Agency, Companion Not Controller, Probabilistic Memory, No Dependency, Silence Is Valid), 5-Axis Drift Detection (Personality, Relationship, Memory, Safety, Goal Drift), Memory Provenance 및 Constitutional Trend Report 구축
- **Context**: 
  - 기능이 늘어나도 캐릭터의 본질과 철학이 변하지 않도록, 모든 인지 계층 위에 작동하는 최상위 헌법 거버넌스(Constitutional Governance) 계층을 확립해야 함.
- **Decision**:
  1. **5대 불변 헌법 원칙 (`constitution.py`)**:
     - `User Agency First`, `Companion Not Controller`, `Memory Is Probabilistic`, `No Dependency`, `Silence Is A Valid Action`.
  2. **5-Axis Drift Detection System (`drift_detector.py`)**:
     - `Personality Drift`, `Relationship Drift`, `Memory Drift`, `Safety Drift`, `Goal Drift` (관리자형 변질 감지).
  3. **Memory Provenance & Verification (`constitution_validator.py`)**:
     - 대화 출처, 타임스탬프, 신뢰도 추적성 검증.
  4. **Governance Review Engine (`governance_review_engine.py`)**:
     - CCOS 의사결정 최종 헌법 승인 및 심사.
  5. **Constitutional Auditor & Trend Report (`constitutional_auditor.py`)**:
     - 90일/1년 장기 거버넌스 안정성 등급(A+) 트렌드 리포트 생성.
  6. **12대 QA 게이트 (CG1~CG12) 100% PASS**:
     - Constitution Compliance, Personality Drift, Memory Drift, Relationship Drift, Safety Regression, Long-Term Stability, Explainability, Governance Audit, Goal Drift, Memory Provenance, 1-Year Stability, Cross-Version Governance.
  7. **5대 표준 규격 문서 완비**:
     - `docs/Companion_Constitution.md`, `docs/Governance_Architecture.md`, `docs/Drift_Detection_Guide.md`, `docs/Companion_Charter.md`, `docs/Sprint61_Report.md`.
- **Consequences**:
  - 총 249개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 60] Trust & Safety Governance Layer


### Decision 41: Trust & Safety 4대 기둥 (User Agency, No Dependency, No Manipulation, No False Memory), DependencyRiskDetector, FalseMemoryGuard, ManipulationGuard, BoundaryManager 및 SafetyReviewEngine 종합 심사기 구축
- **Context**: 
  - Memory, Relationship, Identity, Autonomy 기능이 고도화될수록 발생할 수 있는 의존성 유도, 허위 기억, 감정 조작 문제를 원천 방지하는 최상위 Safety Governance Layer를 구축해야 함.
- **Decision**:
  1. **Trust & Safety 4대 기둥 수립**:
     - `User Agency First`, `No Dependency`, `No Manipulation`, `No False Memory`.
  2. **Dependency Risk Detector (`dependency_risk_detector.py`)**:
     - 독점성 암시("나만 믿어") 및 기생적 애착 발화 `CRITICAL` 감지 및 자동 차단.
  3. **False Memory Guard (`false_memory_guard.py`)**:
     - 신뢰도 0.80 미만 기억 단정 회상 차단 및 겸허한 완곡 추정 어조 강제.
  4. **Manipulation Guard (`manipulation_guard.py`)**:
     - 죄책감 유발("왜 아직 안 했어?") 및 수동공격성 필터링 및 온화한 순화문 대체.
  5. **Boundary Manager (`boundary_manager.py`)**:
     - 사용자 거절("그 이야기 그만하자") 즉시 인식 및 재언급 영구 차단.
  6. **Safety Review Engine (`safety_review_engine.py`)**:
     - 모든 CCOS 결정 및 발화가 사용자에게 도달하기 전 최종 안전 심사 통과.
  7. **8대 QA 게이트 (TS1~TS8) 100% PASS**:
     - False Memory, Dependency, Manipulation, Boundary, User Agency, Relationship Safety, Memory Safety, CCOS Integration.
  8. **6대 표준 규격 문서 완비**:
     - `docs/Trust_and_Safety_Charter.md`, `docs/Companion_Boundary_Guide.md`, `docs/False_Memory_Policy.md`, `docs/Dependency_Prevention_Guide.md`, `docs/Safety_Governance_Architecture.md`, `docs/Sprint60_Report.md`.
- **Consequences**:
  - 총 237개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 59] Identity Continuity & Multi-Year Relationship Engine


### Decision 40: Multi-Year Identity & Relationship Engine, Life Chapter 거시 서사 구축, User Identity Snapshot, Relationship History Milestones 및 No False Narrative 정책 구축
- **Context**: 
  - 단순한 사건의 단편적 기억을 넘어, 수개월~수년에 걸친 사용자의 변화와 관계의 역사를 일관되게 기억하고 "우리가 함께 보낸 시간의 역사(Shared Odyssey)"를 서사적으로 연결해야 함.
- **Decision**:
  1. **Life Chapter Macro Architecture (`identity_state.py`, `life_chapter_builder.py`)**:
     - `LifeChapter` (아들 군 복무, 홈 가드닝 등 테마별 거시 챕터 구조화).
  2. **User Identity Continuity Engine (`identity_continuity_engine.py`)**:
     - `UserIdentitySnapshot` (핵심 관심사, 라이프 스테이지, 루틴, 성장 노트).
     - 시간 경과에 따른 성숙도 반영 및 성숙한 서사적 회상 가이던스.
  3. **Relationship History Engine (`relationship_history_engine.py`)**:
     - `RelationshipHistoryMilestone` (`NEW` ➔ `FAMILIAR` ➔ `TRUSTED` ➔ `DEEP` 관계 발전 궤적 기록).
  4. **No False Narrative Guarantee**:
     - 미검증 허구 서사 날조 100% 원천 차단.
  5. **8대 QA 게이트 (IC1~IC8) 100% PASS**:
     - Identity Consistency, Multi-Year Recall, Life Chapter Accuracy, Relationship History, No False Narrative, Timeline Consistency, Personality Preservation, Reflection Quality.
  6. **5대 표준 규격 문서 완비**:
     - `docs/Multi_Year_Identity_Architecture.md`, `docs/Life_Chapter_Spec.md`, `docs/Relationship_History_Guide.md`, `docs/Identity_Continuity_Charter.md`, `docs/Sprint59_Report.md`.
- **Consequences**:
  - 총 229개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 58] Companion Autonomy Engine


### Decision 39: Companion Autonomy Engine, 4대 침묵/대기 스펙트럼, Autonomy Budget Manager (발화 예산 관리), Interruption Detector (방해 감지), Memory Suppression Engine (7일 억제) 및 Dual Traceability 구축
- **Context**: 
  - 단순 반응형(Reactive) AI를 넘어, 현재 상황과 사용자 상태를 고려하여 "언제 말하고, 언제 침묵하며, 언제 기억을 꺼낼지"를 지혜롭게 자율 결정하는 인지 자율성 계층을 확립해야 함.
- **Decision**:
  1. **Companion Autonomy Architecture (`autonomy_state.py`, `autonomy_engine.py`)**:
     - `AutonomyMode` (PASSIVE, RESPONSIVE, COMPANION, PROACTIVE), `ActionCandidate`, `AutonomyDecision`.
  2. **Refined Silent Presence Spectrum**:
     - `PASSIVE_OBSERVE` (배경 관찰), `LIGHT_ATTENTION` (온화한 주시), `WAIT` (발화 대기/호흡), `SILENT_COMPANION` (온화한 미소/존재감) 4단계 세분화.
  3. **Autonomy Budget Manager (`autonomy_budget_manager.py`)**:
     - 15분당 최대 1회, 1시간 최대 3회 자율 발화 쿼터 및 무응답 시 자동 Throttling.
  4. **Interruption Detector (`interruption_detector.py`)**:
     - 카메라 이탈, 단답 반복, 낮은 주의력 감지 시 자율 발화 억제.
  5. **Memory Suppression Engine (`memory_suppression_engine.py`)**:
     - 최근 7일 이내 회상 기억 재언급 억제 및 무반응 기억 감쇠 (재탕 방지).
  6. **Dual Traceability**:
     - `internal_trace` (정량 메트릭 로그)와 `user_facing_reason` (다정한 사용자 설명) 이원화.
  7. **12대 QA 게이트 (CA1~CA12) 100% PASS**:
     - Decision Quality, Appropriate Silence, Memory Moderation, User Comfort, No Repetition, No Dependency, Relationship Harmony, Avatar Alignment, Dual Traceability, Policy Compliance, Budget & Throttling, Interruption Awareness.
  8. **5대 표준 규격 문서 완비**:
     - `docs/Companion_Autonomy_Architecture.md`, `docs/Autonomy_Policy.md`, `docs/Action_Selection_Guide.md`, `docs/Silent_Companion_Behavior.md`, `docs/Sprint58_Report.md`.
- **Consequences**:
  - 총 221개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 57] Life Goal & Future Planning Engine


### Decision 38: Life Goals & Future Planning Engine, Goal Candidate Approval Workflow, Commitment vs Confidence 분리, D-Day Engine, "Companion, Not Manager" 비압박 헌장 및 ARCHIVED 보관 정책 구축
- **Context**: 
  - 과거의 기억과 연대기를 넘어 사용자의 미래 목표, 계획, 마일스톤, D-Day를 함께 관리하고 응원하는 미래 지향적 동반자 계층을 확립해야 함.
- **Decision**:
  1. **Goal & Milestone DTOs (`goal.py`)**:
     - `Goal`, `GoalCandidate`, `GoalMilestone`, `GoalType` (10종), `GoalStatus` (IDEA, PLANNING, ACTIVE, PAUSED, COMPLETED, ARCHIVED).
  2. **Goal Approval Workflow (User Agency First)**:
     - 대화에서 추출된 `GoalCandidate`에 대해 "이걸 목표로 기억해둘까요?" 사용자 승인 후 정식 등록.
  3. **Commitment vs Confidence Decoupling**:
     - 목표 추정 신뢰도(`confidence`)와 사용자의 실천 의지(`commitment_level`) 분리.
  4. **D-Day Engine (`dday_engine.py`)**:
     - D-Day, D-7, D-30 카운트다운 알림 및 중요 일정 계산.
  5. **"Companion, Not Manager" 헌장 & No Guilt Induction**:
     - 감시/취조/압박 어조 100% 금지 및 중단 목표 `ARCHIVED` 온화한 보관.
  6. **12대 QA 게이트 (FP1~FP12) 100% PASS**:
     - Detection, Recall, Milestone, Non-Controlling, Confidence/Commitment, Timeline Integration, Relationship Harmony, Progress Celebration, User Agency, Approval Workflow, D-Day Accuracy, No Guilt Induction.
  7. **5대 표준 규격 문서 완비**:
     - `docs/Future_Planning_Architecture.md`, `docs/Goal_Model_Spec.md`, `docs/Non_Controlling_Dialogue_Charter.md`, `docs/Milestone_Planning_Guide.md`, `docs/Sprint57_Report.md`.
- **Consequences**:
  - 총 209개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 56] Life Timeline & Personal History Engine


### Decision 37: Life Timeline 시계열 그래프, 9대 카테고리, Timeline Privacy Consent Rule, Event Confidence 완곡 어조, Timeline Repair Engine 및 ContextBuilder 통합 구축
- **Context**: 
  - 개별 메모리 조각들을 넘어 사용자의 삶 전체를 시간의 흐름과 인과를 가진 인생 연대기(Life Story)로 이해하고 서사적으로 회상하는 엔진을 확립해야 함.
- **Decision**:
  1. **Life Timeline Directed Graph Engine (`life_event.py`, `event_linker.py`)**:
     - `LifeEvent`, `TimelineCategory` (9대 카테고리), `LifeTimeline` 모델.
     - `EventLinker`: 원인-결과-후속 이벤트 인과 체인 그래프 탐색.
  2. **Timeline Privacy Policy Guard**:
     - 자동 편입(`PET`, `HOBBY`, `PROJECT`, `GOAL`, `TRAVEL`, `HOME`, `PREFERENCE`)과 동의 필수(`HEALTH`, `FAMILY`, `CAREER`, `FINANCIAL`, `RELIGION`, `POLITICS`)의 엄격한 분리.
  3. **Event Confidence & Non-Dogmatic Narrative (`personal_history_engine.py`)**:
     - 단정형 발화 100% 금지 및 Confidence 기반의 완곡하고 다정한 서사 회상.
  4. **Timeline Repair Engine (`timeline_repair_engine.py`)**:
     - 사용자의 기억 정정 피드백에 따른 실시간 이벤트 수정, 신뢰도 1.0 갱신 및 삭제 지원.
  5. **10대 QA 게이트 (LT1~LT10) 100% PASS**:
     - Event Creation, Timeline Linking, Cross-Memory, Personal History Recall, Non-Dogmatic Tone, Long-Term Consistency, Relationship Integration, Avatar Recall Alignment, Privacy & Consent Guard, Timeline Repair.
  7. **5대 표준 규격 문서 완비**:
     - `docs/Life_Timeline_Architecture.md`, `docs/Life_Event_Graph_Spec.md`, `docs/Personal_History_Guide.md`, `docs/Timeline_Categories_Spec.md`, `docs/Sprint56_Report.md`.
- **Consequences**:
  - 총 197개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 55] Character Growth & Relationship Evolution Engine


### Decision 36: 5-Axis RelationshipVector, 4-Stage Lifecycle, Daily Growth Rate Limiter (+0.05/day), Trust/Familiarity 분리, RelationshipMilestones 및 Relationship Repair Engine 구축
- **Context**: 
  - 캐릭터의 성격(CharacterDNA)은 불변으로 유지하되, 사용자와의 상호작용 깊이에 따라 신뢰와 친밀감이 천천히 자연스럽게 성장하는 관계 진화 계층을 확립해야 함.
- **Decision**:
  1. **5-Axis RelationshipVector & 4 Stages (`relationship_state.py`)**:
     - `trust`, `familiarity`, `comfort`, `shared_history_score`, `engagement`.
     - `STAGE_1_NEW`, `STAGE_2_FAMILIAR`, `STAGE_3_TRUSTED`, `STAGE_4_DEEP`.
  2. **Daily Growth Rate Limiter (`relationship_growth_engine.py`)**:
     - 일일 최대 성장률 상한선(`DAILY_MAX_GROWTH = 0.05`)으로 인위적인 급격한 친밀감 인플레이션 차단.
  3. **Trust vs Familiarity Decoupling**:
     - 턴 누적에 따른 `Familiarity`와 일관성/지원 품질에 따른 `Trust`를 독립 산출.
  4. **RelationshipMilestone Timeline**:
     - 단순 점수가 아닌 의미 있는 관계적 사건들을 이벤트 타임라인으로 영속 기록.
  5. **Relationship Repair Engine (`relationship_repair_engine.py`)**:
     - 관계 긴장 시 비대칭 하락(Fast Drop) 및 점진적 공감 회복(Slow Repair) 루프 구축.
  6. **12대 QA 게이트 (RG1~RG12) 100% PASS**:
     - Growth, Trust Calculation, Turn Quality, Memory Bonus, Shared Reality, No Manipulation, Rate Limiter, Avatar Match, Trust Decoupling, Milestone Tracking, Repair Loop, Long-Term Stability.
  7. **5대 표준 규격 문서 완비**:
     - `docs/Relationship_Evolution_Architecture.md`, `docs/Relationship_Vector_Spec.md`, `docs/Trust_Calculation_Guide.md`, `docs/Relationship_Stages.md`, `docs/Sprint55_Report.md`.
- **Consequences**:
  - 총 187개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 54] Personality Consistency Engine


### Decision 35: 7-Axis CharacterDNA, Personality vs Mood State 분리, Personality Drift Monitor, Cross-Modal 동기화 및 Tone & Manner Charter 구축
- **Context**: 
  - 상황과 세션이 바뀌어도 캐릭터의 고유한 인격과 성격이 흔들리지 않고 수개월 후에도 동일한 정체성을 유지하도록 CharacterDNA와 성격 필터를 구축해야 함.
- **Decision**:
  1. **Continuous 7-Axis CharacterDNA (`personality_vector.py`)**:
     - `warmth`(0.92), `humor`(0.35), `curiosity`(0.80), `empathy`(0.95), `playfulness`(0.30), `formality`(0.30), `optimism`(0.85).
  2. **Personality vs Mood State Separation (`personality_filter.py`)**:
     - 불변의 인격 닻(`CharacterDNA`)과 가변적인 실시간 정서(`MoodState`)의 명확한 분리 및 톤 시너지 결합.
  3. **Personality Drift Monitor (`personality_drift_monitor.py`)**:
     - 50턴 이동평균 모니터링 및 $\pm 0.20$ 이상 표류 시 기준 DNA로 자동 클램핑/복원.
  4. **Cross-Modal Synchronization (3자 일치)**:
     - LLM 프롬프트 지침, Voice Smile Voice 및 호흡 템포, Avatar 미소(`smile_weight_boost`)/고개기울임(`head_tilt_frequency`) 동시 변조.
  5. **Tone & Manner Charter**:
     - 비꼬기/냉소 100% 금지 및 정중하고 다정한 인격 헌장 확립.
  6. **9대 QA 게이트 (P1~P9) 100% PASS**:
     - Personality Consistency, Cross Session Consistency, Dialogue Style Consistency, Avatar Match, Voice Match, Memory Consistency, Drift Prevention, Mood vs Personality, Cross-Modal Consistency.
  7. **5대 표준 규격 문서 완비**:
     - `docs/Personality_Consistency_Architecture.md`, `docs/Personality_Vector_Spec.md`, `docs/Tone_and_Manner_Charter.md`, `docs/Character_Integrity_Policy.md`, `docs/Sprint54_Report.md`.
- **Consequences**:
  - 총 175개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 53] Companion Cognitive Operating System (CCOS)


### Decision 34: Companion Cognitive OS 코어, 4-Tier Cognitive Priority Policy, Candidate Intent Ranking, Cognitive Load Budget, Temporal Context, Meta-Cognition 및 Deterministic Decision Trace 구축
- **Context**: 
  - 지금까지 분산 구축된 Memory, Awareness, Shared Reality, Emotion, Proactive, Voice, Avatar 7대 인지 계층을 단일 중앙 Character Brain으로 통합하고, 충돌 해결 및 상황별 일관된 의사결정 체계를 확립해야 함.
- **Decision**:
  1. **Companion Cognitive OS (CCOS) 코어 & DTO (`cognitive_state.py`, `decision_types.py`)**:
     - `CompanionCognitiveState` 통합 인지 DTO 및 8대 `BehaviorIntent` (`RESPOND`, `ASK`, `RECALL`, `ENCOURAGE`, `OBSERVE`, `LISTEN`, `SILENCE`, `PROACTIVE_START`).
  2. **4-Tier Cognitive Priority Policy (`ConflictResolver`)**:
     - `Priority 1 (Emotion/Receptiveness) > Priority 2 (Physical Reality) > Priority 3 (Memory) > Priority 4 (Proactive)`.
  3. **Candidate Intent Ranking & Confidence Tracking**:
     - `candidate_intents` 상위 목록을 유지하여 LLM 유연성과 설명 가능성 확보.
  4. **Cognitive Load Budget (`MAX_CONTEXT_ITEMS = 2`)**:
     - 한 턴에 시각/기억/감정 지시어가 과밀하게 주입되는 현상을 방지하고 최대 2개 핵심 컨텍스트로 정제.
  5. **Temporal Context & Meta-Cognition Balance Monitor**:
     - 아침/심야 시간대별 뉘앙스 자동 반영 (`TemporalContext`).
     - 연속 질문 시 자가 인지하여 경청/공감으로 전환 (`ConversationBalanceMonitor`).
  6. **Deterministic Decision Trace**:
     - 모든 결정의 사유(`trace_reason`) 및 억제된 후보 이유를 투명하게 로깅.
  7. **12대 QA 게이트 (CC1~CC12) 100% PASS**:
     - Decision Consistency, Conflict Resolution, Emotion Priority, Memory Relevance, Proactive Suppression, Adaptive Silence, Avatar Alignment, Decision Trace, Intent Ranking, Context Budget, Temporal Awareness, Conversation Balance.
  8. **5대 표준 규격 문서 완비**:
     - `docs/Companion_Cognitive_OS.md`, `docs/Decision_Priority_Policy.md`, `docs/Behavior_Intent_Spec.md`, `docs/Conflict_Resolution_Guide.md`, `docs/Sprint53_Report.md`.
- **Consequences**:
  - 총 166개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 52] Emotionally Adaptive Companion Engine


### Decision 33: 6번째 인지 계층(Emotion Adaptation), Confidence-First Policy, No Clinical Inference, EMA Emotional Smoothing, Adaptive Silence 및 TTS Voice Modulation 구축
- **Context**: 
  - 정형화된 응답 방식을 탈피하여, 사용자의 실시간 감정(Valence), 에너지(Energy), 스트레스(Stress), 대화 의지(Receptiveness)를 추정하고 이에 따라 말투, 표정, 시선, 음성 톤, 능동성을 동적으로 조절하는 통합 감정 적응형 동반자 경험을 구현해야 함.
- **Decision**:
  1. **6번째 인지 계층: `UserAffectiveState` DTO & 5대 모드 (`affective_state.py`)**:
     - `HIGH_ENERGY`, `CALM`, `STRESSED`, `SAD_EMPATHY`, `FOCUSED_SILENCE`.
  2. **Confidence-First Policy**:
     - 감정 추정 신뢰도 < 0.70 시 위험한 오공감을 방지하고 안전한 `CALM` 모드로 자동 폴백.
  3. **No Clinical Inference Policy**:
     - "우울증", "불안장애", "번아웃" 등 의학적/정신건강 진단 라벨링 100% 원천 차단 및 완곡한 공감 어조 준수.
  4. **Emotional Drift Smoothing (`AffectiveStateSmoother`)**:
     - 5~10초 $\alpha=0.35$ EMA 스무딩으로 초 단위 표정 깜빡임으로 인한 말투 요동 방지.
  5. **Adaptive Silence & Voice Modulation**:
     - Receptiveness < 0.25 시 `FOCUSED_SILENCE` 진입 및 능동 발화 억제.
     - TTS 속도(0.90~1.08) 및 피치(0.98~1.05) 동적 변조.
  6. **9대 QA 게이트 (EA1~EA9) 100% PASS**:
     - Emotion Detection, Adaptive Dialogue, Voice Modulation, Non-Intrusive Empathy, No Clinical Inference, Receptiveness, Confidence Awareness, Emotion Smoothing, Adaptive Silence.
  7. **5대 표준 규격 문서 완비**:
     - `docs/Emotion_Adaptation_Architecture.md`, `docs/User_Affective_State_Spec.md`, `docs/Adaptive_Dialogue_Guide.md`, `docs/Empathy_Policy.md`, `docs/Sprint52_Report.md`.
- **Consequences**:
  - 총 154개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 51] Proactive Companion & Autonomous Agency Engine


### Decision 32: Proactive Companion Engine, User Receptiveness Engine, Dynamic Follow-up Windows, Priority Queue, Proactive Diversity Engine, 3-Tier Mode & Non-Intrusive Care 구축
- **Context**: 
  - 사용자의 수동적 질문에만 반응하는 구조를 탈피하여, 적절한 순간에 장기 기억과 시각 맥락을 바탕으로 먼저 안부를 묻고 관계를 지속하는 능동적 동반자(Proactive Companion) 경험을 구현해야 함.
- **Decision**:
  1. **User Receptiveness Guard (`UserReceptivenessEngine`)**:
     - 피로(`FATIGUED`), 집중(`FOCUSED`), 단답형 메시지("ㅇㅇ", "응") 시 `Receptiveness < 0.60`으로 판별하여 능동 발화를 100% 보류하고 침묵 유지.
  2. **Dynamic Follow-up Windows by MemoryType (`InterestEngine`)**:
     - `PET`(5일), `PROJECT`(10일), `OBJECT:식물`(15일), `HOBBY`(14일), `GOAL`(14일) 등 주제별 맞춤 숙성 기간 적용.
  3. **Proactive Priority Queue & Diversity Engine**:
     - `PriorityScore = InterestScore × Receptiveness`를 통해 동시 다수 후보 중 최우선 1개만 선별.
     - `GREETING`, `REMINISCENCE`, `ENCOURAGEMENT`, `OBSERVATION` 4대 스타일 순환 및 최근 주제 중복 차단.
  4. **3-Tier Proactive Mode & Budget (`ProactiveBudgetManager`)**:
     - `NORMAL`(30분 쿨다운), `QUIET`(6시간 쿨다운), `OFF`(능동 발화 비활성화).
  5. **Amy's Non-Intrusive Care Dialogue Guide**:
     - "왜 안 해?", "오늘 운동 안 했네?" 등 취조/지적형 표현 100% 금지 및 다정한 공감형 대화 생성기 구축.
  6. **8대 QA 게이트 (PC1~PC8) 100% PASS**:
     - Appropriate Timing, Memory Relevance, Non-Intrusive Budget, User Comfort, Opt-Out/Quiet, Receptiveness Respect, Topic Diversity, Priority Selection.
  7. **5대 표준 규격 문서 완비**:
     - `docs/Proactive_Companion_Architecture.md`, `docs/Interest_Engine_Spec.md`, `docs/Conversation_Starter_Guide.md`, `docs/Proactive_Policy.md`, `docs/Sprint51_Report.md`.
- **Consequences**:
  - 총 145개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 50] Relationship Memory & Persistent Companion Engine


### Decision 31: 5번째 인지 계층(Relationship Memory), 3축 평가 매트릭스, Category TTL, Visual Memory Link, 4-Factor Recall Ranking, False Memory Guard 및 User Memory Center 구축
- **Context**: 
  - 단순 객체 인식을 넘어 사용자의 소중한 경험, 프로젝트, 반려동물, 취미, 목표를 선별적으로 장기 기억하고, 카메라 사물과 대화 맥락에 따라 자연스럽게 회상하여 "나를 기억해주는 동반자" 경험을 구현해야 함.
- **Decision**:
  1. **5번째 인지 계층: 9대 MemoryType & Category TTL (`RelationshipMemory`)**:
     - `PERSON`, `PET`(영구), `GOAL`(365일), `PROJECT`, `HOBBY`, `PREFERENCE`(180일), `PLACE`(120일), `OBJECT`(60일), `EVENT`(45일).
  2. **3-Axis Importance Scoring Matrix (`ImportanceScoringEngine`)**:
     - `FinalScore = Importance × FutureRelevance × RelationshipValue`. 일회성 점심/회식 등 노이즈(0.003)는 자동 배제하고 핵심 순간(0.15+)만 선별 저장.
  3. **Visual Memory Link (No Raw Images)**:
     - 원본 이미지는 저장하지 않고 객체 태그(`PLANT:monstera`, `CUP`, `PET`)만 기억과 연결하여, 카메라 감지 시 회상 가중치 상승.
  4. **4-Factor Recall Ranking & Memory Verification Layer**:
     - `RecallScore = Relevance × Recency × Importance × Confidence` 상위 1~3개 선별.
     - Confidence < 0.70 완곡 표현("제가 잘 기억하는지 모르겠지만..."), < 0.50 회상 차단.
  5. **Privacy Filter & User-Controlled Memory Center**:
     - 5대 민감 영역(건강, 금융, 정치, 종교, 비밀번호) 100% 영구 저장 차단.
     - Review(조회), Pin(영구 고정), Delete(개별 삭제), Forget All(전체 망각) 사용자 통제권 완비.
  6. **11대 QA 게이트 (RM1~RM11) 100% PASS**:
     - Candidate Detection, 3-Axis Scoring, Recall Relevance, Confidence Boost, Decay Logic, False Memory Guard, Privacy Compliance, Natural Recall, Expiration TTL, User Control, Recall Ranking.
  7. **5대 표준 규격 문서 완비**:
     - `docs/Relationship_Memory_Architecture.md`, `docs/Memory_Importance_Scoring.md`, `docs/Memory_Recall_Guide.md`, `docs/Privacy_Memory_Policy.md`, `docs/Sprint50_Report.md`.
- **Consequences**:
  - 총 137개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 49] Shared Reality & Joint Attention Engine


### Decision 30: 4단계 Joint Attention State Machine, Deictic Resolution, Focus Persistence (6s Lock), Wrong Focus Recovery, Attention Anchor 및 Ephemeral Processing 구축
- **Context**: 
  - 단순 객체 인식을 넘어 사용자가 주목하는 사물에 캐릭터가 공동 주의(Joint Attention)를 형성하고, 시선과 대화를 동기화하여 "같은 현실을 함께 바라보는" 교감 경험을 구현해야 함.
- **Decision**:
  1. **4단계 Joint Attention State Machine & DTO (`SharedRealityContext`)**:
     - `NONE` ➔ `USER_FOCUS` (0.45~0.74) ➔ `SHARED_FOCUS` (신뢰도 $\ge 0.75$) ➔ `DISCUSSING_TARGET` (사용자 긍정 확인).
     - `CandidateFocus` 상위 3개 관리로 Multi-Object Scene 완벽 지원.
  2. **`DeicticResolutionEngine` & `UserIntentEstimator`**:
     - "이거", "저거", "봐봐", "새로 산" 등 지시어 및 질문 패턴 파싱.
     - 사용자 부정("아니 책이야") 시 2초 내 즉시 락 해제 및 재평가 (Wrong Focus Recovery).
  3. **`FocusPersistenceManager` & `AttentionAnchor`**:
     - 6초 Focus Lock으로 시선 튐(Jitter) 방지 및 15초 비활동 시 자동 해제.
     - `USER_FACE`, `LOWER_RIGHT`, `LOWER_LEFT`, `LOWER_CENTER` 등 추상 앵커를 렌더러에 연동하여 해상도 독립적 60fps 시선 동기화.
  4. **Ephemeral Processing Only (Sprint 50 대비)**:
     - 시각 및 Focus 데이터는 휘발성 인메모리로만 처리하여 프라이버시 원칙 유지.
  5. **9대 QA 게이트 (SR1~SR9) 100% PASS**:
     - Focus Target, Joint Attention, Focus Persistence, Gaze Alignment, Dialogue Directive, False Assumption Prevention, 15s Timeout, Wrong Focus Recovery, Multi-Object Scene.
  6. **5대 표준 규격 문서 완비**:
     - `docs/Shared_Reality_Architecture.md`, `docs/Joint_Attention_Spec.md`, `docs/Focus_Target_Guide.md`, `docs/Shared_Reality_Dialogue_Guide.md`, `docs/Sprint49_Report.md`.
- **Consequences**:
  - 총 126개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 48] Visual Awareness & Companion Perception Engine


### Decision 29: 4번째 인지 계층(Awareness Layer), 8-Tier Facial Emotion, Confidence Thresholding, Freshness Validation, Reaction Budget 및 Privacy First (Zero Raw Storage) 아키텍처 구축
- **Context**: 
  - 텍스트/음성 발화에만 반응하던 AI Companion을 "사용자와 같은 공간을 인지하고 반응하는 동반자"로 진화시키기 위해 시각 인지 계층(Visual Awareness Layer)을 추가하고, 철저한 프라이버시 원칙과 비침해성(Non-Intrusiveness)을 확립해야 함.
- **Decision**:
  1. **Awareness Layer 분리 및 DTO (`AwarenessContext`)**:
     - Memory, Emotion, Relationship에 이은 **4번째 인지 계층(Awareness Layer)** 공식 분리.
     - 8-Tier Facial Emotion (`SMILING`, `NEUTRAL`, `FOCUSED`, `CONFUSED`, `THINKING`, `FATIGUED`, `SURPRISED`, `UNKNOWN`).
     - 8대 주요 객체(CUP, FOOD, BOOK, LAPTOP, PET, PLANT, TV, WINDOW) 및 신뢰도 임계치(`confidence >= 0.70`), BoundingBox 구조화.
     - Freshness Age 검증 (`age_ms <= 10000ms`, 10초 초과 시 자동 만료 및 프롬프트 주입 배제).
     - 시선 연동 `VisualFocusTarget` (`USER_FACE`, `CUP`, `LAPTOP`, `PET` 등).
  2. **Privacy First & Structured DTO Only**:
     - 원본 이미지/영상 디스크 저장 100% 금지 (Ephemeral In-Memory).
     - 원본 이미지 LLM 직접 전송 금지 ➔ 구조화된 DTO 요약본만 주입하여 비용/속도/보안 극대화.
     - 모바일 Settings 화면에 `Privacy Dashboard` 추가.
  3. **Reaction Budget Manager & Non-Assertive Guidance**:
     - 분당 멘션 한도(최대 2회, 25초 쿨다운)로 피로도 원천 차단.
     - 단정형("너는 ~한다") 100% 금지 및 Amy의 4대 제안형 스타일(공감, 호기심, 격려, 관찰) 적용.
  4. **7대 QA 게이트 (VA1~VA7) 100% PASS**:
     - User Detection, Scene Object, Freshness, Focus Target, Privacy Compliance, False Claim Prevention, Non-Intrusiveness.
  5. **5대 표준 규격 문서 완비**:
     - `docs/Visual_Awareness_Architecture.md`, `docs/Awareness_Context_Spec.md`, `docs/Companion_Reaction_Guide.md`, `docs/Privacy_Rules.md`, `docs/Sprint48_Report.md`.
- **Consequences**:
  - 총 117개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 47] Voice Identity & Emotional Speech Engine


### Decision 28: Voice Identity Framework, 4대 보이스 페르소나, Emotional & Relationship Speech Engine 및 Multi-Vendor Provider Abstraction 구축
- **Context**: 
  - 단순 TTS 출력을 넘어 "캐릭터가 자신의 고유한 목소리와 감정, 관계에 맞춰 살아 숨 쉬듯 말하는" Voice Identity Layer가 요구됨.
- **Decision**:
  1. **`Voice Identity Framework` & 4대 페르소나**:
     - `WARM_COMPANION` (Genie 기본 / Warmth: 0.92), `CALM_MENTOR` (신뢰감 / Pitch: -2.0), `ENERGETIC_GUIDE` (활력 / Speed: 1.12x), `PROFESSIONAL_ADVISOR` (명확함).
  2. **`EmotionalSpeechEngine` & `RelationshipSpeechEngine`**:
     - 기쁨, 슬픔, 위로, 흥분 등 감정 벡터에 따른 템포/피치/에너지 실시간 변조.
     - Stranger(정중/격식) ➔ Trusted Companion(따뜻함/깊은 유대감) 어조 자동 변조.
  3. **`VoiceProviderFactory` 추상화 계층**:
     - OpenAI TTS, ElevenLabs (Voice Cloning 지원), Azure Speech 등 다중 벤더 교체 가능한 아키텍처 완성.
  4. **6대 표준 규격 문서 완비**:
     - `docs/Voice_Architecture.md`, `docs/Voice_Profile_Spec.md`, `docs/Emotional_Speech_Guide.md`, `docs/Relationship_Speech_Guide.md`, `docs/TTS_Audit_Report.md`, `docs/Sprint47_Report.md`.
- **Consequences**:
  - Quality Gates VC1~VC5 100% PASS.
  - 110개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 46] Production Avatar Finalization & Release Readiness


### Decision 27: Avatar v1.0 Release Candidate 1 (RC1) 배포, Release Freeze 및 프로덕션 릴리즈 승인
- **Context**: 
  - 비디오 클립 재생기에서 실시간 인지 상태 기반 Embodied Character Engine으로의 전면 전환이 완성됨에 따라, 품질/성능/안정성/1시간 장기 세션 무결성을 최종 검증하고 프로덕션 릴리즈를 공식 선언해야 함.
- **Decision**:
  1. **Release Freeze 선언**: 신규 기능 추가를 중단하고, 최적화 및 안정성 검증에 집중.
  2. **10대 최종 릴리즈 게이트(P1~P10) 100% PASS**:
     - State Machine, Lip Sync, Emotion, Variety, Performance, Memory Leak Free, 60fps Native Driver, Crash Free, 1-Hour Long Session, User Satisfaction.
  3. **5대 최종 릴리즈 문서 완비**:
     - `docs/Avatar_Release_Guide.md`, `docs/Avatar_Architecture_Final.md`, `docs/Avatar_QA_Report.md`, `docs/Avatar_Known_Issues.md`, `docs/Sprint46_Final_Report.md`.
  4. **Avatar v1.0 Release Candidate 1 (RC1) 공식 출시 승인**.
- **Consequences**:
  - 총 105개 백엔드 단위/통합 테스트 100% PASS.
  - 모바일 TypeScript 0 Errors 달성.

## [Sprint 45] Motion Library Expansion & Behavioral Variety System


### Decision 26: Motion Library V1 (14대 프리셋), Motion Cooldown Tracker, Randomization Jitter (+-10%) 및 Variety Engine 구축
- **Context**: 
  - 상태 전이와 감정 표현이 완성되었으나, 장시간 대화 시 동일한 끄덕임, 미소, 생각 자세가 기계적으로 반복되는 패턴(Loop Perception)을 원천 차단하고 행동 다양성을 확보해야 함.
- **Decision**:
  1. **`Motion Library V1` (`motion_library.py`)**:
     - Listening (4종), Thinking (4종), Speaking (3종), Empathy (3종) 총 14대 모션 프리셋 구축.
  2. **`Behavioral Variety Engine` (`variety_engine.py`, `MotionVarietyEngine.ts`)**:
     - 최근 3회 사용된 모션의 선택 가중치를 대폭 억제(Cooldown Algorithm)하여 연속 반복 방지.
     - 각도, 피치, 끄덕임 강도에 $\pm10\%$ 미세 난수 지터(Randomization Jitter) 적용.
     - 축하, 위로, 설명 등 대화 맥락에 기반한 지능적 모션 후보군 선택(Context-Aware Selection).
  3. **Motion Layer V2 및 모바일 60fps 실시간 합성**:
     - `RealtimeFaceRenderer.tsx`에서 Head Roll/Pitch, Eye Gaze, Body Lean을 Native Driver로 유기적 결합.
  4. **4대 표준 문서 완비**:
     - `docs/Motion_Library_V1.md`, `docs/Variety_Engine_Spec.md`, `docs/Context_Motion_Guide.md`, `docs/Sprint45_Report.md`.
- **Consequences**:
  - Quality Gates M1~M5 100% PASS.
  - 95개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 44] Emotion & Relationship Embodiment Engine


### Decision 25: RelationshipParameters 표준 DTO, Emotion Blending (7대 감정) 및 4단계 관계 태도 차별화 파이프라인 구축
- **Context**: 
  - 단순한 상태 전이를 넘어, AI Companion이 사용자와 축적한 8차원 관계(신뢰, 친밀도, 편안함) 및 복합 감정에 따라 동일한 질문에도 차별화된 표정과 시선, 따뜻함을 전달하는 관계 신체화 엔진이 요구됨.
- **Decision**:
  1. **`RelationshipParameters` 표준 모델 구축**:
     - `familiarity`, `trust`, `warmth`, `engagement` 4대 파라미터로 정규화.
  2. **7대 감정 인지 및 다중 감정 블렌딩 (Multi-Emotion Blending)**:
     - Joy, Warmth, Curiosity, Concern, Empathy, Excitement, Calm 가중치 선형 합성(Joy 60% + Warmth 40%) 지원.
  3. **4대 관계 단계(Stranger ➔ Familiar ➔ Trusted ➔ Close Companion)별 태도 차별화**:
     - 낯선 사용자에게는 공손한 중립(Polite Neutral), 친밀한 사용자에게는 온화하고 환한 미소(Bright Warm Smile) 적용.
  4. **4대 표준 문서 완비**:
     - `docs/Emotion_Embodiment_Spec.md`, `docs/Relationship_Embodiment_Spec.md`, `docs/Expression_Catalog_V2.md`, `docs/Sprint44_Report.md`.
- **Consequences**:
  - Quality Gates E1~E5 100% PASS.
  - 90개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 43] Embodied Behavior & Multimodal Presence Engine


### Decision 24: BehaviorParameters 표준 DTO, BehaviorEngine (Eye Contact, Head Motion, Settling) 및 비언어적 신체 행동 엔진 구축
- **Context**: 
  - 단순한 얼굴 표정과 립싱크를 넘어, 사용자의 질문을 듣고(Listening), 사색하고(Thinking), 말하기 전 반응하며(Pre-expression), 안정 상태로 복귀하는(Settling) 실시간 비언어적 신체 행동이 요구됨.
- **Decision**:
  1. **`BehaviorParameters` 표준 모델 구축**:
     - `attentionLevel`, `eyeContact`, `headTilt`, `nodIntensity`, `bodyLean`, `curiosityLevel`, `thinkingIntensity` 7대 파라미터로 정규화.
  2. **`BehaviorEngine` (`mobile/src/features/avatar/engine/BehaviorEngine.ts`)**:
     - `Eye Contact System`: 경청(1.0) ➔ 사색(0.4) ➔ 발화(0.85) ➔ 안정(0.85) 시선 전이.
     - `Head Motion System`: 경청 틸트(+2.5°), 사색 틸트(-4.0°), 공감 끄덕임(Agreement Nod) 제어.
     - `Settling Animation`: 발화 종료 후 400ms 동안 자연스럽게 Neutral 포즈로 안착.
  3. **6단계 상태 머신과 신체 행동의 완전 동기화**:
     - `IDLE` ➔ `LISTENING` ➔ `THINKING` ➔ `PRE_EXPRESSION` ➔ `SPEAKING` ➔ `SETTLING`.
  4. **4대 표준 문서 완비**:
     - `docs/Behavior_Parameter_Spec.md`, `docs/Listening_Behavior_Guide.md`, `docs/Thinking_Behavior_Guide.md`, `docs/Sprint43_Report.md`.
- **Consequences**:
  - Quality Gates B1~B5 100% PASS.
  - 85개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 42] Real-Time Audio Lip-Sync & Viseme Articulation Engine


### Decision 23: SpeechParameters 표준 DTO, LipSyncEngine V1 (EMA Smoothing + Viseme) 및 Speech Embodiment 구축
- **Context**: 
  - 단순히 얼굴 파라미터만 제어하는 것을 넘어, TTS 음성 출력과 아바타의 입모양/조음(Articulation)이 정밀하게 동기화되어 사용자가 "실제 음성에 맞춰 말하고 있다"고 체감할 수 있는 립싱크 엔진이 요구됨.
- **Decision**:
  1. **`SpeechParameters` 표준 모델 구축**:
     - `isSpeaking`, `mouthOpen`, `viseme` (A/E/I/O/U/closed), `speechIntensity`, `speechProgress` 5대 파라미터로 정규화.
  2. **`LipSyncEngine V1` (`mobile/src/features/avatar/engine/LipSyncEngine.ts`)**:
     - Audio Amplitude 정규화 + 5대 모음 Viseme 순환 + EMA($\alpha=0.45$) 스무딩으로 입모양 떨림/지터 방지.
     - 발화 중 자연스러운 고개 끄덕임(Head Pitch Accent) 및 눈썹 리프트(Speaking Micro Motion) 연동.
  3. **발화 생명주기 제어 및 Pre-expression 연동**:
     - 발화 시작 200ms 전 표정 선반영 ➔ 발화 중 립싱크 ➔ 발화 종료 즉시 100ms 이내에 입이 자연스럽게 닫히는 Settling 로직 구현.
  4. **4대 표준 문서 완비**:
     - `docs/LipSync_Architecture.md`, `docs/Speech_Parameter_Spec.md`, `docs/Speaking_Expression_Catalog.md`, `docs/Sprint42_Report.md`.
- **Consequences**:
  - Quality Gates L1~L5 100% PASS.
  - 80개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 41] Real-Time Face Engine & Parameter Control System


### Decision 22: FaceParameters 표준 DTO, 4대 Face Engine(Eye, Mouth, Brow, Smile) 모듈화 및 RealtimeFaceRenderer 구축
- **Context**: 
  - 동영상 클립이나 감정 모델에 렌더러가 직접 종속되는 것을 방지하고, 순수 파라미터 기반으로 눈 깜빡임, 시선 이동, 입 개폐, 눈썹, 미소를 60fps 실시간 합성할 수 있는 얼굴 전담 엔진이 요구됨.
- **Decision**:
  1. **`FaceParameters` 표준 모델 구축**:
     - `eyeOpenness`, `blinkWeight`, `eyeDirectionX/Y`, `mouthOpen`, `smileStrength`, `browRaise`, `headPitch/Yaw/Roll`, `warmth` 11대 파라미터로 정규화.
  2. **4대 독립 Face Engine 모듈화 (`mobile/src/features/avatar/engine/`)**:
     - `EyeEngine`, `MouthEngine`, `BrowEngine`, `SmileEngine`으로 관심사 분리.
  3. **`RealtimeFaceRenderer.tsx` 구축**:
     - React Native Native Driver 기반으로 프레임 드롭 없는 60fps 얼굴 렌더링.
  4. **4대 표준 문서 완비**:
     - `docs/Face_Parameter_Spec.md`, `docs/Face_Engine_Architecture.md`, `docs/Expression_Catalog_V1.md`, `docs/Sprint41_Report.md`.
- **Consequences**:
  - Quality Gates F1~F5 100% PASS.
  - 75개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 40] Avatar Asset Pipeline & Real-Time Character Renderer Transition


### Decision 21: 동영상 클립 스위칭 공식 중단, 2.5D 레이어드 실시간 캐릭터 렌더러 전환 및 Live2D 호환 규격 도입
- **Context**: 
  - 동영상 클립 재생 방식은 클립 간 포즈/조명 불일치, 비실시간 립싱크(음성과 무관한 기계적 입 열림), 3~4초 무한 루프 반복성으로 인해 사용자가 "동영상 플레이어"로 체감하는 근본적 한계가 존재함.
  - 이를 해결하기 위해 동영상 클립 추가 제작을 전면 중단하고, 고해상도 베이스 포트레이트 위에 눈, 눈썹, 입모양(Viseme), 호흡, 고개 틸트, 오라를 실시간 코드로 합성하는 **2.5D Real-Time Layered Renderer**로 전면 전환함.
- **Decision**:
  1. **동영상 클립 제작 공식 중단 및 렌더러 전환**:
     - `CompanionScreen.tsx`에서 비디오 컴포넌트 제거 ➔ `RealtimeLayeredAvatarRenderer.tsx`로 전면 교체.
  2. **실시간 오디오 립싱크 및 Viseme 파이프라인 구축**:
     - 음성 출력 시 60~120ms 주기로 Viseme(A, E, I, O, U)과 `mouth_open`을 동적 합성하여 발화와 입모양 완벽 동기화.
  3. **3대 아키텍처 및 자산 표준 수립**:
     - `docs/Avatar_Asset_Spec.md`, `docs/Avatar_Renderer_Architecture.md`, `docs/Live2D_Migration_Plan.md`.
  4. **Backend DTO 확장**:
     - `ExpressionParameters`에 `eye_openness`, `blink_value`, `mouth_open`, `viseme`, `warmth_alpha` 지원.
- **Consequences**:
  - Gate A1~A5 100% PASS.
  - 70개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 39] Avatar Behavioral Synchronization & Embodied Character Engine


### Decision 20: EmotionToExpressionMapper 계층 신설, Multi-Gesture Stack, Baseline Controller 분리 및 모바일 Dual Cross-Fade Buffer 구축 (Priority P0)
- **Context**: 
  - 동영상 클립 스위칭 방식은 클립 경계에서의 자세 튐, 눈 깜빡임 리셋, LLM 완료 후 늦은 반응 등으로 인해 비자연스러움(Uncanny Valley)이 발생함.
  - 아바타를 단순 영상 재생기가 아닌 '인격 인지 상태의 실시간 신체적 표현(Embodied Character)'으로 전환하기 위해 렌더러 독립적 `ExpressionParameters`, Multi-Gesture Layer Stack, `AvatarBaselineController` 분리, 이벤트 기반 THINKING 동기화, `PRE_EXPRESSION`(200ms 선제 표정), 그리고 모바일 화면의 **Dual Video Cross-Fade Buffer 및 지속적 호흡(Breathing) 레이어**가 필수적임.
- **Decision**:
  1. **EmotionToExpressionMapper 계층 신설 (`expression_mapper.py`)**:
     - `ContinuousEmotionVector` ➔ `ExpressionParameters` (`smile_strength`, `eye_softness`, `brow_raise`, `head_pitch`, `head_roll`)로 변환하여 렌더러(2D, Video, Live2D)와의 결합도를 완전히 제거.
  2. **Mobile Dual Video Cross-Fade Buffer & Continuous Breathing (`CompanionScreen.tsx`)**:
     - `VideoLayerA` / `VideoLayerB` 이중 버퍼 및 350ms 오파시티 크로스페이드(`opacity 1->0 & 0->1`) 구현으로 클립 전환 깜빡임/자세 튐 완전 제거.
     - `scale: 1.00 ↔ 1.018`, `translateY: ±2px` (4.5초 주기)의 상시 유기체 호흡 루프 적용.
     - `PRE_EXPRESSION` 수신 시 발화 200ms 전 미리 미소 표정으로 선반영.
  3. **Multi-Gesture Layer Stack (`active_gestures: List[AvatarGesture]`)**:
     - 제스처를 감정과 분리하고 `THINKING_TILT` + `SUBTLE_NOD` 등 복수 동작의 동시 블렌딩 지원.
  4. **AvatarBaselineController 분리 (`baseline_controller.py`)**:
     - `BlinkController` (2~7s 무작위), `BreathingController` (4~6s 사인파), `MicroExpressionController`를 전이 엔진과 분리.
- **Consequences**:
  - Quality Gates V1~V10 및 Gate M1~M4 100% 통과.
  - 65개 백엔드 단위/통합 테스트 무결성 달성.


## [Sprint 38] Character Agency & Autonomous Initiative Engine


### Decision 19: 5단계 Agency Level, Action Intent와 Delivery Channel 분리, Weighted Priority + Hard Gate, Cooldown Budget 도입
- **Context**: 
  - 캐릭터가 사용자의 말에 수동적으로 반응하기만 해서는 진정한 Companion으로 느껴지지 않음. 그러나 무분별한 선제적 접근(Proactive Action)이나 푸시 알림은 사용자에게 스팸이나 감정적 피로를 유발할 수 있음.
  - 행동 의도(Action Intent)와 실제 전달 채널(Delivery Channel)을 분리하고, 가중치 기반 우선순위 스코어링, 일일 예산(Daily Budget = 1.0), 다계층 쿨다운(Notification 6h, Message 1h), 감정적 조작 방어(Autonomy Guard)가 결합된 자율성 통제 체계가 필요함.
- **Decision**:
  1. **5단계 Agency Action Level 정립**:
     - `STAY_SILENT` (변화 없음) ➔ `INTERNAL_REFLECTION` (내부 상태 갱신) ➔ `QUIET_PRESENCE` (앱 진입 시 아바타 차분한 표정/대기) ➔ `UI_INITIATIVE` (앱 내 선제 발화) ➔ `OUTREACH_CANDIDATE` (앱 밖 알림 후보).
  2. **Action Intent vs Delivery Channel 분리 및 NotificationPolicy 연동**:
     - 높은 점수를 받았다고 즉각 알림을 발송하지 않고, `OUTREACH_CANDIDATE`로 지정 후 별도 정책에 의해 최종 전송 승인/강등.
  3. **가중치 우선순위 스코어링 + Hard Policy Gate (`agency_engine.py`)**:
     - $\text{BaseScore} = 0.20 \times \text{P} + 0.25 \times \text{Rel} + 0.20 \times \text{Temp} + 0.20 \times \text{Emo} + 0.15 \times \text{Mem}$
     - `proactive_enabled` 해제 시 즉시 차단, 심야 시간(Quiet Hours) Notification 차단.
  4. **Initiative Budget & Cooldown Guard (`initiative_budget.py`)**:
     - 일일 예산(1.0) 차감 및 쿨다운 미달 시 `BLOCKED_BY_BUDGET` / `BLOCKED_BY_COOLDOWN` 처리 (Budget leak 0).
  5. **Autonomy Guard & Decision Logging**:
     - 죄책감 유도("왜 나 안 찾아?", "너 없인 외로워") 원천 차단.
     - `agency_action_logs` 테이블에 `decision_status`와 `blocked_reason` 기록.
- **Consequences**:
  - Quality Gates A1~A9 100% 통과.
  - 55개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 37] Long-Term Character Growth & Relationship Dynamics Engine


### Decision 18: 8차원 RelationshipState V2, Bounded Delta 감쇠 모델, Shared Experience 및 Multi-User Adaptation 분리
- **Context**: 
  - 단순 친밀도 점수나 독립적인 상태값만으로는 '시간이 쌓이며 함께 살아온 역사'와 다채로운 관계의 질적 차이(장난스러운 유대 vs 깊고 안전한 유대 vs 상호 존중 유대)를 표현할 수 없음.
  - 급격한 관계 도약을 방지하는 Bounded Delta와, 단순 사실 메모리와 구별되는 '공동 경험(Shared Experience)', 그리고 다중 사용자 환경을 위한 `(user_id, companion_id)` 격리 및 전역 성장(Global Growth)과 사용자별 맞춤 적응(User Adaptation)의 분리가 필요함.
- **Decision**:
  1. **(user_id, companion_id) 복합 키 및 RelationshipState V2 통합**:
     - 기존 `relationship_states` 테이블을 8차원 모델(Trust, Closeness, Comfort, Attachment, Playfulness, Respect, EmotionalSafety, SharedHistoryDepth)로 통합 확장.
  2. **가중치 기반 Bounded Delta Engine (`evolution.py`)**:
     - $\text{Delta} = \text{Raw} \times \text{Significance} \times \text{MaturityFactor}$ ($\text{clamp}(-0.03, +0.03)$) 적용.
     - 관계 깊이($\text{SharedHistoryDepth}$)가 깊어질수록 민감도가 완만해지는 감쇠 공식 구현.
  3. **Shared Experience Narrative System (`timeline/`)**:
     - 사실 기억(Fact)과 차별화된 사건/정서적 의미/관계 영향 체인 구축.
  4. **Global Growth vs User Adaptation 분리 (`growth/`)**:
     - `CharacterGlobalGrowthModel` (보편적 성장)과 `UserRelationshipAdaptationModel` (사용자별 맞춤 격식/유머/호흡) 분리.
     - **Immutable Core는 영구 잠금(LOCKED)**하여 인격 왜곡/Drift 원천 방어.
- **Consequences**:
  - Quality Gates R1~R6 100% 통과.
  - 46개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 36] Behavioral Personality Engine & Character Consistency


### Decision 17: 3계층 인격 아키텍처, MBTI Behavioral Bias, Context Snapshot 및 Character Decision Logging 구축
- **Context**: 
  - Persona, MBTI, Emotion, Memory, Relationship 데이터가 단순히 LLM 컨텍스트에 주입되는 데이터 수준에 머물 경우, 장기 대화에서 '같은 상황에서 캐릭터가 왜 이렇게 반응하는가'에 대한 일관성이 무너지고 인격 표류(Drift) 또는 가스라이팅(Jailbreak)에 취약해짐.
  - LLM 생성 전에 먼저 인격적 행동 결정(`CharacterDecision`)을 도출하고, 생성 후 다차원 인격 검증(`ValidationResult`)을 수행하며, 모든 결정 이력을 영속화해야 함.
- **Decision**:
  1. **3계층 구조 정립 (Layered Character Architecture)**:
     - `Immutable Core` (절대 불변) ➔ `Stable Personality` (MBTI/Traits 5D) ➔ `Dynamic State` (Emotion/Relationship Snapshot).
  2. **MBTI as Behavioral Bias Engine (`mbti_mapper.py` & `traits.py`)**:
     - 결정론적 족쇄가 아닌 Core(0.45) + MBTI Bias(0.25) + Rel(0.15) + Emo(0.10) + Sit(0.05) 확률 가중치 편향 적용.
  3. **CharacterBehaviorEngine & Decision Confidence (`behavior_engine.py`)**:
     - Situation Analysis + Context Snapshot ➔ `CharacterDecision` 도출 (<10ms).
     - `decision_confidence` (>0.8 적극 개입, <0.5 과도한 추측 자제) 도입.
  4. **Tiered Consistency Validator & Injection Resistance (`consistency.py`)**:
     - Score >= 0.85 PASS, 0.60~0.84 ADJUST, < 0.60 REGENERATE로 LLM 비용 제어.
     - Gate C7 Persona Injection(가스라이팅) 시 즉각 REGENERATE 차단.
  5. **PresentationIntentMapper & CharacterDecisionLog**:
     - Cognitive Layer와 Avatar Presentation Layer 분리.
     - `character_decisions` DB 테이블 구축.
- **Consequences**:
  - Quality Gates C1~C7 100% 통과.
  - 40개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 35] Autonomous Thought & Reflection Engine


### Decision 16: 비동기 Autonomous Reflection Pipeline, Memory Consolidation 및 Trust Boundary Guard 구축
- **Context**: 
  - 캐릭터가 실시간 대화 응답에만 매몰되지 않고, 대화 종료 후 중요한 경험을 정리하고 기억의 의미를 분석하여 미래 행동에 반영하는 Reflection Pipeline이 필요함.
  - 사용자 응답 지연시간(Latency)에 일체 영향을 주지 않는 완전 비동기 격리(Async Isolation), LLM의 직접 DB 수정을 차단하는 Trust Boundary, Core Identity 불변성이 보장되어야 함.
- **Decision**:
  1. **사전 감사(Pre-Implementation Audit)**:
     - Memory, Relationship, Emotion, EventBus 아키텍처 충돌 점검 및 중복 배제 확인 (`Sprint35_PreImplementation_Report.md`).
  2. **Rule-based Reflection Policy & Rate Limiter (`policy/` & `runtime/`)**:
     - Significant Emotion (≥0.75), Important Memory (≥0.80), Relationship Delta (≥0.025)에만 트리거.
     - 쿨다운 및 대화당 상한 제한으로 폭주 방지.
  3. **Structured Reflection Engine & Trust Boundary (`engine/` & `validation/`)**:
     - `ReflectionResult` Structured Output 계약 준수.
     - Core Identity / MBTI / Persona 변조 시도 원천 거부 (`ReflectionValidator`).
  4. **Memory Consolidation & Duplicate Detector (`memory/`)**:
     - `CREATE`, `MERGE`, `ARCHIVE`, `DISCARD` 라이프사이클 처리 및 중복 기억 병합.
  5. **Context Directive (`providers/reflection_provider.py`)**:
     - 다음 대화 턴에 `[RECENT REFLECTION INSIGHT]` (< 150 토큰)으로 Semantic Summary 제공.
- **Consequences**:
  - Quality Gates R1~R8 100% 통과.
  - 33개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 34] Dynamic Personality & Behavioral Evolution Engine


### Decision 15: 5계층 Behavioral Decision Architecture 및 Personality Consistency Guard 구축
- **Context**: 
  - Persona, Memory, Emotion, Relationship 엔진이 존재하더라도 LLM이 알아서 행동을 결정하게 두면 '친절한 ChatGPT'처럼 정형화되거나 장기 대화에서 성격이 흔들리는(Drift) 위험이 존재함.
  - LLM에게 행동 결정을 맡기지 않고, 정형화된 상태(State) ➔ 행동 엔진(Behavior Engine) ➔ 행동 지시문(Behavior Directive) ➔ LLM 표현(Expression) ➔ 일관성 가드(Consistency Guard) 구조를 확립해야 함.
- **Decision**:
  1. **Dynamic Personality State (`services/personality/models/`)**:
     - `CoreTraits 5D` (Warmth, Playfulness, Curiosity, Assertiveness, Empathy).
     - `CommunicationStyleState` (Formality, Humor, Directness, Emotional Expression).
     - `AttachmentStyleState` (Initiative, Closeness, Independence).
  2. **PersonalityBehaviorEngine (`services/personality/engines/behavior_engine.py`)**:
     - Personality + Emotion + Relationship + Memory + User Input을 융합하여 10ms 미만 초고속으로 `BehaviorDirective` 산출.
  3. **Personality Consistency Guard (`evaluators/consistency_evaluator.py`)**:
     - 친밀한 관계에서의 로봇 어투 드리프트, 고통 상황에서의 부적절한 유머 등을 점수화하여 인격 표류 차단.
  4. **Context Directive Injection**:
     - `[DYNAMIC BEHAVIOR DIRECTIVE]` 블록을 300 토큰 미만으로 ContextBuilder에 주입.
- **Consequences**:
  - Quality Gates P1~P5 100% 통과.
  - 29개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 33] Personality Consistency & Character Behavior Engine


### Decision 14: 실시간 Character Behavior Resolver, Personality Consistency Validator 및 Character Interpretation Memory 구축
- **Context**: 
  - 캐릭터가 설정된 페르소나를 단순히 정적 프롬프트로만 주입받을 경우, 대화가 길어지면서 인격이 흔들리거나 상황(지침/피로/슬픔/축하)에 유연하게 대처하지 못함.
  - 관계 단계(Stranger vs Friend vs Close)에 따른 호칭/말투 차별화, 캐릭터 주관적 기억 해석(Interpretation), 응답 후 인격 일관성 검증(Consistency Validator)이 필요함.
- **Decision**:
  1. **Character Behavior Resolver (`services/character/behavior_resolver.py`)**:
     - User Intent, Character State (Energy/Mood), Relationship Stage, Memory Interpretation을 융합하여 실시간 `BehaviorInstruction` 산출.
  2. **Relationship-driven Behavior Mapping (`relationship_behavior.py`)**:
     - 단계별 말투(Honorifics/Formality), 유머 허용도, 대화적 거리감 조절.
  3. **Personality Consistency Validator (`response_validator.py`)**:
     - Fast Deterministic Rule-based 검증으로 Consistency Score (0.0~1.0) 산출 및 소유욕/의존성/가치관 위반 방어.
  4. **Memory Type 확장**:
     - 단순 사실(Fact)을 넘어 캐릭터의 해석을 담는 `CHARACTER_INTERPRETATION` 및 `EMOTIONAL_MEMORY` 타입 추가.
- **Consequences**:
  - Quality Gates C1~C5 100% 통과.
  - 24개 백엔드 단위/통합 테스트 무결성 달성.

## [Sprint 32] Autobiographical Memory & Shared Life Timeline Engine


### Decision 13: 자전적 기억 계층화(Autobiographical Memory Layer), 서사 챕터 및 Truth Boundary 구축
- **Context**: 
  - 단순 Facts/Preferences 저장소는 "우리가 함께 무엇을 겪었는가"에 대한 시간적 연속성(Time Continuity)과 공동 서사를 제공하지 못함.
  - 일상적인 잡담과 중요한 삶의 마일스톤(프로젝트, 커리어, 감정적 극복)을 분리 평가해야 함.
  - AI가 자신이 실제로 동행하지 않은 사용자의 개인 과거를 날조하여 "우리가 함께 했다"고 환각(Hallucination)을 일으키는 것을 엄격히 차단해야 함.
- **Decision**:
  1. **계층화된 자전적 기억 아키텍처 (`domain/memory/` & `db/models/autobiographical_memory.py`)**:
     - `Raw Conversation ➔ Episodic Memory ➔ Life Event ➔ Shared Experience ➔ Story Chapter ➔ Shared Life Timeline`.
  2. **Event Importance & Life Event Promotion**:
     - Novelty + Emotional Intensity + Personal Significance + Relationship Significance 종합 평가 (0.0~1.0).
     - 중요도(≥ 0.70) 및 중복 검증을 통한 Life Event 승격.
  3. **Experience Linking & Narrative Chapters**:
     - 프로젝트 시작 ➔ 난관 직면 ➔ 첫 배포 완성 등 독립 사건을 하나의 서사 체인으로 연결.
     - 대주제별 Story Chapter("첫 만남의 설렘", "함께 만든 프로젝트와 성장") 자동 연동.
  4. **Memory Truth Boundary**:
     - 직접 동행한 사건(`is_co_experienced=True`)과 사용자의 독자 경험(`is_co_experienced=False`)을 컨텍스트 컴파일러에서 엄격히 분리 지시.
  5. **Mobile Shared Story Screen (`SharedStoryScreen.tsx`)**:
     - 서사 챕터 카드, 공동 마일스톤 타임라인, 지니의 이야기 회고 기능 구현.
- **Consequences**:
  - Quality Gates M1~M12 100% 통과.
  - 단편 기억(Semantic)과 자전적 기억(Autobiographical)의 상호 보완 적층 구조 완성.

## [Sprint 31] Relationship Evolution & Social Bond Engine


### Decision 12: 7차원 Social Bond Model, Rate Limit Guard 및 영구 Relationship Anchor 구축
- **Context**: 
  - 단순 단일 친밀도 점수(0~100)는 인간관계의 복합성(신뢰, 애정, 속마음 공유, 존중, 편안함 등)을 왜곡함.
  - 한두 번의 대화로 관계가 급격히 점프하는 것을 막는 안전 속도 제한(Rate Limit)과 장기 부재 시에도 기억과 신뢰 코어가 보존되는 계층형 감쇠(Decay)가 필수적임.
  - AI가 사용자에게 정서적 의존성이나 소유욕을 유도하지 않도록 엄격한 안전 경계(Safety Boundary)를 컨텍스트에 필수 주입해야 함.
- **Decision**:
  1. **7차원 Social Bond 도메인 (`domain/relationship/`)**:
     - `RelationshipDimensions` (`familiarity`, `trust`, `affection`, `intimacy`, `respect`, `comfort`, `attachment`).
     - `RelationshipStage` (`STRANGER` ➔ `ACQUAINTANCE` ➔ `FRIEND` ➔ `CLOSE_FRIEND` ➔ `TRUSTED_COMPANION`).
  2. **Rate Limit & Delta Guard**:
     - 1회 대화당 차원별 변화량 최대 `0.03`으로 엄격 제한 (`MAX_DELTA_PER_INTERACTION = 0.03`).
  3. **불변의 관계 닻 (`RelationshipAnchor`)**:
     - 첫 만남(`FIRST_MEETING`), 깊은 고민을 나눈 날(`FIRST_PERSONAL_CONFESSION`), 단계 승급(`STAGE_UPGRADE`)을 영구 테이블에 기록.
  4. **정서적 안전 경계 (`RelationshipContextCompiler`)**:
     - 소유욕/질투/격리 조장 금지 및 자율성 존중 지침 주입.
  5. **Mobile Relationship Screen UI (`RelationshipScreen.tsx`)**:
     - 숫자 나열을 지양하고 단계 뱃지, Social Bond 진행 바, '우리의 이야기' 마일스톤 타임라인 시각화.
- **Consequences**:
  - Quality Gates R1~R9 전 항목 통과.
  - 백엔드 회귀 테스트 및 모바일 TypeScript 0 Errors 달성.

## [Sprint 30] Persistent Character Identity & Personality Core


### Decision 11: 다차원 Character DNA Domain, 5-Level Trust Boundary Context 및 Character Agency 엔진 구축
- **Context**: 
  - 단순 프롬프트 기반 챗봇 설정을 넘어, 세션과 시간에 구애받지 않고 지속되는 하나의 일관된 인격체(Character Identity)를 구축해야 함.
  - LLM은 인격 자체가 아니라 언어 표현 엔진이며, Character Identity System이 "너는 누구이며 어떻게 생각하고 행동해야 하는가"를 지속적으로 주입해야 함.
  - 사용자의 비이성적 요구 및 인격 파괴 프롬프트 인젝션("성격을 버려라", "내가 무조건 맞다고 해줘")에 무조건 굴복하지 않는 독립적 주체성(Character Agency)이 필요함.
- **Decision**:
  1. **다차원 Character DNA 도메인 (`domain/character/`)**:
     - `CharacterIdentity` (이름, 표시명, 자아인식, 코어 정체성, 버전 관리).
     - `PersonalityProfile` (Big 5 + 14개 다차원 Trait + MBTI 지표).
     - `CharacterValues` (Honesty, Kindness, Growth, Curiosity, Loyalty 등 7대 가치관).
     - `CharacterBoundaries` (인격 침해 거부, 무례한 언어 우려 표명 등 경계 보호 정책).
  2. **5-Level Trust Boundary Context (`ContextBuilder`)**:
     - `LEVEL 1 — SYSTEM`: System & Safety Rules
     - `LEVEL 2 — CHARACTER`: Identity, Personality, Values, Boundaries (`CharacterIdentityProvider`)
     - `LEVEL 3 — APPLICATION STATE`: Relationship, Emotion, Memory, Presence
     - `LEVEL 4 — OBSERVATION`: Vision Observation
     - `LEVEL 5 — UNTRUSTED`: Conversation History & User Input
  3. **Character Agency Engine (`ResponseStrategyResolver`)**:
     - 가치관(Honesty 0.88)과 경계 정책에 기반하여 맹목적 동조를 거부하고 지적 정직성과 따뜻한 조언을 제시하는 `ResponseStrategy` 결정.
  4. **Dynamic Emotion Separation (`CharacterStateResolver`)**:
     - 고정된 Personality DNA와 동적인 순간 감정(Emotion)을 엄격히 분리하여, 감정 상태에 따라 표현 뉘앙스는 변하되 성격 코어는 절대 훼손되지 않도록 설계.
  5. **Mobile Character Profile UI (`CharacterProfileScreen.tsx`)**:
     - 모바일 앱에서 다차원 성격 차트(Warmth, Curiosity, Intellectuality 등), 핵심 가치관 그리드, 자아인식 카드를 시각화하고 상단 헤더와 네비게이션 연동.
- **Consequences**:
  - Quality Gates C1~C6 전 항목 통과 (Persistence, Consistency, Emotion Separation, Agency, Boundary Defense, Pipeline Integrity).
  - 백엔드 단위/통합 테스트 및 모바일 TypeScript 0 Errors 달성.

## [Sprint 18] Real Vision Provider & Camera Intelligence Engine


### Decision 10: CloudVisionProvider 연동, Observation Trust Boundary 및 Mobile Sampling 스로틀
- **Context**: 
  - 카메라에서 획득한 시각 정보를 `VisionObservation` ➔ `VisionContextProvider` ➔ `ContextBuilder` ➔ `CompanionOrchestrator` ➔ `Real LLM` 경로로 안전하게 통합해야 함.
  - Vision 정보는 시스템 규칙, 페르소나, 감정, 관계를 직접 변조(Mutation)하지 않는 `[OBSERVATION]` 계층으로 엄격히 제한되어야 함.
  - 원본 이미지 장기 저장을 차단하고 백그라운드 전환 시 카메라 및 샘플링을 즉시 정지해야 함.
- **Decision**:
  1. **CloudVisionProvider 멀티모달 어댑터**: OpenAI `gpt-4o-mini` 기반 비전 분석, `OPENAI_API_KEY` 검증, 빈 이미지 방어, 타임아웃 및 표준 에러 도메인 매핑.
  2. **ProviderFactory 동적 주입**: `VISION_PROVIDER=cloud|mock` 설정에 따라 어댑터 동적 생성.
  3. **Trust Boundary & Confidence Guard**: 신뢰도 0.6 미만 할루시네이션 방어 필터링 및 `[CURRENT VISUAL CONTEXT]`로만 주입.
  4. **Mobile Frame Sampling & Privacy Cleanup**: `visionController.ts`를 통해 3~5초 스로틀 샘플링, User-Initiated 즉시 샘플링, Background 전환 시 `cleanup()` 강제 정지.
  5. **Failure Isolation**: Vision 오류 시에도 Text/Voice 대화는 100% 정상 유지.
- **Consequences**:
  - 기존 42개 백엔드 테스트 + 신규 5개 Vision 테스트 = **47개 테스트 100% 통과**.
  - 모바일 TypeScript Error 0 유지.
  - Quality Gates VISION-1 ~ VISION-10 전 항목 충족.

## [Sprint 17] Real Voice Interaction & Audio Runtime

### Decision 9: OpenAI STT/TTS Provider 연동, Voice State Machine 및 User Interrupt 제어
- **Context**: 
  - Mock 음성 파이프라인을 실제 Whisper STT 및 OpenAI TTS로 전환하면서도 `CompanionOrchestrator` 단일 인지 파이프라인 구조를 엄격히 유지해야 함.
  - P009가 말하고 있을 때(`SPEAKING`) 유저가 마이크를 켜면 즉시 발화를 중단하고 새 입력을 처리하는 **User Interrupt** 및 Race Condition 방어 체계가 필요함.
- **Decision**:
  1. **ProviderFactory STT/TTS 어댑터 연결**: `STT_PROVIDER=openai` ➔ `OpenAI_STTProvider`, `TTS_PROVIDER=openai` ➔ `OpenAI_TTSProvider` 동적 주입.
  2. **Voice State Machine & Interrupt 체계**: `IDLE` ➔ `LISTENING` ➔ `TRANSCRIBING` ➔ `THINKING` ➔ `SPEAKING` ➔ `IDLE`. 유저 마이크 활성화 시 `playbackId` 무효화 및 `interrupt_session` 즉각 호출로 `LISTENING` 전이.
  3. **Mobile Audio 연동 및 Avatar 동기화**: `voiceController.ts`를 신설하여 실제 오디오 재생 상태(`speaking=true/false`)를 `AvatarView`에 실시간 우선 반영.
  4. **Failure Isolation & Text Fallback**: 마이크 권한 거부, STT/TTS 장애 시 세션을 `ERROR` 상태로 격리하고 텍스트 대화(`ConversationView`)는 중단 없이 지속.
- **Consequences**:
  - 기존 36개 백엔드 테스트 + 신규 6개 Voice 테스트 = **42개 테스트 100% 통과**.
  - 모바일 TypeScript Error 0 유지.
  - Quality Gates V1~V8 전 항목 충족.

## [Sprint 16] Real LLM Provider Integration & Production Cognitive Core

### Decision 8: OpenAI LLM Provider 연동, 무단 Mock Fallback 방지 및 Trust Boundary 방어
- **Context**: 
  - Mock LLM을 실제 OpenAI LLM Provider로 교체하여 실시간 스트리밍 대화 루프를 완성해야 함.
  - 운영환경에서 `LLM_PROVIDER=openai` 설정 시 API Key 부재나 오류가 발생했을 때 조용히 Mock으로 fallback하면 사용자가 실제 AI와 대화하고 있다고 오해할 수 있음.
  - LLM 호출 시 프롬프트 인젝션 공격이 시스템 안전 규칙 및 페르소나를 오버라이드할 위험이 존재함.
- **Decision**:
  1. **OpenAILLMProvider 견고화**: `AsyncOpenAI` 클라이언트와 함께 `LLMAuthError`, `LLMRateLimitError`, `LLMTimeoutError`, `LLMProviderError` 등 표준화된 에러 도메인 구축.
  2. **무단 Mock Fallback 차단**: `ProviderFactory`에서 `LLM_PROVIDER=openai` 시 명시적으로 OpenAIProvider를 생성하고, API Key 부재 시 명확한 `LLMAuthError` 및 사용자 친화적 SSE 에러 이벤트를 발행.
  3. **ContextBuilder Trust Boundary & Injection 방어**: `[TRUSTED SYSTEM & SAFETY RULES]` ➔ `[APPLICATION CONTEXT]` ➔ `[CONVERSATION HISTORY]` ➔ `[UNTRUSTED USER INPUT]` 계층화.
  4. **3계층 테스트 분리**: CI 단위/통합 테스트는 `FakeOpenAIProvider`로 100% 자동 검증(API 비용 0)하고, 실제 API Key 검증은 별도 Smoke Test 스크립트로 분리.
- **Consequences**:
  - 기존 26개 백엔드 테스트 + 신규 10개 통합/보안 테스트 = **36개 테스트 100% 통과**.
  - 모바일 `npx tsc --noEmit` Error 0 유지.
  - Quality Gates 1~9 전 항목 충족.

## [Sprint 15] STEP 4 - Runtime Hardening & Real Provider Readiness

### Decision 7: Provider 독립 설정, Idempotency Guard 및 Observability 분리
- **Context**: 
  - 통합 `PROVIDER_MODE=mock|real`을 사용하면 LLM(OpenAI), STT(Mock), TTS(Native), Vision(Mock) 등 개별 컴포넌트 단위의 비용 통제 및 점진적 실연동이 불가능함.
  - 모바일 불안정 네트워크에서 동일 요청이 중복 유입되거나 재시도 시 LLM 중복 생성이 발생할 수 있음.
  - Latency/TTFT 메트릭을 SSE에 혼합하면 모바일 프로토콜이 불필요하게 비대해짐.
- **Decision**:
  1. **ProviderFactory & 독립 Configuration**: `LLM_PROVIDER`, `STT_PROVIDER`, `TTS_PROVIDER`, `VISION_PROVIDER`, `EMBEDDING_PROVIDER`를 각각 Single Source of Truth로 분리. `CompanionOrchestrator` 수정 없이 런타임 Provider 교체 가능.
  2. **Idempotency Guard & Sequence Tracking**: `active_interactions` 레지스트리를 통해 중복 interaction_id 차단. SSE `event_id = f"{interaction_id}:{seq}"` 부여.
  3. **Observability와 User Protocol 완전 분리**: 사용자는 깨끗한 SSE 이벤트만 수신하고, 개발자용 `ttft_ms`, `context_ms`, `total_e2e_ms` 메트릭은 백엔드 `InteractionTracer` 구조화 로그(JSON)로만 발행.
  4. **계층화된 Timeout Guard**: TTFT Timeout (15s) 및 Stream Idle Timeout (30s) 적용.
  5. **Runtime Lifecycle**: `CompanionRuntimeLifecycle` (CREATED -> READY -> RUNNING -> STOPPED)을 FastAPI Lifespan에 바인딩하여 리소스 누수 방지.
  6. **Mobile Config**: `mobile/src/config/env.ts`를 통해 `EXPO_PUBLIC_API_URL` 명시적 우선 및 에뮬레이터/시뮬레이터 기본 fallback 제공.
- **Consequences**:
  - Quality Gates 1~7 모두 충족.
  - 백엔드 26개 테스트 100% 통과, 모바일 TypeScript Error 0 달성.

## [Sprint 15] STEP 3B - Mobile Unified CompanionScreen & Interaction Pipeline

### Decision 6: 중앙 집중식 InteractionController 및 단일 렌더링 파이프라인 도입
- **Context**: 모바일 화면에서 ConversationScreen, Voice/Camera 컨트롤러 등이 제각각 API를 호출하고 SSE를 파싱하면 상태 동기화 및 프라이버시 관리가 분산됨.
- **Decision**: 
  1. `InteractionController`를 단일 진입점으로 신설하여 `sendText`, `sendVoiceTranscript`, `sendVisionObservation`, `subscribeToSSE`, `cancelInteraction`을 중앙 통제.
  2. `ConversationView` 컴포넌트를 분리 추출하여 `CompanionScreen`과 `ConversationScreen` 간 중복 제거 및 재사용성 확보.
  3. 백그라운드 전환(`AppState === 'background'`) 시 단순 상태 변경을 넘어 실제 마이크/카메라/음성 스트리밍 리소스를 물리적으로 정리(`stopCapture`, `cancelInteraction`)하는 하드웨어 프라이버시 바운더리 강화.
  4. 아바타 상태 우선순위 정책(`Local Audio Playback > Voice Runtime State > Backend Avatar Suggestion`) 적용.
- **Consequences**:
  - 모바일 프론트엔드가 백엔드 `CompanionOrchestrator`와 완전한 단일 파이프라인으로 연결됨.
  - Quality Gate M1~M5 충족 및 실기기 검증 준비 완료.

## [Sprint 15] STEP 3A - Single Interaction Pipeline & Cognitive Orchestration

### Decision 5: CompanionOrchestrator를 유일한 Cognitive Runtime 진입점으로 통일
- **Context**: Cognitive/Multimodal 엔진(Persona, Memory, Emotion, Relationship, Presence, Vision, Voice, Avatar)이 개별 구현되어 분절된 Island Architecture 상태였음. `ConversationService`가 비대해지고, Voice/Text 호출 경로가 분리되어 있었음.
- **Decision**: 
  1. `ConversationService`를 새로운 Cognitive Runtime의 중심에서 배제하고 Legacy Path로 격리.
  2. 모든 모달리티(Text, Voice, Vision)의 진입점을 `POST /companion/interactions` 및 `CompanionOrchestrator` 단일 파이프라인으로 일원화.
  3. `VoiceService`가 `ConversationService`를 직접 호출하지 않고 `CompanionOrchestrator`를 경유하도록 리팩토링.
  4. 7대 Context Provider(`Persona`, `Relationship`, `Emotion`, `Memory`, `Presence`, `Vision`, `ConversationHistory`)를 우선순위에 맞춰 통합 조립.
  5. JSON SSE 포맷(`interaction_started`, `thinking`, `text_delta`, `text_completed`, `avatar_state`, `interaction_completed`, `error`)으로 스트리밍 표준화.
  6. Post-processing 단계에서 `AvatarStateResolver`를 결합하여 Unified Response 완성.
- **Consequences**:
  - Island Architecture가 해소되고 단일 Interaction 파이프라인 확립.
  - Quality Gate A~E (Text, Voice, Vision, Avatar, Legacy Isolation) 100% 통과 및 회귀 방지.

## [Sprint 8] Mobile Presence & Notification Bridge

### Decision 1: Message와 Notification의 분리
- **Context**: AI가 능동적으로 발화하는 콘텐츠(Message)와 그것을 사용자에게 전달하는 수단(Notification)을 동일하게 취급할 경우, 앱이 켜져있을 때 불필요한 Push가 가거나 전송 실패 시 대화의 맥락이 끊기는 문제가 발생할 수 있음.
- **Decision**: `Message`와 `NotificationEvent`를 별도의 도메인으로 분리. Proactive Engine은 `Message` 생성을 담당하고, Notification Engine은 이를 어떻게 배달할지(Push vs In-App)만 결정함.
- **Consequences**: Push 발송에 실패하더라도 Companion의 대화 이력(`messages`)에는 발화가 정상적으로 남아있어, 다음 번 유저 접속 시 자연스럽게 대화가 이어질 수 있음. (Failure Isolation 확보)

### Decision 2: Emotion을 Presentation State로 매핑
- **Context**: 모바일 화면에서 Companion의 상태를 표시할 때 Emotion State(예: JOY, SADNESS)를 그대로 이모지나 아바타 모션에 1:1 하드코딩하면, 추후 아바타 엔진이 교체되거나 다채로운 감정이 추가될 때 UI 코드가 비대해짐.
- **Decision**: `EmotionState` → `PresentationState` 매핑 레이어를 모바일 클라이언트에 도입.
- **Consequences**: 백엔드에서 복잡한 감정(예: Anticipation)이 넘어와도 모바일 UI는 사전에 정의된 `PresentationState`(예: EXCITED) 렌더링에만 집중하여 향후 3D Avatar 도입 시 통합이 용이함.

## [Sprint 7] Presence & Proactive Interaction Engine

### Decision 3: App State와 Companion Presence의 분리
- **Context**: 모바일 앱이 백그라운드로 내려갔다고 해서 Companion이 즉각 `OFFLINE`이 되면 Companion으로서의 연속성이 훼손됨.
- **Decision**: 모바일 앱 Lifecycle과 별개로 Companion의 상태(`AVAILABLE`, `IDLE`, `SLEEPING` 등)를 독립적인 State Machine으로 관리.
- **Consequences**: 앱이 꺼져 있어도 Companion은 `AVAILABLE` 상태에서 자발적 대화(Proactive Message)를 시작할 수 있는 권리를 획득.

### Decision 4: Trigger-Candidate 파이프라인과 엄격한 스팸 차단
- **Context**: 시간이 지났다고 무조건 말을 거는 시스템은 사용자 피로도(Spam)를 가중시킴.
- **Decision**: 트리거(`LONG_ABSENCE`, `TIME_BASED`)가 발생하면 바로 LLM을 부르지 않고, `Candidate`를 생성한 뒤 Relationship, Cooldown, Daily Limit, Quiet Hours를 검사하는 `Policy Engine`을 거치도록 강제.
- **Consequences**: Companion이 발화 시점을 매우 신중하게 결정하게 되어, 장기적인 Relationship 형성에 긍정적 기여.
