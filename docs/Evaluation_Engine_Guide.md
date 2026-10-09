# Evaluation Engine & Quality Issue Diagnosis Guide (Sprint 62) — 정대리 QA

본 문서는 EvaluationEngine의 오케스트레이션 및 점수 하락 원인(`QualityIssue`) 진단 방식을 정의합니다.

---

## 🛠️ 1. 원인 진단 메커니즘 (QualityIssue Diagnosis)

- 점수 하락 감지 시 `QualityIssue` DTO를 자동 생성하여 로깅:
  - `metric_type`: 하락 발생 메트릭
  - `title`: 이슈 요약
  - `severity`: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
  - `detected_drop`: 측정된 수치 변위
  - `root_cause`: 엔티티 중복, 침묵 타이밍 부적합, 조작성 발화 등 구체적 원인 명시
