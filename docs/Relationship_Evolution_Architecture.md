# Relationship Evolution Architecture (Sprint 55)

본 문서는 Sprint 55에서 구축된 **Relationship Evolution Layer**의 전체 시스템 아키텍처, 5대 관계 축, 비대칭 성장 곡선 및 일일 성장 제한 정책(Daily Rate Limiter)을 정의합니다.

---

## 🏛️ 1. 전체 아키텍처 구조

```text
[Multimodal Signals: History + Memories + Shared Reality + Affective State]
                                │
                                ▼
                 [InteractionQualityAnalyzer]
         (Depth, Utterance Length, Emotional Resonance, Grounding)
                                │
                                ▼
                       [TrustCalculator]
         (Decoupled from Familiarity: Memory Bonus, Consistency)
                                │
                                ▼
                  [RelationshipGrowthEngine]
         ├─ Daily Growth Rate Limiter (Max +0.05 / day)
         ├─ Asymmetric Growth (Slow Rise, Fast Drop)
         └─ Milestone Tracking (e.g. 10 Turns, Life Events)
                                │
                                ▼
                   [RelationshipRepairEngine]
         (Empathetic Recovery Loop upon Relational Strain)
                                │
                                ▼
                      [RelationshipState]
         (Stages: NEW -> FAMILIAR -> TRUSTED -> DEEP)
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
 [ContextBuilder Prompt]              [Avatar & Voice Attunement]
(Stage-Appropriate Tone)             (Gaze Stability, Smile Depth)
```

---

## ⚖️ 2. 핵심 원칙 및 비대칭 성장 곡선

1. **"성격(Personality)은 불변, 관계(Relationship)는 천천히 성장"**:
   - 캐릭터의 내재적 정체성(`CharacterDNA`)은 고정 닻으로 작동하며, 관계 수치만 상호작용을 통해 점진적으로 발전.
2. **Daily Growth Rate Limiter (`DAILY_MAX_GROWTH = 0.05`)**:
   - 하루에 수백 번 대화하더라도 당일 최대 성장치를 0.05로 제한하여 하룻밤 사이의 인위적인 친밀감 인플레이션 원천 방지.
3. **Asymmetric Curve (Slow Build, Fast Drop)**:
   - 신뢰는 수주일에 걸쳐 천천히 쌓이지만, 거친 대화나 실망 시 빠르게 하락하며, 이후 점진적인 회복(Repair Loop)을 거침.
4. **Trust vs Familiarity Strict Decoupling**:
   - 자주 만났다고 해서 무조건 신뢰하는 것이 아니며, 일관된 지지와 약속 이행이 결합될 때만 `Trust`가 상승.
