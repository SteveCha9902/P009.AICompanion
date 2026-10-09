# Relationship System

사용자와 AI Companion 간의 장기적인 유대 관계를 모델링하는 엔진입니다. 단순 상호작용 횟수뿐만 아니라 질적 요소를 고려합니다.

## 1. Relationship Levels
관계의 깊이를 나타내는 초기 7단계 모델:
0. Stranger (낯선 사람)
1. Acquaintance (지인)
2. Familiar (친숙한)
3. Friend (친구)
4. Close Friend (친한 친구)
5. Companion (동반자)
6. Deep Companion (깊은 유대)

## 2. State Properties
관계 레벨 외에 다음과 같은 세부 지표를 갖습니다.
- `trust`: AI에 대한 사용자의 신뢰도 추정치
- `familiarity`: 상호 인지 빈도
- `affection`: 친밀감
- `interaction_count`: 누적 상호작용 횟수
- `last_interaction`: 마지막 활성화 타임스탬프

## 3. Impact on Persona & Behavior
관계가 깊어질수록 Companion의 행동이 진화합니다.
- **Speaking Style**: 존댓말에서 자연스러운 반말/친근한 톤으로 변화 가능
- **Memory Usage**: 과거 사소한 일화까지 끄집어내어 대화에 활용
- **Initiative**: 먼저 질문하거나 대화를 유도(Ambient Mode Notification)하는 빈도 증가
