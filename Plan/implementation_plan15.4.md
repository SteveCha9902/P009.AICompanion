# P009.AICompanion - Sprint 15 STEP 4 Pre-Implementation Report
**Runtime Hardening & Real Provider Readiness**

---

## 1. Pre-Implementation Audit (현재 코드베이스 Gap 분석)

| 영역 | 현재 상태 (AS-IS) | 문제점 및 Gap | 개선 방향 (TO-BE) |
| :--- | :--- | :--- | :--- |
| **Mobile Config** | `api.ts`에 특정 IP (`192.168.55.140`) 하드코딩 | 에뮬레이터/실기기/Dev 환경 전환 시 수동 수정 필요 | `config/env.ts` 신설, Platform/Dev 자동 분기 & `.env` 지원 |
| **Backend Runtime** | 기본 FastAPI 앱 구조만 존재 | Request Timeout, Graceful Shutdown, Provider 헬스 검사 부재 | Timeout 미들웨어, 헬스 메트릭, 의존성 Scope 명확화 |
| **Network State** | 3개 상태(`idle`, `thinking`, `responding`)만 존재 | 네트워크 끊김(`DISCONNECTED`), 취소(`CANCELLED`), 재시도(`RETRYING`) 세분화 부재 | 7단계 Network State Machine 및 Exponential Backoff 재시도 도입 |
| **SSE Reliability** | 단순 이벤트 리스너 등록 | 중복 이벤트 수신 가능성, Client Disconnect 시 LLM 자원 낭비 | Event Deduplication, Cancellation 방어, Partial Stream 보존 |
| **Provider Pluggability** | `runtime.py`에 Mock/OpenAI가 고정 주입 | 환경변수에 따른 유연한 Mock ↔ Real Provider 교체 불가 | `ProviderFactory` 신설, `CompanionOrchestrator` 무수정 교체 보장 |
| **Observability** | 기본 `logger.info` 텍스트 로깅 | `interaction_id` 추적 불가, TTFT/단계별 Latency 측정 불가 | Structured Trace Logger 도입 (`ttft_ms`, `context_ms`, `total_ms`) |

---

## 2. 세부 설계 및 개선 계획

### 2-1. Mobile Config (`mobile/src/config/env.ts`)
- **자동 환경 감지**:
  - Android Emulator: `http://10.0.2.2:8000`
  - iOS Simulator: `http://localhost:8000`
  - Physical Device: `process.env.EXPO_PUBLIC_API_URL`
- API 클라이언트(`api.ts`, `interactionController.ts`)가 `getApiBaseUrl()`을 참조하도록 리팩토링.

### 2-2. InteractionController Network State Machine 강화
```text
[IDLE] ───(sendInteraction)───> [CONNECTING] ───(SSE text_delta)───> [STREAMING]
  ▲                                    │                                  │
  │                               (disconnect)                       (complete)
  │                                    ▼                                  ▼
[CANCELLED] <──(cancel)── [DISCONNECTED / RETRYING] ────(error)────> [ERROR]
```

### 2-3. Real Provider Readiness (Provider Factory)
`backend/app/services/providers/factory.py`:
- `LLMProviderFactory.create()`: `MOCK` | `OPENAI`
- `STTProviderFactory.create()`: `MOCK` | `OPENAI`
- `TTSProviderFactory.create()`: `MOCK` | `OPENAI`
- `VisionProviderFactory.create()`: `MOCK` | `CLOUD`
- `EmbeddingProviderFactory.create()`: `MOCK` | `OPENAI`
- `runtime.py`가 Factory를 호출하므로 `CompanionOrchestrator` 코드는 단 한 줄도 수정 없이 런타임 교체 가능.

### 2-4. Runtime Observability & Structured Tracing
`InteractionTracer`를 통해 모든 Interaction에 대해 다음 지표를 구조화 로그 및 SSE 메타데이터에 기록:
- `interaction_id`: 고유 추적 ID
- `input_norm_ms`: 입력 정규화 소요 시간
- `context_gather_ms`: 7대 Provider Context 조립 시간
- `ttft_ms`: **Time To First Token** (첫 번째 토큰 생성 시간)
- `llm_total_ms`: 전체 LLM 스트리밍 시간
- `post_process_ms`: AvatarStateResolver 및 메시지 영속화 시간
- `total_e2e_ms`: 전체 종단간 소요 시간

---

## 3. Quality Gate (STEP 4 완료 기준)

- [ ] **Gate 1 (Test Integrity)**: 기존 21개 백엔드 단위/통합 테스트 100% 통과 유지
- [ ] **Gate 2 (TypeScript Integrity)**: 모바일 `npx tsc --noEmit` 에러 0개
- [ ] **Gate 3 (Provider Pluggability)**: `PROVIDER_MODE=mock` 및 `PROVIDER_MODE=real` 환경변수 전환 테스트
- [ ] **Gate 4 (SSE Failure & Cancellation)**: Client Disconnect 및 Cancel 시 상태 안전 리셋 검증 테스트
- [ ] **Gate 5 (Observability Trace)**: `ttft_ms` 및 `interaction_id` 구조화 로그 및 메타데이터 출력 검증

---

## 4. Single Pipeline 불변 원칙 검증
새로운 Factory, 미들웨어, 트레이서는 `CompanionOrchestrator`의 단일 진입점 파이프라인 외부 또는 Provider 어댑터 계층에만 위치하며, **기존 STEP 3A/3B의 Single Pipeline 구조를 절대 훼손하지 않습니다.**
