# [SB-10 Audit 5] Cognitive Scope Flow & Context Injection Integrity

- **작성자**: 🐟 코다리 (Lead Architect) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-10 Multi-Character Memory Isolation & RAG Anti-Leakage

---

## 1. End-to-End Cognitive Scope Tracing

```text
User Request (POST /chat)
      │
      ▼
CharacterContextResolver (resolves companion_id)
      │
      ▼
MemoryRetriever (filters companion_id = Active)
      │
      ▼
CharacterMemoryGuard (validates retrieved memories scope)
      │
      ▼
ContextBuilder (injects ACTIVE_CHARACTER memory scope ONLY)
      │
      ▼
LLM Generation
      │
      ▼
Memory Extraction & Persistence (stores under companion_id = Active ONLY)
```
