# Context-Aware Motion Guide (Context_Motion_Guide.md)

**Sprint 45: Motion Library Expansion & Behavioral Variety System**  
**작성자**: ✍️ Amy (AI Growth & UX) & 🐍 미나리 과장 (Backend)  
**일자**: 2026-08-30

---

## 1. 질문 유형 및 맥락별 모션 매핑 규격

대화 맥락에 맞춰 최적의 모션을 지능적으로 매핑합니다.

| 질문/대화 맥락 (Context) | 추천 1차 모션 | 보조 모션 | 표정 및 신체 뉘앙스 |
| :--- | :--- | :--- | :--- |
| **1. 축하 / 기쁜 소식** | `SPEAKING_SMALL_HEAD_TURN` | `LISTENING_SIDE_TILT` | 활짝 웃는 환한 미소, 경쾌한 고개 움직임 |
| **2. 위로 / 고민 상담** | `EMPATHY_SUPPORTIVE_LEAN` | `EMPATHY_SOFT_NOD` | 깊은 공감 눈빛, 부드럽게 앞으로 기울인 상체 |
| **3. 복잡한 질문 / 설명** | `THINKING_DOWN_GAZE` | `SPEAKING_GENTLE_EMPHASIS` | 진중한 하단 시선 사색, 설득력 있는 강조 끄덕임 |
| **4. 일상 잡담 / 공유** | `LISTENING_SOFT_NOD` | `SPEAKING_WARM_LEAN` | 편안하고 자연스러운 눈맞춤과 은은한 미소 |

---

## 2. 사용자 반복 인지 방지 가이드 (Repetition Detection Threshold)

- **임계점 (Threshold)**: 사용자는 동일한 모션이 **3회 연속** 또는 **1분 내 4회 이상** 발생할 때 "기계적 루프"로 인식합니다.
- **Variety Engine의 방어선**: 최근 3개 모션을 FIFO 링 버퍼에 기록하고, 해당 모션들의 선택 확률을 70% 이상 억제하여 언제나 새로운 신체 반응을 유도합니다.
