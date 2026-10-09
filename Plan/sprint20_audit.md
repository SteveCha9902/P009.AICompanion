# P009.AICompanion - Sprint 20 Pre-Implementation Audit Report
**Android Real-Device E2E Validation & Product Hardening**

---

## 1. 개요 및 마션

Sprint 20의 목표는 Sprint 15~19에서 구축된 **Single Cognitive Pipeline, Real LLM, Real Voice, Real Vision, Avatar Presentation** 전체 엔진을 실제 Android 스마트폰 단말에서 하나의 통합 AI Companion으로 엔드투엔드 검증하고, 프로덕션 프로토타입 수준으로 하드닝하는 것입니다.

```text
Android Smartphone (CompanionScreen)
        │
        ├── Text Stream (ConversationView)
        ├── Voice Loop (VoiceController -> STT/TTS)
        ├── Vision Loop (VisionController -> Camera Sampling)
        └── Avatar Sync (AvatarView -> State Priority)
        │
        ▼ (POST /api/v1/companion/interactions & SSE)
CompanionOrchestrator (Backend Single Pipeline)
        │
        ├─► 7 Context Providers (Persona, Memory, Rel, Emotion, Presence, Vision, History)
        ├─► Real LLM Provider (OpenAI gpt-4o-mini)
        ├─► Real Voice Provider (Whisper STT / OpenAI Audio TTS)
        └─► Real Vision Provider (gpt-4o-mini Multimodal Vision)
        │
        ▼ (Unified JSON SSE Events)
Android UI Real-Time Presentation (Avatar Speaking & Motion Sync)
```

---

## 2. Phase 0 — 코드베이스 Audit (10대 질문 답변)

### Q1. Sprint 19의 실제 완료 여부
- **확인 완료**: `AvatarStateResolver` (백엔드) ➔ SSE `avatar_state` ➔ `avatarService` (모바일) ➔ `AvatarView` (ErrorBoundary) ➔ `StaticImageRenderer` 렌더링 파이프라인 완비.
- Audio `onStart` / `onEnd`와 `speaking` 상태 동기화 및 User Interrupt 시 즉각 발화 중단 및 `LISTENING` 전이 체계 확립.

### Q2. Stub / Mock Provider 잔존 여부
- **백엔드**: `LLM_PROVIDER=openai`, `STT_PROVIDER=openai`, `TTS_PROVIDER=openai`, `VISION_PROVIDER=cloud` 설정으로 실제 클라우드 API와 100% 연동. (Mock 어댑터는 테스트 및 장애 격리용으로 보존).
- **모바일**: `CameraProvider.ts` 인터페이스가 Expo Camera 네이티브 사양과 일치하도록 추상화 완료.

### Q3. Android 전용 코드 상태
- [config/env.ts](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/config/env.ts)에서 `Platform.OS === 'android'` 감지 시 에뮬레이터 루프백(`http://10.0.2.2:8000`) 자동 라우팅 지원.

### Q4. 환경변수 처리
- **모바일**: `EXPO_PUBLIC_API_URL`을 통해 물리 단말(LAN IP: `http://192.168.x.x:8000`) 또는 프로덕션 HTTPS 엔드포인트 지정 가능.
- **백엔드**: `.env` 파일로 `OPENAI_API_KEY` 및 Provider 분기 관리, 소스코드 및 모바일 번들에 API 키 일체 미포함.

### Q5. API URL 설정
- 하드코딩 없음. `getApiBaseUrl()` 단일 진실 출처를 통해 모든 서비스(`interactionController`, `voiceController`, `visionController`)가 일관되게 참조.

### Q6. Permission (권한) 설정
- 마이크(`RECORD_AUDIO`), 카메라(`CAMERA`) 권한 상태(`UNKNOWN`, `GRANTED`, `DENIED`, `RESTRICTED`) 추적.
- 권한 거부 시 해당 감각(Voice/Vision)만 비활성화되고 Text 대화는 100% 정상 유지(Failure Isolation).

### Q7. Expo 설정
- Expo SDK 52+, `expo-secure-store`, 세로 모드 기본 및 태블릿 적응형 레이아웃 지원.

### Q8. Android Manifest 설정 (개선 대상)
- [app.json](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/app.json)의 `android` 섹션에 `package: "com.p009.aicompanion"` 및 `permissions` 명시 필요.

### Q9. Network Security 설정 (개선 대상)
- 로컬 Wi-Fi 개발 환경에서 HTTP 통신을 허용하기 위해 `usesCleartextTraffic: true` 설정 적용 필요.

### Q10. 현재 테스트 상태
- 백엔드 전체 pytest: **58/58 PASSED (100%)**.
- 모바일 TypeScript: `npx tsc --noEmit` ➔ **0 ERRORS**.

---

## 3. Sprint 20 구현 및 하드닝 계획 (Phase 1 ~ Phase 14)

1. **Phase 1: Android Build & Network Config 보강**:
   - `mobile/app.json`에 `package`, `permissions`, `usesCleartextTraffic` 설정 추가.
   - `env.ts`의 로컬/물리 기기 연결성 검증.
2. **Phase 2 ~ 11: E2E 파이프라인 점검 (Health, Text, Cognitive, Voice, Interrupt, Vision, Avatar, Privacy, Continuity)**:
   - 앱 Background 전환 시 마이크/카메라/오디오 물리적 중단(`cleanup`) 및 복귀 검증.
   - 앱 재시작 후 Conversation/Memory/Relationship 영속성 검증.
3. **Phase 12 ~ 14: Network Chaos & Failure Isolation Test**:
   - Wi-Fi 차단, 백엔드 중단 시 크래시 방지 및 오프라인 상태 피드백.
   - Provider별 단독 오류 시 텍스트 대화 무중단 검증.
4. **최종 데모 시나리오 (17단계 사용자 루프)** 완수.

---

## 4. Quality Gates (Gate A ~ L)

| Gate | 검증 항목 | 검증 방식 |
| :--- | :--- | :---: |
| **Gate A (Build)** | Android Build 설정 및 Manifest 권한 | `app.json` 빌드 구성 검증 |
| **Gate B (Health)** | Backend 통신 및 Offline 처리 | `GET /health` 연결성 검증 |
| **Gate C (Text)** | Real LLM Text Streaming E2E | `text_delta` 스트리밍 검증 |
| **Gate D (Voice)** | Real STT ➔ LLM ➔ TTS E2E | 음성 녹음 및 오디오 재생 루프 |
| **Gate E (Vision)** | Real Camera ➔ Vision ➔ Context E2E | 시각 정보 반영 AI 응답 생성 |
| **Gate F (Avatar)** | Emotion/Voice ➔ AvatarState ➔ Render | 아바타 모션 및 Speaking 동기화 |
| **Gate G (Interrupt)** | Speaking 중 발화 시 TTS 즉각 중단 | `USER_INTERRUPT` 즉시 정지 검증 |
| **Gate H (Privacy)** | Background 진입 시 Sensor 강제 OFF | 백그라운드 리소스 `cleanup()` |
| **Gate I (Continuity)** | 세션/앱 재시작 후 메모리/기록 복구 | Cross-session Context 복원 |
| **Gate J (Failure)** | 개별 Provider 장애 시 앱 크래시 방지 | Failure Isolation 매트릭스 검증 |
| **Gate K (Regression)** | 백엔드 전체 테스트 100% PASS | `pytest` 58개 테스트 통과 |
| **Gate L (TypeScript)** | 모바일 타입/빌드 무결성 | `npx tsc --noEmit` 0 Errors |
