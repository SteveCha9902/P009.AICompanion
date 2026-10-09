# Companion Autonomy Architecture (Sprint 58)

본 문서는 Sprint 58에서 구축된 **Companion Autonomy Engine**의 전체 시스템 아키텍처, 4대 자율 모드(`PASSIVE`, `RESPONSIVE`, `COMPANION`, `PROACTIVE`), 발화 예산 관리자(Autonomy Budget Manager), 방해 감지기(Interruption Detector), 기억 억제 엔진(Memory Suppression Engine) 및 설명 가능한 이원화 결정 로그(Dual Decision Trace) 파이프라인을 정의합니다.

---

## 🏛️ 1. 전체 아키텍처 구조

```text
[Multi-Modal Input: Awareness + Affective State + Memories + Goals + Relationship]
                                       │
                                       ▼
                         [InterruptionDetector]
          (Detects User Busy, Phone Call, Gaze Away, Fatigue -> Suppress)
                                       │
                                       ▼
                       [AutonomyBudgetManager]
            (Throttles Speech: Max 1 / 15m, Max 3 / 1h, Unresponsive Throttle)
                                       │
                                       ▼
                      [MemorySuppressionEngine]
             (Prevents Repeating Topics Within 7 Days / Disinterest)
                                       │
                                       ▼
                            [AutonomyEngine]
                                       │
                                       ▼
                            [ActionSelector]
   ├─ PASSIVE_OBSERVE / LIGHT_ATTENTION / WAIT / SILENT_COMPANION
   ├─ GENTLE_RECALL / SOFT_ENCOURAGEMENT / RESPOND / ASK
   └─ Dual Trace: internal_trace (metrics) + user_facing_reason (warm explanation)
                                       │
                                       ▼
                            [AutonomyPolicy]
             (Enforces 'User Comfort First' Immutable Hard Rules)
                                       │
                                       ▼
                     [Companion Cognitive OS (CCOS)]
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
             [ContextBuilder]               [Avatar Realtime Driver]
            (Gentle Directive)              (Calm Breath, Soft Warm Smile)
```

---

## 🛡️ 2. 핵심 원칙: "Autonomy ≠ Control" & "User Comfort First"

1. **Autonomy ≠ Control (자율성은 통제가 아니다)**:
   - 자율성은 사용자를 통제하거나 대화를 강제하는 것이 아니라, "언제 말하고, 언제 침묵하며, 언제 기억을 꺼낼지"를 지혜롭게 선택하는 능력입니다.
2. **User Comfort First (사용자 편안함 최우선)**:
   - `User Comfort > Curiosity > Memory Utilization > Proactive Agency`.
   - 피로/업무 집중 상태 시 침묵의 동반자(`SILENT_COMPANION` 또는 `WAIT`)로 자동 전환.
