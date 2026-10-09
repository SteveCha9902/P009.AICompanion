# Sprint 4: Memory Engine Architecture & Pre-Implementation Report

> 이 문서는 Sprint 4 시작 전 확정된 Memory Engine의 핵심 아키텍처 원칙을 담고 있습니다.

## 1. Memory Source & Confidence
- **USER_EXPLICIT**: 사용자가 명시적으로 말한 사실 (High Confidence)
- **USER_CONFIRMED**: AI가 물어봤을 때 사용자가 맞다고 확정한 사실 (High Confidence)
- **INFERRED**: 사용자의 말이나 행동을 통해 AI가 추론한 사실 (Lower Confidence)
- **IMPORTED**: 외부 시스템이나 설정에서 가져온 사실
- **SYSTEM_DERIVED**: 시스템(규칙)에 의해 파생된 사실

## 2. Duplicate Detection vs Conflict Resolution
단순히 Embedding Similarity가 높다고 해서 중복(Duplicate)이 아닙니다. 
유사도가 높더라도 `Type`, `Subject`, `Entity`, `Polarity`를 종합적으로 판단하여 다음 중 하나의 관계(Relation Type)로 분류합니다:
- **DUPLICATE**: 완전히 동일한 내용 -> 기존 Memory의 `last_confirmed_at` 및 `confidence` 갱신
- **CONTRADICTORY**: 서로 모순되는 내용 (예: Canon만 좋아함 vs Canon 싫어함) -> 충돌 해결
- **COMPLEMENTARY**: 보완되는 내용 (예: Canon 좋아함 + Fujifilm 좋아함) -> 둘 다 ACTIVE 유지
- **TEMPORAL_UPDATE**: 시간의 흐름에 따른 선호도 변화 (예: 과거엔 Canon, 지금은 Fujifilm) -> 과거는 `SUPERSEDED`, 현재는 `ACTIVE`
- **NEW**: 완전히 새로운 기억

## 3. Temporal Memory 확장성
단순 `expires_at`이 아니라, 시간의 흐름을 반영하기 위해 다음 도메인 속성을 포함합니다.
- `memory_kind`: `PERSISTENT`(지속적), `TEMPORARY`(일시적), `EPISODIC`(특정 사건)
- `valid_from`, `valid_until`: 유효 기간 (향후 Relationship Engine 등에 활용)

## 4. Retrieval Score Normalization
Retrieval 시점(동적 계산)에 다음 공식을 통해 Top K를 산출합니다.
`Score = (0.50 * Semantic Similarity) + (0.20 * (Importance / 100)) + (0.20 * Recency Score) + (0.10 * Confidence)`

## 5. Memory User Control (UI & Privacy)
사용자는 자신에 대해 AI가 무엇을 알고 있는지 투명하게 볼 수 있어야 합니다.
- **List**: 카테고리별(Interests, Goals, Preferences 등) 요약 목록
- **Detail**: 구체적인 내용, Source, Confidence, 날짜, 원본 대화 출처 표시
- **Delete**: 사용자가 직접 기억 삭제 가능

## 6. Failure Isolation
Memory 추출, 임베딩, 검색에 실패하더라도 메인 **Conversation Engine은 절대 중단되지 않아야** 합니다. Vector DB 접근 실패 시 일반 Structured Query(키워드 등)로 Fallback 하도록 설계합니다.

## 7. Final Pipeline
```
USER MESSAGE -> Conversation -> LLM Response (Immediate to User)
       └-> [Background] Memory Extractor -> Candidate -> Validator (Relation check) -> Memory Store (Postgres + pgvector)
                                                                 └-> ContextBuilder <- MemoryContextProvider <- Memory Retriever
```
