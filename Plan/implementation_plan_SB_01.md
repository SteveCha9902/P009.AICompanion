# [SB-1] Character Runtime Foundation Implementation Plan (Refined)

## 1. Goal Description

P009 AI Companion 시스템을 기존 **Single Companion(Genie)** 중심 구조에서 **Multi-Character Runtime Platform**으로 안전하게 확장하기 위한 첫 단계로서, 시스템의 실제 Runtime Isolation Key인 **`companion_id`를 Character Runtime Boundary로 승격**시키고, `CharacterScope`, `CharacterRuntimeContext`(Immutable), `CharacterRuntimeState`(Snapshot), `CharacterContextResolver`를 설계 및 구현합니다.

> **핵심 설계 결정**:
> - **Runtime Isolation Key**: 새로운 `character_id` 체계를 억지로 도입하지 않고 기존 시스템의 Root Owner인 `companion_id`를 그대로 사용 (`CharacterScope(user_id, companion_id)`).
> - **Immutable Configuration vs Dynamic Evolution**: `CharacterRuntimeContext`는 불변(Frozen) 설정 컨텍스트로 유지하고, 동적 상태는 `CharacterRuntimeState`(Snapshot)로 엄격히 분리.
> - **Resolver Scope Limitation**: Resolver는 Context Construction(Identity, Personality, Voice, Avatar, MemoryScope)만 담당하며 인지 엔진의 직접 연산은 각 엔진에 위임.
> - **Strict Cache Isolation**: Resolver 캐시는 반드시 `(user_id, companion_id)` 복합키로 관리하여 캐릭터 간 오염 차단.

---

## 2. 10대 핵심 질문 조사 및 진단 요약

| 번호 | 핵심 질문 | 현행 아키텍처 진단 결과 | SB-1 확정 아키텍처 |
| :--- | :--- | :--- | :--- |
| **1** | **Character Identity 관리 위치** | `domain/character/character_identity.py` 및 `db/models/character_profile.py` | `CharacterProfile`을 `CharacterRuntimeContext.identity`로 캡슐화 |
| **2** | **Companion과 Character의 차이** | `Companion`은 인격체의 Runtime Instance Root, `Character`는 성격/DNA 정의체 | `Companion`(`companion_id`)을 Runtime Boundary로 승격 |
| **3** | **Memory 분리 Key** | `memories.companion_id` 외래키 기반 격리 | `CharacterMemoryScope(companion_id)`로 명시적 스코프 래핑 |
| **4** | **Emotion State 저장 위치** | `emotion_states` (`companion_id` 1:1 유니크 외래키) | `CharacterRuntimeState.emotion` 스냅샷으로 바인딩 |
| **5** | **Relationship State Ownership** | `relationship_states` (`companion_id` + `user_id`) | `CharacterRuntimeState.relationship` 스냅샷으로 바인딩 |
| **6** | **Growth State 관리 단위** | `character_global_growth_states` + `user_relationship_adaptations` | 글로벌/유저 적응 상태를 스코프별 격리 관리 |
| **7** | **Agency 실행 주체** | `agency_action_logs` (`companion_id`="genie", `user_id`) | `companion_id` 기반 로그 및 실행 보장 |
| **8** | **Voice Profile 연결 위치** | `domain/voice/voice_profile.py` | `CharacterRuntimeContext.voice_profile`로 종속성 정렬 |
| **9** | **Avatar Profile 연결 위치** | `db/models/avatar.py` (`avatar_profiles.companion_id`) | `CharacterRuntimeContext.avatar_profile`로 바인딩 |
| **10** | **Interaction 최상위 Context** | `CompanionOrchestrator` -> `ContextBuilder` | `Orchestrator` -> `Resolver.resolve()` -> `RuntimeContext` 파이프라인 |

---

## 3. Proposed Architecture & Implementation Plan

### 3.1 8인 에이전트 Audit 문서 산출물 (`docs/sb1/`)
- [NEW] `docs/sb1/SB1_SYSTEM_ARCHITECTURE.md` (Agent 1: System Architect)
- [NEW] `docs/sb1/SB1_DATA_OWNERSHIP_AUDIT.md` (Agent 2: Database & Domain Analyst)
- [NEW] `docs/sb1/SB1_COGNITIVE_PIPELINE_AUDIT.md` (Agent 3: Cognitive Pipeline Engineer)
- [NEW] `docs/sb1/SB1_MEMORY_SCOPE_AUDIT.md` (Agent 4: Memory & Knowledge Engineer)
- [NEW] `docs/sb1/SB1_DYNAMIC_STATE_AUDIT.md` (Agent 5: State Engine Engineer)
- [NEW] `docs/sb1/SB1_PRESENTATION_AUDIT.md` (Agent 6: Voice & Avatar Engineer)
- [NEW] `docs/sb1/SB1_CLIENT_CONTEXT_AUDIT.md` (Agent 7: API & Mobile Integration Engineer)
- [NEW] `docs/sb1/SB1_REGRESSION_RISK.md` (Agent 8: QA & Integration Engineer)
- [NEW] `docs/sb1/SB1_IMPLEMENTATION_DECISION.md` (통합 의사결정 및 6대 질문 답변)

### 3.2 Core Domain Model 구현
- [NEW] `backend/app/domain/character/character_runtime_context.py`
  - `@dataclass(frozen=True) class CharacterScope(user_id: str, companion_id: str)`
  - `@dataclass(frozen=True) class CharacterMemoryScope(companion_id: str, namespace: str = "default")`
  - `@dataclass(frozen=True) class CharacterRuntimeContext`:
    - `scope: CharacterScope`
    - `identity: CharacterIdentity`
    - `personality: PersonalityProfile`
    - `memory_scope: CharacterMemoryScope`
    - `voice_profile: VoiceProfile`
    - `avatar_profile: AvatarProfile`
  - `@dataclass class CharacterRuntimeState`:
    - `scope: CharacterScope`
    - `emotion: Optional[Any] = None`
    - `relationship: Optional[Any] = None`
    - `growth: Optional[Any] = None`
    - `agency: Optional[Any] = None`
    - `interaction: Optional[Any] = None`

### 3.3 CharacterContextResolver 구현
- [NEW] `backend/app/services/character/context_resolver.py`
  - `CharacterContextResolver`:
    - `async def resolve(self, user_id: str, companion_id: str | None = None) -> CharacterRuntimeContext`
    - Multi-Tenant Cache: `_cache: Dict[Tuple[str, str], CharacterRuntimeContext]`
    - Default Fallback: `companion_id is None` ➔ `"default_companion"` (Genie)
    - Lazy Loading & Database Context Resolution

### 3.4 Orchestrator & ContextBuilder 최소 침투 연동
- [MODIFY] `backend/app/services/companion/orchestrator.py`
  - `CompanionOrchestrator`에 `CharacterContextResolver` 주입
  - `process_interaction` 및 `process_interaction_sync`에서 `resolver.resolve(user_input.user_id, user_input.companion_id)` 호출하여 `runtime_context` 획득 및 Tracer/파이프라인 전달
- [MODIFY] `backend/app/services/companion/runtime.py`
  - `create_companion_orchestrator` Composition Root에 `CharacterContextResolver` 등록

---

## 4. Verification Plan

### Automated Tests (`pytest backend/tests/test_character_runtime_foundation.py`)
- **Test 1: Default Character Resolution** (`companion_id=None` 전달 시 항상 Genie 컨텍스트 생성 검증)
- **Test 2: Explicit Character Resolution** (`companion_id="sua"` 등 전달 시 해당 런타임 스코프 생성 검증)
- **Test 3: Backward Compatibility** (기존 `user_id` 기반 오케스트레이터 및 API 호출 100% 정상 작동 검증)
- **Test 4: Scope Propagation** (`NormalizedInput` -> `Resolver` -> `Orchestrator` -> `Tracer`에 `companion_id` 유지 검증)
- **Test 5: Context Isolation** (`Genie` vs `Sua` 런타임 컨텍스트 비교 시 스코프, 음성, 아이덴티티 완전 격리 검증)
- **Test 6: No Character Context Leakage** (Genie 대화 후 Sua 대화 호출 시 인격 정보 누수 없음 검증)
- **Test 7: Resolver Cache Isolation** (`(user_id, companion_id)` 복합키 기반 캐시 격리 검증)
- **Test 8: Default Resolution Stability** (여러 Companion 존재 시에도 `companion_id=None`이면 디폴트 Genie 보장)
- 전체 pytest 회귀 테스트 스위트 실행

