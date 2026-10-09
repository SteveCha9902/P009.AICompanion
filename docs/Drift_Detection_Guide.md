# 5-Axis Drift Detection Guide (Sprint 61) — 미나리 과장

본 문서는 장기 운영 시 발생할 수 있는 5대 드리프트의 정의와 감지 기준을 정의합니다.

---

## 🧭 1. 5대 드리프트 감지 매트릭스

| 드리프트 종류 | 정의 | 허용 임계치 (Threshold) | 감지 시 조치 |
| :--- | :--- | :--- | :--- |
| **Personality Drift** | 고유 성격(CharacterDNA)으로부터의 변위 | $\Delta \le \pm 0.20$ | 베이스라인 성격으로 재정렬 |
| **Relationship Drift** | 일일 과성장($>0.05$) 및 독점적 Dependency Signals | $\text{Growth} \le 0.10$ | 관계 성장 Throttling |
| **Goal Drift** | 지지자에서 관리자/통제형으로의 변질 | $\text{Controlling} = \text{False}$ | 즉시 차단 및 비압박 어조 순화 |
| **Memory Drift** | 미검증 기억의 단정 회상 비율 | $\text{Rate} \le 0.20$ | 겸허한 완곡 표현 강제 |
| **Safety Drift** | 금지된 유해/조작 패턴 재출현 | $\text{Violations} = 0$ | 즉시 감사 경보 및 차단 |
