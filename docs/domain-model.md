# Domain Model

초기 핵심 Entity 및 관계 모델입니다. 데이터는 PostgreSQL 및 pgvector를 활용해 저장됩니다.

## 1. User & Persona
- `User`: 시스템 사용자 정보
- `Persona`: AI의 성격 데이터 (이름, 특징, 말투, 가치관, 행동 규칙). `values` 필드는 JSON 기반의 파라미터(warm, curious 등) 저장.

## 2. Conversation & Message
- `Conversation`: 연속된 대화의 세션. `id`, `user_id`, `started_at`, `ended_at`, `metadata`.
- `Message`: 대화 내 개별 발화. `id`, `conversation_id`, `role` (user/assistant/system), `content`, `created_at`.

## 3. Companion Internal States
- `Memory`: 과거 대화나 관찰에서 추출된 사실, 선호, 목표. (벡터 임베딩 값 포함)
- `EmotionState`: AI의 감정 스냅샷 (happiness, sadness, anger 등).
- `RelationshipState`: 사용자와의 관계 진척도 (level, trust, familiarity, interaction_count).
- `CompanionState`: 현재의 행동/상태 (presence, attention, activity).

## 4. Entity Relationships
- 1 User -> N Conversations -> N Messages
- 1 User -> N Memories
- 1 User -> 1 RelationshipState (또는 Snapshot History)
- 1 User -> 1 EmotionState (또는 Snapshot History)
