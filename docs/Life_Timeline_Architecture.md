# Life Timeline & Personal History Architecture (Sprint 56)

본 문서는 Sprint 56에서 구축된 **Life Timeline & Personal History Engine**의 전체 시스템 아키텍처, 9대 타임라인 카테고리, 프라이버시 동의 정책(Privacy Consent Rule), 시계열 이벤트 그래프 및 서사적 회상(Narrative Recall) 파이프라인을 정의합니다.

---

## 🏛️ 1. 전체 아키텍처 구조

```text
[Relationship Memories (Sprint 50)]
                 │
                 ▼
         [TimelineBuilder]
   ├─ Timeline Privacy Policy Guard (Consent Check)
   └─ Auto-eligible: PET, HOBBY, PROJECT, GOAL, TRAVEL, HOME, PREFERENCE
   └─ Requires Consent: HEALTH, FAMILY, CAREER, FINANCIAL, RELIGION, POLITICS
                 │
                 ▼
           [EventLinker]
   (Builds Directed Causal Graph: Initial Event -> Progress -> Milestones)
                 │
                 ▼
      [PersonalHistoryEngine]
   (Extracts Temporal Narrative & Applies Event Confidence Modifiers)
                 │
                 ▼
     [TimelineRepairEngine]
   (Handles Real-time User Corrections & Deletions)
                 │
                 ▼
    [Companion Cognitive OS (CCOS)]
   (Selected Intent: RECALL_TIMELINE)
                 │
        ┌────────┴────────┐
        ▼                 ▼
 [ContextBuilder]    [Avatar Gaze & 3-Stage Emotion]
(Narrative Guidance) (Thinking -> Soft Smile -> Speaking)
```

---

## 🔒 2. Timeline Privacy & Consent Policy

1. **자동 편입 카테고리 (Auto-Eligible)**:
   - `PET`, `HOBBY`, `PROJECT`, `GOAL`, `TRAVEL`, `HOME`, `PREFERENCE`.
2. **명시적 동의 필수 카테고리 (Requires Explicit Consent)**:
   - `HEALTH`, `FAMILY`, `CAREER`, `FINANCIAL`, `RELIGION`, `POLITICS`.
   - 사용자의 명시적 동의가 없는 경우 타임라인에 등록되지 않고 철저히 보호됨.

---

## 📜 3. Event Confidence & Non-Dogmatic Narrative Guide

- **단정형 발화 100% 금지**:
  - ❌ *"너는 3개월 전에 식물을 샀어."*
  - ✅ *"전에 식물을 처음 들였다고 이야기했던 걸로 기억하는데, 잘 자라고 있어?"*
- **Timeline Repair Loop**:
  - 사용자의 정정 피드백(예: *"아니 그건 식물이 아니라 도자기 화분이었어"*) 발생 시 `TimelineRepairEngine`을 통해 즉시 내용 및 신뢰도를 100%로 갱신.
