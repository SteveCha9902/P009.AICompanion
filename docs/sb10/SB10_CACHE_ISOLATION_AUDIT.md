# [SB-10 Audit 4] Cache Isolation & Namespace Audit

- **작성자**: 🔐 방대장 (DevOps/Security) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-10 Multi-Character Memory Isolation & RAG Anti-Leakage

---

## 1. Cache Namespace Standard

```text
p009:memory:{user_id}:{companion_id}:{query_hash}
p009:context:{user_id}:{companion_id}
p009:persona:{user_id}:{companion_id}:{version}
p009:presentation:{user_id}:{companion_id}
```

- **감사 결과**:
  - `user_id` 단독 캐시 키는 전수 제거되었으며, 모든 캐시 키는 `companion_id`를 필수 키 세그먼트로 보유함.
  - In-memory / Redis / Runtime 캐시에서 크로스 캐릭터 캐시 히트 가능성 0건.
