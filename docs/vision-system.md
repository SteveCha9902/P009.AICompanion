# Vision System

사용자가 Camera Mode를 활성화하면 Companion이 시각적으로 환경을 이해하는 시스템입니다.

## 1. Privacy-First & On-Device Processing
개인정보 보호를 위해 영상 프레임 원본을 서버로 스트리밍하는 것을 지양합니다.
대신 Mobile Client(Edge) 측에서 경량 모델을 활용하여 다음의 Feature 단위 텍스트 정보만 추출해 서버로 전달합니다.
- `user_present` (boolean)
- `face_detected` (boolean)
- `face_position` (x, y)
- `attention` (0~1)
- `expression_estimate` (neutral, smile 등)

## 2. Fact vs Inference 분리
비전 파이프라인에서 도출된 결과는 '확실한 사실(Fact)'과 '추정(Inference)'으로 분리하여 Companion Brain에 전달합니다.
- Fact: 얼굴이 화면 좌측에 있다.
- Inference: 사용자가 피곤해 보인다. (확정적 기억으로 저장하지 않음)

## 3. Gaze Tracking
추출된 `face_position` 값을 활용해 아바타의 눈동자(Eye) 및 고개(Head) 방향을 실시간으로 역전환(Inverse Kinematics 또는 LookAt Controller)하여 **Companion이 사용자를 바라보는 경험**을 제공합니다.
