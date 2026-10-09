# [SB-12 Audit 4] Presentation Pipeline & Voice/Avatar Binding Audit

- **작성자**: 🌸 진달래 (Vision/Presentation Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-02
- **스프린트**: SB-12 Multi-Character Companion Orchestration & End-to-End Scope Integrity

---

## 1. Presentation Command Scope Binding

```text
PresentationCommand(
    interaction_id=interaction_id,
    companion_id=canonical_companion_id,
    voice_profile=pinned_voice,
    avatar_binding=pinned_avatar,
    expression=resolved_expression,
    gestures=active_gestures
)
```

- **누수 방지 검증**:
  - Genie 요청 처리 중 사용자가 Mani로 스위칭하더라도, Genie 요청의 응답 이벤트와 SSE Avatar State에는 Genie의 음성/아바타 바인딩(`warm_wife_2d` / `nova`)이 유지되며, Mani의 프레젠테이션 파이프라인과 혼선되지 않음.
