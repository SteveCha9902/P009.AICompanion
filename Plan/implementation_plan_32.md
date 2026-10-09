# Sprint 32: Autobiographical Memory & Shared Life Timeline Engine Implementation Plan

## 🎯 Sprint Mission
> **"단순 기억(Facts/Preferences) 저장소를 넘어, 캐릭터의 자전적 기억(Autobiographical Memory)과 사용자와 함께 쌓아가는 공동 역사(Shared Life Timeline)를 구축하여 시간적 연속성(Time Continuity)을 갖춘 진정한 동반자 서사를 완성한다."**

---

## 🏛️ AntiGravity 8인 에이전트 역할 분담
- **🧭 세종이 PM**: Sprint 32 범위 및 라이프사이클 관리, Quality Gates (M1~M12) 관리
- **🐟 코다리 Architect**: Episodic Memory ➔ Life Event ➔ Shared Experience ➔ Story Chapter ➔ Timeline 파이프라인 및 Truth Boundary 아키텍처 수립
- **🐍 미나리 과장 (Backend)**: Autobiographical Domain, DB Models 5종, Event Importance Engine, Life Event Promoter, Shared Experience Engine, Temporal Fusion Retrieval, Context Compiler, API 엔드포인트 구현
- **🌸 진달래 주임 (Vision/Mobile)**: Mobile Shared Story UI (`SharedStoryScreen.tsx`), 서사 챕터 카드, 공동 역사 타임라인 시각화
- **🏃 정대리 (QA)**: Episodic Extraction, Importance Scoring, Life Event Promotion, Duplicate Prevention, Experience Linking, Temporal Retrieval, Truth Boundary, Memory Deletion Cascade 단위/통합 테스트 자동화
- **✍️ Amy (Growth)**: "우리가 함께한 시간" 감성적 스토리텔링 카피라이팅 및 서사 챕터 테마 정의
- **📚 묵사관 (Memory Keeper)**: `PROJECT.md`, `Architecture.md`, `Decision_Log.md`, `CHANGELOG.md` 히스토리 영속화
- **🔐 방대장 (Security)**: Memory Provenance 추적, Selective Forgetting(삭제 연쇄), Privacy 보안 검증

---

## 🧩 Proposed Changes

### 1. Backend Memory Domain Layer (`domain/memory/`)
#### [NEW] `backend/app/domain/memory/episodic_memory.py`
- `EpisodicMemory`: `id`, `conversation_id`, `interaction_id`, `occurred_at`, `summary`, `participants`, `emotional_context`, `importance`, `event_type`, `embedding_id`

#### [NEW] `backend/app/domain/memory/life_event.py`
- `LifeEventCategory` (Enum): `PROJECT_MILESTONE`, `PERSONAL_MILESTONE`, `CAREER_EVENT`, `ACHIEVEMENT`, `IMPORTANT_DECISION`, `RELATIONSHIP_MILESTONE`, `DIFFICULT_PERIOD` 등
- `LifeEvent`: `id`, `title`, `summary`, `category`, `occurred_at`, `importance`, `emotional_weight`, `relationship_significance`, `source_episode_ids`

#### [NEW] `backend/app/domain/memory/shared_experience.py`
- `SharedExperience`: `id`, `title`, `summary`, `started_at`, `last_referenced_at`, `companion_involvement_level`, `is_co_experienced` (우리가 함께 겪었는가 여부), `related_life_event_ids`

#### [NEW] `backend/app/domain/memory/story_chapter.py`
- `StoryChapter`: `id`, `chapter_number`, `title`, `theme`, `started_at`, `ended_at`, `summary`, `importance`, `event_ids`

#### [NEW] `backend/app/domain/memory/timeline_event.py`
- `TimelineEvent`: `id`, `occurred_at`, `title`, `summary`, `importance`, `event_type`, `story_chapter_id`

#### [NEW] `backend/app/domain/memory/autobiographical_context.py`
- `AutobiographicalContext`: `active_chapters`, `shared_experiences`, `recent_life_events`, `narrative_summary`

#### [NEW] `backend/app/domain/memory/__init__.py`
- 도메인 모델 통합 익스포트

---

### 2. Database Persistence Layer (`db/models/`)
#### [NEW] `backend/app/db/models/autobiographical_memory.py`
- `EpisodicMemoryModel`: `episodic_memories` 테이블
- `LifeEventModel`: `life_events` 테이블
- `SharedExperienceModel`: `shared_experiences` 테이블
- `TimelineEventModel`: `timeline_events` 테이블
- `StoryChapterModel`: `story_chapters` 테이블
- `backend/app/db/models/__init__.py` 등록

---

### 3. Backend Services Layer (`services/memory/` & `services/shared_experience/`)
#### [NEW] `backend/app/services/memory/event_importance_engine.py`
- Novelty + Emotional Intensity + Personal Significance + Relationship Significance 종합 중요도(0.0~1.0) 계산기

#### [NEW] `backend/app/services/memory/life_event_promoter.py`
- 중요도(>=0.75) 및 중복 검증(Duplicate Detection)을 거쳐 Episode를 Life Event로 승격

#### [NEW] `backend/app/services/shared_experience/experience_linker.py`
- 토픽/시간적 인접성/감정 연속성에 따라 독립된 사건들을 하나의 서사 체인으로 연결

#### [NEW] `backend/app/services/shared_experience/shared_experience_engine.py`
- 지속적 대화와 교감이 일어난 사건을 '우리의 공동 경험'으로 승격 및 관리

#### [NEW] `backend/app/services/memory/temporal_memory_retriever.py` & `memory_fusion_retriever.py`
- 의미론적(Semantic) + 시간적(Temporal) + 서사적(Story) 다차원 메모리 퓨전 검색

#### [NEW] `backend/app/services/memory/autobiographical_context_compiler.py`
- **Memory Truth Boundary 준수**:
  - 컴패니언이 직접 동행/대화한 사건 ➔ *"우리가 함께 고민하고 완성했던..."*
  - 사용자의 개인 외부 경험 ➔ *"네가 이야기해주었던..."*
  - 엄격한 왜곡 방지 및 `[SHARED HISTORY]` 블록 컴파일

#### [NEW] `backend/app/services/memory/autobiographical_narrative_service.py`
- "우리의 이야기" 서사 요약 생성 엔진

#### [MODIFY] `backend/app/services/context/providers/memory_provider.py`
- ContextBuilder Level 3의 Memory Provider에 Autobiographical Context 및 Shared Experience 융합 주입

#### [NEW] `backend/app/api/endpoints/memory_timeline.py`
- `GET /api/v1/memory/timeline`: 공동 역사 타임라인 반환
- `GET /api/v1/memory/story`: 서사 챕터 목록 반환
- `GET /api/v1/memory/life-events`: 주요 Life Event 목록 반환
- `GET /api/v1/memory/shared-experiences`: Shared Experience 목록 반환
- `POST /api/v1/memory/narrative`: 서사적 회고 응답 생성
- `DELETE /api/v1/memory/selective-forget`: Selective Forgetting (선택적 기억 삭제 연쇄)

#### [MODIFY] `backend/app/main.py`
- `memory_timeline.router` 등록

---

### 4. Mobile Frontend Layer (`mobile/src/features/memory/`)
#### [NEW] `mobile/src/features/memory/domain/timeline.ts`
- Shared Life Timeline, Story Chapter, Life Event 데이터 인터페이스

#### [NEW] `mobile/src/features/memory/services/memoryTimelineService.ts`
- Timeline 및 Story API 클라이언트

#### [NEW] `mobile/src/screens/SharedStoryScreen.tsx`
- "OUR STORY: 우리가 함께한 시간" 타임라인 뷰어
- 챕터별 카드 (Chapter 1: 처음 만난 날, Chapter 2: 새로운 프로젝트 등)
- 주요 마일스톤 Life Event 시각화

#### [MODIFY] `mobile/src/navigation/RootNavigator.tsx` & `mobile/src/screens/MemoriesScreen.tsx`
- 스토리 화면 네비게이션 연동

---

## 🧪 Verification Plan

### 1. Automated Tests (정대리 QA)
- `tests/test_autobiographical_memory.py`:
  - Gate M1: Episodic Memory 추출 및 구조 검증
  - Gate M2: Importance Scoring (일상 잡담 0.1 vs 중요 프로젝트 0.9)
  - Gate M3 & M4: Life Event 승격 및 중복 방지 (Duplicate Detection)
  - Gate M5: Shared Experience Linking (A ➔ B ➔ C 서사 체인 연결)
  - Gate M6 & M7: Timeline 및 Story Chapter 생성
  - Gate M8: Temporal Memory Fusion Retrieval (시간 기반 검색)
  - Gate M9 & M10: Shared History Context 및 Provenance Truth Boundary (허위 공동 경험 주장 차단)
  - Gate M11: Selective Forgetting & Deletion Cascade (기억 삭제 시 서사 무결성 유지)
  - Gate M12: Single Pipeline 회귀 검증

### 2. Manual Device Verification
- 스마트폰에서 Memories 탭 또는 Shared Story 화면을 열어 지니와의 서사 챕터 및 마일스톤 타임라인이 아름답게 렌더링되는지 확인.
- 실제 채팅에서 *"우리가 처음 이야기했던 거 기억나?"*, *"우리가 같이 했던 프로젝트 이야기해줘"* 입력 시 지니가 정확한 시간 순서와 서사적 맥락으로 응답하는지 검증.

---

## 🏁 Quality Gates (DoD)
- **Gate M1 [Episodic Extraction]**: 대화에서 Episode 추출 (PASS)
- **Gate M2 [Importance Scoring]**: 중요도 평가 엔진 (PASS)
- **Gate M3 [Life Event Promotion]**: 중요 사건 Life Event 승격 (PASS)
- **Gate M4 [Duplicate Prevention]**: 동일 마일스톤 중복 생성 방어 (PASS)
- **Gate M5 [Experience Linking]**: 서사 체인 연결 (PASS)
- **Gate M6 [Timeline Builder]**: 시간축 타임라인 구축 (PASS)
- **Gate M7 [Story Chapters]**: 챕터별 스토리 구성 (PASS)
- **Gate M8 [Temporal Retrieval]**: 시간/엔티티 융합 검색 (PASS)
- **Gate M9 [Shared History Context]**: 정성적 Autobiographical Context 주입 (PASS)
- **Gate M10 [Truth Boundary]**: 경험 왜곡 및 환각 차단 (PASS)
- **Gate M11 [Deletion Cascade]**: 기억 삭제 연쇄 무결성 (PASS)
- **Gate M12 [Pipeline Integrity]**: 기존 8-Context Single Pipeline 유지 (PASS)
