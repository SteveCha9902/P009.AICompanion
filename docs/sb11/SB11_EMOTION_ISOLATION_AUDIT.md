# [SB-11 Audit 2] Emotion State & Transition Isolation Audit

- **작성자**: 🐍 미나리 (Backend Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-11 Multi-Character Dynamic State Isolation & Concurrency Safety

---

## 1. Emotion Isolation Verification

```text
Genie Request (Scope: genie_pk) ➔ EmotionState(genie_pk) ➔ Transition/Decay ➔ Save(genie_pk)
Mani Request  (Scope: c_mani)   ➔ EmotionState(c_mani)   ➔ Transition/Decay ➔ Save(c_mani)
Hana Request  (Scope: c_hana)   ➔ EmotionState(c_hana)   ➔ Transition/Decay ➔ Save(c_hana)
```

- **감사 결과**:
  - `EmotionState` 테이블은 `companion_id` (Unique/Indexed)를 보유.
  - Genie의 감정 변화(예: JOY +0.3)가 Mani의 감정 상태에 전혀 영향을 주지 않으며, 동시 요청 시에도 격리된 트랜잭션으로 처리됨.
