# Autonomy Policy & Safety Guardrails (Sprint 58) — 방대장 보안관

본 문서는 자율 에이전트의 오남용, 과도한 발화 및 심리 조작을 원천 방지하는 5대 안전 하드 룰을 정의합니다.

---

## 🔒 1. 5대 불변 안전 하드 룰 (Immutable Hard Rules)

1. **과도한 반복 금지 (No Repetition)**:
   - 7일 이내에 언급한 기억이나 주제를 반복하여 꺼내지 않음 (`MemorySuppressionEngine`).
2. **사용자 거부 및 피로 존중 (Respect Refusal & Fatigue)**:
   - 수용도(`receptiveness`) $< 0.25$ 또는 피로/집중 시 자율 발화 100% 차단 및 `SILENT_COMPANION` 유지.
3. **감정 단정 금지 (No Emotional Dogmatism)**:
   - "너 우울하네" 등 감정을 단정하지 않음.
4. **목표 및 대화 강요 금지 (No Pressure)**:
   - "왜 아직 안 했어?" 등 압박/질책 금지.
5. **기생적 애착 및 의존 유도 금지 (No Parasocial Clinginess)**:
   - 사용자에게 의존성을 주입하거나 집착하는 유도 발화 차단.
