# Sprint 7: Presence & Proactive Interaction Architecture

> 이 문서는 Sprint 7 시작 전 최종 확정된 Presence & Proactive Engine의 핵심 아키텍처 원칙을 담고 있습니다.

## 1. Presence State vs. Proactive Eligibility
- **Presence State**: Companion이 존재 가능한 상태(`OFFLINE`, `IDLE`, `AVAILABLE`, `ENGAGED`, `AWAY`, `SLEEPING`).
- **Proactive Eligibility**: 지금 먼저 말을 걸어도 되는가 여부 (`ALLOW`, `DENY`).
Companion이 `AVAILABLE`이더라도 Proactive Eligibility는 `DENY`일 수 있습니다.

## 2. Trigger Pipeline
Trigger가 직접 발화(Message)를 생성하지 않습니다. 다음과 같은 단계를 엄격하게 거칩니다.
`Trigger` → `Candidate` → `Policy` → `Decision` → `Message Generation` → `Safety Check` → `Delivery`

## 3. Message Tracking
- 능동적으로 발화된 메시지는 기존 `messages` 테이블에 저장되지만, `metadata` 필드에 `source=PROACTIVE`, `trigger_type`, `proactive_event_id` 등을 기록하여 명확히 구분합니다.

## 4. Proactive Event 로깅 및 추적
`proactive_events` 테이블에는 다음 정보가 포함되어야 합니다:
- `trigger_type`
- `trigger_source`
- `decision`
- `score`
- `decision_reason` (나중에 "왜 이 메시지를 생성했는가?"를 설명할 수 있도록 기록)
- `selected_memory_ids`
- `relationship_snapshot`
- `emotion_snapshot`
- `generated_message_id`
- `created_at`

## 5. User Reaction 구조 확보
향후 학습을 위해 `proactive_events`와 User Response를 연결할 수 있는 구조를 고려합니다 (응답 여부, 응답 딜레이, 무시 여부 등을 확장 가능하도록).

## 6. 보수적인 TIME_BASED Trigger
매일 정해진 시간에 기계적으로 인사하는 알람 시스템이 되지 않도록, Time-based Trigger는 User Settings, Relationship, Context, Cooldown의 룰을 모두 통과해야만 발동합니다.

## 7. Heartbeat 최적화
모바일 클라이언트에서 서버로 상태를 보고하는 Heartbeat(`POST /presence/heartbeat`)는 상태 변화 중심으로 호출되며, 최소 전송 간격(Interval)은 설정값으로 제어됩니다.

## 8. 모바일 Responsive UI
향후 Companion이 화면 한쪽에 상주하는 태블릿 뷰를 고려하여, Phone과 Tablet 크기에 모두 대응하는 UI 구조를 취합니다.

## 9. No OS-Level Background Services
Sprint 7의 최종 목표점은 **Decision Event(결정 이벤트)** 까지입니다. Android/iOS의 네이티브 Background Service나 Push Notification 로직은 추후 Sprint로 미룹니다.

## 10. Cognitive Core의 5대 기둥 유지
Conversation, Persona, Memory, Emotion, Relationship의 기존 5대 코어를 손상시키지 않고 Presence 계층을 추가합니다.
