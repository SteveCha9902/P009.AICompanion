# Thinking Behavior Guide (Thinking_Behavior_Guide.md)

**Sprint 43: Embodied Behavior Engine**  
**작성자**: ✍️ Amy (AI Growth & UX) & 🐟 코다리 Architect  
**일자**: 2026-08-30

---

## 1. 사색(Thinking) 행동 메커니즘 개요

사용자가 말을 마친 직후 LLM 응답을 생성하는 구간(1~4초) 동안, 정지 화면처럼 굳어있지 않고 **"질문을 곰곰이 생각하며 답변을 구성하고 있다"**는 인간적인 인지 행동을 표현합니다.

---

## 2. 4대 핵심 사색 신호 (Thinking Cues)

1. **시선 분산 및 하단 시선 이동 (`eyeDirectionY: -0.4`, `eyeContact: 0.4`)**:
   - 생각을 정리할 때 인간이 자연스럽게 시선을 정면에서 아래/옆으로 옮기는 인지적 시선 회피(Gaze Aversion) 재현.
2. **사색 틸트 (`headTilt: -4.0°`, `headPitch: -2.0°`)**:
   - 머리를 반대 방향으로 기울이며 고민하는 표정 형성.
3. **눈동자 정지 및 완만한 눈꺼풀 (`eyeOpenness: 0.8`, `eyeSoftness: 0.6`)**:
   - 시선이 고정되며 생각에 잠긴 부드러운 눈빛 연출.
4. **Pre-expression 선반영 연결 (200ms 전이)**:
   - 생각이 완료되는 순간(`FIRST_TOKEN_READY`), 미소와 눈맞춤이 먼저 반응하여 바로 다음 말하기 단계로 매끄럽게 연결.
