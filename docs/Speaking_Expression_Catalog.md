# Speaking Expression Catalog (Speaking_Expression_Catalog.md)

**Sprint 42: Lip Sync Engine & Speech Embodiment**  
**작성자**: ✍️ Amy (AI Growth & UX) & 🐟 코다리 Architect  
**일자**: 2026-08-30

---

## 1. 5대 발화 표정 카탈로그 (Speaking Style Presets)

음성 스타일 및 대화 맥락에 따라 말하는 동안 결합되는 표정 파라미터 기준값 명세입니다.

| 발화 스타일 (Speaking Style) | `speechIntensity` | `smileStrength` | `browRaise` | `headPitch` Accent | 주 사용 맥락 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Calm Speaking (차분한 대화)** | 0.40 | 0.35 | 0.05 | ±0.8° | 일상 설명, 사실 전달, 차분한 대답 |
| **2. Warm Speaking (다정한 대화)** | 0.65 | 0.70 | 0.20 | ±1.5° | 위로, 격려, 칭찬, 친밀한 일상 공유 |
| **3. Excited Speaking (활기찬 대화)** | 0.85 | 0.85 | 0.35 | ±2.5° | 기쁜 소식 축하, 열정적인 아이디어 제안 |
| **4. Empathetic Speaking (공감 대화)** | 0.50 | 0.45 | 0.25 | ±1.2° | 사용자의 힘든 고민 경청 후 공감 발화 |
| **5. Serious Speaking (진지한 조언)** | 0.60 | 0.10 | -0.15 | ±1.0° | 신중한 피드백, 깊이 있는 고민 상담 |

---

## 2. 발화 시작/종료 전이 (Speech Lifecycle Transition)

1. **발화 시작 (Pre-Speech)**:
   - 음성 출력 150~200ms 전 `smileStrength`와 `headPitch`가 먼저 타깃값으로 부드럽게 상승.
2. **발화 중 (During Speech)**:
   - `mouthOpen`과 `viseme`이 오디오 파형에 맞춰 60~120ms 주기로 활기차게 반응.
3. **발화 종료 (Post-Speech Settling)**:
   - 음성 종료 즉시 100ms 이내에 입이 부드럽게 닫히며(`mouthOpen ➔ 0.0`), 표정은 온화한 미소(Soft Smile)로 정착.
