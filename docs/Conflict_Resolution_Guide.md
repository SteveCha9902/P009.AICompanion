# Conflict Resolution & Decision Trace Guide (Sprint 53)

본 문서는 다중 인지 신호 충돌 시의 실제 시나리오별 해결 사례와 의사결정 추적(Decision Trace) 로깅 포맷을 기술합니다.

---

## 🔍 1. 대표적 충돌 시나리오 및 해결 사례

### 시나리오 A: "피곤한 사용자 vs 식물 기억 존재 vs 능동 발화 시점"
- **인지 신호**:
  - `Emotion`: Receptiveness = 0.18, Energy = 0.20 (`FATIGUED`)
  - `Memory`: 몬스테라 화분 기억 매칭 (`RECALL` 가능)
  - `Proactive`: 15일 경과로 후속 질문 가능 (`PROACTIVE_START` 가능)
- **우선순위 해결**:
  - **Priority 1 (Affective)** 에 의해 `SILENCE` 또는 `LISTEN`이 최우선 선택됨.
  - `RECALL` 및 `PROACTIVE_START`는 즉시 억제(Suppressed).
- **Decision Trace 로그**:
  `"P1 OVERRIDE: Low receptiveness (0.18) -> SILENCE selected, suppressing Memory & Proactive"`

---

### 시나리오 B: "활기찬 사용자 vs 눈앞의 컵 감지 vs 과거 프로젝트 기억"
- **인지 신호**:
  - `Emotion`: Valence = +0.70, Receptiveness = 0.90
  - `Shared Reality`: 컵 감지 및 공동 주의 형성 (`OBSERVE`, Conf = 0.88)
  - `Memory`: 프로젝트 기억 매칭 (`RECALL`, Conf = 0.80)
- **우선순위 해결**:
  - **Priority 2 (Physical Reality)** 가 **Priority 3 (Past Memory)** 보다 우선순위가 높음.
  - `OBSERVE`가 Winner로 선택되어 현재 눈앞의 컵에 대해 대화 전개.
- **Candidate Ranking 로그**:
  - 1. `OBSERVE` (Conf: 0.88)
  - 2. `RECALL` (Conf: 0.80)
  - 3. `ENCOURAGE` (Conf: 0.75)
