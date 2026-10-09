# [SB-3] Character Switching & Full Context Isolation Implementation Plan

## 1. Goal Description

P009 시스템에서 활성 캐릭터 전환(Character Switching) 시 실제 인지 파이프라인(기억, 감정, 관계, 성장, 에이전시, 음성, 아바타) 전체가 대상 캐릭터의 독립된 `CharacterScope` 위에서 동작하도록 보장하고, **Interaction Snapshot Isolation** 및 **Context Leakage Guard**를 통해 캐릭터 간 모든 컨텍스트 누수(Cross-talk)를 구조적으로 차단합니다.

> **핵심 설계 원칙**:
> 1. **Interaction Snapshot Isolation**:
>    - 대화 시작 시 `CharacterScope`를 1회 확정(`InteractionContext`)하며, 대화 진행 중 외부에서 Active Character가 변경되어도 이미 실행 중인 대화는 시작 시점의 인격체를 끝까지 유지.
> 2. **3단계 우선순위 (Priority Hierarchy)**:
>    - `Explicit companion_id` (명시적 지정) > `Active Companion` (Registry 조회) > `Legacy Genie Fallback`
> 3. **Context Leakage Guard**:
>    - Memory, Emotion, Relationship, Voice, Avatar 전 영역의 Scope 일관성을 런타임에 보증하는 `CharacterScopeGuard` 도입.
> 4. **Concurrent Interaction Isolation**:
>    - 서로 다른 캐릭터를 대상으로 동시에 실행되는 Interaction들이 상태를 절대 공유하지 않도록 불변 스냅샷 보장.

---

## 2. Proposed Changes

### 2.1 5대 아키텍처 및 검증 문서 (`docs/sb3/`)
- [NEW] `docs/sb3/SB3_INTERACTION_SCOPE_ARCHITECTURE.md` (InteractionContext 및 스냅샷 격리 아키텍처)
- [NEW] `docs/sb3/SB3_SCOPE_PROPAGATION_AUDIT.md` (전체 12개 인지/프레젠테이션 엔진 Scope 전파 감사 결과)
- [NEW] `docs/sb3/SB3_CONTEXT_ISOLATION_MATRIX.md` (엔진별 격리 매트릭스 및 누수 방지 설계)
- [NEW] `docs/sb3/SB3_SWITCHING_SEMANTICS.md` (중간 전환, 동시 실행 및 명시적 오버라이드 시맨틱스)
- [NEW] `docs/sb3/SB3_REGRESSION_RISK.md` (기존 단일 지니 파이프라인 회귀 위험도 분석)

### 2.2 Domain Layer
- [NEW] `backend/app/domain/interaction/interaction_context.py`
  - `@dataclass(frozen=True) class InteractionContext`:
    - `interaction_id: str`
    - `character_scope: CharacterScope`
    - `character_runtime_context: CharacterRuntimeContext`
    - `character_runtime_state: Optional[CharacterRuntimeState]`
- [NEW] `backend/app/domain/character/character_scope_guard.py`
  - `CharacterScopeGuard`: Scope 불일치 검증 및 `CharacterScopeViolationError`

### 2.3 Orchestrator & ContextBuilder Integration
- [MODIFY] `backend/app/services/companion/orchestrator.py`
  - `NormalizedInput` 진입 시 Priority Hierarchy에 따라 `CharacterScope`를 1회 확정하고 `InteractionContext` 불변 바인딩
  - `InteractionTracer`, `ContextBuilder`, `AvatarStateResolver`, `SSE Events`에 확정된 `canonical_companion_id` 일관 주입
  - Mid-interaction Active Switch 발생 시에도 현재 Interaction의 Scope 불변성 보장

---

## 3. Verification Plan

### Automated Tests (`pytest backend/tests/test_character_switching_isolation.py`)
- **Test 1: Explicit Character Override** (Active=Genie 환경에서 `companion_id="sua"` 명시 시 Sua 런타임 확정)
- **Test 2: Active Character Resolution** (Active 전환 전후 무명시 요청 시 대상 캐릭터로 자동 라우팅)
- **Test 3: Mid Interaction Switch** (Interaction A 실행 중 Active 변경 시 Interaction A는 Genie로 완결 검증)
- **Test 4: New Interaction After Switch** (전환 완료 후 신규 Interaction B는 Sua로 완결 검증)
- **Test 5: Memory Isolation** (Sua 대화 시 Genie의 기억이 RAG 검색에 포함되지 않음을 검증)
- **Test 6: Emotion Isolation** (Genie와 Sua의 감정 상태 및 PAD 모델 완전 격리 검증)
- **Test 7: Relationship Isolation** (Genie와 Sua의 친밀도/신뢰도/관계 단계 완전 격리 검증)
- **Test 8: Voice Isolation** (Genie 음성과 Sua 음성 프로필이 전환 후 정확히 매핑됨을 검증)
- **Test 9: Avatar Isolation** (Genie와 Sua의 아바타 표정/모션 파라미터가 독립적으로 도출됨을 검증)
- **Test 10: Agency Isolation** (Genie의 자율 행동 결정이 Sua 세션에 간섭하지 않음을 검증)
- **Test 11: Concurrent Interaction Isolation** (Genie 대화와 Sua 대화가 동시에 스트리밍되어도 상호 오염 없음 검증)

### Full Regression & Mobile Verification
- 전체 백엔드 42개 테스트 스위트 (`pytest`) 실행
- 모바일 TypeScript 컴파일 검증 (`npx tsc --noEmit`)
