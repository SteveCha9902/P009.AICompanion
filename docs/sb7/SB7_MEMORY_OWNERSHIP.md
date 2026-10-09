# [SB-7 Architecture 2] Memory Ownership & Security Model

- **작성자**: 🔐 방대장 (DevOps/Security) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-01
- **스프린트**: SB-7 Character Memory Isolation & Independent Experience System

---

## 1. 2-Tier Ownership Key (`user_id`, `companion_id`)

모든 메모리 엔티티는 다음 소유권 키를 강제합니다:
- **`user_id`**: 메모리를 소유한 사용자 계정 ID
- **`companion_id`**: 메모리가 속한 고유 컴패니언 인격체 ID

---

## 2. 권한 검증 규칙

- 다른 사용자의 메모리에 접근 시도 시: `403 Forbidden` (`PermissionError`).
- 동일 사용자의 다른 캐릭터 메모리에 접근 시도 시: `Zero Results` 또는 `Access Blocked`.
- `companion_id` 없는 메모리 저장 시도: `ValueError` 발생 및 저장 차단.
