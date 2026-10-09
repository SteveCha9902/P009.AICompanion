# Emotion System

Companion의 감정 상태를 관리하는 엔진입니다. 랜덤하게 감정이 변하지 않으며 대화 내용과 상황에 의해 전이(State Transition)됩니다.

## 1. Emotion State Model
초기에는 0~100 사이의 숫자 값을 갖는 속성들로 구성됩니다.
```json
{
  "happiness": 72,
  "sadness": 10,
  "anger": 0,
  "loneliness": 18,
  "excitement": 65,
  "affection": 54,
  "trust": 71
}
```

## 2. Transition Logic
새로운 감정 상태는 아래 정보들의 조합으로 결정됩니다.
- **Previous Emotion**: 직전의 감정 상태 베이스라인
- **Conversation Analysis**: 현재 발화의 긍정/부정/의도(Sentiment Analysis)
- **User Context & Relationship**: 사용자와의 현재 관계 레벨(친밀도)

## 3. Impact on Behavior
도출된 Emotion은 다음과 같은 요소에 영향을 미칩니다.
- **Persona/Tone**: 대화의 톤앤매너 변화 (예: 흥분 시 짧고 경쾌한 문장)
- **Avatar Expression**: 아바타의 표정(Smile, Sad 등) 및 애니메이션 강도 변경
