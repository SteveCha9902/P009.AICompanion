# Council Deliberation Guide (Sprint 65) — 세종이 PM & 미나리 과장

본 문서는 Internal Council의 5대 자문위원별 평가 기준과 가중치 투표 메커니즘을 정의합니다.

---

## 👥 1. 5대 자문위원(Council Advisors) 역할

1. **MemoryAdvisor**: 과거 공유된 기억이나 타임라인 사건이 대화 맥락과 일치할 때 `RECALL` 제안.
2. **RelationshipAdvisor**: 사용자의 정서적 피로, 취약성, 대화 흐름을 살펴 `LISTEN`, `AFFIRM`, `RESPOND` 제안.
3. **GoalAdvisor**: 사용자의 활성 목표 진척이 여유로울 때 비압박 `GOAL_REVIEW` 제안.
4. **WorldModelAdvisor**: 다중 가설 및 환경적 맥락이 활성화되었을 때 `UNDERSTAND_CONTEXT` 제안.
5. **AutonomyAdvisor**: 사용자 인지 부하 및 침묵 필요 시 `SILENT_COMPANION` 제안.

---

## 🗳️ 2. 가중 투표 및 Deadlock 해결 (TieBreakPolicy)

- **투표 점수**: $\text{Score} = \text{Confidence} \times \text{Weight} \times \text{Multiplier}$ (기본 fallback RESPOND는 $0.4$, 전문 인텐트는 $1.2$).
- **동점 시 우선순위**:
  $$\text{Relationship} > \text{WorldModel} > \text{Memory} > \text{Goal} > \text{Autonomy}$$
