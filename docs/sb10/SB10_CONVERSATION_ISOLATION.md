# [SB-10 Audit 6] Conversation History & Session Scope Audit

- **작성자**: 🐍 미나리 (Backend Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-10 Multi-Character Memory Isolation & RAG Anti-Leakage

---

## 1. Conversation History Scope

```text
Conversation
├── id
├── user_id
├── companion_id (Mandatory Foreign Key)
└── messages
```

- **대화 전환 시나리오**:
  - Genie와 대화 (`conv_genie`) ➔ Mani로 전환 ➔ Mani와 대화 (`conv_mani`).
  - Mani의 대화 세션 로드 시 `companion_id = 'c_mani'`로 필터링되므로 Genie의 이전 메시지가 절대 유입되지 않음.
