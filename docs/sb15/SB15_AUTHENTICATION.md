# [SB-15 Audit 4] Authentication & Authoritative User Identity

- **작성자**: 🔐 방대장 (DevOps/Security Lead) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-15 Production Deployment & Multi-User Server

---

## 1. Authoritative Identity Pipeline

```text
HTTP Request (Header: Authorization: Bearer <JWT_TOKEN>)
       │
[ Auth Middleware / JWT Decoder ] ➔ Verified user_id: 'user_A'
       │
[ Multi-Tenant Scope Binding ]
Client requested companion_id: 'genie_pk'
       │
[ Ownership Verification Check ]
Query: SELECT * FROM companions WHERE id='genie_pk' AND user_id='user_A'
   - Found: PROCEED (CharacterScope(user_A, genie_pk))
   - Not Found / Belongs to user_B: 403 FORBIDDEN / FAIL CLOSED
```

- **클라이언트 입력 신뢰 금지**:
  - 클라이언트 body의 `user_id`를 신뢰하지 않고, 반드시 검증된 JWT 토큰에서 추출한 `user_id`를 Authoritative Identity로 강제 바인딩.
