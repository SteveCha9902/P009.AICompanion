# Avatar System

Companion의 시각적 형태를 표현하는 시스템입니다. 

## 1. Avatar Architecture
초기 렌더러는 2D/2.5D(Live2D 또는 Spline 기반 등)로 시작하며 향후 3D로 교체 가능하도록 인터페이스를 추상화합니다.
```text
AvatarRenderer
    ├── 2DAvatarRenderer
    ├── 2.5DAvatarRenderer
    └── Future3DAvatarRenderer
```

## 2. Animation Sync
Behavior Engine에서 도출된 Action과 Emotion State를 바탕으로 애니메이션을 재생합니다.
- **Expression**: Happiness(미소), Sadness(우울), Affection(따뜻함)
- **Gaze**: Vision System에서 전달된 `face_position`에 맞춰 눈동자/고개 추적
- **Lip Sync**: Voice(TTS) 출력 길이에 맞춘 입 모양 동기화 (초기엔 단순 개폐, 이후 음소 기반 확장)
