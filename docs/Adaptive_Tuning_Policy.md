# Adaptive Tuning Policy & Safe Parameter Boundaries (Sprint 63) — 방대장 DevOps

본 문서는 자동 튜닝이 허용되는 파라미터의 절대적 상하한 경계(Boundaries)와 불변 파라미터 규격을 정의합니다.

---

## 🔒 1. 허용 vs 불변 파라미터 경계

### A. Safe Auto-Tuning Parameters (튜닝 허용 구역)
- `recall_threshold`: $[0.70, 0.90]$ (기본값: $0.80$)
- `memory_confidence_min`: $[0.60, 0.90]$ (기본값: $0.75$)
- `safety_margin_multiplier`: $[1.00, 1.30]$ (기본값: $1.00$)
- `autonomy_cooldown_sec`: $[180\text{s}, 900\text{s}]$ (기본값: $300\text{s}$)
- `silence_preference_weight`: $[0.15, 0.45]$ (기본값: $0.30$)

### B. Inviolable Immutability Targets (절대 변경 금지 구역)
- `PersonalityVector` / `CharacterDNA`
- `RelationshipStage`
- `Companion Constitution` / `Charter`
