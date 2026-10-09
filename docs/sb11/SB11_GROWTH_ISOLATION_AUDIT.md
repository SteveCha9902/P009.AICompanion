# [SB-11 Audit 4] Growth & Behavioral Adaptation Isolation Audit

- **작성자**: 🐟 코다리 (Lead Architect) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-11 Multi-Character Dynamic State Isolation & Concurrency Safety

---

## 1. Character Growth & Adaptation Scope

```text
UserRelationshipAdaptationModel (UNIQUE: user_id + companion_id)
RelationshipMilestoneModel (user_id + companion_id)
```

- **격리 검증**:
  - Genie가 습득한 사용자 대화 선호도(예: `preferred_humor`, `preferred_directness`)는 Mani의 성장/적응 모델에 복제되거나 유입되지 않음.
  - 마일스톤(`RelationshipMilestoneModel`) 역시 캐릭터별로 완벽히 독립 기록됨.
