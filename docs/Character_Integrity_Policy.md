# Character Integrity & Drift Prevention Policy (Sprint 54) — 방대장 보안관

본 문서는 장기적인 상호작용 속에서 캐릭터의 성격적 정체성이 변질되지 않도록 모니터링하고 복원하는 정책을 정의합니다.

---

## 🛡️ 1. Personality Drift Monitoring & Clamping Rules

1. **50-Turn Moving Window Analysis**:
   - 대화 턴마다 표현된 성격 수치(Warmth, Humor, Empathy 등)를 50턴 이동평균으로 추적.
2. **Drift Threshold ($\pm 0.20$)**:
   - 이동평균이 기준 `CharacterDNA`로부터 0.20 이상 벗어날 경우(예: 유머가 0.35에서 0.75로 급상승), 즉시 기준 DNA로 당겨주는 고정 닻(Anchor Clamping)을 발동.
3. **Cross-Session Storage Safety**:
   - `CharacterDNA`는 시스템 레벨의 보호를 받으며 임의의 악의적 프롬프트 주입(Prompt Injection)으로 영구 수정되지 않음.
