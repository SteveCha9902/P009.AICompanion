# [SB-2] Multi-Character Persistence & Registry Implementation Plan (Refined)

## 1. Goal Description

P009 시스템에서 하나의 사용자가 여러 인격체(Companion)를 보유할 수 있도록 하고, 그중 현재 대화 대상인 **Active Companion**을 안전하게 관리하는 **Persistence 및 Registry Layer**를 구축합니다.

> **핵심 아키텍처 원칙**:
> 1. **기존 지니 Companion PK 보존 & Lazy Bootstrap**:
>    - `active_companion_id`에 임의 문자열("default_companion")을 하드코딩하지 않고, 기존 사용자의 `companions.id`를 조회하여 연결.
>    - Preference가 없는 레거시 사용자 접근 시 자동으로 기존 지니 Companion을 찾아 Preference를 생성하는 **Lazy Bootstrap** 적용.
> 2. **DB 무결성 (`UNIQUE(user_id)`)**:
>    - `user_character_preferences` 테이블에 `user_id` Unique 제약조건을 강제하여 활성 캐릭터 중복 생성 원천 차단.
> 3. **Atomic Ownership Validation & Switching**:
>    - `SELECT companion WHERE id = :id AND user_id = :user_id`를 동일 트랜잭션 내에서 수행 후 Preference 업데이트.
> 4. **Selective Cache Invalidation**:
>    - 개별 캐릭터 런타임 컨텍스트 캐시 `(user_id, companion_id)`는 유지하고, 활성 캐릭터 매핑 캐시만 정밀 무효화.
> 5. **Domain Model과 API Schema의 엄격한 분리**:
>    - 도메인 모델(`CharacterSummary`)과 FastAPI Pydantic Response Schema(`CharacterSummaryResponse`, `ActivateCharacterResponse`) 분리.

---

## 2. Proposed Changes

### 2.1 4대 아키텍처 및 마이그레이션 문서 (`docs/sb2/`)
- [NEW] `docs/sb2/SB2_PERSISTENCE_DECISION.md` (Option A vs Option B 비교 분석 및 선정 이유)
- [NEW] `docs/sb2/SB2_REGISTRY_ARCHITECTURE.md` (레지스트리 계층 구조, 도메인/API 분리, 트랜잭션 경계)
- [NEW] `docs/sb2/SB2_ACTIVE_CHARACTER_FLOW.md` (Active Character 전환 흐름, 원자적 검증, 캐시 무효화 정책)
- [NEW] `docs/sb2/SB2_MIGRATION_STRATEGY.md` (Lazy Bootstrap 기반 레거시 지니 무손실 보존 전략)

### 2.2 Persistence & Database Model
- [NEW] `backend/app/db/models/user_character_preference.py`
  - `UserCharacterPreference` (`id`, `user_id` (Unique, Index), `active_companion_id` (FK to companions.id), `updated_at`)
- [MODIFY] `backend/app/db/models/__init__.py`: `UserCharacterPreference` export

### 2.3 Domain Model & API Schema
- [NEW] `backend/app/domain/character/character_summary.py`
  - `@dataclass class CharacterSummary`: `companion_id`, `name`, `role_title`, `avatar_preview`, `voice_name`, `is_active`
- [NEW] `backend/app/api/schemas/character_schema.py`
  - `CharacterSummaryResponse`, `CharacterSummaryListResponse`, `ActivateCharacterResponse`

### 2.4 Repository & Service Layer
- [NEW] `backend/app/repositories/character_registry_repository.py`
  - `CharacterRegistryRepository`:
    - `list_by_user(user_id)`
    - `get_preference(user_id)`
    - `get_active_companion_id(user_id)`
    - `set_active_companion(user_id, companion_id)` (Atomic Transaction)
    - `get_owned_companion(user_id, companion_id)`
- [NEW] `backend/app/services/character/registry_service.py`
  - `CharacterRegistryService`:
    - `list_characters(user_id)`
    - `get_active_companion_id(user_id)` (Lazy Bootstrap 지원)
    - `set_active_companion(user_id, companion_id)` (소유권 검증 및 캐시 Invalidation)
    - `validate_ownership(user_id, companion_id)`

### 2.5 API Layer
- [NEW] `backend/app/api/endpoints/characters.py`
  - `GET /api/v1/characters` : 보유 캐릭터 요약 목록 조회
  - `GET /api/v1/characters/active` : 현재 활성 캐릭터 조회
  - `POST /api/v1/characters/{companion_id}/activate` : 활성 캐릭터 전환
- [MODIFY] `backend/app/api/routes.py`: `/api/v1/characters` 라우터 등록

### 2.6 ContextResolver 연동
- [MODIFY] `backend/app/services/character/context_resolver.py`
  - `CharacterRegistryService` 연동을 지원하여 `companion_id`가 지정되지 않았을 때 활성 캐릭터의 실제 PK로 자동 매핑.

---

## 3. Verification Plan

### Automated Tests (`pytest backend/tests/test_character_registry.py`)
- **Test 1: Existing Genie Registration** (기존 사용자 조회 시 실제 지니 Companion PK로 정상 인식)
- **Test 2: List Characters** (사용자 보유 캐릭터 목록 및 is_active 플래그 정확성 검증)
- **Test 3: Get Active Character** (`GET /characters/active` API 응답 검증)
- **Test 4: Ownership Validation** (타인의 Companion에 대해 활성화 시도 시 403/404 원자적 차단 검증)
- **Test 5: Switch Character** (Genie -> Sua 전환 트랜잭션 정상 수행 및 Active 상태 갱신 검증)
- **Test 6: Resolver Cache Isolation** (캐릭터 전환 후 개별 캐시는 유지되고 Active Resolver는 대상 캐릭터를 정확히 반환)
- **Test 7: Backward Compatibility** (`user_id`만 전달한 대화 파이프라인에서 Active Companion으로 자동 대화 검증)
- **Test 8: No Context Leakage** (캐릭터 전환 전후 메모리 스코프 및 음성/아바타 프로필 비오염 검증)
- **Test 9: Legacy Preference Bootstrap** (Preference 없는 레거시 사용자 접근 시 자동 생성 및 멱등성 검증)
- **Test 10: Concurrent Switching Safety** (동시 활성화 요청 시 단 1개의 Preference Row 유지 및 무결성 보장)

### Full Regression & Mobile Verification
- 백엔드 40개 코어 엔진 전체 회귀 테스트 (`pytest`) 실행
- 모바일 TypeScript 컴파일 검증 (`npx tsc --noEmit`)

