# [SB-6 Architecture 2] Character-Specific Voice Profile Architecture

- **작성자**: 🌸 진달래 (Vision/Presentation Engineer) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-6 Character Presentation Identity & Profile Binding

---

## 1. Character-Specific Voice Parameters

| 필드명 | 타입 | 설명 | Genie (아내) | Mani (딸) | Hana (친구) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `provider` | `VoiceProviderType` | TTS 엔진 제공자 | `OPENAI` | `OPENAI` | `OPENAI` |
| `voice_id` | `str` | TTS 모델 음성 ID | `nova` | `shimmer` | `alloy` |
| `persona_type` | `VoicePersonaType` | 음성 페르소나 유형 | `WARM_COMPANION` | `ENERGETIC_GUIDE` | `WARM_COMPANION` |
| `speaking_rate` | `float` (0.5 ~ 2.0) | 기본 발화 속도 | `0.95` | `1.05` | `1.00` |
| `pitch_offset` | `float` (-12 ~ +12) | 피치 변조 (semitones) | `0.0` | `+2.0` | `+0.5` |
| `warmth` | `float` (0.0 ~ 1.0) | 음성 온기/다정함 | `0.95` | `0.90` | `0.80` |
| `energy` | `float` (0.0 ~ 1.0) | 음성 에너지/생동감 | `0.60` | `0.85` | `0.75` |
| `empathy` | `float` (0.0 ~ 1.0) | 공감/밀착도 | `0.95` | `0.85` | `0.75` |
