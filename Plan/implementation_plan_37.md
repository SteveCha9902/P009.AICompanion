# Sprint 37: Long-Term Character Growth & Relationship Dynamics Engine (Enhanced Plan)

## 🎯 Sprint Mission
> **"캐릭터가 단순히 사실을 기억하는 것을 넘어, 사용자와 나눈 상호작용의 의미를 해석하고, 8차원 관계(Relationship Dynamics V2)를 점진적으로 진화시키며, 전역 성장(CharacterGlobalGrowth)과 사용자 맞춤 적응(UserRelationshipAdaptation)을 분리하여 발전시키는 Long-Term Growth & Dynamics Engine을 완성한다."**

---

## 🏛️ AntiGravity 8인 에이전트 역할 분담
- **🧭 세종이 PM**: Sprint 37 목표 관리 및 멀티유저 관계 격리 총괄, Quality Gates (R1~R6) 관리
- **🐟 코다리 Architect**: `(user_id, companion_id)` 복합 키 스키마, `RelationshipState V2` 통합, 가중치 기반 Bounded Delta Engine, `CharacterGlobalGrowth` vs `UserAdaptation` 분리 아키텍처 수립
- **🐍 미나리 과장 (Backend)**: `services/character/relationship/`, `growth/`, `timeline/` 도메인/엔진 구현, DB 마이그레이션 및 Orchestrator 후처리 연동
- **🌸 진달래 주임 (Vision/Avatar)**: 8차원 `RelationshipVector`의 `comfort`, `attachment` 및 `user_adaptation`에 맞춘 아바타 아이들 제스처/호흡 반응 연결
- **🏃 정대리 (QA)**: Gate R1~R6 (관계 연속성, 점진적 진화, 공동 경험 인식, Drift 없는 성장, 관계별 행동 차별화, 성찰 안정성) 테스트 자동화
- **✍️ Amy (Growth)**: 사용자 페르소나별 3단계 관계 서사(Stranger ➔ Friend ➔ Deep Bond) 성장 시나리오 검증
- **📚 묵사관 (Memory Keeper)**: `PROJECT.md`, `CHANGELOG.md`, `Decision_Log.md`, `walkthrough.md` 업데이트
- **🔐 방대장 (Security)**: Immutable Core 절대 불변성 보장, 멀티유저 데이터 격리 및 침해 차단

---

## 🔄 Cognitive Execution Pipeline (Sprint 37 Architecture)

```
                       USER INPUT
                           │
                           ▼
                  Situation Analysis
                           │
                           ▼
              CharacterBehaviorEngine
   (Immutable Core + Stable MBTI + Emotion + 
    RelationshipState V2 (8D) + UserRelationshipAdaptation +
    CharacterGlobalGrowth + Shared Experience)
                           │
                           ▼
                   CharacterDecision
                           │
                           ▼
                     LLM Generation
                           │
                           ▼
             CharacterConsistencyValidator
                           │
                           ▼
              Interaction Interpretation
         (Emotional Meaning + Relational Meaning)
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
Memory Extraction   Relationship Delta    Shared Experience
                    (Significance *        (Milestones)
                     Maturity Weighted)
                           │                   │
                           └─────────┬─────────┘
                                     ▼
                          Selective Reflection Trigger
                               (Rate < 20%)
                                     │
                                     ▼
                             Growth Engine
               (Global Growth + User-specific Adaptation)
                                     │
                                     ▼
                      Updated Character & Rel State
```

---

## 🧩 Proposed Changes

### 1. Database Schema (`backend/app/db/models/character_growth.py` & `relationship.py`)
#### [MODIFY] `backend/app/db/models/relationship.py` (RelationshipState V2 통합)
- `RelationshipStateModel` (`relationship_states` 테이블)을 8차원 벡터로 완전 흡수:
  - `user_id` (String Index, Composite Unique with companion_id)
  - `companion_id` (String Index)
  - `trust`, `closeness`, `comfort`, `attachment`, `playfulness`, `respect`, `emotional_safety`, `shared_history_depth` (Float)
  - `stage` (String)

#### [NEW] `backend/app/db/models/character_growth.py`
- `CharacterGlobalGrowthModel` (`character_global_growth_states` 테이블):
  - `companion_id` (String PK/Unique)
  - `support_style` (String)
  - `initiative_tendency` (String)
  - `global_learned_behavior` (JSON)
  - `updated_at` (DateTime)
- `UserRelationshipAdaptationModel` (`user_relationship_adaptations` 테이블):
  - `id` (UUID PK)
  - `user_id` (String Index)
  - `companion_id` (String Index)
  - `UNIQUE(user_id, companion_id)`
  - `preferred_formality` (Float)
  - `preferred_humor` (Float)
  - `preferred_directness` (Float)
  - `support_preference` (String)
  - `conversation_rhythm` (String)
  - `updated_at` (DateTime)
- `RelationshipMilestoneModel` (`relationship_milestones` 테이블):
  - `user_id`, `companion_id`, `milestone_type`, `significance`, `summary`, `created_at`

---

### 2. Relationship Dynamics & Weighted Evolution Engine (`services/character/relationship/`)
#### [NEW] `backend/app/services/character/relationship/domain.py`
- `RelationshipVector` (8D: trust, closeness, comfort, attachment, playfulness, respect, emotional_safety, shared_history_depth)
- `RelationshipDelta`: `raw_delta`, `significance_weight`, `maturity_factor`, `final_delta` ($\text{clamp}(-0.03, +0.03)$)
- `RelationshipMilestone`

#### [NEW] `backend/app/services/character/relationship/evolution.py`
- `RelationshipEvolutionEngine`:
  - `calculate_delta(interaction, significance, current_maturity) -> RelationshipDelta`
  - 관계 깊이(SharedHistoryDepth)가 높을수록 Delta Sensitivity가 점진적으로 완만해지는 감쇠 공식 적용.

---

### 3. Shared Experience System (`services/character/timeline/`)
#### [NEW] `backend/app/services/character/timeline/shared_experience.py`
- `SharedExperienceEngine`: 사실 메모리와 차별화된 사건/정서적 의미/관계 영향 체인 관리.

---

### 4. Character Growth & User Adaptation (`services/character/growth/`)
#### [NEW] `backend/app/services/character/growth/domain.py`
- `CharacterGlobalGrowthState` (캐릭터 전반의 보편적 성장)
- `UserRelationshipAdaptationState` (특정 사용자 맞춤형 말투/호흡 적응)
- **Immutable Core는 절대 수정 불가 (LOCKED)**

#### [NEW] `backend/app/services/character/growth/growth_engine.py`
- `CharacterGrowthEngine`: 전역 성장과 사용자별 적응을 분리하여 점진적 갱신.

---

### 5. Orchestrator & ContextBuilder Integration
#### [MODIFY] `backend/app/services/companion/orchestrator.py`
- Context Snapshot에 `user_id`를 전달하여 8D `RelationshipVector` 및 `UserRelationshipAdaptation` 로드.
- 대화 종료 후 비동기 파이프라인에서 가중치 Bounded Delta 및 Adaptation 갱신.

---

## 🧪 Verification Plan

### 1. Automated Tests (정대리 QA)
- `tests/test_character_growth_and_relationship_dynamics.py`:
  - **Gate R1 [Relationship Continuity & Multi-User Isolation]**: 세션 간 및 사용자별(User A vs User B) 격리 및 연속성 검증
  - **Gate R2 [Weighted Gradual Evolution]**: Significance 및 Maturity 가중치 기반 $\text{Delta} \le 0.03$ 검증
  - **Gate R3 [Shared Experience Recognition]**: Fact Memory vs Shared Experience 분리 검증
  - **Gate R4 [Character Growth without Personality Drift]**: 1000회 시뮬레이션 후 Immutable Core 불변 검증
  - **Gate R5 [Relationship-specific Behavior]**: Stranger vs Close 및 맞춤 적응(Adaptation)별 행동 차별화 검증
  - **Gate R6 [Reflection Stability]**: 성찰 트리거 비율 < 20% 안정성 검증

---

## 🏁 Quality Gates (DoD)
- **Gate R1 [Continuity & Multi-User Isolation]**: PASS
- **Gate R2 [Weighted Gradual Evolution]**: PASS
- **Gate R3 [Shared Experience Separation]**: PASS
- **Gate R4 [Drift-Free Core Lock]**: PASS
- **Gate R5 [Rel-specific Behavior & Adaptation]**: PASS
- **Gate R6 [Reflection Stability (<20%)]**: PASS
- **Backend Test Suite**: 전체 45+ 테스트 100% PASS
- **Mobile TypeScript**: 0 Errors
