# [SB-7 Architecture 5] Memory Write & Extraction Binding Policy

- **작성자**: 🐍 미나리 (Backend Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-7 Character Memory Isolation & Independent Experience System

---

## 1. Memory Write Validation Policy

- `CharacterRuntimeContext`에서 추출된 `companion_id`가 누락된 메모리 저장 요청은 원천 차단됩니다 (`ValueError("companion_id is required for memory persistence")`).
- 대화에서 발생한 사실적/사건적 기억만 `Memory` 테이블에 저장되며, 캐릭터의 원형적 취향 및 성격은 `CharacterProfile`/`CharacterDNA`에 분리 보관됩니다.
