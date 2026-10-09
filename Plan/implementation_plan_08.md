# SPRINT 8 PRE-IMPLEMENTATION REPORT: Mobile Presence & Notification Bridge

> [!NOTE]
> 본 리포트는 P009.AICompanion Sprint 8 (Mobile Presence & Notification Bridge) 구현을 시작하기 위한 사전 분석 및 실행 계획서입니다. 승인 시 아래 계획에 따라 순차적으로 코딩이 진행됩니다.

---

## 1. Core Architecture: Mobile Bridge
Sprint 8은 Backend에 구축된 Cognitive Core(Brain)와 모바일 앱(Presentation/Interaction)을 이어주는 브릿지를 만듭니다. 핵심은 **AI가 백그라운드에서 직접 도는 것이 아니라**, 백엔드의 Proactive Decision이 Mobile Notification으로 전달되는 구조입니다.

## 2. Notification Domain (Message와 분리)
- `Message`: Companion이 실제로 발화한 대화 내용.
- `NotificationEvent`: 모바일 OS를 통해 메시지를 유저에게 전달하는 방식과 그 상태 (`CREATED`, `QUEUED`, `SENT`, `DELIVERED`, `OPENED`, `FAILED`, `DISMISSED`).
- `messages` 테이블과 별개로 `notification_events` 테이블을 통해 발송 이력과 사용자 반응(Opened, Dismissed)을 추적합니다.

## 3. Notification Provider & Policy 추상화
- `BaseNotificationProvider(ABC)` 인터페이스를 구축하여 향후 FCM, APNs, Expo 등으로 쉽게 교체할 수 있도록 합니다. 이번 Sprint에서는 Mock/Expo 구조를 준비합니다.
- `Notification Policy`: Proactive Policy를 통과했더라도, 앱이 현재 Foreground에 있다면 Push를 보내지 않고 In-App Delivery로 전환하며, 유저의 알림 설정(Never Disturb 등)을 검사합니다.

## 4. Deep Link 연동
- Notification 페이로드에 `deep_link: "p009://conversation/{conversation_id}"`를 포함합니다.
- 푸시 알림을 탭하면 즉시 `ConversationScreen`으로 진입하여 해당 메시지 컨텍스트를 이어나갈 수 있도록 모바일 라우팅을 설계합니다.

## 5. Mobile Presence UI & Emotion Mapping
- 모바일 화면 상단이나 별도 영역에 Companion의 존재를 시각화하는 `Presence Surface`를 구축합니다 (예: `● Available`, 표정 이모지).
- **Emotion → Presentation State**: Emotion State(CALM, JOY, EMPATHY 등)를 직접 UI에 하드코딩하는 것이 아니라, Presentation State로 추상화하여 시각적 표현(안정된 표정, 밝은 표정 등)으로 매핑합니다.

## 6. Phone / Tablet Adaptive Layout
- **Phone**: 컴패니언 표정/상태가 상단에 작게 표시되고 대화 위주의 뷰.
- **Tablet**: 좌측/우측 또는 분할 화면(Split View)을 활용하여 Companion Info(Presence, Emotion)와 대화(Conversation)가 동시에 넓게 보이는 반응형(Adaptive) 레이아웃을 구성합니다. 향후 카메라 연동 시 이 넓은 공간을 활용하게 됩니다.

## 7. Camera Interface Stub
- 카메라 권한 획득이나 실시간 비전 처리까지는 가지 않지만, Sprint 10을 대비하여 `CameraProvider` 인터페이스(Vision Analyzer → User State) 스터브를 미리 설계해 둡니다.

## 8. Database Schema & API
- **Models**: `NotificationEvent`, `NotificationSettings`
- **API**: 
  - `POST /api/v1/notifications/register` (Token 등록)
  - `GET/PUT /api/v1/notifications/settings`
  - `POST /api/v1/notifications/{id}/opened` (사용자 탭 추적)

## 9. Failure Isolation
- Push 발송 실패, Provider 장애, 토큰 만료 등의 이슈가 발생하더라도 `ConversationEngine`이나 `ProactiveEngine` 자체는 에러 없이 정상적으로 다음 동작을 이어가도록(Graceful Fallback) 완벽히 격리합니다.

## 10. Implementation Order (실행 순서)
1. **Repository 분석 및 Domain 모델링**: `NotificationEvent`, `NotificationSettings` 추가 (Alembic 마이그레이션).
2. **Notification Repository & Provider 인터페이스**: DB 연동 및 `BaseNotificationProvider` 작성.
3. **Notification Policy Engine**: Foreground/Background 상태 및 설정에 따른 Push vs In-App 분기 로직.
4. **Proactive → Notification Bridge 연결**: 능동 발화 시 Notification 파이프라인 호출.
5. **API & Context**: REST API 구축.
6. **Mobile - Deep Link & Notification Service**: 모바일 앱에서 Push Token 관리 및 라우팅.
7. **Mobile - Phone/Tablet Adaptive Layout**: 반응형 UI 및 Presence Surface 렌더링.
8. **Emotion → Presentation State 매핑**: Companion UI 상태 변화 연동.
9. **CameraProvider Interface Stub**: 향후 확장을 위한 인터페이스 확보.
10. **Testing & Verification**: 18개 테스트 시나리오 검증.

> [!IMPORTANT]
> Sprint 8을 기점으로 P009는 두뇌(Core)에서 빠져나와 **스마트폰/태블릿이라는 물리적 감각 기관과 교류**하기 시작합니다. 본 사전 계획서에 대한 검토 및 승인을 요청드립니다.
