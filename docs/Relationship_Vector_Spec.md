# Relationship Vector Specification (Sprint 55)

본 문서는 사용자와 캐릭터 간의 관계 상태를 표현하는 `RelationshipVector`, `RelationshipMilestone` 및 `RelationshipState` 규격을 기술합니다.

---

## 📦 1. RelationshipVector DTO

```typescript
interface RelationshipVector {
  trust: number;               // 0.0 ~ 1.0 (신뢰도: 일관성, 정서적 안정감)
  familiarity: number;         // 0.0 ~ 1.0 (친숙도: 상호작용 턴 수, 세션 빈도)
  comfort: number;             // 0.0 ~ 1.0 (편안함: 침묵의 편안함, 자연스러움)
  sharedHistoryScore: number;  // 0.0 ~ 1.0 (공유 기억 및 사건 축적도)
  engagement: number;          // 0.0 ~ 1.0 (대화 몰입도)

  totalInteractionTurns: number;
  totalSharedMemoriesCount: number;
  consecutiveDaysMet: number;
  lastInteractionTimestampMs: number;
}
```

---

## 🌟 2. RelationshipMilestone DTO

```typescript
interface RelationshipMilestone {
  milestoneId: string;
  timestampMs: number;
  title: string;
  importance: number;          // 0.0 ~ 1.0
  memoryRefs: string[];        // 연관된 RelationshipMemory ID 목록
  eventDateStr: string;        // "YYYY-MM-DD"
}
```
