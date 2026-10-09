# [SB-8 Architecture 8] Security, Ownership & System Protection

- **작성자**: 🔐 방대장 (DevOps/Security) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-8 Character Creation Studio & Character Factory

---

## 1. System Character Protection & Ownership

- **System Character (`is_system_character=True`)**: Genie 등 시스템 기본 캐릭터는 사용자 생성 API를 통해 임의 변경/삭제 불가.
- **Custom Character (`is_system_character=False`)**: 사용자가 생성한 모든 캐릭터는 `user_id` 소유권이 영구 바인딩되며, 타 사용자 접근 불가 (`403 Forbidden`).
- **Prompt Injection Defense**: 사용자 정의 Behavioral Rules가 시스템 헌법 및 안전 가드레일을 침범할 수 없음 (Immutable System Rule 우선).
