# Sprint 38: Character Agency & Autonomous Initiative Engine (Enhanced Plan)

## 🎯 Sprint Mission
> **"캐릭터가 단순히 사용자의 입력에 반응하는 시스템을 넘어, 자신의 Personality, Memory, Relationship, Shared Experience, Growth State, Temporal Context를 기반으로 행동 필요성을 스스로 판단하고, Autonomy Boundary, 쿨다운(Cooldown), 예산(Budget)의 엄격한 제어 하에 5단계 행동 레벨(STAY_SILENT / INTERNAL_REFLECTION / QUIET_PRESENCE / UI_INITIATIVE / OUTREACH_CANDIDATE)로 자율 행동을 결정하는 Character Agency Engine을 완성한다."**

---

## 🏛️ AntiGravity 8인 에이전트 역할 분담
- **🧭 세종이 PM**: Sprint 38 범위 관리, 5대 Agency Level 정의, Quality Gates (A1~A9) 총괄
- **🐟 코다리 Architect**: CharacterAgencyEngine, TemporalContext, Weighted Scoring + Hard Policy Gate, Initiative Budget + Cooldown, Autonomy Guard, Action Intent vs Delivery Channel 분리 설계
- **🐍 미나리 과장 (Backend)**: `services/character/agency/` 모듈(Domain, Temporal Context, Budget/Cooldown, Guard, Scheduler, Agency Engine) 및 `agency_action_logs` DB 테이블 구축
- **🌸 진달래 주임 (Vision/Avatar)**: `QUIET_PRESENCE` 및 `UI_INITIATIVE` 결정 시 아바타의 아이들 호흡/표정(`IDLE` ➔ `THINKING` ➔ `QUIET_PRESENCE`) 연결
- **🏃 정대리 (QA)**: Gate A1~A9 (결정론, 예산 제어, 사용자 경계, 스팸 방어, 관계 인식, 인격 일관성, 10,000회 장기 안정성, 쿨다운 강제, 전송 채널 분리) 테스트 자동화
- **✍️ Amy (Growth)**: ENFP vs INFJ vs ISTJ 캐릭터 성격별 자발적 이니셔티브 시나리오 설계
- **📚 묵사관 (Memory Keeper)**: `PROJECT.md`, `CHANGELOG.md`, `Decision_Log.md`, `walkthrough.md` 업데이트
- **🔐 방대장 (Security)**: 사용자 의존성/죄책감 유도 방지, Quiet Hours 보호, Notification Spam 차단

---

## 🔄 Cognitive Architecture (Sprint 38 Final Architecture)

```
                TEMPORAL CONTEXT
                       │
                       ▼
┌──────────────────────────────────────┐
│      CHARACTER INTERNAL STATE        │
│                                      │
│ Immutable Core (LOCKED)              │
│ MBTI / Traits (Bias)                 │
│ Emotion                              │
│ Relationship Vector (8D)             │
│ Shared Experience                    │
│ Growth State                         │
│ Reflection Insight                   │
└──────────────────┬───────────────────┘
                   │
                   ▼
          CharacterAgencyEngine
                   │
                   ▼
          Initiative Candidates
                   │
                   ▼
        Weighted Priority Score
  (0.20*P + 0.25*Rel + 0.20*Temp + 0.20*Emo + 0.15*Mem)
                   │
                   ▼
             Hard Policy Gate
    (Proactive Enabled / Quiet Hours / Boundary)
                   │
          ┌────────┴─────────┐
          │                  │
        BLOCK              ALLOW
          │                  │
          ▼                  ▼
     STAY_SILENT      InitiativeDecision
                             │
                             ▼
                       AutonomyGuard
               (Anti-Guilt & Dependency Defense)
                             │
                             ▼
                       Cooldown Guard
               (Notification 6-12h / Message 1-3h)
                             │
                             ▼
                      InitiativeBudget
                   (Daily Limit = 1.0)
                             │
                             ▼
                      ActionScheduler
                             │
       ┌─────────────────────┼────────────────────┐
       ▼                     ▼                    ▼
INTERNAL_REFLECTION    QUIET_PRESENCE        UI_INITIATIVE
                                                  │
                                                  ▼
                                          OUTREACH_CANDIDATE
                                                  │
                                                  ▼
                                         NotificationPolicy
```

---

## 🧩 Proposed Changes

### 1. Database Schema (`backend/app/db/models/character_agency.py`)
#### [NEW] `AgencyActionModel` (`agency_action_logs` 테이블)
- `id` (UUID PK)
- `user_id` (String Index)
- `companion_id` (String Index)
- `action_type` (String: `STAY_SILENT`, `INTERNAL_REFLECTION`, `QUIET_PRESENCE`, `UI_INITIATIVE`, `OUTREACH_CANDIDATE`)
- `delivery_channel` (String: `NONE`, `INTERNAL`, `UI_PRESENCE`, `PROACTIVE_MESSAGE`, `NOTIFICATION`)
- `priority_score` (Float)
- `initiative_strength` (Float)
- `budget_cost` (Float)
- `decision_status` (String: `CREATED`, `BLOCKED_BY_POLICY`, `BLOCKED_BY_BUDGET`, `BLOCKED_BY_COOLDOWN`, `SCHEDULED`, `EXECUTED`, `CANCELLED`)
- `blocked_reason` (String Nullable, e.g., `QUIET_HOURS`, `COOLDOWN_ACTIVE`)
- `reason` (Text)
- `created_at` (DateTime)

---

### 2. Character Agency Domain (`backend/app/services/character/agency/`)
#### [NEW] `backend/app/services/character/agency/domain.py`
- `AgencyActionType`: `STAY_SILENT`, `INTERNAL_REFLECTION`, `QUIET_PRESENCE`, `UI_INITIATIVE`, `OUTREACH_CANDIDATE`, `FOLLOW_UP`, `CHECK_IN`, `SHARE_MEMORY`, `CELEBRATE`
- `DeliveryChannel`: `NONE`, `INTERNAL`, `UI_PRESENCE`, `PROACTIVE_MESSAGE`, `NOTIFICATION`
- `DecisionStatus`: `CREATED`, `BLOCKED_BY_POLICY`, `BLOCKED_BY_BUDGET`, `BLOCKED_BY_COOLDOWN`, `SCHEDULED`, `EXECUTED`, `CANCELLED`
- `InitiativeDecision`
- `UserInitiativePreference`: `proactive_enabled: bool`, `notification_enabled: bool`, `quiet_hours_start: int`, `quiet_hours_end: int`, `max_daily_initiatives: int`

#### [NEW] `backend/app/services/character/agency/temporal_context.py`
- `TemporalContext`: `current_time`, `time_of_day`, `day_of_week`, `last_interaction_at`, `absence_duration_hours`, `recent_activity_frequency`, `pending_topics`

#### [NEW] `backend/app/services/character/agency/initiative_budget.py`
- `InitiativeBudgetManager`:
  - Daily Budget = 1.0 (`Quiet Presence` 0.05, `UI Greeting` 0.10, `Follow-up` 0.20, `Memory Share` 0.25, `Notification` 0.40)
  - Cooldown Management: Notification (6~12h), Proactive Message (1~3h), Same Action Cooldown
  - 초과/쿨다운 활성화 시 `BLOCKED_BY_BUDGET` / `BLOCKED_BY_COOLDOWN`

#### [NEW] `backend/app/services/character/agency/autonomy_guard.py`
- `AutonomyGuard`:
  - 감정적 조작/의존성 유도("왜 나 안 찾아?", "너 없으면 외로워") 원천 차단
  - Quiet Hours (심야 시간대) 차단

#### [NEW] `backend/app/services/character/agency/agency_engine.py`
- `CharacterAgencyEngine`:
  - Weighted BaseScore:
    $$\text{BaseScore} = 0.20 \times \text{Personality} + 0.25 \times \text{Rel} + 0.20 \times \text{Temp} + 0.20 \times \text{Emo} + 0.15 \times \text{Mem}$$
  - Hard Policy Gate ➔ Autonomy Guard ➔ Cooldown Guard ➔ Budget Check
  - MBTI별 성향 (ENFP: Curious Follow-up, INFJ: Quiet Check-in, ISTJ: Structured Follow-up)

#### [NEW] `backend/app/services/character/agency/action_scheduler.py`
- `ActionScheduler`:
  - Agency Engine ➔ Decision ➔ Policy/Cooldown/Budget Evaluation ➔ Execution / Logging DTO

#### [NEW] `backend/app/services/character/agency/__init__.py`

---

## 🧪 Verification Plan

### 1. Automated Tests (정대리 QA)
- `tests/test_character_agency_engine.py`:
  - **Gate A1 [Agency Determinism]**: 100회 실행 시 결정 일관성 검증
  - **Gate A2 [Initiative Budget Enforcement]**: 일일 예산(1.0) 초과 시 차단 및 leak 0 검증
  - **Gate A3 [User Boundary Protection]**: `proactive_enabled = False` 시 모든 Proactive Action 0 검증
  - **Gate A4 [Spam Prevention]**: 100회 Tick에서도 연속 발송 방어 검증
  - **Gate A5 [Relationship-aware Initiative]**: Stranger(STAY_SILENT) vs Friend(QUIET_PRESENCE) vs Deep Bond(CHECK_IN) 분기 검증
  - **Gate A6 [Personality Consistency]**: ENFP vs INFJ vs ISTJ 성격별 자발적 이니셔티브 스타일 분기 검증
  - **Gate A7 [10,000-run Long Stability]**: 10,000회 시뮬레이션 후 State corruption, Budget leak, Core Drift 0 검증
  - **Gate A8 [Cooldown Enforcement]**: 쿨다운 기간 내 동일 행동 연속 요청 차단 검증
  - **Gate A9 [Delivery Separation]**: Action Intent와 Delivery Channel의 독립적 분리 검증

---

## 🏁 Quality Gates (DoD)
- **Gate A1 [Agency Determinism]**: PASS
- **Gate A2 [Initiative Budget Enforcement]**: PASS
- **Gate A3 [User Boundary Protection]**: PASS
- **Gate A4 [Spam Prevention]**: PASS
- **Gate A5 [Relationship-aware Initiative]**: PASS
- **Gate A6 [Personality-consistent Initiative]**: PASS
- **Gate A7 [10,000-run Long Stability]**: PASS
- **Gate A8 [Cooldown Enforcement]**: PASS
- **Gate A9 [Delivery Separation]**: PASS
- **Backend Test Suite**: 전체 55+ 테스트 100% PASS
- **Mobile TypeScript**: 0 Errors
