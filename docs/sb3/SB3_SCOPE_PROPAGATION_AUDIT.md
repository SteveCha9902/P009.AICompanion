# [SB-3 Architecture 2] Scope Propagation & Hidden Default Audit

- **작성자**: 🐍 미나리 (Backend Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-3 Character Switching & Full Context Isolation

---

## 1. 전 엔진별 Scope 파라미터 전달 전수 점검

| 인지/프레젠테이션 엔진 | 입력 단위 | Scope 전달 메커니즘 | 하드코딩 여부 | 판정 |
| :--- | :--- | :--- | :--- | :--- |
| **`MemoryRetriever`** | `companion_id` | `search_memories(companion_id, ...)` | 없음 | 격리 완비 ✅ |
| **`EmotionService`** | `companion_id` | `get_current_emotion(companion_id)` | 없음 | 격리 완비 ✅ |
| **`RelationshipService`** | `companion_id`, `user_id` | `get_state(companion_id, user_id)` | 없음 | 격리 완비 ✅ |
| **`AvatarStateResolver`** | `companion_id` | `resolve(companion_id)` | fallback 존재 | 격리 완비 ✅ |
| **`VoiceService`** | `runtime_context` | `voice_profile` 동적 바인딩 | fallback 존재 | 격리 완비 ✅ |
| **`AgencyActionLogger`** | `companion_id`, `user_id` | `log_action(user_id, companion_id, ...)` | 없음 | 격리 완비 ✅ |
| **`ContextBuilder`** | Providers (8 Tier) | `CharacterIdentityProvider(companion_id)` 등 | 없음 | 격리 완비 ✅ |
| **`InteractionTracer`** | `companion_id`, `user_id` | `InteractionTracer(..., companion_id)` | 없음 | 격리 완비 ✅ |

---

## 2. Hidden Default 처리 원칙

- 파이프라인 내부에서 `companion_id = "genie"` 또는 `"default_companion"`을 무조건 하드코딩으로 폴백하던 패턴을 배격하고,
- **`CharacterRegistryService.get_active_companion_id(user_id)` ➔ `Lazy Bootstrap` ➔ `Existing Genie PK`**의 단일 진실 출처 경로를 통해 일관되게 주입되도록 정렬 완료.
