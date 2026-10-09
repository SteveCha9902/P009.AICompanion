# Behavior Parameter Specification (Behavior_Parameter_Spec.md)

본 문서는 **P009.AICompanion Sprint 43**의 신체 행동 매개변수(`BehaviorParameters`) DTO 표준 규격을 정의합니다.

---

## 1. BehaviorParameters TypeScript / Pydantic 인터페이스

```typescript
export interface BehaviorParameters {
  attentionLevel: number;      // 0.0 (주의 분산) ~ 1.0 (고도 집중)
  eyeContact: number;          // 0.0 (시선 회피) ~ 1.0 (사용자 정면 응시)
  headTilt: number;            // -10.0° ~ +10.0° (갸우뚱/기울기)
  nodIntensity: number;        // 0.0 ~ 1.0 (끄덕임 강도)
  bodyLean: number;            // -1.0 (뒤로 기댐) ~ +1.0 (앞으로 기울임)
  curiosityLevel: number;      // 0.0 ~ 1.0 (호기심/흥미 지수)
  thinkingIntensity: number;   // 0.0 ~ 1.0 (사색/고민 깊이)
}
```

---

## 2. 세부 파라미터 규격 표

| 파라미터명 | 타입 | 허용 범위 | 기본값 | 주요 역할 |
| :--- | :--- | :--- | :--- | :--- |
| `attentionLevel` | Float | `0.0 ~ 1.0` | `0.80` | 시선 집중도 및 불필요한 미세 노이즈 억제 |
| `eyeContact` | Float | `0.0 ~ 1.0` | `0.85` | 사용자와의 눈맞춤 비율 (경청 시 1.0, 생각 시 0.4) |
| `headTilt` | Float | `-10.0 ~ 10.0` | `0.0` | 상황에 따른 고개 기울기 (경청 +2.5°, 생각 -4.0°) |
| `nodIntensity` | Float | `0.0 ~ 1.0` | `0.0` | 동의 및 경청 끄덕임 가중치 |
| `bodyLean` | Float | `-1.0 ~ 1.0` | `0.0` | 관심 표현을 위한 전방 상체 기울임 |
| `curiosityLevel` | Float | `0.0 ~ 1.0` | `0.50` | 눈썹 및 눈 크기 보정 |
| `thinkingIntensity`| Float | `0.0 ~ 1.0` | `0.0` | 사색 시 시선 분산 및 고개 틸트 스케일 |
