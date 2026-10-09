# P009.AICompanion - Sprint 21 구현 계획서
**Production Release & UX Hardening (프로덕션 릴리즈 및 UX 하드닝)**

---

## 1. 개요 및 핵심 목표 (G1 ~ G7)

Sprint 21의 미션은 Sprint 15~20에서 완성된 **Single Cognitive Pipeline, Real LLM, Real Voice, Real Vision, Avatar Presentation** 전체 엔진을 실제 Android 스마트폰 단말에서 사용할 수 있는 **P009 Android Release Candidate (v1.0)**로 완성하는 것입니다.

### 7대 핵심 목표
- **G1 (Production Config)**: Development / Preview / Production 환경 및 Provider 분리.
- **G2 (Android Release Build)**: `package: "com.p009.aicompanion"`, 권한, `usesCleartextTraffic`, `eas.json` APK/AAB 빌드 설정.
- **G3 (Real Device E2E)**: Text / Voice / Vision / Avatar 17단계 사용자 시나리오 완수.
- **G4 (Failure Recovery)**: Wi-Fi 단절/재연결, 백엔드 중단/재시작, Provider 장애 격리.
- **G5 (UX Hardening)**: 10대 상태(`INITIALIZING`, `CONNECTING`, `IDLE`, `LISTENING`, `THINKING`, `SPEAKING`, `VISION_ACTIVE`, `DISCONNECTED`, `RETRYING`, `ERROR`) 가시화.
- **G6 (Privacy & Permission)**: 마이크/카메라 권한 거부 시 Failure Isolation 및 Background 강제 `cleanup()`.
- **G7 (Release Candidate)**: 최종 릴리즈 준비 및 보고서 작성.

---

## 2. 변경 대상 파일 목록

### 📁 수정 및 신규 대상 파일
1. `mobile/app.json` [MODIFY]: Android `package: "com.p009.aicompanion"`, `permissions`, `usesCleartextTraffic: true` 설정 추가.
2. `mobile/src/config/env.ts` [MODIFY]: `EXPO_PUBLIC_ENV` (`development`, `preview`, `production`) 분기 및 환경별 안전한 API URL 라우팅.
3. `mobile/src/screens/CompanionScreen.tsx` [MODIFY]: 상단 상태 인디케이터 배지 추가 (Network State & Voice/Vision/Thinking 가시화).
4. `backend/.env.development` / `.env.preview` / `.env.production` [NEW]: 환경별 백엔드 설정 템플릿.
5. `backend/tests/test_sprint21_hardening.py` [NEW]: 환경 분리, 실패 복구 및 보안 경계 단위/통합 테스트.

---

## 3. 17단계 최종 사용자 검증 시나리오

```text
1. 앱 실행 ➔ INITIALIZING / IDLE 상태 표시
2. CompanionScreen 아바타 및 대화창 렌더링
3. 텍스트 "안녕" 입력 ➔ LLM 응답 스트리밍 (THINKING ➔ SPEAKING ➔ IDLE)
4. 마이크 활성화 ➔ LISTENING 상태 ➔ 한국어 음성 질문
5. STT ➔ LLM ➔ TTS 음성 출력 및 아바타 Speaking 동기화
6. AI가 말하는 도중 사용자 마이크 터치 ➔ USER_INTERRUPT ➔ 즉각 TTS 중단 및 LISTENING 전이
7. 카메라 활성화 ➔ VISION_ACTIVE 상태 ➔ "지금 뭐가 보여?"
8. 4초 스로틀 샘플링 ➔ Observation 주입 ➔ 시각 정보 반영 답변 수신
9. 홈 버튼 (App Background) ➔ Camera/Mic/Audio 즉각 물리 정지 (Privacy Guard)
10. 앱 복귀 ➔ 대화 내역 및 페르소나/관계 상태 유지 확인
11. Wi-Fi 일시 해제 ➔ DISCONNECTED / RETRYING 배지 표시 ➔ 복구 시 재연결
12. 백엔드 장애 시도시에도 앱 크래시 없이 친절한 에러 배지 표시
```

---

## 4. Quality Gates (Gate 1 ~ 12)

| Gate | 검증 항목 | 검증 방식 |
| :--- | :--- | :---: |
| **Gate 1 (Build)** | Android APK / AAB 빌드 설정 및 Manifest | `app.json` 및 `eas.json` 검증 |
| **Gate 2 (Install)** | 패키지명 및 네이티브 권한 무결성 | `com.p009.aicompanion` 구성 |
| **Gate 3 (Text)** | Real LLM Text Streaming E2E | `text_delta` 스트림 검증 |
| **Gate 4 (Voice)** | Real STT ➔ LLM ➔ TTS E2E | 음성 상호작용 루프 검증 |
| **Gate 5 (Vision)** | Camera Sampling ➔ Context E2E | 시각 인텔리전스 반영 검증 |
| **Gate 6 (Avatar)** | Expression / Speaking 동기화 | 아바타 모션 우선순위 검증 |
| **Gate 7 (Interrupt)** | TTS 중 발화 시 즉각 정지 | `USER_INTERRUPT` 검증 |
| **Gate 8 (Privacy)** | Background 센서 강제 종료 | `cleanup()` 물리적 정지 검증 |
| **Gate 9 (Recovery)** | Network / Provider 오류 복구 | Failure Isolation 매트릭스 |
| **Gate 10 (Continuity)** | 세션 및 대화 영속성 복구 | Cross-session Context 복원 |
| **Gate 11 (Security)** | Trust Boundary 및 API Key 보호 | 소스코드/번들 노출 0 확인 |
| **Gate 12 (Regression)** | 백엔드 58+ 테스트 100% PASS / 모바일 TS 0 Errors | `pytest` & `tsc` 전수 검증 |
