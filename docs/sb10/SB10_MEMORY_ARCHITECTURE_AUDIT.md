# [SB-10 Audit 1] Memory Architecture & Tripartite Scope Audit

- **작성자**: 🐍 미나리 (Backend Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-10 Multi-Character Memory Isolation & RAG Anti-Leakage

---

## 1. 3대 메모리 스코프 모델 정의 (Tripartite Memory Scope)

```mermaid
graph TD
    UserContext[User Context] --> ScopeRouter{Scope Classifier}
    ScopeRouter -->|1. User Global Scope| GlobalMem[User Global Memory<br/>- user_id only<br/>- Global Preferences & Facts]
    ScopeRouter -->|2. Character Scope| CharMem[Character Memory<br/>- (user_id, companion_id)<br/>- 100% Strict Logical Isolation]
    ScopeRouter -->|3. Shared Scope| SharedExp[Shared Experience<br/>- Explicit Visibility Policy<br/>- Cross-Character Opt-in Only]
```

### 1.1 User Global Memory
- **소유권**: 사용자 개인에게 귀속되는 전역 정보 (이름, 글로벌 설정, 공통 팩트).
- **격리 규칙**: 캐릭터 간의 사적인 대화나 감정은 여기에 저장되지 않음.

### 1.2 Character Memory (Core Focus)
- **소유권**: `(user_id, companion_id)` 페어에 엄격히 귀속.
- **격리 규칙**: `companion_id`가 없는 조회는 즉시 Fail-Closed (`CharacterScopeRequiredError`) 처리.

### 1.3 Shared Experience
- **소유권**: 사용자 및 참여 캐릭터 간 명시적으로 허용된 공유 경험.
- **격리 규칙**: 단순히 `user_id`가 동일하다는 이유로 자동 공유되지 않으며, 명시적 `participants` 및 `visibility` 필터 적용.

---

## 2. Fail-Closed 원칙
- `companion_id` 누락 시 "전체 검색"을 수행하지 않고 즉시 거부(`CharacterScopeRequiredError`).
- "Scope를 모르면 검색하지 않는다."
