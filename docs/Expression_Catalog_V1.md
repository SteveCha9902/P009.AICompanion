# Expression Catalog V1 (Expression_Catalog_V1.md)

**Sprint 41: Real-Time Face Engine**  
**작성자**: ✍️ Amy (AI Growth & UX) & 🐟 코다리 Architect  
**일자**: 2026-08-30

---

## 1. 7대 기본 표정 카탈로그 (Catalog Presets)

Face Engine에서 사용되는 7대 표준 표정의 `FaceParameters` 기준값 명세입니다.

| 표정 명칭 (Expression) | `eyeOpenness` | `browRaise` | `smileStrength` | `mouthOpen` | `headRoll` / `Pitch` | `warmth` | 주요 사용 맥락 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Neutral (평온)** | 0.85 | 0.0 | 0.20 | 0.0 | 0.0° / 0.0° | 0.40 | 일상 대기 (Idle) 상태 |
| **2. Soft Smile (은은한 미소)** | 0.90 | 0.10 | 0.45 | 0.0 | 1.0° / 0.0° | 0.60 | 친근한 인사 및 긍정적 수긍 |
| **3. Warm Smile (따뜻한 미소)** | 0.85 | 0.20 | 0.70 | 0.15 | 2.5° / 1.0° | 0.85 | 공감, 위로, 깊은 유대감 표현 |
| **4. Bright Smile (환한 미소)** | 1.00 | 0.35 | 0.90 | 0.40 | 3.0° / 2.0° | 0.95 | 칭찬, 축하, 즐거운 대화 |
| **5. Curious (호기심/경청)** | 1.00 | 0.40 | 0.30 | 0.0 | 3.5° / 2.0° | 0.60 | 사용자 말 집중 경청 (Listening) |
| **6. Concerned (진지/걱정)** | 0.80 | -0.20 | 0.05 | 0.0 | -1.5° / -1.0° | 0.50 | 고민 상담, 진지한 조언 |
| **7. Thinking (사색/생각)** | 0.75 | 0.10 | 0.15 | 0.0 | -4.0° / -2.0° | 0.45 | 답변 생성 중 (LLM 지연 구간) |

---

## 2. 표정 전환 보간 규칙 (Transition Interpolation)

- **보간 시간**: 표정 변경 시 기본 `300ms ~ 450ms` Cubic-Bezier(Ease-In-Out) 커브 적용.
- **Pre-expression 선반영**: `Thinking` ➔ `Warm Smile` 전이 시 음성 시작 200ms 전에 미리 80% 도달.
