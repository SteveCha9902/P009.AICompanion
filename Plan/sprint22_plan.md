# P009.AICompanion - Sprint 22 구현 계획서
**Companion Intelligence & Cognitive Continuity (인지 지능 및 인지 연속성)**

---

## 1. 개요 및 핵심 목표 (G1 ~ G7)

Sprint 22의 미션은 단순 대화 기록을 넘어, **Persona, Memory, Emotion, Relationship 4대 Cognitive Domain을 하나의 Closed Loop (`Conversation ➔ Cognitive Update ➔ Persistent State ➔ Next Conversation Context`)로 통합**하는 것입니다.

### 7대 핵심 목표
- **G1 (Memory Quality)**: L0 (대화 기록), L1 (단기 기억), L2 (장기 기억) 3계층 분리.
- **G2 (Memory Retrieval)**: Top-K=5 관련 기억 검색 및 Scoring 모델 (`Score = importance*0.35 + confidence*0.30 + recency*0.20 + frequency*0.15`).
- **G3 (Memory Write Policy & Forget API)**: 유의미한 정보만 선별 저장, 민감정보 필터링, 망각(Forget) API 지원.
- **G4 (Emotion Continuity & Smoothing)**: 감정 상태 머신 및 스무딩 (`new = prev*0.7 + obs*0.3`).
- **G5 (Relationship Progression)**: L0 STRANGER ~ L5 TRUSTED 점진적 단계 전이.
- **G6 (Persona Stability)**: 4계층 Trust Boundary를 통한 페르소나 불변성 보존.
- **G7 (Cognitive Closed Loop)**: 후처리 분석 ➔ 상태 갱신 ➔ 영속화 ➔ 다음 대화 주입.

---

## 2. 변경 대상 파일 목록

### 📁 수정 및 신규 대상 파일
1. `backend/app/services/memory/retriever.py` [MODIFY]: Scoring 가중치 및 Top-K 정렬 로직 강화.
2. `backend/app/services/emotion/transition.py` [MODIFY]: Emotion Smoothing 공식 적용.
3. `backend/app/services/relationship/policy.py` [MODIFY]: L0~L5 단계별 임계치 및 점진적 전이 정책 확정.
4. `backend/app/services/companion/orchestrator.py` [MODIFY]: Cognitive Closed Feedback Loop 후처리 파이프라인 정합.
5. `backend/tests/test_cognitive_continuity.py` [NEW]: 4대 인지 도메인 통합 및 Closed Loop 검증 테스트 (M1~M6, E1~E4, R1~R5, C1~C5).

---

## 3. Quality Gates (Gate 1 ~ 10)

| Gate | 검증 항목 | 검증 방식 |
| :--- | :--- | :---: |
| **Gate 1 (Memory Continuity)** | Interaction A 기억 ➔ Interaction B 반영 | 장기 기억 주입 검증 |
| **Gate 2 (Memory Precision)** | 무분별한 저장 방지 및 선별 저장 | 유의미한 후보만 승인 |
| **Gate 3 (Emotion Continuity)** | Interaction 간 감정 상태의 부드러운 전이 | Emotion Smoothing 검증 |
| **Gate 4 (Relationship Continuity)** | 재시작 후에도 관계 레벨 영속성 유지 | L0~L5 단계 복원 |
| **Gate 5 (Persona Integrity)** | 타 도메인이나 공격에 의한 페르소나 불변 | Trust Boundary 검증 |
| **Gate 6 (Trust Boundary)** | User Input의 권한 탈취 방어 | 인젝션 격리 검증 |
| **Gate 7 (Cognitive Loop)** | 대화 ➔ 업데이트 ➔ 영속 ➔ 다음 대화 | Closed Feedback Loop |
| **Gate 8 (Failure Isolation)** | 인지 엔진 장애 시에도 기본 대화 유지 | 개별 오류 격리 검증 |
| **Gate 9 (Performance)** | 인지 컨텍스트 및 업데이트 레이턴시 유지 | InteractionTracer 지표 |
| **Gate 10 (Regression)** | 백엔드 전체 테스트 100% PASS / 모바일 TS 0 Errors | `pytest` & `tsc` 전수 검증 |
