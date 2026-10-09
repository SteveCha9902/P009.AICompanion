# SPRINT 4 PRE-IMPLEMENTATION REPORT: Memory Engine

> [!NOTE]
> 본 리포트는 P009.AICompanion Sprint 4 (Memory Engine)의 실제 구현을 시작하기 전 작성된 사전 분석 및 실행 계획서입니다. 승인 시 이 계획을 바탕으로 코드 구현이 시작됩니다.

---

## 1. Sprint 3 완료 상태
- `User -> Companion -> Persona` 장기 도메인 분리 완료.
- `PersonaContextProvider`를 통한 Semantic Mapping 및 Trust Boundary (프롬프트 인젝션 방어) 구현.
- 모바일 설정 UI 및 Preset API 연동 완료.

## 2. Current ContextBuilder
- 현재 `[TRUSTED SYSTEM RULES]` 하단에 각 Provider가 주입하는 어플리케이션 컨텍스트를 순차적으로 삽입하고, 유저 발화는 가장 마지막에 `[UNTRUSTED USER INPUT]`으로 격리하여 주입하는 구조입니다.

## 3. Current Persona Architecture
- Persona는 수치적 성격(0~100)을 지니고 있으며 LLM에는 의미론적 수식어(low, high 등)로 번역되어 전달됩니다. 이는 Companion의 기본 성향을 의미하며 구체적인 사용자 정보(Memory)와는 다릅니다.

## 4. Current Database
- `users`, `companions`, `personas`, `conversations`, `messages`로 구성되며, PostgreSQL + Alembic 마이그레이션이 적용된 상태입니다.

## 5. Memory Domain Model
- Memory는 단순 대화 히스토리가 아니라, **재사용 가치가 있는 구조화된 지식**입니다.
- **Attributes**: `id`, `companion_id`, `type`, `content`, `subject`, `importance`(0-100), `confidence`(0.0-1.0), `source`(USER/INFERRED/SYSTEM), `source_message_id`, `created_at`, `updated_at`, `last_accessed_at`, `expires_at`, `status`(ACTIVE/SUPERSEDED/DELETED).

## 6. Memory Schema
- 테이블명: `memories`.
- PostgreSQL의 `pgvector` 확장을 활용하여 `embedding` 컬럼(Vector)을 추가함으로써 Semantic Search 기능을 구현합니다.

## 7. Memory Type
- `PERSONAL_FACT`, `PREFERENCE`, `DISLIKE`, `INTEREST`, `HABIT`, `GOAL`, `IMPORTANT_EVENT`, `RELATIONSHIP_FACT` 의 범주를 사용합니다.

## 8. Memory Lifecycle
- `Conversation Message 완료` -> `비동기(Background) Extraction` -> `Validation (중복/충돌 체크)` -> `DB & Vector Store 저장` -> `이후 대화 시 Retrieval` -> `Context Builder 주입`

## 9. Extraction Architecture
- LLM에 백그라운드 태스크로 `MemoryExtractor`를 할당합니다.
- 최근 N개의 메시지를 분석해 "장기적으로 유용한 새로운 정보가 있는가?"를 묻고 구조화된 JSON 리스트로 응답받습니다 (Structured Data). 일상적인 잡담(예: "오늘 날씨 좋네")은 무시합니다.

## 10. Validation Architecture
- 생성된 Candidate를 즉시 저장하지 않고 검증 단계를 거칩니다.
  1. 내용 명확성 및 유용성 평가 (일시적 정보 폐기).
  2. 추론과 명시적 사실의 분리 (Confidence 조정).

## 11. Duplicate Detection
- 새로운 Memory Candidate의 임베딩을 통해 기존 DB와 Vector Search를 수행합니다.
- Semantic Similarity가 매우 높은 동일 주제의 기억이 있을 경우, 새 레코드를 만들지 않고 기존 레코드의 `updated_at`과 `confidence`만 갱신합니다.

## 12. Conflict Resolution
- 기존 Memory와 상충되는 정보(예: "이전엔 Canon 선호, 지금은 Fujifilm 선호")가 발생하면, 기존 Memory의 `status`를 `SUPERSEDED`로 변경하고 새 Memory를 `ACTIVE`로 인서트하여 과거 데이터 소실 없이 맥락을 유지합니다.

## 13. Embedding Architecture
- `BaseEmbeddingProvider` 인터페이스를 설계하고, `OpenAIEmbeddingProvider`를 통해 텍스트(`content` + `subject` + `type`)를 Vector로 변환합니다. 실패 시에도 Fallback(단순 Keyword or 구조화 검색)을 가능케 하도록 결합도를 낮춥니다.

## 14. Retrieval Architecture
- 유저 메시지가 들어오면 `MemoryRetriever`가 해당 메시지를 임베딩하여 Vector Search를 수행합니다. 연관성 있는 `ACTIVE` 상태의 Memory만 가져옵니다.

## 15. Ranking Formula
Retrieval 시 Vector Similarity만 맹신하지 않고 Hybrid Scoring을 수행합니다.
- `Score = (Similarity * 0.5) + (Importance * 0.2) + (Recency(시간 가중치) * 0.2) + (Confidence * 0.1)`
- Top K(예: 3~5개)만 선별하여 Context Budget 폭발을 막습니다.

## 16. MemoryContextProvider
- `ContextProvider`를 상속받아, Retriever가 반환한 기억들을 문자열 블록으로 포맷팅합니다.
- 예: `[RETRIEVED APPLICATION CONTEXT: MEMORY]\nKNOWN USER INFORMATION:\n- User prefers Fujifilm cameras.`

## 17. API 설계
- `GET /api/v1/memories`: 현재 활성화된 기억 목록 반환.
- `GET /api/v1/memories/{id}`: 특정 기억 단건 반환.
- `DELETE /api/v1/memories/{id}`: 기억 삭제 (Soft Delete: 상태를 DELETED로 변경).

## 18. Mobile UI 설계
- Settings 안에 **Memory (What I Remember)** 화면 신설.
- 사용자에게 수집된 기억을 리스트로 명확히 노출하며, 각 항목 옆에 **[Delete]** 버튼을 두어 스스로 제어할 수 있게 합니다.

## 19. Privacy & Security
- Memory는 유저별(`companion_id`)로 엄격하게 격리되며, `DELETE` 시 즉시 응답에서 제외됩니다.
- Memory는 `System Rules`를 덮어쓸 수 없으며 (Trust Boundary 하위 계층), Application Context로만 취급됩니다.

## 20. 예상 변경 파일
- `backend/app/db/models/memory.py`
- `backend/alembic/versions/` (pgvector 및 테이블 추가)
- `backend/app/services/memory/extractor.py`, `retriever.py`, `embedding.py`
- `backend/app/services/context/providers/memory_provider.py`
- `backend/app/api/endpoints/memories.py`
- `mobile/src/screens/MemoryScreen.tsx`, `api.ts`

## 21. Implementation Order
1. Memory Domain & DB Schema (pgvector)
2. Memory Repository
3. Embedding Provider Interface & Implementation
4. Memory Extractor (Structured Output from LLM)
5. Memory Validator (Duplicate & Conflict Handling)
6. Memory Retriever (Ranking Formula)
7. MemoryContextProvider 연동
8. API & Mobile UI
9. Memory Quality/Consistency Test 작성

> [!IMPORTANT]
> SPRINT 4의 목표는 단순 RAG (Retrieval-Augmented Generation)가 아니라, **유의미한 장기 기억의 생성-검증-재조합-갱신**을 수행하는 하이브리드 엔진을 구축하는 것입니다. 본 사전 계획서에 대한 검토 및 승인을 요청드립니다.
