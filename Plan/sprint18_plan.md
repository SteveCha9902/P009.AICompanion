# P009.AICompanion - Sprint 18 구현 계획서
**Real Vision Provider & Camera Intelligence Engine (실제 비전 프로바이더 및 카메라 지능 엔진)**

---

## 1. Pre-Implementation Audit (사전 감사 결과)

| 컴포넌트 | 현재 상태 (AS-IS) | 문제점 및 Gap | Sprint 18 개선 방안 (TO-BE) |
| :--- | :--- | :--- | :--- |
| **Vision Adapter** (`cloud_vision_adapter.py`) | 레거시 `gpt-4-vision-preview` 호출 | 모델 구버전, 빈 이미지 방어 및 예외 매핑 부재 | `CloudVisionProvider` 고도화 (`gpt-4o-mini`, Empty Image 방어, 타임아웃, 에러 정규화) |
| **Vision Factory** (`factory.py`) | 기본 import 분기만 존재 | 명시적 검증 및 환경변수 일관성 필요 | `VISION_PROVIDER=cloud|mock` 설정에 따라 엄격한 생성 및 에러 처리 |
| **Vision Endpoint** (`endpoints/vision.py`) | `MockVisionProvider` 하드코딩 | 환경변수 미반영 | `ProviderFactory.get_vision_provider()` DI 적용 |
| **Trust Boundary** (`vision_context.py`) | `[CURRENT VISUAL CONTEXT]` 생성 | 0.6 미만 신뢰도 방어 존재 | `[OBSERVATION]` 티어 유지 및 감정/관계 직접 변조 차단 확인 |
| **Mobile Sampling** (`CameraProvider.ts`) | 단순 Stub 클래스만 존재 | 권한 상태, 3~5s 샘플링 스로틀, Background 클린업 부재 | `visionController.ts` 및 `CameraProvider` 실제 샘플링/권한/클린업 구현 |

---

## 2. 변경 대상 파일 목록

### 📁 수정 및 신규 대상 파일
1. `backend/app/services/vision/adapters/cloud_vision_adapter.py` [MODIFY]: `gpt-4o-mini` 비전 분석, 빈 이미지 방어, 타임아웃, 예외 매핑
2. `backend/app/services/providers/factory.py` [MODIFY]: `VISION_PROVIDER=cloud|mock` 동적 인스턴스화
3. `backend/app/api/endpoints/vision.py` [MODIFY]: `ProviderFactory`를 통한 의존성 주입
4. `mobile/src/services/camera/CameraProvider.ts` [MODIFY]: Camera Permission 및 Frame Capture 인터페이스 구체화
5. `mobile/src/services/visionController.ts` [NEW]: 3~5초 Frame Sampling, User-Initiated 샘플링, Background 강제 정리
6. `mobile/src/screens/CompanionScreen.tsx` [MODIFY]: `visionController` 연동 및 카메라 권한/클린업 제어
7. `backend/tests/test_vision_integration.py` [NEW]: Vision 어댑터, Observation 파이프라인, Context 주입, Failure Isolation 테스트

---

## 3. 핵심 비전 파이프라인 및 Trust Boundary 흐름

```text
[Mobile Camera]
       │
       ▼ (3~5s Throttle or User-Initiated "지금 뭐가 보여?")
[VisionController (Mobile)]
       │
       ▼ (POST /api/v1/vision/sessions/{id}/observations)
[VisionService (Backend)]
       │
       ├─► Real Vision Provider (OpenAI gpt-4o-mini Vision)
       │       │
       │       ▼ (Face, Scene, Objects, Confidence)
       ├─► [VisionObservation] (Deduplication & Confidence >= 0.6 Filter)
       │
       ▼
[VisionContextProvider]
       │
       ▼ (Builds [CURRENT VISUAL CONTEXT])
[ContextBuilder]
       │
       ├─► [TRUSTED] System & Safety Rules
       ├─► [APPLICATION] Persona, Rel, Emotion, Memory, Presence
       ├─► [OBSERVATION] Vision Observation  <── (Trust Boundary: No Direct State Mutation)
       └─► [UNTRUSTED] User Input ("지금 뭐가 보여?")
       │
       ▼
[CompanionOrchestrator] ──► Real LLM ──► Unified Response ──► Mobile UI
```

---

## 4. Quality Gates (VISION-1 ~ VISION-10)

| Gate | 검증 항목 | 검증 방식 |
| :--- | :--- | :---: |
| **VISION-1** | Real Camera Capture & Permission | 권한(`GRANTED`, `DENIED`) 및 캡처 인터페이스 |
| **VISION-2** | Frame Sampling Throttle | 3~5초 간격 샘플링 및 즉시 샘플링 |
| **VISION-3** | Real Vision Provider | `CloudVisionProvider` 이미지 분석 및 JSON 파싱 |
| **VISION-4** | VisionObservation Persistence | 세션별 Observation 저장 및 중복 제거(Deduplication) |
| **VISION-5** | VisionContextProvider Injection | `[CURRENT VISUAL CONTEXT]` 신뢰도 0.6 이상 정상 주입 |
| **VISION-6** | Real LLM Vision Response | 시각 정보가 반영된 AI 응답 생성 E2E 검증 |
| **VISION-7** | Background Camera Shutdown | Background 진입 시 즉시 캡처/샘플링 중단 |
| **VISION-8** | Vision Failure Isolation | Vision 에러 시에도 Text/Voice 대화 무중단 유지 |
| **VISION-9** | Backend Regression Test | 기존 42개 + 신규 Vision 테스트 100% PASS |
| **VISION-10**| TypeScript Integrity | 모바일 `npx tsc --noEmit` 에러 0개 |

---

## 5. Scope Protection
- 30FPS 실시간 클라우드 비전 스트리밍, 3D Avatar, Lip Sync, Always-on Camera 등은 이번 Sprint 범위에서 엄격히 제외합니다.
