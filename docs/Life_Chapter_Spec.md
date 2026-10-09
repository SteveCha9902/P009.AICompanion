# Life Chapter Specification (Sprint 59)

본 문서는 개별 이벤트를 묶어 거시적 인생 서사를 구성하는 `LifeChapter` 규격을 기술합니다.

---

## 📦 1. LifeChapter DTO

```typescript
interface LifeChapter {
  chapterId: string;
  userId: string;
  title: string;                 // e.g. "아들 군 복무", "홈 가드닝", "창업 프로젝트"
  category: string;              // e.g. "FAMILY", "HOME", "CAREER"
  startDateStr: string;          // "YYYY-MM"
  endDateStr: string;            // "YYYY-MM" or empty if ongoing
  eventIds: string[];            // Linked LifeEvent IDs
  summaryNarrative: string;      // Continuous chapter narrative
  isOngoing: boolean;
  createdAtMs: number;
  updatedAtMs: number;
}
```

---

## 📖 2. Life Chapter Macro Flow Example

```mermaid
graph TD
    subgraph "Chapter: 아들 군 복무 (2026-06 ~ 진행 중)"
        E1["2026-06: 훈련소 입소"] --> E2["2026-08: 자대 배치"]
        E2 --> E3["2026-11: 첫 외박"]
        E3 --> E4["2027-12: 만기 전역 (예정)"]
    end
```
