# [SB-17 Doc 2] Conversation Mode Resolver Specification

- **작성자**: 🐟 코다리 (Lead Architect) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-17 Natural Conversation, Dynamic Cadence & Quiet Empathy

---

## 1. 7 Conversation Modes

| 모드 | 진입 조건 | 문장 수 | 질문 허용 | 공감 우선순위 |
| :--- | :--- | :--- | :--- | :--- |
| **NORMAL** | 일상 대화 | 1 ~ 3 문장 | Question Budget 허용 | 보통 |
| **EMOTIONAL_SUPPORT**| 고민, 기쁨, 감정 공유 | 1 ~ 3 짧은 문장 | 1개 이하 | 높음 |
| **QUIET_EMPATHY** | 피로, 극심한 슬픔, "그냥", "몰라" | **1 ~ 2 짧은 문장** | **0개 (금지)** | **최상 (경청/임재)** |
| **INFORMATION** | 명시적 사실/카메라/지식 요청 | 필요 충분 | 필요 시 허용 | 낮음 |
| **PLAYFUL** | 농담, 장난, 가벼운 티키타카 | 1 ~ 2 문장 | 유쾌한 반문 허용 | 보통 |
| **DEEP_CONVERSATION**| 철학, 장기 고민, 긴 이야기 | 2 ~ 4 문장 | 심층 질문 허용 | 높음 |
| **CLOSING** | "잘게", "쉴래", "그만하자" | **1 문장** | **0개 (금지)** | 보통 (따뜻한 배웅) |
