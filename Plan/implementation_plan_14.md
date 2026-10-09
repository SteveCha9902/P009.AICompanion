# P009.AICompanion - Sprint 14: Unified Companion Orchestration Engine Pre-Implementation Report

## 1. Gap Analysis (현재 코드와 기획의 차이)

Repository 분석 결과, 기존 Sprint 1~13 코드와 이번 Sprint 14 최종 기획 사이에는 아래와 같은 간극(Gap)이 존재합니다.

1. **God Object (ConversationService)**: 현재 `backend/app/services/conversation_service.py`가 Persona 로딩, Emotion 동기 호출, Context 조립, LLM 스트리밍, Memory 비동기 호출을 모두 직접 제어하고 있습니다. Event Bus가 없으며 강결합 상태입니다.
2. **Raw Text LLM Output**: `llm_provider.stream()`이 Raw Text만 반환합니다. `emotion_candidate`, `relationship_signal`, `presentation` 힌트 등을 구조화된 형태(Structured Candidate)로 출력하지 못합니다.
3. **Context Priority 미보장**: `ContextBuilder`가 `providers` 리스트의 순서에만 의존하여 Context를 생성합니다. 우선순위(System > User Intent > App Context > History > User Input)가 명확히 보장되지 않습니다.
4. **Interaction ID 부재**: `request_id`만 존재하며, Vision, Voice, Text 이벤트를 하나로 추적할 수 있는 범용 `interaction_id`(`INT-YYYYMMDD-XXXX`) 체계가 없습니다.

## 2. Sprint 14 Architecture Rules (반영 사항)

위 Gap을 해소하기 위해 아래 원칙을 엄격하게 적용하여 구현합니다.

### Rule 1: Event Bus 분리 (Sync vs Async)
- **Sync/Critical**: Interaction State 갱신, Response Delivery, TTS, Avatar Presentation
- **Async/Background**: Memory Extraction, Relationship Update, Analytics, Event Logging
- *장애 격리*: DB 부하로 인해 Memory 저장이 늦어져도(Async) 실시간 Avatar 애니메이션과 음성(Sync)은 멈추지 않아야 합니다.

### Rule 2: Orchestrator vs Engine
- `CompanionRuntime`과 `CompanionOrchestrator`는 비즈니스 로직을 직접 수행하지 않고 **실행 순서와 조정(Pipeline)**만 담당합니다.
- **"Orchestrator coordinates, Engine decides."**

### Rule 3: LLM Candidate & Validator Pattern
LLM은 DB 상태를 직접 변경할 권한이 없습니다. LLM 출력은 반드시 구조화된 Candidate여야 합니다.
```json
{
  "response": { "text": "오늘 많이 힘들었구나." },
  "emotion_candidate": { "primary": "EMPATHY", "intensity": 0.7 },
  "relationship_signal": { "type": "SUPPORT_PROVIDED", "confidence": 0.8 },
  "memory_candidates": [],
  "presentation": { "expression": "gentle", "energy": 0.35 }
}
```
처리 순서: `LLM ➔ Candidate ➔ Validator/Policy ➔ Engine ➔ Actual State 변경`

### Rule 4: Normalized Interaction & Observability
- Text, Voice, Vision 입력은 `Normalized Interaction`으로 통합되며 단일 `interaction_id`를 부여받습니다.
- 여러 Context Provider(Vision Observation, Memory, Persona)는 **병렬로 동시 수집**하되, **Context Assembly는 명확한 순서로 직렬화**합니다.

### Rule 5: Strict Trust Boundaries & Priority
Context Assembly 시 아래 순서와 Trust 레벨을 절대적으로 보장합니다.
1. `SYSTEM / SAFETY` (Trusted)
2. `CURRENT USER INTENT`
3. `APPLICATION CONTEXT` (Persona, Relationship, Emotion, Memory, Presence, Vision[Observation])
4. `CONVERSATION HISTORY`
5. `USER INPUT` (Untrusted)

### Rule 6: Failure Isolation
- Memory, Vision, Emotion, Relationship, Avatar 중 어느 하나가 실패해도 기본 **Text Conversation Pipeline은 절대로 중단되지 않아야 합니다.**

---

## 3. Implementation Plan (13 Steps)

1. Repository / 코드 갭 분석 (현재 완료)
2. CompanionRuntime Domain 설계
3. Event Bus 설계 (Sync/Async 분리)
4. Interaction State Machine 구현
5. Unified Context Pipeline 리팩토링 (우선순위 강제 적용)
6. Conversation + Memory + Emotion + Relationship 통합 파이프라인 구축
7. Voice + Vision 통합 (Observation ➔ Emotion ➔ Avatar 구조 확보)
8. Avatar + TTS Synchronization (Mobile Runtime 제어 구조 완성)
9. Proactive + Background Restore 통합
10. Mobile CompanionScreen 연동
11. Integration Test
12. Full Multimodal E2E (Phone & Tablet)
13. Sprint Report 작성

---
## User Review Required

지시해주신 구조적 제약 사항을 완벽히 수용하여 **Gap Analysis 및 수정된 Architecture Rules**를 반영했습니다. 
이 내용을 기반으로 Task 리스트를 생성하고 STEP 2(`CompanionRuntime Domain` 설계)부터 바로 코딩(구현)에 착수해도 될까요?
