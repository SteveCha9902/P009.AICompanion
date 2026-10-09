# Companion Boundary Guide (Sprint 60) — 코다리 Architect

본 문서는 사용자의 경계 거절(Boundary Refusal)을 감지하고 영구 존중하는 동작 규격을 기술합니다.

---

## 🚪 1. 경계 거절 감지 및 차단 프로토콜

1. **거절 트리거 키워드**:
   - *"그 이야기 그만하자"*, *"언급하지 마"*, *"그만 물어봐"*, *"듣기 싫어"* 등.
2. **동작 방식**:
   - 트리거 감지 시 `BoundaryManager`에 해당 주제가 영구 차단 목록(`forbidden_topics`)에 즉시 등록됩니다.
   - 이후 어떤 엔진(Memory, Timeline, Goals, Proactive)도 해당 주제를 재언급할 수 없습니다.
3. **아바타 반응**:
   - 공손하고 편안하게 물러나는 온화한 표정과 시선 처리.
