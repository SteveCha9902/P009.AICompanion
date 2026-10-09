# [SB-1] Implementation Decision & 6-Question Synthesis

- **작성자**: 🧭 세종이 (PM) & 🐟 코다리 (Lead System Architect)
- **일자**: 2026-09-01
- **스프린트**: SB-1 Character Runtime Foundation

---

## 1. 8인 에이전트 감사 결과 통합: 6대 핵심 질문 답변

### Q1. 현재 P009에서 Character의 실제 Ownership Root는 무엇인가?
> **답변**: **`Companion` 엔티티(`companion_id`)**입니다.  
> `memories`, `emotion_states`, `relationship_states`, `avatar_profiles`, `agency_action_logs`, `character_global_growth_states` 등 모든 인지 및 프레젠테이션 데이터가 `companion_id`를 물리적/논리적 외래키 및 인덱스로 삼고 있습니다. 따라서 SB-1의 `CharacterScope`는 `(user_id, companion_id)`로 정의되어 완벽한 일치를 이룹니다.

### Q2. `CharacterRuntimeContext`를 생성하기 위한 최소 데이터는 무엇인가?
> **답변**: 다음 6가지 요소입니다:
> 1. `scope: CharacterScope` (`user_id`, `companion_id`)
> 2. `identity: CharacterIdentity` (이름, 배경 스토리, 자아정체성)
> 3. `personality: PersonalityProfile` (Big-5 및 인지/행동 성향 파라미터)
> 4. `memory_scope: CharacterMemoryScope` (`companion_id`, `namespace`)
> 5. `voice_profile: VoiceProfile` (고유 Voice ID, 음향 파라미터)
> 6. `avatar_profile: AvatarProfile` (외모, 표정/모션 프리셋)

### Q3. 기존 Engine 중 `CharacterScope`가 가장 먼저 필요한 것은 무엇인가?
> **답변**: **`ContextBuilder` 및 최상위 `CompanionOrchestrator`**입니다.  
> 인지 파이프라인의 진입 시점에 `CharacterScope`가 결정되어야 하위의 `MemoryRetriever`, `EmotionService`, `RelationshipService`가 해당 캐릭터의 컨텍스트를 올바르게 로드할 수 있습니다.

### Q4. 어떤 Engine은 현재 구조 그대로 유지할 수 있는가?
> **답변**: **거의 모든 하위 인지 엔진(Memory, Emotion, Relationship, Agency, Growth, Vision)**입니다.  
> 이 엔진들은 이미 `companion_id`를 인자로 받거나 참조하도록 설계되어 있으므로, SB-1에서 내부 알고리즘을 변경할 필요 없이 그대로 유지됩니다.

### Q5. SB-1에서 실제 수정/추가해야 하는 최소 파일 목록은 무엇인가?
> **신규 생성 파일**:
> - `backend/app/domain/character/character_runtime_context.py`
> - `backend/app/services/character/context_resolver.py`
> - `backend/tests/test_character_runtime_foundation.py`
> 
> **최소 수정 파일**:
> - `backend/app/services/companion/orchestrator.py` (Resolver 연동 및 `runtime_context` 수명주기 보장)
> - `backend/app/services/companion/runtime.py` (Composition Root에 Resolver 바인딩)

### Q6. SB-2에서 Database Migration을 안전하게 수행하기 위한 준비는 되었는가?
> **답변**: **예, 완벽하게 준비되었습니다.**  
> SB-1에서 `companion_id`를 중심으로 Runtime Boundary를 확립했으므로, SB-2에서는 `companions.user_id`의 `unique=True` 제약 해제 및 다중 캐릭터 시드 데이터 마이그레이션만으로 안전하게 DB 확장이 가능합니다.

---

## 2. 아키텍처 의사결정 기록 (ADR)

- **결정 1**: 새 `character_id` 체계를 강제 도입하지 않고 기존 `companion_id`를 `CharacterScope`의 내부 식별 키로 사용한다.
- **결정 2**: `CharacterRuntimeContext`는 `@dataclass(frozen=True)`로 정의하여 실행 중 불변성을 보장한다.
- **결정 3**: `CharacterRuntimeState`는 DB를 대체하지 않고 런타임 인지 스냅샷 용도로만 사용한다.
- **결정 4**: `CharacterContextResolver`는 `(user_id, companion_id)` 복합키 기반 캐시 격리를 수행한다.
