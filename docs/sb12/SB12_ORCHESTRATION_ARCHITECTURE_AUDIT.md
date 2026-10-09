# [SB-12 Audit 1] Orchestration Architecture & End-to-End Scope Integrity Audit

- **작성자**: 🐟 코다리 (Lead System Architect) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-12 Multi-Character Companion Orchestration & End-to-End Scope Integrity

---

## 1. End-to-End Orchestration Pipeline

```mermaid
graph TD
    Request[User Interaction Request] --> Resolver[CharacterContextResolver]
    Resolver --> ScopePinning[Scope Pinning: CharacterScope + InteractionContext]
    ScopePinning --> Snapshot[Character Runtime Snapshot Fixed]
    
    Snapshot --> Cognition[1. Cognition: Memory/RAG + ContextBuilder + LLM]
    Snapshot --> DynamicState[2. Dynamic State: Emotion + Relationship + Growth + Agency]
    Snapshot --> Presentation[3. Presentation: Voice Binding + Avatar Profile + LipSync]
    
    Cognition --> Commit[4. Scoped State Commit: interaction_id + companion_id]
    DynamicState --> Commit
    Presentation --> Emit[5. Final SSE / Voice Response Emit]
```

- **절대 불변 원칙**:
  - 요청 진입 시 생성된 `CompanionInteractionContext`는 불변(Immutable)이며, 전체 파이프라인에서 `activeCharacter`를 중간에 재조회하지 않고 Pinned Scope를 끝까지 유지함.
