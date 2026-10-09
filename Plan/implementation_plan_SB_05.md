# [SB-5] Character Lifecycle Management & Safe Evolution Implementation Plan

## 1. Goal Description

생성된 AI Character를 단순 CRUD 데이터가 아닌 장기적으로 기억, 관계, 성장 기록을 축적하는 디지털 인격체로 취급하고, 기존 Cognitive History를 100% 보존하면서 Character Profile과 DNA를 안전하게 Evolution할 수 있는 **Character Lifecycle Management System**을 구축합니다.

> **대표님 6대 핵심 피드백 반영**:
> 1. **Character 생성 시 Version 1 (INITIAL) 즉시 생성**:
>    - `ChangeType`: `INITIAL`, `COSMETIC`, `MINOR`, `MAJOR`
>    - `INITIAL`, `MINOR`, `MAJOR`만 `CharacterVersion` 생성 (`COSMETIC`은 프로필 즉시 갱신).
> 2. **`dna_snapshot` 경계 한정 (DNA Only)**:
>    - Identity, Personality Traits, Values, Speech Principles만 포함하며 Memory/Emotion/Relationship/Growth/Agency 제외.
> 3. **CharacterContextResolver 런타임 캐시 Invalidation**:
>    - 수정 시 `resolver.invalidate(user_id, companion_id)`를 호출하여 다음 대화에서 갱신된 DNA 즉시 반영.
> 4. **`UNIQUE(companion_id, version)` 및 동시성 제어**:
>    - `character_versions` 테이블에 복합 유니크 제약조건 적용.
> 5. **Agency / Proactive Action 차단**:
>    - `ARCHIVED`, `DELETED` 상태의 캐릭터는 대화뿐만 아니라 Agency Action 및 Proactive Trigger 원천 차단.
> 6. **HTTP Error Code 표준화 (HTTP 409 Conflict)**:
>    - Active/System 캐릭터 조작 충돌 및 부적절한 상태 전이(Deleted Restore 등)에 `409 Conflict` 명문화.

---

## 2. Proposed Changes

### 2.1 5대 아키텍처 및 정책 문서 (`docs/sb5/`)
- [NEW] `docs/sb5/SB5_LIFECYCLE_ARCHITECTURE.md` (생명주기 상태 전이 머신 및 런타임 캐시 무효화)
- [NEW] `docs/sb5/SB5_CHARACTER_VERSIONING.md` (Version 1 INITIAL 정책, `dna_snapshot` 스키마 및 `UNIQUE(companion_id, version)`)
- [NEW] `docs/sb5/SB5_UPDATE_CLASSIFICATION.md` (INITIAL, COSMETIC, MINOR, MAJOR 분류 규칙)
- [NEW] `docs/sb5/SB5_ARCHIVE_DELETE_POLICY.md` (Agency 차단, Active/System 보호, HTTP 409 표준)
- [NEW] `docs/sb5/SB5_REGRESSION_RISK.md` (지니 보존 및 17대 자동화 테스트 계획)

### 2.2 DB Model Layer
- [MODIFY] `backend/app/db/models/companion.py`
  - `lifecycle_status` (String(20), default="available")
  - `is_system_character` (Boolean, default=False)
  - `archived_at` (DateTime, nullable=True)
  - `deleted_at` (DateTime, nullable=True)
- [NEW] `backend/app/db/models/character_version.py`
  - `CharacterVersionModel` (`UNIQUE(companion_id, version)`)
- [MODIFY] `backend/app/db/models/__init__.py`

### 2.3 Domain & Service Layer
- [NEW] `backend/app/domain/character/lifecycle_status.py` (`CharacterLifecycleStatus` enum)
- [NEW] `backend/app/domain/character/change_classification.py` (`ChangeType` - INITIAL, COSMETIC, MINOR, MAJOR)
- [NEW] `backend/app/domain/character/update_request.py` (`CharacterUpdateRequest`)
- [MODIFY] `backend/app/services/character/creation_service.py` (생성 시 Version 1 INITIAL 스냅샷 삽입)
- [NEW] `backend/app/services/character/lifecycle_service.py` (Update, Archive, Restore, Delete, Invalidate)
- [MODIFY] `backend/app/services/character/context_resolver.py` (Archived/Deleted 런타임 차단 및 `invalidate` 메서드 추가)

### 2.4 API Layer & Schemas
- [MODIFY] `backend/app/api/schemas/character_schema.py` (`CharacterUpdateRequest`, `CharacterLifecycleResponse`, `CharacterVersionResponse`)
- [MODIFY] `backend/app/api/endpoints/characters.py`
  - `PATCH /api/v1/characters/{companion_id}`
  - `POST /api/v1/characters/{companion_id}/archive`
  - `POST /api/v1/characters/{companion_id}/restore`
  - `DELETE /api/v1/characters/{companion_id}`
  - `GET /api/v1/characters/{companion_id}/versions`
  - `GET /api/v1/characters?include_archived=true`

---

## 3. Verification Plan

### Automated Tests (`pytest backend/tests/test_character_lifecycle.py`) - 17대 테스트
- **Test 1**: Cosmetic Update (Avatar/Voice 변경 시 DNA 업데이트, Version 유지)
- **Test 2**: Personality Update & Version 2 Creation (MINOR/MAJOR 시 Version 2 생성)
- **Test 3**: Memory Preservation on Evolution (DNA 수정 후 기존 기억 데이터 100% 보존)
- **Test 4**: Archive Character & Runtime Block (아카이브 후 대화/Resolver 차단)
- **Test 5**: Active Character Archive Reject (409 Conflict 차단)
- **Test 6**: Restore Character & State Transition (복원 시 Available 상태 전이)
- **Test 7**: Soft Delete Character (Soft delete 및 무손실 보존)
- **Test 8**: Deleted Character Runtime Reject (삭제 캐릭터 런타임 차단)
- **Test 9**: Deleted Character Activation Reject (409 Conflict 차단)
- **Test 10**: Character Version History (V1 INITIAL -> V2 MINOR -> V3 MAJOR 이력 조회)
- **Test 11**: System Character (Genie) Protection (지니 아카이브/삭제 403 차단)
- **Test 12**: Ownership Validation on Lifecycle Ops (타인 캐릭터 403 차단)
- **Test 13**: Transaction Rollback on Failure (DB 에러 시 롤백 무결성)
- **Test 14**: Runtime Context Cache Invalidation (수정 후 캐시 무효화 및 신규 DNA 로딩)
- **Test 15**: Version Concurrency & Unique Constraint (`UNIQUE(companion_id, version)` 무결성)
- **Test 16**: Archived Character Agency Block (아카이브 상태 시 Agency/Proactive 차단)
- **Test 17**: Invalid Lifecycle Transition Reject (DELETED -> RESTORE 시 409 Conflict 차단)

### Full Regression & Mobile Verification
- 전체 백엔드 44개 테스트 스위트 (`pytest`) 실행
- 모바일 TypeScript 컴파일 검증 (`npx tsc --noEmit`)
