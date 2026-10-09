# [SB-10 Audit 2] Memory Repository & Scope Audit

- **작성자**: 🐍 미나리 (Backend Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-10 Multi-Character Memory Isolation & RAG Anti-Leakage

---

## 1. Memory Access Scope Rules

1. **Write Scope**: `validate_memory_write(user_id, companion_id, content)`를 통해 `companion_id`가 누락된 메모리 삽입 원천 차단 (`ValueError`).
2. **Read/Search Scope**: `MemoryRepository.search_similar(companion_id=...)` 및 `get_by_id` 시 반드시 `companion_id` 필터를 강제.
3. **Delete/Lifecycle Scope**: Archived/Deleted 상태의 캐릭터에 대한 기억 접근 차단 (`PermissionError`).
