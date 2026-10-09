# [SB-7 Architecture 6] Memory Cache Isolation & Invalidation Policy

- **작성자**: 🔐 방대장 (DevOps/Security) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-01
- **스프린트**: SB-7 Character Memory Isolation & Independent Experience System

---

## 1. 메모리 캐시 키 격리 규칙

- **표준 캐시 키**: `memory_cache:{user_id}:{companion_id}:{query_hash}`
- **절대 금지**: `memory_cache:{user_id}:{query_hash}` (사용자 단위 공유 캐시 금지)

---

## 2. Invalidation 트리거

- 해당 `companion_id`에 신규 메모리가 추가되거나 갱신될 때
- 캐릭터 전환 및 아카이브 발생 시
- `MemoryRetriever.invalidate_cache(user_id, companion_id)` 호출.
