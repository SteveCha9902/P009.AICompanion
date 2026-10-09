# API Contract (Draft)

초기 REST API 및 WebSocket 명세서입니다.

## 1. REST API
- `POST /api/v1/users`: 유저 및 기본 페르소나 매핑 생성
- `POST /api/v1/conversations`: 신규 대화 세션 오픈
- `POST /api/v1/conversations/{id}/messages`: 사용자 텍스트 전송 (Response Pipeline 트리거 후 답변 반환)
- `GET /api/v1/users/{id}/memory`: 추출된 Memory 목록 조회
- `GET /api/v1/users/{id}/state`: 현재 Companion State, Emotion, Relationship 조회

## 2. WebSocket (Real-time Avatar Mode 용)
Interactive Mode에서는 텍스트뿐만 아니라 비전(Gaze), 오디오 볼륨 등의 센서 데이터를 지속적으로 송수신해야 하므로 WebSocket 채널을 활용합니다.
- `WS /ws/v1/companion/{user_id}`
  - Client -> Server: `{"type": "vision_update", "face_position": [0.3, 0.5]}`
  - Server -> Client: `{"type": "behavior_action", "action": "look_at", "target": [0.3, 0.5]}`

## 3. Push Notification (Ambient Mode)
- `POST /api/v1/devices/register`: FCM/APNs 푸시 토큰 등록
- Backend 내부 Scheduler에서 특정 조건 만족 시 Firebase Admin SDK 등을 통해 Push 발송
