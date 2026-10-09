# [SB-7] Character Memory Isolation & Independent Experience System Implementation Plan

## 1. Goal Description

P009.AICompanion 플랫폼에서 각각의 캐릭터(Genie, Mani, Hana 등)가 독립적인 기억, 경험, 상호작용 기록을 축적할 수 있도록 **Character-level Memory Isolation & Experience Boundary System**을 구축합니다.

> **핵심 격리 원칙**:
> 1. **Character Memory ≠ User Memory**:
>    - 캐릭터의 기억은 `(user_id, companion_id)` 단위로 완벽하게 논리 격리됩니다.
>    - `Genie ↔ User`, `Mani ↔ User`, `Hana ↔ User` 상호 간 기억 누수 제로 (`Cross-Character Leakage = 0`).
> 2. **Character DNA vs Memory 분리**:
>    - 캐릭터의 관심사/취향(Mani: 미술, 아이돌 등)은 Character DNA/Profile에 속하며,
>    - 대화 중 발생한 구체적 사건("지난주 아빠가 미술학원에 데려다 줌")만 Episodic/Semantic Memory로 축적됩니다.
> 3. **SB-5 Lifecycle Guard 연동**:
>    - `ARCHIVED` 또는 `DELETED` 상태의 캐릭터는 런타임 Memory Retrieval이 차단되지만, 물리적 데이터는 영구 보존됩니다.
> 4. **Strict Scope Binding & Cache Isolation**:
>    - Memory Retrieval/Write 시 `companion_id`가 누락된 저장을 원천 차단합니다.
>    - 캐시 키는 `memory_cache:{user_id}:{companion_id}:{query_hash}`로 엄격히 격리됩니다.

---

## 2. Proposed Changes

### 2.1 9대 아키텍처 및 정책 문서 (`docs/sb7/`)
- [NEW] `docs/sb7/SB7_MEMORY_ARCHITECTURE.md` (전체 멀티 캐릭터 메모리 아키텍처)
- [NEW] `docs/sb7/SB7_MEMORY_OWNERSHIP.md` (사용자 및 캐릭터 소유권 모델)
- [NEW] `docs/sb7/SB7_MEMORY_ISOLATION.md` (Genie/Mani/Hana 논리 격리 보장 규칙)
- [NEW] `docs/sb7/SB7_RETRIEVAL_SCOPE.md` (Retrieval 파이프라인 및 Vector Filter 명세)
- [NEW] `docs/sb7/SB7_MEMORY_WRITE_POLICY.md` (Memory Write/Extraction 바인딩 정책)
- [NEW] `docs/sb7/SB7_CACHE_ISOLATION.md` (메모리 캐시 격리 및 무효화 정책)
- [NEW] `docs/sb7/SB7_LIFECYCLE_MEMORY_POLICY.md` (SB-5 아카이브/삭제 시 메모리 보존 및 가드 정책)
- [NEW] `docs/sb7/SB7_REGRESSION_RISK.md` (회귀 위험도 분석 및 15대 테스트 계획)
- [NEW] `docs/sb7/SB7_IMPLEMENTATION_DECISION.md` (최종 구현 결산 보고서)

### 2.2 Domain & Repository Layer
- [MODIFY] `backend/app/domain/character/character_runtime_context.py` (`CharacterMemoryScope` 보강)
- [MODIFY] `backend/app/repositories/memory_repository.py` (Lifecycle Guard 및 Scope Filter 강화)

### 2.3 Service Layer
- [NEW] `backend/app/services/memory/character_memory_guard.py` (`CharacterMemoryGuard`: Scope 및 Lifecycle 검증)
- [MODIFY] `backend/app/services/memory/retriever.py` (Character Scope 및 캐시 격리 지원)
- [MODIFY] `backend/app/services/context/providers/memory_provider.py` (CharacterScope 명시적 바인딩)

---

## 3. Verification Plan

### Automated Tests (`pytest backend/tests/test_character_memory_isolation.py`) - 15대 테스트
- **Test 1**: Genie Memory Isolation
- **Test 2**: Mani Memory Isolation (딸 일상/미술/음악 기억)
- **Test 3**: Hana Memory Isolation (친구 취미/카메라 기억)
- **Test 4**: Cross Character Retrieval Prevention (Mani ➔ Genie 기억 검색 차단)
- **Test 5**: Cross Character Memory Write Prevention
- **Test 6**: Character Switch Memory Isolation (Genie ➔ Mani ➔ Hana ➔ Genie)
- **Test 7**: ContextBuilder Character Memory Isolation
- **Test 8**: Memory Extraction Character Binding
- **Test 9**: Archived Character Memory Access (SB-5 Lifecycle Guard)
- **Test 10**: Ownership Validation (403 Forbidden)
- **Test 11**: Legacy Genie Memory Compatibility
- **Test 12**: Memory Retrieval Cache Isolation (`memory_cache:u:c:q`)
- **Test 13**: Embedding Search Character Isolation
- **Test 14**: Concurrent Character Interaction Isolation
- **Test 15**: No Character ID Failure Safety

### Full Regression & Mobile Verification
- 전체 백엔드 46개 테스트 스위트 (`pytest`) 실행
- 모바일 TypeScript 컴파일 검증 (`npx tsc --noEmit`)
