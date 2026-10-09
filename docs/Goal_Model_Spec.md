# Goal & Milestone Model Specification (Sprint 57)

본 문서는 미래 목표와 마일스톤을 정의하는 `GoalCandidate`, `Goal`, `GoalMilestone` 및 `DDayInfo` 규격을 기술합니다.

---

## 📦 1. Goal & Milestone DTOs

```typescript
interface GoalCandidate {
  candidateId: string;
  userId: string;
  title: string;
  goalType: GoalType;
  confidence: number;                  // 0.0 ~ 1.0
  suggestedConfirmationPrompt: string; // "이걸 목표로 기억해둘까요?"
  createdAtMs: number;
}

interface Goal {
  goalId: string;
  userId: string;
  title: string;
  goalType: GoalType;
  status: GoalStatus;                  // IDEA, PLANNING, ACTIVE, PAUSED, COMPLETED, ARCHIVED
  confidence: number;                  // 0.0 ~ 1.0 (추정 신뢰도)
  commitmentLevel: number;             // 0.0 ~ 1.0 (사용자의 실천/몰입도)
  milestones: GoalMilestone[];
  targetDateStr: string;               // "YYYY-MM-DD"
  createdAtMs: number;
  updatedAtMs: number;
}

interface GoalMilestone {
  milestoneId: string;
  title: string;
  isCompleted: boolean;
  targetDateStr: string;
  completedAtMs?: number;
}

interface DDayInfo {
  title: string;
  targetDateStr: string;
  daysRemaining: number;
  ddayTag: string;                     // "D-Day", "D-7", "D-30"
}
```
