# Motion Library Specification V1 (Motion_Library_V1.md)

본 문서는 **P009.AICompanion Sprint 45**의 12대 신체 동작 라이브러리(Motion Library V1) 표준 카탈로그 규격을 정의합니다.

---

## 1. 12대 신체 동작 라이브러리 카탈로그 (Motion Catalog)

| 카테고리 (Category) | 모션 ID | 모션 명칭 | 신체 파라미터 변위 (Displacement) | 주 사용 맥락 |
| :--- | :--- | :--- | :--- | :--- |
| **Listening (경청)** | `LISTENING_SOFT_NOD` | 은은한 경청 끄덕임 | `nodIntensity: 0.4, headPitch: +1.5°` | 일상적인 대화 청취 |
| | `LISTENING_DEEP_NOD` | 깊은 공감 끄덕임 | `nodIntensity: 0.8, headPitch: +3.0°` | 중요한 이야기 경청 |
| | `LISTENING_SIDE_TILT` | 호기심 갸우뚱 | `headTilt: +3.0°, eyeContact: 1.0` | 흥미로운 질문 경청 |
| | `LISTENING_FOCUS_LEAN` | 전방 집중 기울임 | `bodyLean: +0.4, attentionLevel: 1.0` | 비밀/진지한 이야기 |
| **Thinking (사색)** | `THINKING_TILT` | 사색 틸트 | `headTilt: -4.0°, headPitch: -2.0°` | 일반적인 추론/생각 |
| | `THINKING_DOWN_GAZE` | 하단 시선 사색 | `eyeDirectionY: -0.5, eyeContact: 0.3` | 깊은 고민/기억 회상 |
| | `THINKING_SIDE_GAZE` | 측면 시선 분산 | `eyeDirectionX: +0.4, eyeContact: 0.4` | 새로운 아이디어 구상 |
| | `THINKING_REFLECTION` | 침묵의 성찰 | `headRoll: -2.5°, eyeSoftness: 0.8` | 감정적 성찰/조언 준비 |
| **Speaking (발화)** | `SPEAKING_GENTLE_EMPHASIS` | 부드러운 강조 | `headPitchAccent: ±1.5°, smile: 0.6` | 사실 및 답변 전달 |
| | `SPEAKING_WARM_LEAN` | 다정한 전방 기울임 | `bodyLean: +0.3, warmth: +0.2` | 위로 및 격려 발화 |
| | `SPEAKING_SMALL_HEAD_TURN` | 미세 고개 회전 | `headYaw: ±2.0°, smile: 0.7` | 경쾌한 이야기 전달 |
| **Empathy (공감)** | `EMPATHY_SOFT_NOD` | 따뜻한 위로 끄덕임 | `nodIntensity: 0.5, eyeSoftness: 0.9` | 슬픔/고민 위로 |
| | `EMPATHY_CONCERN_TILT` | 염려 틸트 | `headTilt: +2.0°, browRaise: -0.2` | 걱정스러운 상황 공감 |
| | `EMPATHY_SUPPORTIVE_LEAN` | 지지적 기울임 | `bodyLean: +0.5, eyeContact: 0.95` | 완벽한 심리적 안전감 |
