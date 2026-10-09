# [SB-9 Architecture 3] Zustand Character Store & State Machine Specification

- **작성자**: 🏃 정대리 (QA Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-01
- **스프린트**: SB-9 Multi-Character Mobile Studio & Real-Time Switching UX

---

## 1. Store Responsibility Contract

- **Store가 관리하는 것**:
  - `characterList: CharacterSummary[]`
  - `activeCharacterId: string | null`
  - `activeCharacter: CharacterSummary | null`
  - `isLoading: boolean`
  - `isSwitching: boolean`
  - `error: string | null`
  - `lastUpdated: number | null`
- **Store가 관리하지 않는 것 (Backend Sole Ownership)**:
  - Memory, Emotion, Relationship, Growth, Agency, LLM Context, Character DNA.
