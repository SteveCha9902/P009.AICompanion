# [SB-8 Architecture 6] Voice & Avatar Factory Binding

- **작성자**: 🌸 진달래 (Vision/Presentation) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-01
- **스프린트**: SB-8 Character Creation Studio & Character Factory

---

## 1. Presentation Binding Pipeline

- `CharacterFactory`는 캐릭터 생성 시 SB-6 `CharacterPresentationProfileModel` 엔티티를 함께 생성하여 `(Voice, Avatar, Expression, Gesture)`의 1:1 관계를 데이터베이스에 원자적으로 저장합니다.
- 사용자가 선택한 `voice_id`(`shimmer`, `nova`, `alloy` 등)와 `avatar_preset`(`lovely_daughter_2d`, `warm_wife_2d` 등)이 프레젠테이션 프로필로 컴파일됩니다.
