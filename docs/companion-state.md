# Companion State

P009에는 UI와 독립적인 명시적인 Companion State Model이 존재합니다. 

## 1. Core State Properties
아래 값들은 Companion Core에 의해 중앙 관리되며, Avatar UI나 Background Event 엔진 등에서 소비됩니다.

```json
{
  "presence": "active | idle | sleeping | busy",
  "attention": 82,
  "activity": "conversation",
  "emotion": { /* EmotionState 참조 */ },
  "relationship": { /* RelationshipState 참조 */ },
  "user_context": {
    "present": true,
    "face_detected": true,
    "attention": true
  },
  "environment_context": "quiet"
}
```

## 2. Unification across Modes
- **Ambient Mode**: `presence`가 `idle`이거나 `sleeping`일 때 OS 백그라운드 태스크에 의해 간헐적으로 업데이트.
- **Interactive Avatar Mode**: 앱이 포그라운드에 있을 때 실시간 센서 입력을 받아 `user_context`와 `attention` 등이 지속적으로 변동.
