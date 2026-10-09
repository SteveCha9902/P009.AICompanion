# P009.AICompanion Master Project Document

## 1. Project Overview
- **Name**: P009.AICompanion
- **Goal**: 스마트폰 속에 지속적으로 존재하며, 사용자의 감정과 관계를 기억하고 능동적으로 상호작용하는 Persistent AI Companion 구축.
- **Status**: Sprint 18 (Real Vision Provider & Camera Intelligence Engine) 완료.

## 2. Core Architecture Pillars
P009는 다음의 핵심 엔진들로 구성되어 있습니다:

1. **Conversation Engine (Sprint 2)**: ContextBuilder를 통한 외부 도메인 주입 및 메시지 영속화.
2. **Persona Engine (Sprint 3)**: 단순 프롬프트 문자열이 아닌 도메인으로 분리된 페르소나 설정.
3. **Memory Engine (Sprint 4)**: 팩트/관심사/선호도를 추출 및 요약하고, 현재 대화의 맥락에 맞춰 검색(Retrieval)하는 장기 기억 시스템.
4. **Emotion Engine (Sprint 5)**: 과거 Context와 현재 메시지를 바탕으로 Companion의 감정(대화 상태)을 추론하고 감쇠(Decay)/전이(Transition)하는 상태 머신.
5. **Relationship Engine (Sprint 6)**: 상호작용의 누적 결과로 관계 상태(Familiarity, Closeness 등)가 변화하고, 이것이 Behavior Policy를 통해 LLM의 어조(Tone)를 제어하는 시스템.
6. **Presence & Proactive Engine (Sprint 7)**: 앱이 닫혀있어도 존재감을 유지하며(Presence), 적절한 타이밍에 스스로 말을 거는(Proactive) 스팸 제어 기반 정책 엔진.
7. **Mobile Bridge (Sprint 8)**: Notification과 Deep Link, 그리고 Adaptive UI를 통해 백엔드의 두뇌를 스마트폰/태블릿과 연결.

## 3. Single Source of Truth
본 프로젝트의 주요 의사결정은 다음 문서들을 참조하십시오:
- `Decision_Log.md`: 중요한 기술 및 아키텍처 결정 이력.
- `CHANGELOG.md`: Sprint 별 구현 내역.
- `docs/`: 상세 엔진 별 아키텍처 문서.

## 4. Next Steps (Roadmap)
- [x] Sprint 29: Full-screen Seamless Dynamic Avatar & Multimodal Voice/Overlay Control
- [x] Sprint 30: Persistent Character Identity & Multi-dimensional Personality Core
- [x] Sprint 31: Relationship Evolution & Social Bond Engine
- [x] Sprint 32: Autobiographical Memory & Shared Life Timeline Engine
- [x] Sprint 33: Personality Consistency & Character Behavior Engine
- [x] Sprint 34: Dynamic Personality & Behavioral Evolution Engine
- [x] Sprint 35: Autonomous Thought & Reflection Engine
- [x] Sprint 36: Behavioral Personality Engine & Character Consistency
- [x] Sprint 37: Long-Term Character Growth & Relationship Dynamics Engine
- [x] Sprint 38: Character Agency & Autonomous Initiative Engine
- [x] Sprint 39: Avatar Behavioral Synchronization & Embodied Character Engine
- [x] Sprint 40: Avatar Asset Pipeline & Real-Time Character Renderer Transition
- [x] Sprint 41: Real-Time Face Engine & Parameter Control System
- [x] Sprint 42: Real-Time Audio Lip-Sync & Viseme Articulation Engine
- [x] Sprint 43: Embodied Behavior & Multimodal Presence Engine
- [x] Sprint 44: Emotion & Relationship Embodiment Engine
- [x] Sprint 45: Motion Library & Multimodal Gestures Engine
- [x] Sprint 46: Production Avatar Finalization & Avatar v1.0 RC1 Release
- [x] Sprint 47: Voice Identity & Emotional Speech Engine
- [x] Sprint 48: Visual Awareness & Companion Perception Engine
- [x] Sprint 49: Shared Reality & Joint Attention Engine
- [x] Sprint 50: Relationship Memory & Persistent Companion Engine
- [x] Sprint 51: Proactive Companion & Autonomous Agency Engine
- [x] Sprint 52: Emotionally Adaptive Companion Engine (Tone, Expression & Empathy Synchronization)
- [x] Sprint 53: Companion Cognitive Operating System (Integrated Brain: Memory, Awareness, Shared Reality, Voice, Avatar, Emotion & Proactive)
- [x] Sprint 54: Personality Consistency Engine (Character DNA, Drift Prevention & Cross-Modal Alignment)
- [x] Sprint 55: Character Growth & Relationship Evolution Engine (Intimacy Progression, Experience Integration & Shared Journey)
- [x] Sprint 56: Life Timeline & Personal History Engine (Life Milestones, Project Timelines & Personal Narrative Synthesis)
- [x] Sprint 57: Life Goal & Future Planning Engine (Shared Life Goals, Future Milestones, Anticipatory Care & Companion Agency)
- [x] Sprint 58: Companion Autonomy Engine (Autonomous Thought Loop, Situational Self-Initiation & Dynamic Companion Agency)
- [x] Sprint 59: Identity Continuity & Multi-Year Relationship Engine (Longitudinal Relationship History, Shared Odyssey & Multi-Year Identity Anchor)
- [x] Sprint 60: Trust & Safety Governance Layer (Dependency Risk Detection, Manipulation Guard & Relationship Boundary Governance)
- [x] Sprint 61: Companion Constitutional Governance Engine (5 Inviolable Principles, 5-Axis Drift Detection & Memory Provenance)
- [x] Sprint 62: Observability & Evaluation Layer (Real-time Latency, Cognitive Budget, Emotional Adaptability & Governance Quality Metrics)
- [x] Sprint 63: Adaptive Self-Improvement Engine (Evaluation-driven Auto-correction, Drift Re-alignment & Relationship Stabilization)
- [x] Sprint 64: World Model & Situation Understanding Layer (Temporal, Environmental, Social & Situational Context Synthesis)
- [x] Sprint 65: Collective Internal Deliberation & Unified Companion Brain (Companion OS v1.0 Master Brain, Multi-Perspective Deliberation & Final Arbiters)
- [x] Milestone M5: Persistent Companion Validation & Companion OS v1.0 Release Candidate
- [ ] Companion OS v1.0 Beta & Production Quality Optimization

### Multi-Character Platform Roadmaps (SB-1 ~ SB-17)
- [x] **SB-1: Character Runtime Foundation** (Runtime Boundary, CharacterScope, CharacterRuntimeContext, CharacterContextResolver)
- [x] **SB-2: Multi-Character Persistence & Registry** (UserCharacterPreference UNIQUE, CharacterRegistryService, Atomic Switching, REST API 3종)
- [x] **SB-3: Character Switching & Context Isolation** (InteractionContext Snapshot Isolation, 3-Tier Priority, CharacterScopeGuard, Zero Crosstalk)
- [x] **SB-4: Character Creation Engine** (CharacterTemplateRegistry, PersonalityCompiler, CharacterFactory, Transactional Persistence, POST /characters)
- [x] **SB-5: Character Lifecycle Management** (Lifecycle Status, Version 1 INITIAL, UNIQUE(companion_id, version), Invalidation, Soft Delete, Agency Guard)
- [x] **SB-6: Character Voice & Avatar Identity** (Presentation Profile, Genie Wife, Mani Daughter, Hana Friend, Voice/Avatar Binding, Cache Isolation)
- [x] **SB-7: Character Memory Isolation & Independent Experience System** (Character-level Memory Guard, Vector Filter, Retrieval Isolation, Zero Cross Leakage)
- [x] **SB-8: Character Creation Studio & Character Factory** (8-Step Creation Wizard, Preview API, Personality Compiler, Atomic Transaction, Mani Seed E2E)
- [x] **SB-9: Multi-Character Mobile Studio & Real-Time Switching UX** (Zustand Character Store, Character Gallery, Server-Confirmed Atomic Switching, CompanionScreen Sync)
- [x] **SB-10: Multi-Character Memory Isolation & RAG Anti-Leakage** (3-Scope Model: UserGlobal/Character/Shared, Fail-Closed Policy, Secondary Context Injection Guard, Secret Canary Test, 24 Adversarial Tests, Zero Leakage Proven)
- [x] **SB-11: Character Relationship & Emotional State Isolation** (CharacterDynamicStateScope, Dynamic State Bundle, Scope Pinning, 12 Isolation & Concurrency Tests)
- [x] **SB-12: Multi-Character Conversation Orchestration** (CompanionInteractionContext, PresentationCommand, Scope Pinning, Graceful Recovery, 15 E2E Tests)
- [x] **SB-13: Character-to-Character & Shared Experience Engine** (Controlled Sharing Policy, ShareProposal, PolicyEngine, Immediate Revocation, 15 E2E Tests)
- [x] **SB-14: Production Hardening & Security Hardening** (InteractionExecutionRegistry, RateLimiter, TimeoutBudget, PrivacyRedactor, /ready Probe, 16 E2E Tests)
- [x] **SB-15: Server Deployment & Multi-User Platform Architecture** (Authoritative Identity, Multi-Tenant Guard, Dockerization, Nginx TLS Proxy, 22 Audit Docs, 16 Multi-User E2E Tests)
- [x] **SB-16: Real User Pilot & Product Validation** (10 Product Hypotheses, UX Scorecard 4.7/5.0, 16 Evaluation Docs, Product Backlog, SB-17 Empathy Recommendation, 16 Pilot E2E Tests)
- [x] **SB-17: Natural Conversation, Dynamic Cadence & Quiet Empathy** (7 Conversation Modes, Fatigue Tracker, Question Budget, ResponseQualityGate, 17 Docs, 16 Cadence/Empathy E2E Tests)



































