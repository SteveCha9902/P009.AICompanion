# [SB-9 Architecture 1] Mobile Repository & Runtime Integration Audit

- **작성자**: 🐟 코다리 (Lead Architect) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-9 Multi-Character Mobile Studio & Real-Time Switching UX

---

## 1. Current State Audit

- **Backend Ready**:
  - `GET /api/v1/characters` (캐릭터 요약 목록)
  - `GET /api/v1/characters/active` (현재 활성 캐릭터)
  - `POST /api/v1/characters/{companion_id}/activate` (원자적 활성화 스위칭)
  - `POST /api/v1/characters/preview` (사전 컴파일 프리뷰)
  - `POST /api/v1/characters` (9개 엔티티 원자적 생성)
- **Mobile Gap Analysis**:
  - 현재 `RootNavigator.tsx`는 `CharacterProfileScreen`만 단일 탭으로 연결되어 있어 전체 캐릭터 갤러리 탐색 및 원터치 전환 UI가 부재함.
  - `Zustand`에 Multi-Character Store가 부재하여 활성 캐릭터의 변경이 `CompanionScreen` 및 `ConversationScreen`에 실시간 전파되지 못함.
- **Resolution Strategy**:
  - `useCharacterStore.ts` 및 `CharacterGalleryScreen.tsx` 신규 구현.
  - `CompanionScreen.tsx`와 `RootNavigator.tsx`를 확장하여 활성 캐릭터 상태 및 8단계 생성 위저드 연동.
