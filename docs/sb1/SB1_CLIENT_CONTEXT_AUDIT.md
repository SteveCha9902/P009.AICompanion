# [SB-1 Audit 7] Client & API Context Audit

- **작성자**: ✍️ Amy (Growth & Marketing) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-1 Character Runtime Foundation

---

## 1. Client & API 계층의 Character Context 흐름

### 1.1 API Request Flow
- `POST /api/v1/conversations/interactions` 엔드포인트:
  - Header: `X-User-ID` (기본값 `"default_user"`)
  - Body Payload: `message`, `conversation_id`, 선택적 `companion_id`
  - 백엔드 변환: `NormalizedInput(user_id=x_user_id, companion_id=body.companion_id, content=body.message)`

### 1.2 Mobile State Management (Zustand & React Native)
- `mobile/src/state/useAppStore.ts`:
  - 현재 단일 `companionState` (emotion, relationshipLevel) 유지.
  - 향후 SB-3(Character Switching Runtime)에서 `activeCompanionId` 및 멀티 캐릭터 갤러리 상태로 확장될 예정이며, 현재 SB-1 단계에서는 모바일 수정 없이 백엔드 런타임 호환성을 완벽히 지원함.

---

## 2. DTO와 Domain Context의 분리 원칙

```text
API Request Payload
        │
        ▼
NormalizedInput (Transport DTO: user_id, companion_id, content)
        │
        ▼
CompanionOrchestrator
        │
        ▼
CharacterContextResolver.resolve(user_id, companion_id)
        │
        ▼
CharacterRuntimeContext (Domain Context: Immutable)
```
- Transport DTO인 `NormalizedInput`에 무거운 도메인 객체를 포함하지 않고 순수 파라미터만 전달하여 레이어 간 결합도를 최소화합니다.
