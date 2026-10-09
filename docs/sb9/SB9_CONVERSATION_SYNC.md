# [SB-9 Architecture 5] Conversation Screen Scope Synchronization

- **작성자**: 🐍 미나리 (Backend Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-01
- **스프린트**: SB-9 Multi-Character Mobile Studio & Real-Time Switching UX

---

## 1. Conversation Scope Isolation

- 대화 화면(`ConversationScreen`, `CompanionScreen`)은 `useCharacterStore`의 `activeCharacter`를 구독합니다.
- 캐릭터 전환 즉시:
  1. 기존 대화 메시지 스트림 및 입력을 새 캐릭터 세션으로 분리합니다.
  2. LLM 컨텍스트 헤더 `x-user-id` 및 `active_companion_id`가 새 캐릭터 ID로 원자적 교체됩니다.
  3. 이전 캐릭터의 기억 및 감정 컨텍스트가 새 캐릭터에게 전달되지 않습니다 (Zero Leakage).
