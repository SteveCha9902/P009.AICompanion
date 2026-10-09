# Voice Profile & Speech Style Specification (Voice_Profile_Spec.md)

**문서 버전**: v1.0 DTO Specification  
**작성자**: 🐟 코다리 Architect  
**일자**: 2026-08-30

---

## 1. 4대 보이스 페르소나 카탈로그 (Voice Personas)

| Persona Type | 대상 보이스 ID | 기본 톤 & 음향 특성 | 최적 용도 |
| :--- | :--- | :--- | :--- |
| **`WARM_COMPANION`** | `genie_warm_v1` (nova) | 따뜻한 공명, 포근한 미소 톤, 높은 공감도 (Warmth: 0.92, Empathy: 0.95) | **Genie 기본 컴패니언 음성** |
| **`CALM_MENTOR`** | `mentor_calm_v1` (onyx) | 차분하고 안정된 저음, 깊은 신뢰감 (Confidence: 0.90, Pitch: -2.0) | 조언, 사색, 멘토링 세션 |
| **`ENERGETIC_GUIDE`** | `guide_spark_v1` (shimmer) | 밝고 경쾌한 하이톤, 높은 활력 (Energy: 0.90, Pitch: +2.5) | 동기부여, 피트니스, 축하 |
| **`PROFESSIONAL_ADVISOR`** | `advisor_pro_v1` (alloy) | 명확한 발음, 정중한 템포 (Confidence: 0.95, Rate: 1.02) | 업무 분석, 정보 전달 |

---

## 2. SpeechStyleParameters DTO 스펙

```typescript
interface SpeechStyleParameters {
  speakingRate: number;      // 0.5 ~ 2.0 (1.0 = 표준 템포)
  pitchOffset: number;       // -12.0 ~ +12.0 (반음 단위)
  volumeGainDb: number;      // -20.0 ~ +10.0 dB
  energy: number;            // 0.0 ~ 1.0
  warmth: number;            // 0.0 ~ 1.0
  pauseMultiplier: number;   // 0.5 ~ 2.5 (문장 간 호흡/쉼표 길이)
  ssmlStyle?: string;        // "cheerful", "empathetic", "warm", "formal", "chat"
  emphasisWords: string[];   // 발화 강조 키워드
}
```
