# Future Planning & Life Goals Architecture (Sprint 57)

본 문서는 Sprint 57에서 구축된 **Life Goals & Future Planning Engine**의 전체 시스템 아키텍처, GoalCandidate 확인 승인 워크플로우, D-Day 계산 및 비압박형 회상(Non-Controlling Recall) 파이프라인을 정의합니다.

---

## 🏛️ 1. 전체 아키텍처 구조

```text
[Conversation Input & Life Timeline]
                 │
                 ▼
          [GoalExtractor]
   (Extracts Intentions -> Generates GoalCandidate)
                 │
                 ▼
      [User Confirmation Loop]
   ("이걸 목표로 기억해둘까요?" -> Approved)
                 │
                 ▼
         [PlanningEngine]
   ├─ 10 GoalTypes & 6 GoalStatuses (IDEA -> ACTIVE -> COMPLETED / ARCHIVED)
   ├─ Commitment Level & GoalMilestones Decomposition
   └─ Gentle Archiving (No Failure Labeling)
                 │
                 ▼
           [DDayEngine]
   (Calculates D-Day, D-7, D-30 Countdown Notes)
                 │
                 ▼
        [GoalRecallEngine]
   (Follows 'Companion, Not Manager' Charter -> Non-controlling Inquiry / Celebration)
                 │
                 ▼
    [Companion Cognitive OS (CCOS)]
   (Intents: PLAN / GOAL_REVIEW / CELEBRATE_PROGRESS)
                 │
        ┌────────┴────────┐
        ▼                 ▼
 [ContextBuilder]    [Avatar Emotion Embodiment]
(Encouraging Prompt) (Thoughtful -> Warm Concern -> Proud Celebration)
```

---

## 🛡️ 2. 핵심 원칙: "Companion, Not Manager"

1. **User Agency First (사용자 주체성 최우선)**:
   - 모든 목표는 사용자의 소유이며, AI는 제안/회상/격려만 수행.
2. **No Guilt Induction & ARCHIVED Policy**:
   - 목표 중단 시 "실패"나 "포기"로 라벨링하지 않고 `ARCHIVED`로 온화하게 보관.
3. **Goal Candidate Approval Workflow**:
   - 지나가는 말을 무단으로 목표에 등록하지 않고 사용자의 명시적 승인을 거쳐 등록.
