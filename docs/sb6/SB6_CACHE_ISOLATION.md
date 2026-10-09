# [SB-6 Architecture 6] Presentation Cache Isolation & Invalidation

- **작성자**: 🔐 방대장 (DevOps/Security) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-01
- **스프린트**: SB-6 Character Presentation Identity & Profile Binding

---

## 1. 캐시 격리 키 표준

- **금지 패턴**: `presentation:{user_id}` (Cross-character 누수 유발)
- **표준 패턴**: `presentation:{user_id}:{companion_id}`
  - 예: `presentation:user_01:genie_pk`, `presentation:user_01:mani_pk`, `presentation:user_01:hana_pk`

---

## 2. Invalidation 트리거

- `PATCH /api/v1/characters/{companion_id}/presentation` 호출 성공 시
- `POST /api/v1/characters/{companion_id}/archive` 및 `DELETE` 시
- `CharacterPresentationResolver.invalidate(user_id, companion_id)`를 즉시 호출하여 구버전 캐시 삭제.
