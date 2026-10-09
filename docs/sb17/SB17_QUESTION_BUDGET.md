# [SB-17 Doc 5] Question Budget Manager Specification

- **작성자**: 🏃 정대리 (QA Lead) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-17 Natural Conversation, Dynamic Cadence & Quiet Empathy

---

## 1. Sliding Question Budget Algorithm

- 최근 3턴 중 AI가 질문한 횟수 `recent_questions_count` 추적:
  - `count >= 2`: 질문 예산 소진(Budget Depleted) ➔ 다음 턴 질문 생성 강제 억제 (`question_allowed = False`).
  - 사용자의 답변이 단문일 때 질문 억제 가중치 2배 적용.
