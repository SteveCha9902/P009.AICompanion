# [SB-7 Architecture 7] Lifecycle-Aware Memory Governance Policy

- **작성자**: 🐟 코다리 (Lead Architect) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-7 Character Memory Isolation & Independent Experience System

---

## 1. Character Lifecycle vs. Memory State

| 캐릭터 상태 (SB-5) | 런타임 Memory Retrieval | 물리적 메모리 데이터 | 복원 시 동작 |
| :--- | :--- | :--- | :--- |
| **AVAILABLE** | 정상 검색 및 축적 가능 | 보존 | - |
| **ARCHIVED** | 런타임 검색 차단 (`PermissionError`) | **영구 보존** (Non-destructive) | `RESTORE` 시 즉시 검색 재개 |
| **DELETED** | 런타임 검색 차단 (`PermissionError`) | **소프트 삭제 보존** | 복구 가능 |
