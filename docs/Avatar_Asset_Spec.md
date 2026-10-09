# Avatar Asset Specification (Avatar_Asset_Spec.md)

본 문서는 **P009.AICompanion**의 실시간 캐릭터 렌더러(Real-Time Character Renderer) 및 Live2D 호환을 위한 아바타 자산 패키지 규격을 정의합니다.

---

## 1. 아바타 자산 유형 정의

- **캐릭터 이름**: Genie
- **자산 유형**: AI 생성 고해상도 포트레이트 기반 2.5D 레이어드 캐릭터 (Layered Digital Human)
- **표준 해상도**: 1024 x 1024 (모바일 2x/3x 레티나 최적화)
- **컬러 포맷**: 32-bit RGBA PNG (알파 채널 투명도 지원)

---

## 2. 필수 레이어 분리 구조 (Layer Stack)

아바타는 정적 비디오가 아닌 아래 7대 레이어의 실시간 알파 합성으로 렌더링됩니다:

```
[Layer 7] Facial Warmth / Blush Layer (Alpha Blend 0.0 ~ 1.0)
    ▲
[Layer 6] Mouth Viseme Layer (CLOSED, A, E, I, O, U)
    ▲
[Layer 5] Eye Layer (OPEN, HALF, BLINK) + Pupil Micro Gaze
    ▲
[Layer 4] Eyebrow Layer (NORMAL, RAISED, FURROWED)
    ▲
[Layer 3] Head Transform Layer (Pitch ±10°, Yaw ±10°, Roll ±10°, Breathing Scale)
    ▲
[Layer 2] Base Portrait Layer (Body, Shoulders, Neck, Static Face Silhouette)
    ▲
[Layer 1] Aura / Glow Background Layer (Dynamic Color Glow by State)
```

---

## 3. 실시간 제어 파라미터 규격 (Parameter Schema)

| 파라미터명 | 타입 / 범위 | 기본값 | 설명 |
| :--- | :--- | :--- | :--- |
| `eye_openness` | Float (0.0 ~ 1.0) | 1.0 | 눈의 열림 정도 (1.0 = 완전 뜸, 0.0 = 깜빡임) |
| `blink` | Float (0.0 ~ 1.0) | 0.0 | 눈 깜빡임 가중치 (2~7초 주기 자동 생성) |
| `brow_raise` | Float (-1.0 ~ 1.0) | 0.0 | 눈썹 위치 (-1: 찡그림, 0: 평온, +1: 놀람/집중) |
| `smile_strength` | Float (0.0 ~ 1.0) | 0.0 | 입꼬리 및 눈웃음 강도 (0: 무표정, 1.0: 활짝 웃음) |
| `mouth_open` | Float (0.0 ~ 1.0) | 0.0 | 음성 진폭에 따른 입 벌림 정도 |
| `viseme` | Enum (`CLOSED`, `A`, `E`, `I`, `O`, `U`) | `CLOSED` | 실시간 발화 음소에 따른 입모양 형태 |
| `head_pitch` | Float (-10.0 ~ 10.0°) | 0.0 | 고개 끄덕임 / 상하 각도 |
| `head_roll` | Float (-10.0 ~ 10.0°) | 0.0 | 고개 갸우뚱 / 좌우 기울기 |
| `warmth` | Float (0.0 ~ 1.0) | 0.5 | 친밀도 및 볼 붉어짐(Blush) 강도 |
| `breathing_scale` | Float (0.98 ~ 1.02) | 1.0 | 4.5초 주기 유기체 호흡 펄스 |

---

## 4. 음소 ➔ Viseme 매핑 규칙

| 한국어 모음 / 음소 | 대응 Viseme | 입 모양 형태 |
| :--- | :--- | :--- |
| 침묵, 자음 (ㅁ, ㅂ, ㅍ) | `CLOSED` | 입 다문 상태 |
| ㅏ, ㅑ, ㅐ, ㅔ | `A` | 상하로 크게 열린 형태 |
| ㅓ, ㅕ | `E` | 자연스럽게 열린 중립 형태 |
| ㅣ, ㅟ | `I` | 좌우로 넓게 벌려진 형태 |
| ㅗ, ㅛ | `O` | 동그랗게 모인 형태 |
| ㅜ, ㅠ, ㅡ | `U` | 작고 둥글게 내민 형태 |

---

## 5. 자산 패키지 디렉터리 레이아웃
```
mobile/assets/avatar/
├── portrait_base.png         # 고해상도 기본 신체/얼굴 베이스
├── eyes_open.png             # 눈 뜬 상태
├── eyes_half.png             # 게슴츠레 / 생각하는 눈
├── eyes_closed.png           # 눈 감은 상태 (깜빡임용)
├── mouth_closed.png          # 기본 닫힌 입
├── mouth_viseme_a.png        # 모음 A 입모양
├── mouth_viseme_e.png        # 모음 E 입모양
├── mouth_viseme_i.png        # 모음 I 입모양
├── mouth_viseme_o.png        # 모음 O 입모양
├── mouth_viseme_u.png        # 모음 U 입모양
├── eyebrow_normal.png        # 기본 눈썹
├── eyebrow_raised.png        # 올려진 눈썹
└── facial_blush.png          # 볼 터치 / 따뜻함 레이어
```
