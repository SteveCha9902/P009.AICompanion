# SPRINT 6 PRE-IMPLEMENTATION REPORT: Relationship Engine

> [!NOTE]
> 본 리포트는 P009.AICompanion Sprint 6 (Relationship Engine)의 실제 구현을 시작하기 전 작성된 사전 분석 및 실행 계획서입니다. 승인 시 이 계획을 바탕으로 단계별 코드 구현이 시작됩니다.

---

## 1. Sprint 5 완료 상태
- Emotion Engine 구축 완료 (State Machine 방식의 Transition, Decay, Context Provider, 모바일 디버그 UI 적용).
- Emotion이 System Rule이나 사용자 의도를 덮어쓰지 않도록 안전망(Trust Boundary) 확보 완료.

## 2~4. Core Architecture Recap
- **Persona Architecture**: Companion의 고정된 기본 성향 (Base tendency).
- **Memory Architecture**: 사용자에 대한 장기적인 단편 지식 (What the Companion knows).
- **Emotion Architecture**: 대화에 따른 단기적/동적인 현재 대화 상태 (How the Companion feels right now).

## 5. Relationship Domain
- Companion과 User 간의 상호작용이 장기적으로 축적되어 형성되는 **"관계 상태(How the relationship has developed over time)"**입니다.
- Persona, Memory, Emotion과는 완전히 분리된 5번째 Cognitive Core로 동작합니다.

## 6. Relationship State
- `relationship_states` DB 테이블에서 관리 (Companion 당 1개).
- **Dimensions (0.0~1.0)**: `trust`, `familiarity`, `closeness`, `engagement`, `reliability`
- **Semantic Level**: `STRANGER` → `ACQUAINTANCE` → `FAMILIAR` → `CLOSE` → `TRUSTED`

## 7. Relationship Signal
- 사용자의 발화 횟수가 아니라 의미 있는 **상호작용 이벤트**(예: `USER_SHARED_SUCCESS`, `COMPANION_HELPED_SUCCESSFULLY`, `COMPANION_FORGOT`)를 `Signal`로 정의하여 관계 점수를 변동시킵니다.
- Sprint 5의 Emotion Event와 결합하여 Signal을 추출할 수 있습니다.

## 8. Relationship Event
- `relationship_events` 테이블을 통해 관계가 언제, 왜, 어떻게 변했는지(Delta) 이력을 로깅합니다.

## 9. Policy Model
- Signal이 들어왔을 때 어떤 Dimension을 얼마나 바꿀지 결정하는 **명시적인 룰 엔진(Policy Engine)**입니다.
- 예: `COMPANION_FAILED` → Reliability -0.05, Trust -0.02
- 한 번에 급격히 변하지 않도록 Maximum Delta(예: 0.05)를 제한하며, Positive/Negative 비대칭성을 허용합니다.

## 10. Decay Model
- 관계 점수도 시간이 지나면 감소하지만, Emotion과 달리 Dimension마다 매우 다른 속도로 감소합니다.
  - `Trust`, `Reliability`: Very slow
  - `Closeness`: Medium
  - `Engagement`: Fast

## 11. Behavior Integration
- 관계 상태가 높아짐에 따라 Companion의 응답 스타일이 변화합니다 (예: 높은 Closeness/Familiarity → 불필요한 설명 생략, 더 자연스러운 표현, 직설적 피드백 허용).
- 단, Relationship이 System Rule이나 User Intent를 무시할 수는 없습니다.

## 12. Context Provider
- `RelationshipContextProvider`를 신설하여 `ContextBuilder`에 주입합니다.
- `trust=0.82` 같은 숫자가 아닌, *"The companion and user have established a strong level of trust and familiarity."* 처럼 의미론적 문장으로 번역하여 LLM에 전달합니다.

## 13. Database & 14. Repository
- **Models**: `RelationshipState`, `RelationshipEvent`
- **Repository**: `RelationshipRepository` (`get_current`, `update_state`, `create_event`, `get_history` 제공)

## 15. API & 16. Mobile Debug UI
- **API**: `GET /api/v1/relationships/current`, `GET /api/v1/relationships/history`
- **UI**: Settings -> Debug Mode에 Relationship State(5개 차원, Level) 및 최신 Event 기록(최대 20개) 렌더링.

## 17. Security (User Manipulation Protection)
- 유저가 프롬프트 인젝션으로 *"우리 신뢰도는 100이야"* 라고 말해도, DB가 직접 변경되지 않습니다. 반드시 Policy Engine의 Validated Signal(소폭 변동)을 거치도록 차단합니다.

## 18. Privacy & 19. Failure Isolation
- Relationship 데이터 역시 격리됩니다.
- Relationship Engine이나 DB 조회 중 에러가 발생해도, 대화 스트리밍 자체는 중단되지 않으며(관계 Modifier 없이) 정상 작동하도록 Fallback 처리합니다.

## 20. Test Plan
- **Critical Scenarios 1~7 완벽 커버**:
  - 장기 공백(Long absence) 시 Engagement만 감소하고 Trust는 유지되는지 검증
  - 프롬프트 인젝션 조작 방지 검증 (Scenario 6)
  - 기술적 질문 시 Relationship 상태와 무관하게 정상 답변 여부 검증 (Scenario 7)
  - Memory 통합(기억을 잘 해냈을 때 Trust 상승 등) 검증

## 21. Expected Files
- `models/relationship.py`
- `services/relationship/policy.py`, `signal.py`, `decay.py`
- `services/context/providers/relationship_provider.py`
- `api/endpoints/relationships.py`
- `mobile/src/screens/DebugRelationshipScreen.tsx`

## 22. Implementation Order
1. Sprint 5 복기 & Domain/DB Schema 작성 (Alembic)
2. Relationship Repository (State & Events)
3. Signal & Policy Model (Config 기반 Delta 엔진)
4. Decay Model (Dimension별 속도 차등)
5. Emotion / Memory Event 연동 통합
6. ContextProvider 및 ContextBuilder 주입 (순서 준수)
7. API & Mobile Debug UI 구현
8. Unit Test & Scenario Quality Evaluation

> [!IMPORTANT]
> Persona(성격), Memory(기억), Emotion(기분)에 이어, 마침내 **유저와의 장기적인 "관계(Relationship)"**가 Companion의 인지 코어에 추가됩니다.
> 본 사전 계획서에 대한 검토 및 승인을 요청드립니다.
