# Sprint 6: Relationship Engine Architecture

> 이 문서는 Sprint 6 시작 전 최종 확정된 Relationship Engine의 핵심 아키텍처 원칙을 담고 있습니다.

## 1. Relationship → Behavior Layer
Relationship State(숫자)를 직접 LLM Prompt에 전달하지 않습니다. 반드시 다음 계층을 거칩니다:
`Relationship State → Behavior Policy → Behavior Modifier → Context Builder → LLM`
- 예: High Familiarity → reduce repetitive explanations, reference relevant shared history.
- 예: High Trust → allow more direct feedback.

## 2. Relationship Direction
Sprint 6에서는 "Companion-side relationship state"로 한정합니다. 즉, Companion이 User와의 상호작용을 통해 형성하고 평가한 관계 상태입니다. 

## 3. Signal Severity (Impact)
단순한 Signal이 아닌, Severity/Impact(`LOW`, `MEDIUM`, `HIGH`, `CRITICAL` 또는 `0.0~1.0`) 개념을 추가합니다. 
사소한 API 실패(LOW)와 중요한 사용자 기억 망각(MEDIUM/HIGH)이 관계에 미치는 타격을 다르게 취급합니다.

## 4. Relationship as Learned Interaction
단순히 "좋은 행동 = +점수"가 아니라, Interaction History에서 **학습(Learned)되는 상태**입니다.
예를 들어, 사용자가 짧은 답변을 요구했고 Companion이 이에 성공적으로 적응(Adaptation)했다면, 이는 Reliability와 Trust, Familiarity의 상승으로 이어집니다.

## 5. Relationship Level Calculation
5개 Dimension의 단순 평균이 아닙니다.
- **주요 기준**: `Trust`, `Familiarity`, `Closeness`
- **Activity 기준**: `Engagement`는 현재의 상호작용 활성도를 나타내는 별도 차원으로, Level 계산의 핵심 축에서 분리합니다.

## 6. Final Architecture Flow
`Interaction` → `Signal Extraction` → `Signal Validation` → `Relationship Policy` → `Relationship State Update` → `Relationship Behavior Policy` → `Behavior Modifier` → `Context Builder` → `LLM`

## 7. Final Cognitive Core 5대 요소
1. **Conversation**: What are we talking about now?
2. **Persona**: Who is the Companion?
3. **Memory**: What does the Companion know about the User?
4. **Emotion**: What is the Companion's current conversational state?
5. **Relationship**: How has the relationship with the User developed?
이 다섯 Domain은 서로 대체되거나 통합되지 않으며, 모두 독립적인 파이프라인으로 Context를 구성합니다.
