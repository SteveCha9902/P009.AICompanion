# Memory System

단순히 지난 대화 n개를 Context에 붙여넣는 방식(Rolling Window)이 아닙니다. 의미 있는 장기 기억(Long-term Memory)을 추출하고 검색하는 엔진입니다.

## 1. Memory Types
- `FACT`: "사용자는 X-E5 카메라에 관심이 있다."
- `PREFERENCE`: "사용자는 휴대성이 좋은 기기를 선호한다."
- `EVENT`: "어제 X-E5와 R8을 비교했다."
- `GOAL`: "AI Companion 프로젝트를 개발 중이다."

## 2. Memory Extraction Pipeline
매 메시지마다 또는 대화 세션 종료 시 비동기적으로 실행됩니다.
```text
Conversation -> Memory Extractor (LLM 기반 요약/분석) -> Candidate Memory 생성 
-> Importance & Confidence 평가 -> Memory Store (DB) 저장
```

## 3. Memory Retrieval Pipeline
새로운 User Message가 들어올 때 관련된 과거 기억을 가져옵니다.
```text
Current Message -> Query Embedding -> Vector Search (pgvector)
-> Importance & Recency & Relationship Relevance 조합 점수 산출
-> Top N Memories 필터링 -> Context Builder로 전달
```
