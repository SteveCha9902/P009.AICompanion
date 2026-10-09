# [SB-1 Audit 6] Presentation Layer (Voice & Avatar) Audit

- **작성자**: 🌸 진달래 (Vision & Avatar Lead) & ✍️ Amy (Growth & Marketing)
- **일자**: 2026-09-01
- **스프린트**: SB-1 Character Runtime Foundation

---

## 1. 음성(Voice) 및 아바타(Avatar) 파이프라인 분석

### 1.1 Voice Pipeline Audit
- **현행 구조**:
  - `domain/voice/voice_profile.py`에 `VoiceProfile`이 정의되어 있으나, `VoiceService` 및 기본 설정에서 `genie_warm_v1` / `ko-KR-SunHiNeural` 고정 프리셋을 참조하는 경향이 있음.
- **SB-1 정렬 조치**:
  - `CharacterRuntimeContext.voice_profile`을 도입하여, 향후 캐릭터별 고유 Voice ID(예: 수아 `ko-KR-JiMinNeural`, 하나 `ko-KR-InJoonNeural`)를 동적으로 주입받을 수 있는 인터페이스 경계 확립.

### 1.2 Avatar Pipeline Audit
- **현행 구조**:
  - `db/models/avatar.py`의 `AvatarProfile`은 이미 `companion_id`를 외래키(1:1 Unique)로 가지고 있음.
  - `AvatarStateResolver.resolve(companion_id)`는 전달받은 `companion_id`를 기준으로 표정 및 애니메이션 파라미터를 정상 분기하고 있음.
- **SB-1 정렬 조치**:
  - `CharacterRuntimeContext.avatar_profile`에 아바타 설정을 포함하여 런타임에서 즉시 참조 가능하도록 바인딩.

---

## 2. 4대 핵심 질문 답변

| 핵심 질문 | 현황 및 진단 결과 |
| :--- | :--- |
| **Voice가 User에 귀속되는가?** | 아니오. Voice는 Character(Companion)의 고유 음성 정체성입니다. |
| **Voice가 Companion에 귀속되는가?** | **예. Companion별 Voice Profile로 귀속됩니다.** |
| **Global Configuration인가?** | 기본 fallback 프로필이 존재하지만, Companion별 개별 설정이 가능하도록 설계됩니다. |
| **Avatar는 어떤 Entity와 연결되는가?** | **`companion_id`에 1:1로 직결**되어 있습니다. |
