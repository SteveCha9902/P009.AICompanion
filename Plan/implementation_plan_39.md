# Sprint 39: Avatar Behavioral Synchronization & Embodied Character Engine Implementation Plan

## 🎯 Sprint Mission
> **"아바타를 단순한 동영상 클립 스위칭 재생기가 아닌, 인격과 인지 상태(Cognitive State)의 실시간 신체적 표현(Embodied Character)으로 전환한다. 6단계 상태 머신(IDLE ➔ LISTENING ➔ THINKING ➔ PRE_EXPRESSION ➔ SPEAKING ➔ SETTLING), 연속 감정 벡터(Continuous Emotion Vector), 다층 애니메이션 레이어(Base Idle, Emotion, Attention, Gesture, Lip Sync), 부드러운 상태 전이 엔진(Transition Smoothing Engine)을 구축한다."**

---

## 🏛️ AntiGravity 8인 에이전트 역할 분담
- **🧭 세종이 PM**: Sprint 39 범위 관리, 6-State 라이프사이클 및 4-Clock 동기화 요구사항 총괄, Quality Gates (V1~V7) 관리
- **🐟 코다리 Architect**: AvatarBehaviorEngine, Continuous Emotion Vector, 6-State Machine, Layered Animation Architecture, AvatarStateTransitionEngine, Renderer-Agnostic Adapter 설계
- **🐍 미나리 과장 (Backend)**: `services/character/avatar/` 백엔드 도메인/엔진(Behavior Controller, Transition Planner, Continuous Emotion, Micro-expression Scheduler) 및 SSE 파이프라인 확장
- **🌸 진달래 주임 (Vision/Avatar/Mobile)**: 모바일 `AvatarView`를 단일 동영상 재생기에서 **다층 레이어드 렌더러(Continuous Base Idle + Smooth Emotion Interpolation + Gesture Overlay + Micro-expression Blending)**로 고도화
- **🏃 정대리 (QA)**: Gate V1~V7 (상태 전이 연속성, 발화 전 프리 익스프레션 타이밍, 레이어드 블렌딩, 연속 감정 벡터, 제스처 독립성, 렌더러 교체 가능성, 60fps 렌더링 안정성) 테스트 자동화
- **✍️ Amy (Growth)**: 감정 강도별 미세 표정 시나리오(약한 미소 ➔ 따뜻한 미소 ➔ 밝은 웃음) 및 사용자 몰입도 UX 검증
- **📚 묵사관 (Memory Keeper)**: `PROJECT.md`, `CHANGELOG.md`, `Decision_Log.md`, `walkthrough.md` 업데이트
- **🔐 방대장 (DevOps/Security)**: 모바일 60fps 렌더링 부하 최소화 및 메모리 누수 방지

---

## 🔄 Cognitive & Embodied Architecture (Sprint 39)

```
                 Character Cognitive Engine
    (Personality + MBTI + Emotion + Relationship 8D + Growth + Agency)
                              │
                              ▼
                      CharacterDecision
                              │
                              ▼
                ⭐ AvatarBehaviorController
                              │
       ┌──────────────────────┼──────────────────────┐
       ▼                      ▼                      ▼
 Emotion Layer          Motion Layer           Speech Layer
(Valence, Arousal,   (Idle, Head Tilt,       (Viseme, Lip Sync,
 Warmth, Intensity)   Listening Nod, Gesture) Pre-expression Timing)
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              ▼
                 AvatarStateTransitionEngine
              (300~800ms Smooth Interpolation
               & Micro-Expression Blending)
                              │
                              ▼
                    Avatar Behavior DTO
                   (SSE / Real-time Sync)
                              │
                              ▼
                  Embodied Avatar Renderer
       (Continuous Base Idle + Gesture Asset Blend + Lip Sync)
```

---

## 🎭 6-Stage Avatar Behavioral State Machine

```
              ┌───────────┐
              │   IDLE    │ ◄────────────────────────┐
              └─────┬─────┘                          │
                    │ User speaks                    │
                    ▼                                │
              ┌───────────┐                          │
              │ LISTENING │                          │
              └─────┬─────┘                          │
                    │ Speech End (0ms)               │
                    ▼                                │
              ┌───────────┐                          │
              │ THINKING  │ (100~500ms, Subtle gaze) │
              └─────┬─────┘                          │
                    │ CharacterDecision (500~800ms)  │
                    ▼                                │
            ┌────────────────┐                       │
            │ PRE_EXPRESSION │ (800~1000ms, Eye/Smile)
            └───────┬────────┘                       │
                    │ TTS Starts (1000ms~)           │
                    ▼                                │
              ┌───────────┐                          │
              │ SPEAKING  │ (Lip sync & Gesture)     │
              └─────┬─────┘                          │
                    │ TTS Ends                       │
                    ▼                                │
              ┌───────────┐                          │
              │ SETTLING  │ (200~400ms)              │
              └─────┬─────┘                          │
                    └────────────────────────────────┘
```

---

## 🧩 Proposed Changes

### 1. Backend Character Avatar Domain (`backend/app/services/character/avatar/`)
#### [NEW] `backend/app/services/character/avatar/domain.py`
- `AvatarBehavioralState`: `IDLE`, `LISTENING`, `THINKING`, `PRE_EXPRESSION`, `SPEAKING`, `SETTLING`
- `ContinuousEmotionVector`:
  - `valence: float` (-1.0 ~ +1.0)
  - `arousal: float` (0.0 ~ 1.0)
  - `warmth: float` (0.0 ~ 1.0)
  - `confidence: float` (0.0 ~ 1.0)
  - `intensity: float` (0.0 ~ 1.0)
- `AvatarAttentionState`: `eye_contact_ratio: float`, `head_tilt_angle: float`, `listening_nod_intensity: float`, `eyebrow_raised: bool`
- `AvatarGestureType`: `NONE`, `SUBTLE_NOD`, `EMPHATIC_NOD`, `THINKING_TILT`, `WARM_LEAN`, `CHEERFUL_WAVE`, `GENTLE_SHRUG`
- `AvatarBehaviorPlan`:
  - `state: AvatarBehavioralState`, `emotion: ContinuousEmotionVector`, `attention: AvatarAttentionState`, `gesture: AvatarGestureType`, `pre_expression_duration_ms: int`, `transition_curve: str`

#### [NEW] `backend/app/services/character/avatar/behavior_controller.py`
- `AvatarBehaviorController`:
  - `CharacterDecision` ➔ `AvatarBehaviorPlan` 매핑 (<5ms)
  - Discrete enum에서 Continuous Vector로의 감정 세분화 (예: `happy` ➔ 약한 미소 / 온화한 미소 / 활짝 웃음)

#### [NEW] `backend/app/services/character/avatar/transition_engine.py`
- `AvatarStateTransitionEngine`:
  - `current_plan` ➔ `target_plan` 사이의 부드러운 상태 보간(300~800ms Ease-In-Out) 계산
  - 눈 깜빡임(Blink 2~7s 랜덤 주기) 및 호흡(Breathing 4~6s 주기) 베이스라인 유지

#### [NEW] `backend/app/services/character/avatar/__init__.py`

---

### 2. Orchestrator & SSE Pipeline Extension
#### [MODIFY] `backend/app/services/companion/orchestrator.py`
- SSE `AVATAR_STATE` 이벤트 페이로드에 6-State 및 `AvatarBehaviorPlan` (Continuous Emotion, Attention, Transition Parameters) 포함

---

### 3. Mobile Layered Avatar System (`mobile/src/components/avatar/`)
#### [MODIFY] `mobile/src/components/avatar/AvatarView.tsx`
- 단순 단일 비디오 스위칭에서 **다층 레이어드 렌더러(Continuous Idle Base + Animated Facial Layer + Gesture Clip Overlay + Smooth Fade Transition)**로 고도화
- 텍스트/TTS 시작 전 `PRE_EXPRESSION` 상태를 수신하여 선제적으로 표정/눈빛 전환

---

## 🧪 Verification Plan

### 1. Automated Tests (정대리 QA)
- `tests/test_avatar_behavior_sync_engine.py`:
  - **Gate V1 [State Transition Continuity]**: `IDLE` ➔ `LISTENING` ➔ `THINKING` ➔ `PRE_EXPRESSION` ➔ `SPEAKING` ➔ `SETTLING` 상태 전이 무결성
  - **Gate V2 [Pre-Expression Timing]**: 발화 시작 전 200~300ms 선제 표정 반영 플랜 생성 검증
  - **Gate V3 [Continuous Emotion Vector]**: Discrete enum을 넘어선 `valence`, `warmth`, `intensity` 연속 보간 검증
  - **Gate V4 [Gesture Decoupling]**: Emotion과 Gesture가 독립적으로 조합되는지 검증 (e.g. `warm` + `slow_nod`)
  - **Gate V5 [Attention & Listening Reactions]**: 사용자 발화 중 미세 끄덕임 및 시선 집중 플랜 검증
  - **Gate V6 [Blink & Breathing Baseline]**: 무반응 상태에서도 호흡(4~6s)과 눈 깜빡임(2~7s) 파라미터 유지 검증
  - **Gate V7 [Renderer Swappability]**: Behavior Plan DTO가 2D/Video/Live2D 렌더러와 독립적인지 검증

### 2. Full Regression & Mobile Build Test
- 전체 55개 기존 백엔드 테스트 및 모바일 TypeScript 0 Errors 확인.

---

## 🏁 Quality Gates (DoD)
- **Gate V1 [State Transition Continuity]**: PASS
- **Gate V2 [Pre-Expression Timing]**: PASS
- **Gate V3 [Continuous Emotion Vector]**: PASS
- **Gate V4 [Gesture Decoupling]**: PASS
- **Gate V5 [Attention & Listening]**: PASS
- **Gate V6 [Blink & Breathing Baseline]**: PASS
- **Gate V7 [Renderer Swappability]**: PASS
- **Backend Test Suite**: 전체 60+ 테스트 100% PASS
- **Mobile TypeScript**: 0 Errors
