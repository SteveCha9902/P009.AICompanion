# Lip-Sync Architecture (LipSync_Architecture.md)

본 문서는 **P009.AICompanion Sprint 42**의 실시간 립싱크 엔진(LipSyncEngine V1) 및 발화 구현(Speech Embodiment) 파이프라인을 정의합니다.

---

## 1. 립싱크 아키텍처 핵심 파이프라인

```
[TTS Audio Stream]
        │
        ▼ (Audio Events: start, amplitude, viseme, end)
[Speech Timing Pipeline]
        │
        ▼ (SpeechParameters DTO)
[LipSyncEngine V1]
   ├── 1. Audio Amplitude ➔ Mouth Open Normalizer (0.0 ~ 1.0)
   ├── 2. Viseme Articulation Framework (A, E, I, O, U, CLOSED)
   ├── 3. Speech Smoothing (EMA Filter: No Jitter)
   └── 4. Speaking Micro Motion (Head Accent ±1.5°, Brow Accent)
        │
        ▼ (Target Render Parameters)
[RealtimeFaceRenderer (60 FPS Native Driver)]
```

---

## 2. 립싱크 스무딩 (Speech Smoothing Filter)

입모양이 오디오 진폭 노이즈로 인해 부자연스럽게 떨리는 지터(Jitter) 현상을 방지하기 위해 **지수 이동 평균(Exponential Moving Average, EMA)** 필터를 적용합니다:

$$\text{MouthOpen}_{t} = \alpha \cdot \text{RawAmplitude}_{t} + (1 - \alpha) \cdot \text{MouthOpen}_{t-1}$$

- **보간 계수 ($\alpha$)**: `0.45` (빠른 발화 반응성과 부드러운 전이의 최적 밸런스)
- **개폐 전환 속도**: 열림 시 `60ms`, 닫힘 시 `90ms` 감쇠 커브.

---

## 3. 5대 대표 모음 Viseme 매핑 규격

| Viseme | 조음 형태 | 가중치 및 모양 |
| :--- | :--- | :--- |
| `A` | 상하 개방형 | `scaleY: 1.4, scaleX: 1.0` (치아 보임) |
| `E` | 자연스러운 중립 개방 | `scaleY: 1.2, scaleX: 1.1` |
| `I` | 좌우 확장형 | `scaleY: 1.05, scaleX: 1.3` (입꼬리 당김) |
| `O` | 원형 개방형 | `scaleY: 1.35, scaleX: 0.85` (동그랗게 모임) |
| `U` | 축소 원형 돌출형 | `scaleY: 1.15, scaleX: 0.75` |
| `CLOSED` | 완전 폐쇄형 | `scaleY: 1.0, scaleX: 1.0` |

---

## 4. 말하는 동안의 미세 동작 (Speaking Micro Motion)

- **Head Accent**: 문장의 강조 지점마다 고개 상하 미세 끄덕임 (`headPitch: ±1.5°`).
- **Eyebrow Accent**: 활기찬 발화 시 눈썹 미세 상승 (`browRaise: +0.15`).
- **Rhythmic Gaze**: 사용자 시선 유지율 90% 유지 + 간헐적 시선 미세 이동.
