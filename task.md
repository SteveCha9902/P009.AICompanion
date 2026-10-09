# Sprint 18 Task Checklist

- [x] **Core Architecture & Trust Boundary**:
  - [x] Camera ➔ Frame Sampling ➔ Preprocessing ➔ VisionProvider ➔ VisionObservation ➔ ContextBuilder ➔ CompanionOrchestrator ➔ Real LLM
  - [x] Vision은 `[OBSERVATION]` 티어로만 취급 (감정/관계 직접 변조 차단)
- [x] **Provider Architecture & Factory**:
  - [x] `VISION_PROVIDER=cloud|mock` 설정 지원 (`factory.py`)
- [x] **Raw Image Storage Policy**:
  - [x] 원본 이미지 장기 저장 차단 (Capture ➔ Analyze ➔ Observation ➔ Dispose)
- [x] **CloudVisionProvider 고도화**:
  - [x] `gpt-4o-mini` 비전 분석, 얼굴/시선/표정/객체 인식, 빈 이미지 방어, 타임아웃, 예외 매핑 (`cloud_vision_adapter.py`)
- [x] **Mobile Frame Sampling & VisionController**:
  - [x] `visionController.ts` 작성, 4초 스로틀 샘플링, User-Initiated 즉시 샘플링, Background 강제 정리
- [x] **Failure Isolation & Privacy Cleanup**:
  - [x] Vision 에러 시 텍스트/음성 대화 무중단 유지 및 Background 카메라 정지
- [x] **Tests & Quality Gates VISION-1 ~ VISION-10**:
  - [x] 백엔드 전체 테스트 47개 100% PASS, 모바일 TypeScript 0 에러
