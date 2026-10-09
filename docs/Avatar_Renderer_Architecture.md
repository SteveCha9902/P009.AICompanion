# Avatar Renderer Architecture (Avatar_Renderer_Architecture.md)

본 문서는 동영상 클립 스위칭 방식을 완전히 대체하는 **실시간 레이어드 캐릭터 렌더러(Real-Time Layered Character Renderer)**의 설계 및 동작 파이프라인을 정의합니다.

---

## 1. 아키텍처 핵심 원칙

1. **No Video Clip Switching**: 비디오 파일 교체로 인한 깜빡임/자세 튐/루프 경계 리셋을 원천 차단합니다.
2. **Single High-Res Base + Dynamic Compositing**: 최고 화질의 베이스 포트레이트 위에 눈, 눈썹, 입모양, 호흡, 고개 틸트를 실시간 코드로 합성(Compositing)합니다.
3. **Synchronous Real-Time Lip-Sync**: TTS 오디오 재생 시간에 맞춰 음소(Viseme)와 진폭(Amplitude)으로 입모양을 실시간 구동합니다.
4. **Renderer-Agnostic Parameter Interface**: 백엔드에서 전달되는 DTO는 렌더러 구현체(2D Reanimated, Skia, Live2D Cubism, 3D WebGL)에 종속되지 않습니다.

---

## 2. 렌더링 파이프라인 (Dataflow)

```
                       [Backend Cognitive Engine]
                                    │
                                    ▼
                         [CharacterDecision]
                                    │
                                    ▼
                     [AvatarBehaviorController]
                                    │
                                    ▼
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
[EmotionToExpressionMapper]   [LipSync/Viseme Engine]   [AvatarBaselineController]
 (smile, eye_soft, brow)       (mouth_open, A/E/I/O/U)    (blink 2-7s, breath 4.5s)
       │                            │                            │
       └────────────────────────────┼────────────────────────────┘
                                    ▼
                      [Real-Time Avatar DTO (SSE)]
                                    │
                                    ▼
               [Mobile RealtimeLayeredAvatarRenderer]
            ┌────────────────────────────────────────┐
            │  1. Dynamic Aura Ring (State Color)    │
            │  2. Base Portrait (High-Res 1024x1024) │
            │  3. Head Transform Matrix (Pitch/Roll) │
            │  4. Eyebrow Interpolator (Spring)      │
            │  5. Eye State Selector (Open/Half/Blink│
            │  6. Viseme Mouth Blending (Crossfade)  │
            │  7. Organic Breathing Loop (Scale)     │
            └────────────────────────────────────────┘
                                    │
                                    ▼
                            [60 FPS Display]
```

---

## 3. 실시간 립싱크(Lip-Sync) 구동 로직

1. **오디오 재생 감지 (`voiceState === 'speaking'`)**:
   - 오디오 출력 중 60~120ms 주기로 음소 시퀀스(A ➔ E ➔ I ➔ O ➔ U)를 순환하며 자연스러운 조음(Articulation) 구현.
   - 음성 진폭에 맞춰 `mouth_open` 스케일을 0.2 ~ 0.8 사이로 동적 보조.
2. **발화 종료 (`speaking === false`)**:
   - 100ms 이내에 즉각 `CLOSED` 상태로 자연스럽게 복귀.

---

## 4. 성능 최적화 전략 (Performance & FPS)

- **React Native Reanimated & useNativeDriver**: 모든 스케일, 회전, 투명도 변화를 네이티브 UI 스레드에서 직접 처리하여 JS 스레드 부하 제로화.
- **Asset Pre-caching**: 모든 분리 레이어 PNG는 앱 기동 시 메모리에 프리로드되어 렌더링 지연(Zero Lag) 보장.
