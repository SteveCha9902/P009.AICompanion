# Personality Vector Specification (Sprint 54)

본 문서는 캐릭터 고유의 성격을 규정하는 `CharacterDNA` 및 멀티모달 표출 DTO `CrossModalPersonalityManifest` 규격을 기술합니다.

---

## 🧬 1. CharacterDNA 7-Axis Vector

```typescript
interface CharacterDNA {
  warmth: number;       // 0.0 ~ 1.0 (따뜻함, 다정함, 친절도: Default 0.92)
  humor: number;        // 0.0 ~ 1.0 (위트, 유머, 장난기: Default 0.35)
  curiosity: number;    // 0.0 ~ 1.0 (호기심, 지적 탐구심: Default 0.80)
  empathy: number;      // 0.0 ~ 1.0 (공감 능력, 배려: Default 0.95)
  playfulness: number;  // 0.0 ~ 1.0 (명랑함, 발랄함: Default 0.30)
  formality: number;    // 0.0 ~ 1.0 (격식, 정중함: Default 0.30)
  optimism: number;     // 0.0 ~ 1.0 (낙관성, 긍정성: Default 0.85)

  companionId: string;
  version: number;
}
```

---

## 📦 2. CrossModalPersonalityManifest DTO

```typescript
interface CrossModalPersonalityManifest {
  // 1. LLM Prompt Directives
  toneDescription: string;
  keyPhraseGuidance: string;

  // 2. TTS Voice Parameters
  speechRate: number;              // 0.90 ~ 1.08
  speechPitch: number;             // 0.98 ~ 1.05
  smileVoiceIntensity: number;     // 0.0 ~ 1.0 (Warmth x 0.9)
  pauseDurationScale: number;      // Calm mode: 1.15

  // 3. Avatar Physical Modulators
  smileWeightBoost: number;        // Warmth x 0.35
  headTiltFrequency: number;       // Curiosity x 0.40
  breathingStability: number;      // 0.95
}
```
