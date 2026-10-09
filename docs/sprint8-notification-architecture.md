# Sprint 8: Mobile Presence & Notification Architecture

> 이 문서는 Sprint 8 시작 시 정의된 Notification Bridge와 Mobile Presence의 핵심 아키텍처 원칙입니다.

## 1. Notification vs Message
- **Message**: Companion이 실제로 생성한 발화 내용. (`messages` 테이블 보관)
- **Notification**: 이 메시지를 사용자 모바일 기기로 전달하는 "배달" 행위. (`notification_events` 테이블 보관)
동일한 Message라도 사용자가 앱을 켜고 있다면 In-App Rendering으로 처리되고 Push Notification은 생성되지 않을 수 있습니다.

## 2. Notification Policy & Bridge
Proactive 결정(ALLOW) 이후의 파이프라인:
`Decision ALLOW` → `Message Generation` → `Notification Candidate 생성` → `Notification Policy 검사 (앱 상태, 푸시 설정 검토)` → `Push / In-App 전달 분기`

## 3. Abstract Notification Provider
특정 Push 서비스에 종속되지 않도록 `BaseNotificationProvider`를 통해 캡슐화합니다.

## 4. Companion Presentation State
Emotion State를 그대로 UI에 묶지 않고 `PresentationState`로 한 번 변환합니다.
- `Emotion (JOY)` → `Presentation (SMILE)`
- 향후 아바타 엔진 교체나 업데이트에 유연하게 대응합니다.

## 5. Adaptive UI
태블릿과 스마트폰의 디스플레이 환경에 맞게 `CompanionScreen`은 Phone 모드(위/아래 레이아웃)와 Tablet 모드(좌/우 Split 뷰)를 모두 지원하도록 구성합니다.

## 6. Camera Stub
카메라 연동은 Sprint 10에서 진행하되, `CameraProvider` (Frame -> Vision Analyzer -> User State)의 모바일 인터페이스 뼈대는 미리 정의해 둡니다.
