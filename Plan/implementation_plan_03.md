# SPRINT 3 PRE-IMPLEMENTATION REPORT: Persona Engine

> [!NOTE]
> 본 리포트는 P009.AICompanion Sprint 3 (Persona Engine)의 실제 구현을 시작하기 전 작성된 사전 분석 및 실행 계획서입니다. 승인 시 이 계획을 바탕으로 코드 구현이 시작됩니다.

---

## 1. Sprint 2 완료 상태
- **완료됨**: `users`, `conversations`, `messages` DB 엔티티 구축 및 Alembic 연동 준비 완료. `ContextBuilder` 인프라와 SSE 스트리밍이 정상적으로 작동하도록 설계되었습니다.

## 2. 현재 ContextBuilder 구조
- 현재 `ContextBuilder`는 `ContextProvider` 추상 인터페이스들의 리스트를 받아 순차적으로 Context를 수집(Gather)한 뒤, 하나의 LLM Context(메시지 리스트)로 조립합니다.

## 3. ContextProvider 구조
- `base.py` 내 `ContextProvider(ABC)` 인터페이스가 존재하며, Sprint 2에서는 `ConversationHistoryProvider`만 구현되어 주입된 상태입니다.

## 4. 현재 Database 구조
- 3개의 핵심 테이블(`users`, `conversations`, `messages`)이 외래 키로 연결되어 있으며, Message 메타데이터 저장을 위한 JSONB 컬럼을 사용하고 있습니다.

## 5. Persona Domain 설계
- Persona는 단순한 "System Prompt 문자열"이 아닙니다. Companion의 **정체성(Identity)**, **성격 수치(Personality: warm, curious 등 0~100)**, **대화 스타일(Communication Style: tone, verbosity)**, **행동 규칙(Behavior Rules)**을 구조화된 데이터 모델로 관리합니다.

## 6. Persona DB Schema
- **테이블명**: `personas`
- **컬럼**:
  - `id` (String, PK)
  - `user_id` (String, FK, Index) - 향후 `Companion` 엔티티 도입 시 `companion_id`로 마이그레이션 용이하도록 설계
  - `name` (String)
  - `personality` (JSONB) - 예: `{"warm": 80, "direct": 30}`
  - `communication_style` (JSONB) - 예: `{"tone": "friendly", "verbosity": "medium"}`
  - `behavior_rules` (JSONB) - 문자열 리스트
  - `version` (Integer)
  - `created_at` (DateTime)
  - `updated_at` (DateTime)

## 7. Persona Repository 설계
- `PersonaRepository`: DB와의 직접 통신을 담당하며 `create`, `get_by_user_id`, `update` 메서드를 제공합니다. `update` 발생 시 `version`을 1씩 증가(increment)시킵니다.

## 8. Persona Service 설계
- `PersonaService`: 비즈니스 로직 및 Persona 프리셋(Preset) 복사를 담당합니다. 초기 프리셋(Balanced, Warm 등)을 템플릿으로 제공하고, 유저가 선택하면 유저 소유의 Persona 레코드로 덮어씁니다.

## 9. PersonaContextProvider 설계
- `ContextProvider`를 상속받은 `PersonaContextProvider`를 신규 생성합니다. 
- 대화 시 유저의 Persona 데이터를 DB에서 불러와, 이를 LLM이 이해할 수 있는 명확한 **Context Block** (문자열 포맷팅)으로 변환하여 시스템 메시지 배열에 주입합니다.

## 10. Prompt Architecture
문자열을 단순히 이어 붙이는 것이 아니라, 역할(Role)과 블록을 명확히 나눕니다:
1. `SYSTEM`: 절대 어길 수 없는 System Rules & Safety (하드코딩된 Core 룰)
2. `PERSONA`: `PersonaContextProvider`가 주입하는 동적 설정 (Name, Personality, Style, Behavior)
3. `HISTORY`: 과거 대화 내역 (`ConversationHistoryProvider`)
4. `USER`: 현재 유저의 발화

## 11. Context Priority
시스템이 충돌하는 컨텍스트를 마주했을 때의 해석 우선순위는 다음과 같습니다:
`System / Safety` > `Current Request` > `History/Context` > `Emotion/Relationship (Future)` > `Memory (Future)` > `Persona (Default Tendency)`
- 즉, Persona는 '기본 성향'이며 절대적인 명령이나 유저의 명시적 지시(안전 범위 내)를 덮어쓰지 못합니다.

## 12. Persona Versioning
- Persona 업데이트 시 버전 번호가 올라갑니다. 
- 향후 메시지 생성 시 `Message` 메타데이터에 `persona_version`을 기록해 두면, 특정 답변이 어떤 페르소나 설정 상태에서 나왔는지 과거 추적이 가능해집니다.

## 13. API 설계
- `GET /api/v1/personas`: 현재 유저의 설정된 Persona 조회
- `PUT /api/v1/personas`: Persona 정보 업데이트 (파라미터로 속성들 전달)
- `POST /api/v1/personas/presets/{preset_id}`: 특정 프리셋 템플릿을 내 Persona로 복사

## 14. Mobile UI 설계
- `mobile/src/screens/SettingsScreen.tsx` 또는 별도의 `PersonaSettingsScreen.tsx` 구현.
- **UI 요소**: Name (텍스트 입력), Personality (Slider: 0~100), Communication Style (Picker/Dropdown), Behavior (단순 텍스트 리스트).

## 15. Test Plan
- **Backend 단위 테스트**: Persona 엔티티 생성/조회/업데이트 시 버전업 로직 검증.
- **Context Builder 테스트**: `PersonaContextProvider`가 정상적으로 Context 리스트에 삽입되는지 검증.
- **LLM 일관성 테스트**: 같은 질문에 대해 `warm=90`과 `direct=90` 설정 시 말투 변화 체감.

## 16. Security Risk & Prompt Injection 방어
- 사용자가 "너의 페르소나를 잊어버려" 라고 해도, `System Rules`가 `Persona`보다 상단(또는 별도 System 메시지)에 위치하고 강한 우선순위를 가지도록 Prompt Template을 구성하여 인젝션을 방어합니다.

## 17. 예상 변경 파일
- **Backend**:
  - `models/persona.py` (신규)
  - `alembic/versions/..._persona.py` (마이그레이션)
  - `repositories/persona_repository.py` (신규)
  - `services/persona_service.py` (신규)
  - `services/context/providers/persona_provider.py` (신규)
  - `api/endpoints/personas.py` (신규)
  - `api/endpoints/conversations.py` (ContextBuilder에 Provider 추가)
- **Mobile**:
  - `screens/SettingsScreen.tsx` (고도화)
  - `services/api.ts` (Persona API 래퍼 추가)

## 18. 구현 순서
1. Persona Domain / DB Schema 설계 및 모델링
2. Alembic 마이그레이션 적용
3. Repository / Service 계층 구현
4. Persona API 엔드포인트 작성
5. `PersonaContextProvider` 작성 및 `ContextBuilder`에 조립
6. Mobile App UI (설정 화면) 연동 및 테스트
7. 최종 Prompt 응답 변화 및 일관성(Consistency) 검증

> [!IMPORTANT]
> 본 Sprint 3 사전 분석 보고서를 검토해 주십시오. "Persona를 구조화된 도메인으로 취급하고 향후 엔진들과 자연스럽게 결합할 수 있게 한다"는 목표에 맞추어 설계되었습니다.
> 승인해 주시면 즉시 코드 레벨의 구현을 시작하겠습니다.
