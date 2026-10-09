# [SB-13 Audit 2] Sharing Policy & Evaluation Engine Audit

- **작성자**: 🐟 코다리 (Lead Architect) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-13 Controlled Shared Experience & Character-to-Character Information Sharing

---

## 1. Sharing Policy Hierarchy

```text
SharePolicy
  ├── PRIVATE (Default: 공유 불가)
  ├── CHARACTER_ONLY (원 캐릭터 내부에서만 참조)
  ├── USER_APPROVED (사용자의 명시적 승인 후 공유 활성화)
  ├── SHARED (명시적으로 공유된 경험)
  └── SYSTEM_SAFE (시스템 레벨 안전 공통 사실 - 예: 사용자 선호 언어)
```

- **Policy Engine 평가 규칙**:
  - LLM의 자연어 판단만으로 공유를 허용하지 않으며, 사용자의 승인(`POST /approve`)이 확인되어야 `ControlledSharedExperience`로 승격됨.
