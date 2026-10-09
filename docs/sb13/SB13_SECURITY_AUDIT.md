# [SB-13 Audit 5] Security, Ownership & Dynamic State Protection Audit

- **작성자**: 🔐 방대장 (DevOps/Security) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-13 Controlled Shared Experience & Character-to-Character Information Sharing

---

## 1. Zero Direct State Mutation Principle

```text
Genie ➔ Share Proposal ➔ Policy Engine ➔ Shared Experience ➔ Mani LLM Context
  ❌ NO: Genie ➔ Mani Emotion +1
  ❌ NO: Genie ➔ Mani Relationship +1
  ❌ NO: Genie ➔ Mani Growth +1
  ❌ NO: Genie ➔ Mani Agency Task
```

- **보안 격리 표준**:
  - 공유 경험이 생성되거나 조회되더라도 대상 캐릭터의 Emotion, Relationship, Growth, Agency 등의 동적 상태는 일체 직접 변조되지 않으며, 각 캐릭터가 독립적으로 인지/해석함.
  - User A의 공유 경험은 User B에게 절대 노출되지 않는 테넌트 격리(`user_id` 일치성) 보장.
