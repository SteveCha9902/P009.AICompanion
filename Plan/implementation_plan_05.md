# SPRINT 5 PRE-IMPLEMENTATION REPORT: Emotion Engine

> [!NOTE]
> 본 리포트는 P009.AICompanion Sprint 5 (Emotion Engine)의 실제 구현을 시작하기 전 작성된 사전 분석 및 실행 계획서입니다. 승인 시 이 계획을 바탕으로 단계별 코드 구현이 시작됩니다.

---

## 1. Sprint 4 완료 상태
- Memory Engine 구축 완료 (Memory Lifecycle, Validator/Duplicate 처리, DB pgvector, Hybrid Retriever, Context Provider).
- 대화 생성 후 Background Task로 Memory가 추출/갱신되는 시스템 확립.

## 2. Current ContextBuilder
- 현재 주입 순서: `SYSTEM RULES > PERSONA > MEMORY > HISTORY > USER INPUT`

## 3. Persona Architecture
- Companion의 장기적이고 고정적인 **기본 성향**(Base Personality)을 담당 (예: Warm=80, Direct=40).

## 4. Memory Architecture
- 유의미한 장기 지식을 추출하고 검색 시점에 점수 기반(Recency, Importance 등)으로 가져와 Context에 주입.

## 5. Emotion Domain
- P009에서 Emotion은 인간의 감정이 아닌 **"Companion의 현재 대화 상태 (Conversational Emotional State)"**로 정의됩니다.
- 감정은 System Rule이나 Persona 자체를 바꾸지 않으며, 대화 톤(Tone)과 반응 방식(Behavior)에만 영향을 미칩니다.

## 6. Emotion State
- `emotion_states` 테이블에서 관리 (Companion 당 1개 레코드 유지).
- **Core Metrics**: `valence`(-1.0 ~ +1.0), `arousal`(0.0 ~ 1.0), `warmth`, `engagement`, `tension`
- **Metadata**: `primary_emotion`(Enum), `secondary_emotion`, `confidence`, `trigger`, `updated_at`, `last_trigger_at`.

## 7. Emotion Event (History)
- `emotion_events` 테이블에서 Transition(감정 변화) 이력을 로깅.
- 향후 Sprint (Relationship Engine)에서 두 사람 간의 교감 신호(`shared_experience`)로 활용할 기반 데이터입니다.

## 8. User Emotion
- 사용자의 감정 상태(예: SADNESS, ANGER)를 추정하되, 이를 Companion의 감정과 동일시하지 않으며 장기 메모리에 강제 기록(예: "사용자는 우울하다")하지 않습니다. Context 내부 참조용으로만 사용합니다.

## 9. Companion Emotion
- User Emotion에 대응하는 AI의 대화 상태 (예: User=SADNESS → Companion=EMPATHY, High Warmth).

## 10. Transition Model
- `Previous State + Current User Message + Context (Memory/Persona) = New State`. 
- 매번 초기화되지 않고 State Machine처럼 동작합니다 (예: CALM -> JOY -> FRUSTRATION).

## 11. Decay Model
- 시간 기반 감쇠 함수 적용: `intensity(t) = initial_intensity * exp(-λt)`. 
- 대화가 없으면 시간이 지남에 따라 점진적으로 중립(CALM) 또는 Persona 기본값으로 회귀합니다.

## 12. Emotion Extraction
- LLM에 구조화된(Structured) 출력을 요청하여 현재 발화에서 유의미한 감정 신호를 분석합니다. (User 감정과 Companion 변화 권고안 모두 포함)

## 13. Memory Integration
- 검색된 Memory 내용이 현재 대화와 결합될 때 감정의 Trigger가 될 수 있습니다 (예: 과거 말했던 목표 달성 소식 -> 강한 JOY/PRIDE 생성).

## 14. Persona Integration
- Emotion은 Persona 값을 덮어쓰지 않고 가중치나 수식어로 작용합니다. (예: 원래 Warm한 Persona가 JOY 상태가 되면 "더욱 밝고 에너제틱하게" 반응).

## 15. Context Provider
- `EmotionContextProvider`를 신설하여 `ContextBuilder`에 주입.
- 주입 시 숫자(Valence 0.8)가 아닌 의미론적 문장("The companion is currently empathetic, warm, and highly engaged.")으로 변환하여 프롬프트 인젝션 방어 및 LLM 이해도를 높입니다.

## 16. API 설계
- `GET /api/v1/emotions/current`: 현재 Companion State 반환.
- `GET /api/v1/emotions/history`: 디버깅용 Transition Event 반환.

## 17. Database
- `emotion_states` (1:1 Companion 관계)
- `emotion_events` (1:N Companion 관계, 이력 로깅)

## 18. Mobile Debug UI
- 일반 사용자 화면에는 숫자를 숨기지만, Settings -> Debug Mode에서 현재 `Primary Emotion`, `Valence`, `Warmth`, `Tension` 등의 실시간 수치를 모니터링할 수 있는 패널 추가.

## 19. Failure Isolation
- Emotion Extraction이나 DB 처리 에러 시, 대화를 차단하지 않고 Default State(`CALM`, `Neutral`)로 Fallback하여 정상 응답을 보장합니다.

## 20. Privacy & 21. Security
- Emotion 내역 역시 외부 노출 불가 (격리). Trust Boundary 계층에서 Emotion은 User Input이나 System Rule을 절대 덮어쓸 수 없는(Override 불가) 중간 우선순위(Application Context)로 취급됩니다.

## 22. Test Plan
- Extraction 분리 검증 (User vs Companion)
- 감쇠(Decay) 및 변화(Transition) 검증
- 장애 시(Failure) Fallback 작동 여부 검증 (E2E)

## 23. Expected Files
- `backend/app/db/models/emotion.py`
- `backend/app/services/emotion/extractor.py`, `transition.py`, `decay.py`
- `backend/app/services/context/providers/emotion_provider.py`
- `backend/app/api/endpoints/emotions.py`
- `mobile/src/screens/DebugEmotionScreen.tsx`

## 24. Implementation Order
1. Sprint 4 복기 & Domain/DB Schema 작성 (Alembic)
2. Emotion Repository (State & Events)
3. Emotion Extractor & Transition Logic (LLM 기반)
4. Decay Model 구현 (시간 가중치)
5. User/Companion Emotion 분리 로직 통합
6. ContextProvider 및 ContextBuilder 적용
7. API & Mobile Debug UI 구현
8. Unit Test & Scenario Quality Evaluation

> [!IMPORTANT]
> Emotion Engine은 **"감정을 흉내내는 것"이 아니라 "현재 대화의 톤과 매너를 동적으로 조절하는 상태 머신(State Machine)"**입니다. 본 사전 계획서에 대한 검토 및 승인을 요청드립니다.
