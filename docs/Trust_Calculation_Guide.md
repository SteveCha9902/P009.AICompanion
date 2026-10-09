# Trust Calculation & Repair Guide (Sprint 55)

본 문서는 신뢰도(Trust)의 독립적 산출 공식, 품질 평가 지표 및 관계 회복(Relationship Repair) 메커니즘을 정의합니다.

---

## 📊 1. 턴 품질(Turn Quality) 및 신뢰도 증분 산출 공식

1. **상호작용 품질 평가 (`InteractionQualityAnalyzer`)**:
   - 발화 길이 > 25자: $+0.20$
   - 발화 길이 < 4자(단답형): $-0.15$
   - 진솔한 정서 표현 ($|\text{valence}| > 0.40$): $+0.20$
   - 시각적 현실 공유 객체 감지: $+0.10$
2. **신뢰도 증분 (`TrustCalculator`)**:
   $$\Delta \text{Trust} = (\text{TurnQuality} - 0.35) \times 0.015 + (\text{MemoryBonus: } 0.005)$$
   - 일일 최대 성장률 상한선(`0.05`) 적용.

---

## 🩹 2. 관계 회복 루프 (Relationship Repair Loop)

1. **관계 긴장(Strain) 발생 시**:
   - 비대칭 하락 적용 (Trust 및 Comfort가 $0.15 \sim 0.20$ 즉시 감소).
2. **점진적 회복 (Gradual Repair)**:
   - 긍정적인 상호작용($\text{Quality} > 0.50$)이 재개될 때마다 $+0.02 \sim +0.03$씩 조심스럽고 진솔하게 회복.
