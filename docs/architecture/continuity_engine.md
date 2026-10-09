# Continuity Engine & Long-Term Relationship Architecture

---

## 1. 개요 및 계층 구조

```text
                 User Interaction
                        │
                        ▼
             CompanionOrchestrator
                        │
                        ▼
                 ContextBuilder
                        │
       ┌────────────────┼────────────────┐
       │                │                │
       ▼                ▼                ▼
  Conversation        Memory        Relationship
     History          Engine           Engine
       │                │                │
       └────────────────┼────────────────┘
                        ▼
              Continuity Engine
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
     Memory Recall   Relationship   Temporal
                      Context       Context
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                 ContextBuilder
                        │
                        ▼
                   Real LLM
                        │
                        ▼
               Response Analysis
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Memory        Emotion     Relationship
       Update         Update        Update
          │             │             │
          └─────────────┼─────────────┘
                        ▼
               Continuity Snapshot
```

---

## 2. 5대 Memory 분류 체계
1. **FACT**: 사용자의 변하지 않는 직업, 환경 등 객관적 사실.
2. **PREFERENCE**: 기술적 설명 선호, 사진 촬영 취미 등 개인 선호.
3. **EVENT**: 프로젝트 시작, 가족 여행 등 특정 시점의 중요 사건.
4. **GOAL**: AICompanion 완성 등 달성하고자 하는 목표.
5. **RELATIONSHIP_EVENT**: 애칭 명명, 장기 부재 후 복귀, 신뢰 형성 마일스톤.

---

## 3. Temporal Context & Reunion Context
- **Temporal Context**: 마지막 대화 경과일(`last_interaction_at`), 누적 관계 일수, 대화 빈도를 자연어 문맥으로 변환하여 LLM에 주입.
- **Reunion Context**: 장기 부재 후 재접속 시 "다시 왔네! 전에 이야기하던 카메라 프로젝트는 어떻게 됐어?" 형태로 자연스럽게 과거 사건을 회상하며 대화 개시.
