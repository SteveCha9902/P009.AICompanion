# Focus Target & Gaze Alignment Guide (Sprint 49)

본 문서는 사물 인식 및 사용자 발화에 따라 아바타의 시선(Gaze)과 고개 각도(Pitch/Roll)가 동기화되는 원리와 앵커 매핑 가이드를 기술합니다.

---

## 👁️ 1. Gaze & Head Tilt Synchronization Matrix

| Focus Target | Attention Anchor | Head Pitch | Head Roll | Avatar Gaze Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **USER_FACE** | `USER_FACE` | `0.0°` | `0.0°` | 사용자의 눈을 정면으로 부드럽게 응시 (기본 깜빡임 루프) |
| **CUP** | `LOWER_RIGHT` | `+3.5°` | `+2.0°` | 우측 하단 컵을 살짝 내려다보며 호기심 어린 고개 기울임 |
| **BOOK / PET** | `LOWER_LEFT` | `+3.5°` | `-2.0°` | 좌측 하단 책이나 반려동물을 다정하게 응시 |
| **LAPTOP** | `LOWER_CENTER` | `+4.0°` | `+0.5°` | 중앙 하단 화면/키보드 작업을 집중하여 바라봄 |
| **PLANT / WINDOW** | `UPPER_RIGHT` | `-2.5°` | `+1.5°` | 우측 상단 화분이나 창가 풍경을 편안하게 올려다봄 |
| **TV / MONITOR** | `UPPER_LEFT` | `-2.5°` | `-1.5°` | 좌측 상단 모니터를 바라보며 함께 몰입 |

---

## ⏱️ 2. Focus Lock & Inactivity Timeout 규칙
1. **Focus Lock (6초)**:
   - 사용자가 대상을 가리키거나 시선이 형성되면 6초간 시선 위치가 고정됩니다.
   - 주변의 다른 객체(지나가는 그림자 등)로 인해 시선이 1초 만에 튀는 현상(Gaze Twitching)을 방지합니다.
2. **Inactivity Timeout (15초)**:
   - 15초 동안 추가적인 언급이나 상호작용이 없으면 자동으로 `USER_FACE`(정면 응시)로 복귀합니다.
3. **Wrong Focus Recovery (즉시 복구)**:
   - 사용자가 "아니 책이야"라고 수정하면 6초 락이 즉시 해제되고 2초 내에 책(`LOWER_LEFT`)으로 시선이 재정렬됩니다.
