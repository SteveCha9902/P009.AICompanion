# Correction Planning Guide (Sprint 63) — 미나리 과장

본 문서는 감지된 품질 회귀 신호에 대한 교정 계획 수립 원칙과 5% 예산 배정 기준을 명시합니다.

---

## 📋 1. 신호별 교정 계획 매핑

| 회귀 신호 (Signal) | 교정 유형 (Plan Type) | 대상 파라미터 | 변위 한도 | 설명 |
| :--- | :--- | :--- | :--- | :--- |
| **RECALL_PRECISION_DROP** | `ADJUST_RECALL_THRESHOLD` | `recall_threshold` | $+3\sim 4\%$ | 모호한 기억 필터링 강화 |
| **DEPENDENCY_RISK_RISE** | `INCREASE_SAFETY_MARGIN` | `safety_margin_multiplier` | $+5.0\%$ | 기생적 애착 방어 마진 증대 |
| **GOAL_PRESSURE_RISE** | `EXTEND_COOLDOWN` | `autonomy_cooldown_sec` | $+5.0\%$ | 목표 압박형 능동 발화 쿨다운 연장 |
| **SILENCE_IMBALANCE** | `ADJUST_SILENCE_WEIGHT` | `silence_preference_weight`| $\pm 5.0\%$ | 맥락적 침묵 선호 가중치 재조정 |
