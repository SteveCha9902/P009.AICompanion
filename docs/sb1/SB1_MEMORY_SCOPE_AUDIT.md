# [SB-1 Audit 4] Memory & Knowledge Scope Audit

- **작성자**: 🐍 미나리 (Backend Lead) & 📚 묵사관 (Memory Keeper)
- **일자**: 2026-09-01
- **스프린트**: SB-1 Character Runtime Foundation

---

## 1. Memory Engine 격리 구조 조사

### 1.1 Memory Repository & Model Key 분석
- `memories` 테이블:
  ```python
  companion_id = Column(String, ForeignKey("companions.id"), index=True, nullable=False)
  ```
- `autobiographical_memories` 및 `life_timelines`: 모두 `companion_id` 필드를 보유.
- `MemoryRetriever.search_memories(companion_id, query_embedding, limit)`:
  - 쿼리 검색 조건에 `companion_id == target_companion_id`가 필수 조건으로 바인딩되어 있음.

---

## 2. 4대 핵심 질문에 대한 답변

| 질문 | 답변 | 상태 |
| :--- | :--- | :--- |
| **현재 Memory Retrieval이 user_id 기준인가?** | 아니오. `companion_id` 기준입니다. | 격리 완료 |
| **conversation_id 기준인가?** | 대화 히스토리(최근 10턴)는 `conversation_id`, 시맨틱 장기 기억은 `companion_id` 기준입니다. | 분리 완료 |
| **companion_id 기준인가?** | **예. 장기 기억의 핵심 Partition Key는 `companion_id`입니다.** | 완벽 격리 |
| **namespace가 존재하는가?** | 메모리 타입(`MemoryType.FACT`, `EMOTIONAL_MEMORY` 등)으로 분류되며, SB-1에서 `CharacterMemoryScope` 도입으로 네임스페이스를 표준화합니다. | 표준화 진행 |

---

## 3. 격리 보장성 및 향후 계획

- `CharacterMemoryScope(companion_id, namespace="default")`를 `CharacterRuntimeContext` 내에 명시하여, 향후 다른 캐릭터(수아, 하나 등)가 등록되어도 벡터 임베딩 검색 시 지니의 기억이 절대 누수되지 않도록 보장합니다.
