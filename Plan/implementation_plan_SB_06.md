# [SB-6] Character Presentation Identity & Profile Binding Implementation Plan

## 1. Goal Description

기존 P009 Cognitive Architecture(Memory, Emotion, Relationship, Growth, Agency, Lifecycle)의 안정성을 100% 유지하면서, 각 캐릭터가 자신만의 **Voice + Avatar + Expression + Gesture + Presentation Style**을 독립적으로 갖는 **Multi-Character Presentation Runtime**을 구축합니다.

> **3대 기준 캐릭터 Presentation Identity**:
> - **Genie (사랑스러운 아내 / 배우자)**: 따뜻하고 친밀하며 부드러운 음성과 애정 어린 아바타 표정.
> - **Mani (사랑스러운 딸 / 가족·딸)**: 밝고 사랑스러우며 생동감 넘치는 하이톤 음성과 활기찬 아바타 표현 (**AI 비서/어시스턴트 정의 절대 금지**).
> - **Hana (취미 친구 / 친구)**: 밝고 활발하며 편안한 음성과 캐주얼한 아바타 제스처.

---

## 2. Core Architectural Principles

1. **Personality와 Presentation의 엄격한 분리**:
   - `Personality`: 내면의 정체성 및 가치관 (Warmth, Empathy, Conscientiousness 등).
   - `Presentation`: 외면의 발현 방식 (Voice, Speed, Energy, Avatar, Expression, Gesture, Gaze).
2. **Read-only Cognitive Integration**:
   - Memory, Emotion, Relationship, Growth, Agency 엔진은 수정하지 않고, Presentation Planner가 상태를 읽어 표정/음성 변조에 활용.
3. **Presentation Cache Isolation**:
   - 캐시 키는 `presentation:{user_id}:{companion_id}`로 엄격히 격리.
4. **SB-5 Lifecycle Guard 연동**:
   - `ARCHIVED` 또는 `DELETED` 상태의 캐릭터는 Presentation 로딩 및 런타임 진입 즉시 차단.
5. **Zero Cross-Character Leakage**:
   - 캐릭터 전환(Switch) 시 이전 캐릭터 음성/애니메이션 정지 및 신규 캐릭터 Presentation 완전 동기화.

---

## 3. Proposed Changes

### 3.1 8대 아키텍처 및 정책 문서 (`docs/sb6/`)
- [NEW] `docs/sb6/SB6_PRESENTATION_ARCHITECTURE.md`
- [NEW] `docs/sb6/SB6_VOICE_PROFILE_ARCHITECTURE.md`
- [NEW] `docs/sb6/SB6_AVATAR_PROFILE_ARCHITECTURE.md`
- [NEW] `docs/sb6/SB6_PERSONALITY_PRESENTATION_BOUNDARY.md`
- [NEW] `docs/sb6/SB6_PROFILE_BINDING_FLOW.md`
- [NEW] `docs/sb6/SB6_CACHE_ISOLATION.md`
- [NEW] `docs/sb6/SB6_REGRESSION_RISK.md`
- [NEW] `docs/sb6/SB6_IMPLEMENTATION_DECISION.md`

### 3.2 DB Model Layer
- [NEW] `backend/app/db/models/character_presentation_profile.py` (`CharacterPresentationProfileModel`, `UNIQUE(companion_id)`)
- [MODIFY] `backend/app/db/models/__init__.py`

### 3.3 Domain Layer
- [NEW] `backend/app/domain/character/presentation_profile.py`
  - `VoiceProfileConfig`, `AvatarProfileConfig`, `ExpressionProfileConfig`, `GestureProfileConfig`
  - `CharacterPresentationProfile`, `CharacterPresentationContext`
- [MODIFY] `backend/app/domain/character/character_runtime_context.py` (Presentation 통합)
- [MODIFY] `backend/app/domain/character/__init__.py`

### 3.4 Service Layer
- [NEW] `backend/app/services/character/presentation_resolver.py` (`CharacterPresentationResolver`)
- [MODIFY] `backend/app/services/character/context_resolver.py` (Presentation 바인딩 연동)
- [MODIFY] `backend/app/services/character/lifecycle_service.py` (Presentation 캐시 Invalidation 연동)

### 3.5 API Layer & Schemas
- [MODIFY] `backend/app/api/schemas/character_schema.py` (`CharacterPresentationResponse`, `CharacterPresentationUpdateRequest`)
- [MODIFY] `backend/app/api/endpoints/characters.py`
  - `GET /api/v1/characters/{companion_id}/presentation`
  - `PATCH /api/v1/characters/{companion_id}/presentation`

---

## 4. Verification Plan

### Automated Tests (`pytest backend/tests/test_character_presentation_profile.py`) - 15대 테스트
- **Test 1**: Genie Presentation Resolution (아내 페르소나 및 음성/아바타)
- **Test 2**: Mani Presentation Resolution (사랑스러운 딸 페르소나 및 음성/아바타)
- **Test 3**: Hana Presentation Resolution (취미 친구 페르소나 및 음성/아바타)
- **Test 4**: Character-specific Voice Binding
- **Test 5**: Character-specific Avatar Binding
- **Test 6**: Character Switch Presentation Sync (Genie -> Mani -> Hana -> Genie)
- **Test 7**: Presentation Cache Isolation (`presentation:{user_id}:{companion_id}`)
- **Test 8**: Presentation Cache Invalidation
- **Test 9**: Archived Character Presentation Reject (SB-5 Guard)
- **Test 10**: Ownership Validation (403 Forbidden)
- **Test 11**: Genie Backward Compatibility
- **Test 12**: Voice Cross-Character Leakage Prevention
- **Test 13**: Avatar Cross-Character Leakage Prevention
- **Test 14**: Runtime Context Presentation Consistency
- **Test 15**: Presentation Update Rollback on DB failure

### Full Regression & Mobile Verification
- 전체 백엔드 45개 테스트 스위트 (`pytest`) 실행
- 모바일 TypeScript 컴파일 검증 (`npx tsc --noEmit`)
