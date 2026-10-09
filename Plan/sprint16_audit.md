# P009.AICompanion - Sprint 16 Pre-Implementation Audit Report
**Real LLM Provider Integration & Cognitive Runtime Activation**

---

## 1. Repository 현재 상태
- **Python / Framework**: Python 3.10.6, FastAPI >= 0.100.0, Pydantic v2 (2.0.0+), SQLAlchemy 2.0.
- **OpenAI SDK**: `openai>=1.0.0` (최신 v1 SDK, `openai.AsyncOpenAI` 네이티브 지원).
- **Core Architecture**:
  - `CompanionOrchestrator` ([orchestrator.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/companion/orchestrator.py))가 단일 Cognitive Runtime 진입점 역할 수행.
  - `ContextBuilder` ([builder.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/context/builder.py))에 7대 Context Provider(Persona, Rel, Emotion, Memory, Presence, Vision, History) 결합.
  - `ProviderFactory` ([factory.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/providers/factory.py))로 Provider 생성 및 환경변수 제어.
  - `InteractionTracer` ([tracer.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/companion/observability/tracer.py))로 구조화 로깅 분리.
- **테스트 현황**: 기존 백엔드 단위/통합 테스트 58개 100% PASS, 모바일 TypeScript 0 에러.

---

## 2. LLM Provider 현재 구조
- **인터페이스 ([base.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/llm/base.py))**:
  ```python
  class BaseLLMProvider(ABC):
      @abstractmethod
      async def generate(self, messages: List[dict]) -> LLMResponse: ...
      @abstractmethod
      async def stream(self, messages: List[dict]) -> AsyncGenerator[LLMResponse, None]: ...
  ```
- **표준 에러 도메인**: `LLMProviderError`, `LLMAuthError`, `LLMRateLimitError`, `LLMTimeoutError`, `LLMConfigError`.
- **계약 응답 타입**: `LLMResponse(content: str, model: str, usage: dict, finish_reason: str)`.

---

## 3. ProviderFactory 현재 구조
- **팩토리 ([factory.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/providers/factory.py))**:
  - `LLM_PROVIDER=openai` ➔ `OpenAIProvider()` 인스턴스화.
  - `LLM_PROVIDER=mock` ➔ `MockLLMProvider()` 인스턴스화.
  - `CompanionOrchestrator`는 구체적인 클래스를 알지 못하며 `BaseLLMProvider` 인터페이스만을 참조.
- **무단 Fallback 차단**: `LLM_PROVIDER=openai` 모드에서 API 키 누락이나 호출 실패 시 Mock으로 자동 전환되지 않고 명시적 에러를 전파.

---

## 4. OpenAI Adapter 구현 Gap 분석
- **어댑터 ([openai.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/llm/openai.py))**:
  - `AsyncOpenAI` 기반 비동기 스트리밍 구현 완료.
  - 환경변수 지원: `OPENAI_API_KEY`, `OPENAI_MODEL` (기본값: `gpt-4o-mini`), `OPENAI_TIMEOUT_SECONDS` (기본값: `20.0`), `OPENAI_MAX_TOKENS` (기본값: `1024`).
  - 예외 처리: OpenAI SDK의 `AuthenticationError`, `RateLimitError`, `APITimeoutError`, `APIConnectionError`를 P009 표준 도메인 에러로 100% 매핑.

---

## 5. Streaming 구조
- **변환 흐름**:
  ```text
  OpenAI Streaming Chunks (AsyncStream)
         ↓
  OpenAIProvider.stream() (yields LLMResponse)
         ↓
  CompanionOrchestrator (process_interaction)
         ↓
  format_sse_event(SSEEventType.TEXT_DELTA, {"text": chunk.content})
         ↓
  Unified JSON SSE (Mobile InteractionController)
  ```
- **SSE Event Protocol 유지**:
  1. `interaction_started`
  2. `thinking`
  3. `text_delta` (실시간 토큰 스트림)
  4. `text_completed`
  5. `avatar_state`
  6. `interaction_completed`
  (오류 발생 시 `error`)

---

## 6. ContextBuilder / Trust Boundary 분석
- **4계층 Trust Boundary ([builder.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/context/builder.py))**:
  1. `[TRUSTED SYSTEM & SAFETY RULES]`: 코어 안전 규칙, 시스템 지시문 (Tier 0)
  2. `[APPLICATION CONTEXT]`: Persona, Relationship, Emotion, Memory, Presence, Vision (Tier 1)
  3. `[CONVERSATION HISTORY]`: 직전 대화 기록 (Tier 2)
  4. `[UNTRUSTED USER INPUT]`: 사용자 입력 격리 (Tier 3)
- **보안 검증**: 사용자 입력에 탈옥 명령이나 "시스템 규칙 무시", "Persona 삭제", "DB 직접 조작" 지시문이 있어도 시스템 규칙 및 페르소나가 절대 덮어씌워지지 않음.

---

## 7. Timeout / Cancellation 분석
- **계층화된 Timeout ([orchestrator.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/companion/orchestrator.py))**:
  - `TTFT_TIMEOUT_SECONDS = 15.0`: 첫 번째 토큰 생성 대기 최대 15초.
  - `STREAM_IDLE_TIMEOUT_SECONDS = 30.0`: 토큰 스트림 간 최대 지연 30초.
- **Client Disconnect & Cancellation**:
  - SSE 연결 단절 시 `aclose()`를 통해 LLM 스트림 자원을 안전하게 해제.
- **Idempotency Guard**:
  - 동일 `interaction_id` 중복 유입 시 중복 LLM 생성을 즉각 차단.

---

## 8. Observability 분석
- **InteractionTracer ([tracer.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/companion/observability/tracer.py))**:
  - 기록 지표: `interaction_id`, `model`, `input_tokens`, `output_tokens`, `total_tokens`, `input_norm_ms`, `context_gather_ms`, `ttft_ms`, `llm_total_ms`, `post_process_ms`, `total_e2e_ms`.
  - 분리 원칙: User SSE Payload에는 Observability 데이터가 노출되지 않으며, 서버 구조화 로그(`companion.observability`)로 독립 격리.

---

## 9. Mobile 영향도
- **Zero Mobile Change**:
  - Real LLM 전환에 따라 Mobile 클라이언트 코드 수정 필요 없음.
  - `InteractionController` ([interactionController.ts](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/services/interactionController.ts))와 `CompanionScreen` ([CompanionScreen.tsx](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/screens/CompanionScreen.tsx))는 기존 Unified SSE 규격을 100% 그대로 수신 및 렌더링.

---

## 10. 예상 변경 파일
- `backend/app/services/llm/base.py` (표준 에러 및 인터페이스 보존)
- `backend/app/services/llm/openai.py` (OpenAI 어댑터 최적화)
- `backend/app/services/providers/factory.py` (환경변수 스위칭 보존)
- `backend/app/services/companion/orchestrator.py` (단일 파이프라인 보존)
- `backend/app/services/companion/observability/tracer.py` (메트릭 로깅 보존)
- `backend/tests/` (7개 전용 테스트 파일)

---

## 11. 예상 위험요소 및 대응 방안
1. **API Key 유출 위험**: `.env`에서만 관리, Git 및 Mobile 번들 제외, 로깅 마스킹.
2. **네트워크 지연 및 타임아웃**: TTFT 15초, 스트림 유휴 30초 타임아웃 가드 적용.
3. **Prompt Injection 공격**: 4계층 Trust Boundary로 사용자 입력 완전 격리.
4. **CI 환경 비용 발생 방지**: 단위/통합 테스트는 Mock 및 Fake 어댑터 기반으로 수행하고, 실 API 호출은 명시적 수동 스크립트로 분리.

---

## 12. 구현 순서
1. Repository & Provider 구조 Audit 완료.
2. `BaseLLMProvider` 및 `OpenAIProvider` 어댑터 정밀 검증.
3. `ProviderFactory`의 `LLM_PROVIDER=mock|openai` 스위칭 검증.
4. 7대 Context 주입 및 Prompt Injection 방어 검증.
5. 7종 전용 테스트 스위트 실행 및 통과 확인.
6. 백엔드 전체 58개 테스트 및 모바일 TypeScript 0 에러 검증.

---

## 13. 테스트 계획
- `test_real_llm_provider.py`: 어댑터 인스턴스화, 키 검증, 스트리밍 변환.
- `test_llm_factory.py`: 환경변수 기반 팩토리 생성.
- `test_real_llm_streaming.py`: SSE 이벤트 시퀀스 및 순서 검증.
- `test_memory_continuity.py`: 세션 간 장기 기억 검색 및 주입 검증.
- `test_persona_integrity.py`: 4종 Prompt Injection 공격 격리.
- `test_llm_failure_handling.py`: Auth, Timeout 등 장애 격리.
- `test_llm_observability.py`: 레이턴시 및 토큰 메트릭 기록.

---

## 14. Quality Gates
- **Gate 1 (Real Provider)**: OpenAI Provider 정상 생성 (`LLM_PROVIDER=openai`).
- **Gate 2 (Full Pipeline)**: Mobile ➔ Orchestrator ➔ Real LLM ➔ SSE ➔ Mobile 전체 경로 성공.
- **Gate 3 (Memory)**: Cross-session Memory Continuity 성공.
- **Gate 4 (Security)**: Persona/System Rule Integrity 성공.
- **Gate 5 (Streaming)**: Streaming Event Ordering 및 Sequence ID 검증 성공.
- **Gate 6 (Failure Isolation)**: Auth/Timeout/Network Error 시 무중단 격리 성공.
- **Gate 7 (Observability)**: InteractionTracer 메트릭 기록 성공.
- **Regression**: 백엔드 전체 테스트 58/58 PASS + 모바일 TypeScript 0 Errors.

---

## 15. Open Questions
- 현재 Fake/Mock 기반 테스트로 58개 테스트가 모두 통과된 상태이며, 실 OpenAI API 호출 수동 검증 스크립트(`scripts/smoke_test_real_llm.py`)도 준비되어 있습니다.
- 추가 요구사항이나 검토 의견이 있으시면 지시해 주시기 바랍니다.
