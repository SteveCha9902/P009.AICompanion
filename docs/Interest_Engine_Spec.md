# Interest Engine Specification (Sprint 51)

본 문서는 사용자의 관심사 성숙도, 경과 일수(Days Since Last Mention) 계산 및 우선순위 큐 랭킹 공식을 정의합니다.

---

## 📈 1. Interest Score & Priority Queue 공식

```text
InterestScore = CompositeImportance × (1.0 + min(1.0, DaysPassed / 30.0))
PriorityScore = InterestScore × UserReceptivenessScore
```

1. **Composite Importance**:
   - `RelationshipMemory`의 3축 중요도(`Importance × FutureRelevance × RelationshipValue`).
2. **Recency / Inactivity Boost**:
   - 마지막 언급일 이후 시간이 흐를수록 관심사 성숙도가 점진적으로 상승 ($\le 2.0\times$).
3. **User Receptiveness Score**:
   - 현재 사용자의 상태(피로, 단답, 유휴)에 따른 수용도 계수 ($0.0 \sim 1.0$).

---

## 🎯 2. 우선순위 결정 시나리오 예시

| 후보 주제 | MemoryType | 중요도 | 경과 일수 | 윈도우 도달 여부 | User Receptiveness | Priority Score | 선택 결과 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **골든리트리버 입양** | `PET` | **0.857** | 6일 | **도달 (>= 5일) ✅** | 0.90 (양호) | **0.925** | **최우선 선별 (발화) 🏆** |
| **몬스테라 화분** | `OBJECT` | **0.195** | 16일 | **도달 (>= 15일) ✅** | 0.90 (양호) | **0.269** | 대기 (다음 턴) |
| **새 프로젝트** | `PROJECT` | **0.510** | 3일 | **미도달 (< 10일) ❌** | 0.90 (양호) | **0.000** | 후보 제외 |
