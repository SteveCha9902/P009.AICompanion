# Behavior System

단순히 질문(Query)에 답(Response)하는 것을 넘어 상황에 맞는 주도적 행동을 선택하는 엔진입니다. 향후 자율형(Autonomous) Companion의 기반이 됩니다.

## 1. Trigger Events
사용자의 텍스트 입력 외에도 다음과 같은 이벤트가 행동의 트리거가 됩니다.
- 사용자의 침묵 (User Silent)
- 앱 화면으로 돌아옴 (User Returns)
- 카메라에 사용자 인식됨 (Camera detects user)
- 내부 감정 상태의 급격한 변화 (Emotion Spike)
- 연관된 과거 중요 기억의 Recall

## 2. Action Selection
`Companion State`를 바탕으로 `Behavior Interpreter`가 적절한 `Action`을 결정합니다.
```text
Event: User silent for 30s + Attention High 
-> Action: "무슨 생각 해요?" (Initiate conversation)

Event: Emotion transitions to Happiness 80+
-> Action: Trigger "Smile" animation + Look at user
```

## 3. Avatar Behavior Pipeline
생성된 Action은 UI 레이어로 전달되어 아바타 렌더링에 반영됩니다. LLM의 텍스트 생성과 아바타 애니메이션(Expression, Gaze 등)이 동기화되도록 Presentation Layer와 분리되어 설계됩니다.
