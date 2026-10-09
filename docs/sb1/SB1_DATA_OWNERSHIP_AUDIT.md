# [SB-1 Audit 2] Database & Domain Data Ownership Audit

- **작성자**: 📚 묵사관 (Memory Keeper) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-1 Character Runtime Foundation

---

## 1. 주요 테이블별 PK / FK 및 소유권(Ownership) 전수 분석

| 테이블명 (`__tablename__`) | Primary Key | Foreign Key / Owner Key | 소유권 단위 (Ownership Root) | 다중 인격 분리 상태 |
| :--- | :--- | :--- | :--- | :--- |
| `users` | `id` (String) | - | User Root | Global |
| `companions` | `id` (String) | `user_id` -> `users.id` | **Companion Runtime Root** | 1 User : N Companion (현재 unique=True) |
| `character_profiles` | `id` (String) | `companion_id` (String) | Companion | 1:1 Persona Definition |
| `character_personalities` | `id` (String) | `companion_id` (String) | Companion | 1:1 Big-5 DNA Definition |
| `memories` | `id` (String) | `companion_id` -> `companions.id` | **Companion Memory Scope** | `companion_id` 완전 격리 |
| `emotion_states` | `id` (String) | `companion_id` -> `companions.id` | **Companion Emotion Scope** | `companion_id` 1:1 격리 |
| `emotion_events` | `id` (String) | `companion_id` -> `companions.id` | Companion Emotion Log | `companion_id` 격리 |
| `relationship_states` | `id` (String) | `companion_id`, `user_id` | **Companion + User Bond** | 복합 소유권 (`companion_id` 격리) |
| `relationship_events` | `id` (String) | `companion_id` | Companion Bond Log | `companion_id` 격리 |
| `avatar_profiles` | `id` (String) | `companion_id` -> `companions.id` | Companion Visual Scope | `companion_id` 1:1 격리 |
| `voice_sessions` | `session_id` | `user_id`, `companion_id`, `conversation_id` | Interaction Session | 세션별 `companion_id` 격리 |
| `agency_action_logs` | `id` (String) | `user_id`, `companion_id` | Companion Agency Log | `companion_id` 격리 |
| `character_global_growth_states` | `id` (String) | `companion_id` | Global Character Growth | `companion_id` 1:1 격리 |
| `user_relationship_adaptations` | `id` (String) | `user_id`, `companion_id` | User-Companion Adaptation | Unique(`user_id`, `companion_id`) |

---

## 2. 핵심 발견 사항 (Critical Findings)

1. **`companion_id`가 이미 전체 시스템의 실질적인 격리 키**:
   - 모든 인지 엔진(기억, 감정, 관계, 아바타, 에이전시, 성장)이 `companion_id`를 외래키 또는 인덱스로 참조하고 있습니다.
2. **`character_id` 컬럼의 부재 및 도입 불필요**:
   - 시스템에는 별도의 `character_id` 외래키가 존재하지 않으며, `Companion` 엔티티 자체가 "인격체 인스턴스" 역할을 수행하고 있습니다.
   - 따라서 `CharacterScope`를 `(user_id, companion_id)`로 정의하는 것이 DB 스키마 변경 없이 완벽한 정합성을 달성하는 최적의 설계입니다.
3. **SB-2 마이그레이션 사전 준비사항**:
   - `companions.user_id`에 걸려 있는 `unique=True` 제약조건을 SB-2에서 제거(1:N 허용)하기만 하면 물리적 멀티 캐릭터 DB 구조가 즉시 완성됩니다.
