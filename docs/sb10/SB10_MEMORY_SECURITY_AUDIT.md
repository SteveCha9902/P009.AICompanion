# [SB-10 Audit 5] Memory Security & Ownership Audit

- **작성자**: 🔐 방대장 (DevOps/Security) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-10 Multi-Character Memory Isolation & RAG Anti-Leakage

---

## 1. Multi-User & Multi-Character Ownership Boundary

```text
User A ───> Character A (Genie) ───> Memory A
   │
   X (403 Forbidden)
   ▼
User B ───> Character B (Mani)  ───> Memory B
```

- **보안 감사 항목**:
  1. `wrong user_id`: 타 사용자의 캐릭터 기억 요청 시 `PermissionError` (403) 차단.
  2. `wrong companion_id`: 다른 캐릭터 ID를 요청할 경우 소유권 및 라이프사이클 가드가 차단.
  3. `missing companion_id`: 빈 값 전달 시 `CharacterScopeRequiredError` (Fail-Closed).
  4. `forged companion_id`: DB에 없는 위조 ID 접근 시 404/403 차단.
