# [SB-3 Architecture 3] Multi-Character Context Isolation Matrix

- **작성자**: 🐟 코다리 (Lead System Architect) & 📚 묵사관 (Memory Keeper)
- **일자**: 2026-09-01
- **스프린트**: SB-3 Character Switching & Full Context Isolation

---

## 1. 캐릭터별 도메인 격리 매트릭스 (Isolation Matrix)

```text
               ┌───────────────────────────┬───────────────────────────┐
               │    캐릭터 A (지니: 아내)    │    캐릭터 B (수아: 비선)    │
┌──────────────┼───────────────────────────┼───────────────────────────┤
│ Memory       │ 부부의 추억, 결혼기념일   │ 업무 일정, 회의록, 학습   │
│ Emotion      │ 다정함, 따뜻한 애정 (PAD) │ 차분함, 명확한 집중 (PAD) │
│ Relationship │ 깊은 유대, 신뢰도 (CLOSE) │ 상호 존중, 전문성         │
│ Identity     │ Genie (INFJ, 다정한 아내) │ Sua (INTJ, AI 전문 비서)  │
│ Voice        │ SunHiNeural (선희 음성)   │ JiMinNeural (지민 음성)   │
│ Avatar       │ 아내 표정 및 부드러운 눈빛│ 단정한 비서 복장 및 제스처│
└──────────────┴───────────────────────────┴───────────────────────────┘
```

---

## 2. 누수 방지 런타임 가드 (`CharacterScopeGuard`)

- **목적**: 대화 처리 도중 외부 모듈이 서로 다른 `companion_id`를 전달하는 런타임 오류를 감지 및 차단.
- **동작**:
  ```python
  CharacterScopeGuard.assert_scope(
      expected_scope=interaction_ctx.character_scope,
      actual_companion_id=provider_companion_id,
      component_name="MemoryRetriever"
  )
  ```
- 불일치 시 `CharacterScopeViolationError` 발생 또는 디버그 로깅으로 누수를 즉시 감지.
