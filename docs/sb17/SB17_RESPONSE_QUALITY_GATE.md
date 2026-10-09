# [SB-17 Doc 8] Response Quality Gate & Mechanical Empathy Defense

- **작성자**: 🏃 정대리 (QA Lead) & ✍️ Amy (AI Growth & Persona Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-17 Natural Conversation, Dynamic Cadence & Quiet Empathy

---

## 1. Quality Gate Violations & Deterministic Trimming

- **위반 규칙 1 (질문 차단 위반)**: `QUIET_EMPATHY`에서 물음표(`?`) 발견 시 후속 질문 문장 자동 제거.
- **위반 규칙 2 (기계적 공감 반복 방어)**: "많이 힘들었겠구나", "정말 힘들었겠다" 등 판에 박힌 어구 감지 시 캐릭터 고유의 어투로 변형.
- **위반 규칙 3 (문장 수 초과)**: 4문장 이상 과다 설명 시 상위 2~3문장으로 압축.
