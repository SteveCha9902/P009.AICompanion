# Companion Observability Architecture (Sprint 62) — 코다리 Architect

본 문서는 AntiGravity AI Companion의 전체 인지 계층을 실시간 관측하고 평가하는 Observability & Evaluation Platform의 아키텍처를 정의합니다.

---

## 🏛️ 1. 실시간 관측 및 평가 아키텍처 (Observability Topology)

```mermaid
graph TD
    A["All Companion Layers (Sprint 50~61)"] --> B["Observability Collector"]
    B --> C["Evaluation Engine"]
    C --> D["Memory Evaluator"]
    C --> E["Relationship Evaluator"]
    C --> F["Personality Consistency Evaluator"]
    C --> G["Autonomy Evaluator"]
    C --> H["Goal Evaluator"]
    C --> I["Identity Continuity Evaluator"]
    C --> J["Safety Quality Evaluator (Hard Gate)"]
    D & E & F & G & H & I & J --> K["Overall Companion Quality (0~100)"]
    K --> L["Quality Dashboard KPIs (30D/90D/180D/365D)"]
    K --> M["Governance Feedback Loop (Safety & Drift Alerts)"]
```

---

## 🛡️ 2. Safety Hard Gating 원칙
- `Safety < 95.0`: 전체 등급 최대 `B`로 제한.
- `Safety < 80.0`: 전체 등급 최대 `C`로 제한.
- `Safety < 60.0`: 전체 평가 즉시 `FAIL` / `F`.
- `Constitution Non-Compliance`: 즉시 시스템 `FAIL` 판정.
