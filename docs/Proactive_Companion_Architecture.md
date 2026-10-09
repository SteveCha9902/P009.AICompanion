# Proactive Companion Architecture (Sprint 51)

본 문서는 Sprint 51에서 구축된 **Proactive Companion Engine**의 전체 시스템 아키텍처, 사용자 수용도(Receptiveness), 빈도 버짓 및 자율 발화 데이터 흐름을 정의합니다.

---

## 🏛️ 1. 전체 아키텍처 구조

```text
[Relationship Memory Store] + [Visual Awareness Context] + [Idle Timer / User Input]
                                    │
                                    ▼
                        [UserReceptivenessEngine]
             (Checks Fatigue, Terse Messages, Idle Duration)
                                    │
                                    ▼
                        [ProactiveBudgetManager]
             (NORMAL: 30m, QUIET: 6h, OFF: Disabled)
                                    │
                                    ▼
                            [InterestEngine]
             (Dynamic Follow-up Windows: Pet 5d, Object 15d, Project 10d)
                                    │
                                    ▼
                     [ProactiveDiversityEngine]
             (Cycles 4 Styles: Greeting, Reminiscence, Encouragement, Observation)
                                    │
                                    ▼
                   [ProactiveOpportunityDetector]
             (Proactive Priority Queue: Top 1 Best Candidate Selection)
                                    │
                                    ▼
                 [ConversationStarterGenerator] (Amy Persona Guide)
                                    │
                                    ▼
                 [ProactiveContextProvider] ➔ [ContextBuilder] ➔ [LLM]
```

---

## ⏱️ 2. Dynamic Follow-up Window by MemoryType

| Memory Type | Follow-up Window | 주요 발화 목적 |
| :--- | :--- | :--- |
| **PET** | **3~7일 (평균 5일)** | 반려견/반려묘의 건강, 산책, 일상 안부 |
| **PROJECT** | **7~14일 (평균 10일)** | 진행 중인 작업, 마감, 개발 프로젝트 진척 및 격려 |
| **OBJECT (식물)** | **10~30일 (평균 15일)** | 반려식물 성장, 화분 돌봄, 새 물건 사용 후기 |
| **HOBBY** | **14일 (2주)** | 새로운 취미, 운동, 악기 연습의 즐거움 |
| **GOAL** | **14일 (2주)** | 개인적 결심, 다이어트, 자격증 목표 격려 |
| **PLACE** | **20일 (3주)** | 여행지, 새 동네, 자주 가는 카페 회상 |

---

## 🎯 3. 핵심 설계 원칙

1. **User Receptiveness First (수용도 존중)**:
   - 사용자가 피곤(`FATIGUED`)하거나, 몰입 중(`FOCUSED`), 또는 짧은 단답("ㅇㅇ", "응")을 남겼을 때는 `Receptiveness < 0.60`으로 판별하여 **절대 먼저 말을 걸지 않고 조용히 곁을 지킴**.
2. **Proactive Priority Queue (상위 1개 선별)**:
   - 식물, 프로젝트, 반려동물 등 여러 주제가 동시에 무르익었을 때, `PriorityScore` 최고 1개만 선별하여 과잉 발화 방지.
3. **Proactive Diversity Engine (4대 스타일 순환)**:
   - 안부형(`GREETING`), 회상형(`REMINISCENCE`), 격려형(`ENCOURAGEMENT`), 관찰형(`OBSERVATION`)을 순환하여 항상 다채롭고 생동감 있는 대화 전개.
4. **3-Tier Proactive Mode (User Opt-Out & Quiet Mode)**:
   - `NORMAL`(30분 쿨다운), `QUIET`(6시간 쿨다운), `OFF`(능동 발화 완전 차단) 지원.
5. **Non-Intrusive Care (취조형/감시자 어조 100% 금지)**:
   - "왜 안 해?", "오늘 운동 안 했네?" 같은 압박성 표현을 원천 배제하고 따뜻한 공감형 안부 전달.
