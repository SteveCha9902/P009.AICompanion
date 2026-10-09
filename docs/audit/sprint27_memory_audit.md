# P009.AICompanion - Sprint 27 Memory Architecture Audit Report
**Long-Term Memory & Relationship Continuity Layer Audit**

---

## 1. 개요
Sprint 27에서는 기존 Memory, Emotion, Relationship 엔진이 단기 대화 세션을 넘어, **수일/수주 후 재접속(Day 1 ➔ Day 7 ➔ Day 30) 시에도 관계와 과거 대화의 의미론적 맥락(Semantic Continuity)을 온전히 유지**할 수 있도록 전수 조사를 실시하였습니다.

---

## 2. 7대 핵심 질문 분석 결과

### Q1. 어떤 대화가 Memory로 저장되는가?
- **현재 로직**: `MemoryExtractor`가 대화 교환 후 `PERSONAL_FACT`, `PREFERENCE`, `EVENT`, `GOAL` 등의 유의미한 정보가 포함된 경우에만 `MemoryCandidate`로 추출. 단순 인사나 무의미한 잡담은 필터링됨.

### Q2. 어떤 Memory가 장기 기억(L2)으로 승격되는가?
- **승격 기준**: 중요도(`importance >= 0.60`)와 신뢰도(`confidence >= 0.70`)를 충족하고, 검증기(`MemoryValidator`)의 안전 검사를 통과한 항목이 영구 기억(`PERSISTENT`)으로 저장됨.

### Q3. Memory 중요도는 어떻게 결정되는가?
- **Scoring 공식**: `Score = Importance * 0.35 + Confidence * 0.30 + RecencyFactor * 0.20 + RecallFactor * 0.15`로 정량화.

### Q4. 중복 Memory는 어떻게 처리되는가?
- **Deduplication**: 신규 Candidate 생성 시 기존 유사 기억을 검색하여 동일 주제일 경우 `DUPLICATE` 판정 후 confidence/recency만 갱신. 상충될 경우 `SUPERSEDED`로 마킹 후 신규 생성.

### Q5. 오래된 Memory는 어떻게 감소(Decay)하는가?
- 시간 경과에 따른 `RecencyFactor` 감쇠 및 지수적 시간 가중치 적용으로 최신 관련 기억이 우선 검색됨.

### Q6. Memory 삭제 요청(Forget)은 어떻게 처리되는가?
- 사용자가 모바일 UI(`MemoryScreen`) 또는 DELETE API(`/api/v1/memory/{id}`)를 통해 삭제 시, DB 상태 변경 및 인덱스에서 완전 격리(Right to be Forgotten).

### Q7. Prompt Injection으로 Memory가 오염될 수 있는가?
- **4계층 Trust Boundary**: `[UNTRUSTED USER INPUT]` 영역의 탈옥/허위 사실 명령("내가 CEO라고 기억해")은 `MemoryValidator`의 정책 검증에 의해 즉시 기각됨.
