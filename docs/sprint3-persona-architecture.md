# Sprint 3: Persona Engine Architecture & Pre-Implementation Report

> 이 문서는 Sprint 3 시작 전 확정된 Persona Engine의 핵심 아키텍처 원칙을 담고 있습니다.

## 1. Companion Domain Concept
P009의 장기 도메인 구조에 따라 Persona를 User에 직접 종속시키지 않습니다.

**최종 Domain 구조:**
```
User
 ↓
Companion
 ↓
Persona
 ↓
Memory / Emotion / Relationship / Voice / Avatar
```
Sprint 3에서는 전체 Companion 기능을 구현하지 않지만, DB 스키마 및 도메인은 `User -> Companion -> Persona` 구조를 따릅니다.

## 2. Persona Domain Completion
Persona는 다음 6가지 요소를 모두 포함합니다.
- Identity
- Personality
- Communication Style
- Values (신규)
- Behavior Tendencies
- Boundaries (신규)

## 3. Personality Score Semantics
Personality 점수는 0~100의 수치를 사용하지만, LLM에는 숫자 그대로 전달하지 않고 Semantic Mapping을 거쳐 의미 기반으로 전달합니다.
- `0~20`: very low
- `21~40`: low
- `41~60`: moderate
- `61~80`: high
- `81~100`: very high

## 4. Preset 구조
초기 Persona Preset(balanced, warm 등)은 DB Entity가 아닌 Static Configuration(`presets/`) 파일로 관리합니다. 유저가 선택 시 `PersonaService`를 통해 `Companion`의 개별 `Persona` 레코드로 복사됩니다.

## 5. Persona Versioning
현재는 `persona.version` 컬럼을 사용하며, 수정 시 1씩 증가합니다.
(미래에 `persona_versions` 이력 테이블로 확장할 수 있도록 구조를 대비합니다.)

## 6. Message Persona Version
`Message` 엔티티의 `metadata` 필드에 현재 응답을 생성한 `persona_version`을 기록하여 디버깅 및 추적성을 확보합니다.

## 7. Context Priority
현재 Response 생성 시 컨텍스트 간의 "영향력(Influence) 우선순위"는 다음과 같습니다.
1. System / Safety
2. Current User Request
3. Current Context
4. Relationship / Emotion
5. Relevant Memory
6. Persona (기본 성향)
7. Default Behavior

## 8. Trust Boundary (Prompt Injection 방어)
단순한 프롬프트 순서 변경을 넘어, 영역별로 Trust 수준을 엄격히 분리합니다.
- **System Rules**: Trusted
- **Persona**: Trusted Application Context
- **Memory**: Retrieved Application Context
- **User Message**: Untrusted Input (명령으로 승격 불가)

## 9. Persona Realism Boundary
Persona는 자연스러운 행동 방식을 정의하지만, **현실 세계의 물리적 경험을 허위로 만들어내지 않도록** (예: "나는 실제로 네 방에 있어") Behavior Boundary 규칙에 명시하여 환각(Hallucination)을 방지합니다.

## 10. Final Persona Architecture
```
User
 ↓
Companion
 ↓
Persona
 ↓
PersonaContextProvider
 ↓
ContextBuilder
 ↓
LLM Provider
 ↓
Response
```
