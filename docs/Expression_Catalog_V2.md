# Expression Catalog V2 (Expression_Catalog_V2.md)

**Sprint 44: Emotion & Relationship Embodiment Engine**  
**작성자**: ✍️ Amy (AI Growth & UX) & 🌸 진달래 주임 (Vision/Mobile)  
**일자**: 2026-08-30

---

## 1. 7대 고도화 표정 카탈로그 V2 (Advanced Expressions)

감정과 관계 상태가 복합적으로 결합된 Expression Layer V2 프리셋입니다.

| 표정 명칭 (Expression V2) | `smileStrength` | `eyeSoftness` | `browRaise` | `headRoll` / `Pitch` | `warmth` | 감정 및 관계 결합 맥락 |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Neutral (공손한 평온)** | 0.20 | 0.70 | 0.00 | 0.0° / 0.0° | 0.40 | Stranger 단계 대기 상태 |
| **2. Soft Smile (다정한 미소)** | 0.50 | 0.85 | +0.10 | +1.5° / 0.0° | 0.65 | Familiar 단계 일상 공감 |
| **3. Warm Smile (깊은 유대 미소)**| 0.75 | 0.95 | +0.20 | +2.5° / +1.0° | 0.85 | Trusted 단계 위로 및 깊은 신뢰 |
| **4. Bright Smile (생동감 넘치는 웃음)**| 0.95 | 0.90 | +0.35 | +3.5° / +2.0° | 0.95 | Close Companion 단계 축하 및 장난 |
| **5. Curious (흥미진진한 경청)** | 0.35 | 0.75 | +0.40 | +4.0° / +2.5° | 0.65 | 새로운 질문 및 흥미로운 이야기 |
| **6. Concerned (진심 어린 염려)** | 0.05 | 0.65 | -0.30 | -2.0° / -1.5° | 0.55 | 사용자의 슬픔/힘든 일에 대한 진지한 태도 |
| **7. Empathetic (따뜻한 위로)** | 0.45 | 0.95 | +0.15 | +2.0° / 0.0° | 0.90 | 깊은 감정적 교감 및 심리적 안전감 제공 |

---

## 2. 실시간 표정 블렌딩 렌더링 예시

- **상황**: 사용자가 기쁜 소식을 전했을 때 (`Joy` 감정 발생)
  - `Stranger` 사용자 ➔ **Soft Smile** (공손하고 차분한 축하, `smileStrength: 0.55`)
  - `Close Companion` 사용자 ➔ **Bright Smile** (자기 일처럼 크게 기뻐하는 환한 미소, `smileStrength: 0.95`, 볼 홍조)
