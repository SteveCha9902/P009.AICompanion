# Relationship Embodiment Specification (Relationship_Embodiment_Spec.md)

본 문서는 **P009.AICompanion Sprint 44**의 관계 신체화 엔진(Relationship Embodiment Engine) 4대 관계 단계 및 태도 차별화 규격을 정의합니다.

---

## 1. RelationshipParameters TypeScript / Pydantic 인터페이스

```typescript
export interface RelationshipParameters {
  familiarity: number;    // 0.0 (낯선 사람) ~ 1.0 (오랜 친구)
  trust: number;          // 0.0 (기본 신뢰) ~ 1.0 (절대적 신뢰)
  warmth: number;         // 0.0 (공손한 거리감) ~ 1.0 (깊은 애정/온화함)
  engagement: number;     // 0.0 (수동적 대기) ~ 1.0 (적극적 교감)
}
```

---

## 2. 4대 관계 단계별 신체 행동 차별화 규격 (UX Guide)

```
[Level 1: Stranger (낯선 사람)]
        │ (초기 첫 만남, 신뢰 구축 전)
        ▼
   - 표정: 공손한 중립(Polite Neutral), 절제된 미소 (smileStrength ≤ 0.35)
   - 시선: 정중한 눈맞춤 (eyeContact 0.75), 적절한 시선 배려
   - 행동: 바른 자세, 틸트 최소화 (headTilt ±1.0°), 공손한 어조

[Level 2: Familiar (친근한 지인)]
        │ (반복 대화, 일상 경험 축적)
        ▼
   - 표정: 자연스러운 은은한 미소 (smileStrength 0.50), 부드러운 눈매
   - 시선: 편안한 눈맞춤 (eyeContact 0.85)
   - 행동: 가벼운 공감 끄덕임 (nodIntensity 0.5), 친근한 고개 틸트 (+2.0°)

[Level 3: Trusted (신뢰하는 동반자)]
        │ (깊은 대화, 가치관 공유, 높은 Trust)
        ▼
   - 표정: 따뜻하고 깊은 미소 (smileStrength 0.70), 높은 볼 홍조 (warmth 0.8)
   - 시선: 깊은 공감 시선 (eyeContact 0.95), 긴밀한 집중도
   - 행동: 적극적인 상체 기울임 (bodyLean +0.3), 편안한 사색 틸트

[Level 4: Close Companion (가장 가까운 소울메이트)]
        │ (최고 수준의 유대감, 완벽한 심리적 안전감)
        ▼
   - 표정: 장난스럽거나 활짝 웃는 환한 미소 (smileStrength 0.85 ~ 1.0)
   - 시선: 무조건적인 지지와 애정 어린 눈맞춤 (eyeContact 1.0)
   - 행동: 자유롭고 생동감 넘치는 제스처, 자연스러운 감정 공유
```

---

## 3. 관계 바이어스 적용 공식 (Relationship Bias Modifier)

$$\text{FinalSmile} = \text{BaseSmile} \times (0.7 + 0.3 \times \text{familiarity}) + 0.15 \times \text{warmth}$$
$$\text{FinalEyeContact} = \text{BaseEyeContact} \times (0.8 + 0.2 \times \text{trust})$$

- ➔ **동일한 대화 입력이라도 사용자와 쌓아온 신뢰와 친밀도에 따라 표정과 눈빛이 완전히 다르게 반응**합니다.
