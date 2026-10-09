# [SB-13 Audit 7] Cache Namespacing & Audit Event Logging Audit

- **작성자**: 🔐 방대장 (DevOps/Security) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-13 Controlled Shared Experience & Character-to-Character Information Sharing

---

## 1. Cache & Audit Event Standards

- **캐시 키 네임스페이스**:
  `p009:shared_experience:{user_id}:{character_id}`
- **감사 이벤트 로그 (Audit Event Bus)**:
  - `SHARE_PROPOSED`: 제안 접수
  - `SHARE_APPROVED`: 사용자/시스템 승인
  - `SHARE_DENIED`: 제안 거부
  - `SHARE_REVOKED`: 공유 철회
  - `SHARE_RETRIEVED`: 캐릭터에 의한 컨텍스트 조회
