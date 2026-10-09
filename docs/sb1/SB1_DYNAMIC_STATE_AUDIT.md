# [SB-1 Audit 5] Dynamic State Engine Audit

- **작성자**: 🐟 코다리 (Lead System Architect) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-1 Character Runtime Foundation

---

## 1. Dynamic Cognitive State 소유권 전수 조사

| 인지 상태 (Dynamic State) | Owner Entity | 저장 위치 (Storage) | 식별 Key | 수명주기 (Lifecycle) | 로드 시점 | 업데이트 시점 | 영속성 (Persistence) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Emotion** | Companion | `emotion_states` | `companion_id` (Unique) | 지속적 감쇠 및 전이 | ContextProvider 로드 시 | 상호작용 직후 | DB 영속 |
| **Relationship** | Companion + User | `relationship_states` | `companion_id`, `user_id` | 상호작용 누적 진화 | ContextProvider 로드 시 | 일치/위반 검증 시 | DB 영속 |
| **Growth** | Companion + User | `character_global_growth_states` / `user_relationship_adaptations` | `companion_id` / `(user_id, companion_id)` | 장기 적응형 학습 | ContextProvider 로드 시 | 주기적 배치/상호작용 후 | DB 영속 |
| **Agency** | Companion | `agency_action_logs` | `companion_id`, `user_id` | 백그라운드 주기 실행 | Agency 루프 실행 시 | 결정 및 행동 후 | DB Log 영속 |
| **Interaction** | Session | `InteractionStateMachine` | `interaction_id` / `companion_id` | 단일 대화 턴 수명 | 대화 시작 시 | 단계별 상태 전이 | 메모리 휘발 |

---

## 2. CharacterRuntimeState 설계 원칙

- `CharacterRuntimeState`는 각 엔진의 DB 상태를 대체하는 새로운 Source of Truth가 아닙니다.
- **역할**: 대화 실행 시점의 Dynamic Cognitive Snapshot 컨테이너 역할만 수행합니다.
```python
@dataclass
class CharacterRuntimeState:
    scope: CharacterScope
    emotion: Optional[Any] = None
    relationship: Optional[Any] = None
    growth: Optional[Any] = None
    agency: Optional[Any] = None
    interaction: Optional[Any] = None
```
