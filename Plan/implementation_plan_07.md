# SPRINT 7 PRE-IMPLEMENTATION REPORT: Presence & Proactive Interaction Engine

> [!NOTE]
> 본 계획서는 P009.AICompanion Sprint 7 (Presence & Proactive Interaction Engine)의 실제 구현을 위한 사전 분석 및 실행 계획입니다. 승인 시 아래의 순서에 따라 코딩이 진행됩니다.

---

## 1. Core Architecture
Sprint 7은 P009의 기존 Cognitive Core (Conversation, Persona, Memory, Emotion, Relationship)를 수정하지 않고, 그 위에 **Presence(존재 상태)**와 **Proactive(능동적 발화)**라는 새로운 추상화 계층을 추가합니다. 

`Trigger → Candidate → Policy → Decision → Message Generation → Safety Check → Delivery` 의 엄격한 파이프라인을 구축하여, LLM이 임의로 시도때도 없이 말을 거는 것(Spam)을 사전에 차단합니다.

## 2. Presence Domain
Companion의 현재 상태를 나타내는 `Presence State`를 정의합니다.
- `OFFLINE`, `IDLE`, `AVAILABLE`, `ENGAGED`, `AWAY`, `SLEEPING`
- **중요**: 앱의 생명주기(App State)와 Companion의 Presence State를 분리하여, 앱이 백그라운드에 있어도 Companion은 `AVAILABLE` 상태일 수 있도록 설계합니다.

## 3. Proactive Domain & Triggers
사용자가 먼저 말을 걸지 않아도 Companion이 대화를 시작할 수 있는 Trigger를 정의합니다. 초기 구현 대상은 다음과 같습니다:
- `RETURNED_USER` (사용자가 다시 앱으로 돌아왔을 때)
- `LONG_ABSENCE` (장기간 미사용 시)
- `CONVERSATION_CONTINUATION` (이전 대화의 맥락이 이어질 때)
- `TIME_BASED` (시간 기반, 아침 인사 등)

## 4. Policy & Decision Engine (Anti-Spam)
Proactive Score를 계산하여 `ALLOW` 또는 `DON'T_SPEAK`를 결정합니다.
- **Anti-Spam 장치**: Cooldown (예: 최소 120분 대기), Daily Limit (예: 일 3회), Quiet Hours (예: 23:00~07:00 금지), Duplicate Prevention, Recent Proactive History 체크.
- **Relationship 영향**: `STRANGER`인 경우 Proactive 억제, `CLOSE`인 경우 허용 빈도 상승.

## 5. User Control
사용자가 Proactive 설정을 완벽하게 통제할 수 있도록 모바일 앱 Settings에 UI를 추가합니다.
- Enable/Disable, Daily Limit, Cooldown, Quiet Hours
- `Never disturb` 기능 제공.

## 6. Database & Repository
3개의 신규 테이블(모델)을 추가합니다:
1. `presence_states`: Companion 당 1개의 현재 상태와 시간 기록.
2. `proactive_events`: Proactive 결정 내역, Score, Trigger, Reason 등의 히스토리 로깅.
3. `proactive_settings`: User 별 Proactive 활성화 여부 및 Anti-Spam 설정값.

## 7. Context Builder & LLM Generation
- `PresenceContextProvider`를 추가하여 현재 상황(Application Context)을 LLM에 주입합니다.
- Policy Engine이 `ALLOW` 결정을 내렸을 때만 LLM이 Proactive Message를 생성하도록 합니다.

## 8. Mobile Integration (No OS Background Yet)
- 앱 내에 `PresenceSettingsScreen.tsx`를 구현합니다.
- API (`GET /presence`, `POST /presence/heartbeat`, `GET/PUT /proactive/settings`)를 연동합니다.
- **Background Execution 주의**: Android/iOS 네이티브 백그라운드 서비스나 Push Notification은 Sprint 7에서 구현하지 않고, Engine의 추상화 계층(Decision Event -> Mobile Notification)까지만 마련해 둡니다.

## 9. Failure Isolation
- Presence/Proactive 엔진에 오류가 발생하더라도 챗봇 본연의 Conversation 기능은 절대 중단되지 않고 Graceful Fallback 되도록 예외처리를 보장합니다.

## 10. Test Plan
다음 14개의 Critical Scenarios를 단위/통합 테스트를 통해 검증합니다:
1. OFFLINE → AVAILABLE 전환
2. AVAILABLE → ENGAGED 전환
3. ENGAGED → IDLE 전환
4. IDLE → AVAILABLE 전환
5. Proactive ON 작동 확인
6. Proactive OFF 차단 확인
7. Quiet Hours 차단 확인
8. Cooldown 차단 확인
9. Daily Limit 차단 확인
10. Relationship에 따른 Decision 검증
11. Memory 기반 Trigger 활용 검증
12. Emotion 기반 Tone 영향 검증
13. 중복 Proactive 메시지 방지
14. Failure Isolation (기본 대화 유지)

## 11. Implementation Order (실행 순서)
1. **Domain & DB Schema**: `PresenceState`, `ProactiveEvent`, `ProactiveSettings` 모델 작성 및 Alembic 마이그레이션.
2. **Repository**: DB 접근 계층 구현.
3. **Presence Engine**: 상태 전이(State Machine) 로직 구현.
4. **Proactive Engines**: Trigger, Policy, Decision, Cooldown 시스템 구축.
5. **API**: REST Endpoint 개발.
6. **Context Provider**: `PresenceContextProvider` 통합 및 ContextBuilder 업데이트.
7. **Mobile UI**: React Native 서비스 및 셋팅 화면 구현.
8. **Testing**: 14가지 Scenario 단위/통합 테스트 작성.

> [!IMPORTANT]
> Sprint 7을 통해 P009는 "질문에 대답하는 챗봇"을 넘어, 사용자에게 **존재감을 드러내는 주도적인 동반자(Proactive Companion)**로 진화하게 됩니다.
> 본 사전 계획서에 대한 검토 및 승인을 요청드립니다.
