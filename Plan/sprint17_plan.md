# P009.AICompanion - Sprint 17 구현 계획서
**Real Voice Interaction & Audio Runtime (실제 STT/TTS 음성 상호작용 및 오디오 런타임)**

---

## 1. Pre-Implementation Audit (사전 감사 결과)

| 컴포넌트 | 현재 상태 (AS-IS) | 문제점 및 Gap | Sprint 17 개선 방안 (TO-BE) |
| :--- | :--- | :--- | :--- |
| **STT Provider** (`openai_adapter.py`) | 기본 Whisper 호출만 존재 | 빈 오디오 예외 처리, 한국어 설정, 에러 매핑 부재 | `OpenAI_STTProvider` 견고화 (Empty Audio 방어, 타임아웃, 에러 정규화) |
| **TTS Provider** (`openai_adapter.py`) | 기본 TTS 호출만 존재 | Empty Text 방어, Voice Context 연동, 예외 래핑 부재 | `OpenAI_TTSProvider` 견고화 (`tts-1`, voice preset, WAV/MP3 버퍼) |
| **ProviderFactory** (`factory.py`) | `STT_PROVIDER=openai`, `TTS_PROVIDER=openai` 미연결 | `pass`로 Mock만 반환 | `OpenAI_STTProvider`, `OpenAI_TTSProvider` 정상 인스턴스화 연결 |
| **Voice Endpoint** (`endpoints/voice.py`) | `MockSTTProvider`, `MockTTSProvider` 하드코딩 | 환경변수 반영 불가 | `ProviderFactory`를 통한 의존성 주입으로 전면 전환 |
| **User Interrupt** | 기본 세션 인터럽트 메서드만 존재 | Audio Player 재생 중단 및 이전 콜백 무효화 Race Condition 방어 부재 | `playbackId` 기반 검증 및 모바일 `voiceController` 즉각 중단 연동 |
| **Mobile Audio** | `CompanionScreen`에 UI 버튼만 존재 | 실제 음성 세션 생성, 오디오 전송, 재생 연동 부재 | `voiceController.ts` 및 `CompanionScreen` 실시간 음성 루프 완성 |

---

## 2. 변경 대상 파일 목록

### 📁 수정 및 신규 대상 파일
1. `backend/app/services/voice/adapters/openai_adapter.py` [MODIFY]: Whisper STT & Audio TTS 견고화 (빈 입력, 타임아웃, 예외 매핑)
2. `backend/app/services/providers/factory.py` [MODIFY]: `STT_PROVIDER=openai`, `TTS_PROVIDER=openai` 팩토리 연결
3. `backend/app/api/endpoints/voice.py` [MODIFY]: `ProviderFactory`를 통한 STT/TTS 동적 주입
4. `mobile/src/services/voiceController.ts` [NEW]: 모바일 음성 세션, 레코딩 상태, TTS 오디오 재생 및 Interrupt 제어
5. `mobile/src/screens/CompanionScreen.tsx` [MODIFY]: `voiceController` 연동, 마이크 인터럽트 및 아바타 상태 동기화
6. `backend/tests/test_voice_integration.py` [NEW]: STT/TTS 어댑터, 상태 머신 전이, User Interrupt, Text Fallback 테스트

---

## 3. 핵심 아키텍처 및 Interrupt 처리 흐름

```text
[Mobile CompanionScreen]
        │
        ├─► [User Press Mic] ──► (If Speaking -> Interrupt Audio Player & Cancel Current Playback)
        │                             │
        ▼                             ▼
[VoiceController] ─────────────► [POST /api/v1/voice/sessions/{id}/interrupt]
        │
        │ 1. Record Audio (WAV)
        │ 2. POST /api/v1/voice/sessions/{id}/audio
        ▼
[VoiceService (Backend)]
        │
        ├─► [State: TRANSCRIBING] ──► Real STT (OpenAI Whisper)
        │                                 │
        ├─► [State: THINKING]     ──► NormalizedInput
        │                                 │
        │                                 ▼
        │                    [CompanionOrchestrator] (Single Cognitive Pipeline)
        │                                 │
        │                                 ▼ (Real LLM gpt-4o-mini)
        │                    [UnifiedResponse + AvatarState]
        │                                 │
        ├─► [State: SPEAKING]     ──► Real TTS (OpenAI Audio tts-1)
        │                                 │
        ▼                                 ▼
[Response: Audio Bytes] ─────────► [VoiceController.playAudio()]
                                          │
                                          ├─► AvatarView (Speaking State Sync)
                                          └─► Audio Finished -> [State: IDLE]
```

---

## 4. Quality Gates V1 ~ V8

| Gate | 검증 항목 | 검증 방식 |
| :--- | :--- | :---: |
| **Gate V1** | Real STT Provider 정상 동작 | 한국어/빈 오디오/타임아웃 단위 테스트 |
| **Gate V2** | Real TTS Provider 정상 동작 | 음성 합성 및 바이트 스트림 반환 테스트 |
| **Gate V3** | Voice ➔ Orchestrator ➔ LLM 연결 | `VoiceService.process_audio` 전체 파이프라인 검증 |
| **Gate V4** | 음성 응답 바이트 반환 | TTS 결과 응답 데이터 무결성 검증 |
| **Gate V5** | Voice State Machine 전이 | `IDLE` ➔ `LISTENING` ➔ `TRANSCRIBING` ➔ `THINKING` ➔ `SPEAKING` ➔ `IDLE` |
| **Gate V6** | Speaking 중 User Interrupt | 인터럽트 시 세션 상태 즉각 `LISTENING` 전이 및 오디오 정지 |
| **Gate V7** | Voice 실패 시 Text Fallback | STT/TTS 실패 시에도 `ConversationView` 정상 유지 |
| **Gate V8** | Regression & Type Integrity | 기존 36개 테스트 100% PASS + TypeScript 0 Errors |

---

## 5. Scope Protection
- Vision Real Provider, 3D Avatar, Lip Sync, Always-on Mic 등은 이번 Sprint 범위에서 엄격히 제외합니다.
