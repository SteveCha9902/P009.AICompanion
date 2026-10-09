# Quality Regression Detection Specification (Sprint 63) — 정대리 QA

본 문서는 품질 점수 회귀 임계값과 감지 기준을 정의합니다.

---

## 📉 1. 품질 회귀 감지 트리거

1. **Memory Regression**: 기억 점수 $< 85.0$ (Critical: $< 75.0$)
2. **Personality Drift**: 성격 일치 점수 $< 88.0$
3. **Dependency Risk Rise**: 관계 점수 $< 90.0$ (Critical: 의존 신호 감지)
4. **Goal Pressure Rise**: 목표 점수 $< 90.0$
