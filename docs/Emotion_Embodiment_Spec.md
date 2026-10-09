# Emotion Embodiment Specification (Emotion_Embodiment_Spec.md)

본 문서는 **P009.AICompanion Sprint 44**의 감정 신체화 엔진(Emotion Embodiment Engine) 7대 핵심 감정 규격 및 다중 감정 블렌딩(Emotion Blending) 파이프라인을 정의합니다.

---

## 1. 7대 핵심 감정 및 파라미터 매핑 규격

| 핵심 감정 (Emotion) | `valence` / `arousal` | `smileStrength` | `eyeSoftness` | `browRaise` | `headRoll` / `Pitch` | 주요 신체적 특징 |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Joy (기쁨)** | `+0.85 / +0.75` | 0.85 ~ 1.00 | 0.85 | +0.25 | +2.0° / +1.5° | 활짝 웃는 눈웃음, 입꼬리 대폭 상승, 밝은 오라 |
| **2. Warmth (다정/온화)** | `+0.60 / +0.40` | 0.55 ~ 0.70 | 0.95 | +0.10 | +3.0° / +1.0° | 부드럽고 따뜻한 눈빛, 은은한 미소, 볼 홍조 |
| **3. Curiosity (호기심)** | `+0.30 / +0.65` | 0.30 ~ 0.45 | 0.70 | +0.40 | +4.0° / +2.5° | 크게 뜬 눈, 호기심 어린 갸우뚱 틸트, 높은 시선 집중 |
| **4. Concern (걱정/염려)** | `-0.40 / +0.50` | 0.00 ~ 0.10 | 0.60 | -0.35 | -2.0° / -1.5° | 살짝 모인 미간(Furrowed), 진지한 시선, 입 다묾 |
| **5. Empathy (깊은 공감)** | `+0.20 / +0.30` | 0.35 ~ 0.50 | 0.90 | +0.15 | +2.0° / 0.0° | 사용자 감정에 맞춘 차분한 공감, 느린 호흡 |
| **6. Excitement (열정/흥분)** | `+0.90 / +0.90` | 0.90 ~ 1.00 | 0.80 | +0.50 | ±3.0° / +2.0° | 높은 에너지, 빠른 끄덕임, 눈썹 큰 상승 |
| **7. Calm (평온/안정)** | `+0.10 / +0.20` | 0.20 ~ 0.30 | 0.75 | 0.00 | 0.0° / 0.0° | 고요한 기본 상태, 규칙적인 4.5s 유기체 호흡 |

---

## 2. 다중 감정 블렌딩 (Multi-Emotion Blending)

인지 엔진에서 도출된 복합 감정(예: Joy 60% + Warmth 40%)은 선형 가중합(Weighted Linear Interpolation)으로 합성됩니다:

$$\text{FinalParameter} = \sum_{i=1}^{N} w_i \cdot \text{Param}(\text{Emotion}_i) \quad \left( \sum w_i = 1.0 \right)$$

- **결과 예시**: `Joy (0.6)` + `Warmth (0.4)`
  - `smileStrength`: $0.85 \times 0.6 + 0.60 \times 0.4 = 0.75$
  - `eyeSoftness`: $0.85 \times 0.6 + 0.95 \times 0.4 = 0.89$
  - ➔ 매우 자연스럽고 온화하면서도 기쁨이 묻어나는 복합 표정이 실시간 도출됩니다.
