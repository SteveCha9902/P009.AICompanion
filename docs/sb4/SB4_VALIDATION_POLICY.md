# [SB-4 Architecture 5] Character Validation Policy & Duplicate Prevention

- **작성자**: 🏃 정대리 (QA Lead) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-4 Character Creation Engine & Personality DNA Factory

---

## 1. 유효성 검증 규칙 (Validation Rules)

| 항목 | 검증 기준 | 위반 시 응답 |
| :--- | :--- | :--- |
| **Name** | 1~50자, 공백만으로 구성 금지, 특수문자 정규화 | `400 Bad Request` |
| **Duplicate Name** | 동일 유저(`user_id`) 내에서 동일 정규화 이름 존재 여부 검사 | `409 Conflict` |
| **MBTI** | 대소문자 무시 16종 표준 MBTI 매핑 검사 | `400 Bad Request` |
| **Template** | `CharacterTemplateRegistry`에 등록된 템플릿 여부 검사 | `400 Bad Request` |
| **Voice & Avatar** | 지원되는 Voice ID / Avatar Preset 검사 (기본값 지원) | 유효 기본값 자동 폴백 |

---

## 2. 이름 중복 정책 (Duplicate Name Policy)

- 동일 사용자가 동일한 이름의 캐릭터를 중복 생성할 경우 혼동 및 컨텍스트 충돌을 유발하므로, `409 Conflict`를 반환하여 이름 변경을 요구합니다.
