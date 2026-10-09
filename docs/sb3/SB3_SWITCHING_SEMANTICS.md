# [SB-3 Architecture 4] Character Switching Semantics & Priority Hierarchy

- **작성자**: 🧭 세종이 (PM) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-3 Character Switching & Full Context Isolation

---

## 1. Scope 결정 3단계 우선순위 (Priority Hierarchy)

대화 요청이 인입될 때 다음 3단계 우선순위에 따라 단 1개의 `CharacterScope`가 확정됩니다:

1. **Explicit `companion_id` (명시적 요청)**:
   - 사용자가 API 요청 Payload에 `companion_id="sua"`를 명시한 경우.
   - 현재 활성 캐릭터가 Genie여도, 해당 단일 요청은 **Sua**로 확정 실행.
2. **Active Companion (활성 캐릭터 선호도)**:
   - `companion_id`가 생략(`None`)된 경우.
   - `CharacterRegistryService.get_active_companion_id(user_id)`를 조회하여 현재 활성화된 캐릭터로 확정 실행.
3. **Legacy Genie Fallback (기본 폴백)**:
   - 레지스트리 선호도가 없거나 DB 미구성 환경인 경우.
   - 기존의 Genie(`default_companion`)로 안전하게 확정 실행.

---

## 2. 동시 실행(Concurrent Interactions) 시맨틱스

- 사용자가 동일 세션 또는 다중 디바이스에서 지니 대화(Req A)와 수아 대화(Req B)를 동시에 호출할 경우:
  - Req A의 `InteractionContext` ➔ `CharacterScope(user_id, "genie")`
  - Req B의 `InteractionContext` ➔ `CharacterScope(user_id, "sua")`
- 두 상호작용은 각각 독립된 파이프라인에서 실행되며, 메모리 임베딩 검색/감정 계산/아바타 렌더링에 일체의 상호 오염이 발생하지 않습니다.
