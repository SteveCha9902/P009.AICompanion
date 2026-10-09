# P009.AICompanion - Sprint 12: Continuity & Always-On Presence Engine (Final)

## 1. Core Architecture Principles

> [!IMPORTANT]
> **"앱이 살아있는 것"이 아니라 "Companion의 상태가 살아있는 것"**
> Always-On의 핵심은 앱의 백그라운드 무한 실행이 아니라, **Continuity Engine**을 통한 Companion 상태의 영속성과 매끄러운 재개(Resume)입니다.
> 
> **Privacy Rules (Trust Boundary)**
> - `BACKGROUND`: Camera ❌, Microphone ❌, Vision ❌, Voice ❌ / Presence ✅, Relationship ✅, Memory ✅, Proactive ✅
> - `FOREGROUND (Interactive)`: Camera ✅, Microphone ✅(권한), Vision ✅, Voice ✅, Avatar ✅, Conversation ✅

## 2. 3-Tier State Separation

단순한 Mobile Session을 넘어 상태를 세분화하여 관리합니다:
1. **Device State**: `FOREGROUND`, `BACKGROUND`, `SUSPENDED`, `TERMINATED`
2. **Companion Presence**: `OFFLINE`, `IDLE`, `AVAILABLE`, `ENGAGED`, `AWAY`, `SLEEPING`
3. **Interaction Session**: `ACTIVE`, `PAUSED`, `RESUMABLE`, `ENDED`

## 3. Remote Push & Notification Pipeline

Notification은 Proactive Engine의 최종 결과물로서 Remote Push 구조(APNs/FCM)를 기본 아키텍처로 삼습니다. (개발/테스트용 Local Fallback 제공)

**NotificationEvent Schema 확장**
알림 탭 시 정확한 문맥으로 복귀할 수 있도록 연결 고리를 추가합니다.
- `id`, `companion_id`, `proactive_event_id`, `conversation_id`, `notification_type`, `status`, `created_at`, `delivered_at`, `opened_at`, `dismissed_at`

**Pending Interaction State**
- Companion이 백그라운드에서 특정 이벤트를 준비했다면, `Pending State`로 저장하여 사용자가 나중에 앱을 열었을 때 선제적으로 발화할 수 있도록 지원합니다.

## 4. Restore Pipeline (Sprint 12 핵심 산출물)

앱 재실행 시 무거운 전체 로드가 아닌, "지금 필요한 Context"만 선별하여 조립하는 **Continuity Engine**을 구축합니다.

`App Launch` ➔ `Identify User/Companion` ➔ `Load Persona & Relationship` ➔ `Retrieve Relevant Memory` ➔ `Load Last Conversation` ➔ `Load Pending Proactive Event` ➔ **`Build Continuity Context`** ➔ `Companion Resume`

## 5. Anti-Spam (Proactive Filters)

알림 피로도를 낮추기 위해 기존 Proactive Engine에 필터를 추가합니다.
- Cooldown (연속 발생 차단)
- Daily Limit (일일 제한)
- Quiet Hours (방해 금지 시간)
- Duplicate Prevention (중복 방지)

## 6. Verification Plan

### Critical Scenarios
- **Background Privacy**: 앱 Background 진입 시 카메라/마이크 완전 차단 확인.
- **Continuity Restore**: Notification 탭 시 `proactive_event_id`를 기반으로 이전 Context가 정상 복구되고 아바타/음성이 이어지는지 확인.
- **Pending State**: Notification을 무시하고 나중에 앱을 열어도, Pending된 할 말이 팝업/음성으로 전달되는지 확인.
- **Anti-Spam**: Quiet Hours 및 Cooldown 시 알림이 차단되는지 확인.
