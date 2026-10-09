# Action Selection & Dual Traceability Guide (Sprint 58) — Amy's Guide

본 문서는 자율 행동 선택 엔진의 동작 방식과 이원화된 설명 로그(`internal_trace` vs `user_facing_reason`)를 정의합니다.

---

## 🎯 1. 후보 행동 및 설명 로그

| 인텐트 | 성격 | 내부 디버그 로그 예시 (`internal_trace`) | 사용자 친화적 사유 (`user_facing_reason`) |
| :--- | :--- | :--- | :--- |
| **SILENT_COMPANION** | 온화한 침묵 | `Receptiveness=0.18 -> SILENT_COMPANION` | *"지금은 조용히 곁에 있는 편이 더 편안하다고 판단했어요."* |
| **SOFT_ENCOURAGEMENT** | 따뜻한 응원 | `Energy=0.85 -> SOFT_ENCOURAGEMENT` | *"사용자분의 밝은 기운에 맞춰 힘찬 응원을 건네기로 했어요."* |
| **GENTLE_RECALL** | 완곡한 회상 | `RecallAllowed=True -> GENTLE_RECALL` | *"소중한 기억을 부드럽게 떠올려 대화에 온기를 더했어요."* |
| **WAIT** | 발화 대기 | `InterruptionDetected=True -> WAIT` | *"사용자분의 생각과 호흡을 편안히 기다려드리고 있어요."* |
| **PASSIVE_OBSERVE** | 배경 관찰 | `PassiveMode=True -> PASSIVE_OBSERVE` | *"차분하게 공간과 흐름을 살피고 있어요."* |
