# Proactive Intelligence & Personal Routine Architecture

---

## 1. 개요 및 의사결정 흐름

```text
User / Environment Context
        ↓
Presence + Memory + Relationship + Routine Time
        ↓
Context Evaluation (ProactiveDecisionEngine)
        ↓
Should I act?
        ├─► [NO]  ➔ Silent (아무 행동도 하지 않음)
        └─► [YES] ➔ Intent Generation
                    ↓
            Safety / Permission Check
                    ↓
            Anti-Spam 2.0 (Cooldown, Limit, Quiet Hours)
                    ↓
            Local Notification / In-App Presence
                    ↓
            User Reaction (Open / Dismiss / Respond)
                    ↓
            Preference Learning & Feedback
```

---

## 2. Proactive Scoring & Decision Matrix

$$ProactiveScore = Relevance \times 0.30 + Confidence \times 0.25 + Timing \times 0.20 + Relationship \times 0.15 + Freshness \times 0.10$$

### 감점 요소 (Suppression Penalties)
- **Quiet Hours**: `22:00 ~ 07:00` ➔ Score 0.0 (강제 DENY)
- **Cooldown Interval**: 최근 발송 후 4시간 이내 ➔ 강제 DENY
- **Daily Cap**: 1일 3회 초과 ➔ 강제 DENY
- **Topic Duplicate**: 동일 주제 연속 제안 ➔ 강제 DENY
- **Threshold**: 최종 계산 점수가 `0.60` 미만 시 침묵(`DENY`) 유지.

---

## 3. Personal Routine Detection
- 사용자의 대화 시간대 패턴(예: 평일 09:00 근방 반복 대화)을 관찰 횟수 및 일관성(`confidence >= 0.85`) 기반으로 루틴 후보 생성 및 사용자 승인형 제안.
