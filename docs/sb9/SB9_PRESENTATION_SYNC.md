# [SB-9 Architecture 6] Voice & Avatar Safety and Presentation Synchronization

- **작성자**: 🌸 진달래 (Vision/Presentation) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-01
- **스프린트**: SB-9 Multi-Character Mobile Studio & Real-Time Switching UX

---

## 1. Presentation Transition Safety

- **Voice Safety**:
  - 캐릭터 전환 트리거 즉시 이전 캐릭터의 TTS Audio 재생을 중단하고 오디오 큐를 즉시 플러시(`flushAudioQueue`)합니다.
  - 새 캐릭터의 Voice Profile(`shimmer`, `nova` 등)로 오디오 엔진이 안전하게 교체됩니다.
- **Avatar Safety**:
  - 전환 즉시 아바타 프리셋(`lovely_daughter_2d`, `warm_wife_2d` 등)이 리셋되며 이전 제스처/표정 글리치 없이 중립 상태에서 새 캐릭터 모션을 로드합니다.
