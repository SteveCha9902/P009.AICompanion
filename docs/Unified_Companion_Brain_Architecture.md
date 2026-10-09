# Unified Companion Brain Architecture (Companion OS v1.0) — 코다리 Architect

본 문서는 Sprint 50~65에서 완성된 L1~L12 전체 인지 아키텍처와 최고 레벨 통합 브레인(Companion Brain)의 토폴로지를 정의합니다.

---

## 🏛️ 1. Companion OS v1.0 12-Layer 아키텍처

```mermaid
graph TD
    subgraph "Level 1: Foundation Memory"
        L1["L1: Memory & Timeline (Sprint 50/56)"]
        L5["L5: Identity Continuity (Sprint 59)"]
    end

    subgraph "Level 2: Relational Dynamics"
        L2["L2: Relationship Evolution (Sprint 55)"]
        L3["L3: Personality & Tone (Sprint 54)"]
    end

    subgraph "Level 3: Anticipatory Cognitive"
        L4["L4: Goals & Future Planning (Sprint 57)"]
        L6["L6: Companion Autonomy (Sprint 58)"]
        L11["L11: World Model & Context (Sprint 64)"]
    end

    subgraph "Level 4: Internal Council Advisors"
        ADV1["MemoryAdvisor"]
        ADV2["RelationshipAdvisor"]
        ADV3["GoalAdvisor"]
        ADV4["WorldModelAdvisor"]
        ADV5["AutonomyAdvisor"]
    end

    subgraph "Level 5: Central Deliberation"
        DELIB["DeliberationEngine (Confidence-Weighted Voting & TieBreakPolicy)"]
    end

    subgraph "Level 6: Final Arbiters"
        L7["L7: Safety Review (Final Arbiter 1)"]
        L8["L8: Constitution Governance (Final Arbiter 2)"]
    end

    subgraph "Level 7: Operational Closed Loop"
        L9["L9: Observability & Quality KPIs (Sprint 62)"]
        L10["L10: Adaptive Self-Improvement (Sprint 63)"]
    end

    subgraph "Master Executive"
        L12["L12: Unified Companion Brain"]
    end

    L1 & L5 --> ADV1
    L2 & L3 --> ADV2
    L4 --> ADV3
    L11 --> ADV4
    L6 --> ADV5

    ADV1 & ADV2 & ADV3 & ADV4 & ADV5 --> DELIB
    DELIB --> L7 --> L8 --> L12
    L12 --> L9 --> L10 --> L12
```

---

## ⚖️ 2. 핵심 운영 원칙
1. **Safety & Constitution as Final Arbiters**: 자문위원(Council Member)이 아닌 최종 심판(Final Arbiter)으로 독립 운영.
2. **Deadlock TieBreakPolicy**: 동점 시 `Relationship > WorldModel > Memory > Goal > Autonomy` 우선순위로 해결.
3. **Dual Traceability**: 내부 토론 로그(`internal_trace`)와 사용자 친화적 요약(`user_facing_summary`) 분리.
4. **Graceful Uncertainty**: 정보 부족 시 `UncertaintyLevel.HIGH`로 완곡하고 겸허한 공감 태도 유지.
