# SPRINT 2 PRE-IMPLEMENTATION REPORT: Conversation Engine

> [!NOTE]
> 본 리포트는 P009.AICompanion Sprint 2 (Conversation Engine)의 실제 구현을 시작하기 전, 요구사항과 아키텍처 원칙에 입각하여 작성된 사전 분석 및 실행 계획서입니다. 승인 시 이 계획을 바탕으로 실제 코드 구현이 시작됩니다.

---

## 1. Sprint 1 완료 상태
- **완료됨**: React Native(Expo) 모바일 셸, 전역 상태(Zustand), Navigation, 기본 Backend 헬스체크 연동 등 Foundation 구축 완료.

## 2. Current Repository 분석
- 현재 `backend/` 폴더에는 `main.py`와 `requirements.txt`만 존재하며, DB나 핵심 비즈니스 로직은 비어있습니다.
- `mobile/` 폴더에는 기본적인 5개 스크린과 서비스 구조가 마련되어 있으나, UI는 Dummy 데이터로 채워져 있습니다.

## 3. 현재 Conversation 관련 코드
- `ConversationScreen.tsx` 내부에 로컬 `useState`를 활용한 더미(Dummy) 메시지 리스트와 입력창만 존재합니다. 백엔드 로직은 전혀 없습니다.

## 4. Database 구조
- **현재**: DB 연동 코드(ORM 등)가 존재하지 않습니다.
- **계획**: PostgreSQL(pgvector 지원 환경)과 `SQLAlchemy` + `Alembic`을 도입하여 `User`, `Conversation`, `Message` 엔티티를 생성합니다.

## 5. 기존 API 구조
- 단일 엔드포인트 `GET /health`만 존재합니다.

## 6. 기존 LLM 관련 코드
- 존재하지 않습니다.

## 7. 재사용 가능한 Component
- `services/api.ts` (API 호출 래퍼)
- `state/useAppStore.ts` (전역 상태 관리 구조)
- `services/storage.ts` (현재 유저/세션 키 저장용)

## 8. Missing Components
- Database Models & Migrations
- Conversation Repository & Service
- Context Builder
- LLM Provider Abstraction
- Mobile SSE (Server-Sent Events) Streaming Client

---

## 9. Conversation Architecture
LLM이나 UI에 종속되지 않는 독립적인 코어를 설계합니다.
```text
Mobile UI -> API Router -> Conversation Service -> Context Builder -> LLM Provider Abstraction -> LLM
```

## 10. LLM Provider Architecture
- 파이썬 `abc.ABC`를 활용해 `BaseLLMProvider` 인터페이스 생성 (`generate`, `stream` 메서드 강제).
- 구체 클래스로 `OpenAIProvider`를 구현하여 실제 API를 통신하되, 서비스 레이어는 `BaseLLMProvider` 인터페이스만 바라보게(Dependency Inversion) 합니다.

## 11. Context Builder Architecture
- 단순 프롬프트 하드코딩을 피하고, `System Context` + `Conversation History (최근 N개)` + `Current User Message`를 조합하는 `ContextBuilder` 클래스를 작성합니다.
- 향후 Memory, Persona 모듈이 이 클래스 내부에 주입(Inject)되어 확장될 수 있도록 뼈대를 잡습니다.

## 12. Streaming 방식
- **결정**: **Server-Sent Events (SSE)**
- **사유**: WebSocket은 양방향 실시간 통신에 유리하지만, 이번 Sprint의 '단방향 스트리밍 텍스트 응답'에는 SSE(HTTP/1.1)가 훨씬 가볍고 모바일(React Native)에서도 폴리필(e.g., `react-native-sse` 또는 향상된 `fetch`)로 쉽게 처리할 수 있습니다. FastAPI의 `StreamingResponse`와 찰떡궁합입니다.

## 13. Database 변경 계획
최소 2개의 테이블을 설계합니다 (User는 Mocking 또는 심플 테이블 적용):
- `conversations`: id, user_id, title, created_at
- `messages`: id, conversation_id, role (user/assistant/system), content, metadata (JSONB), created_at

## 14. API 변경 계획
- `POST /api/v1/conversations`: 새 대화 생성
- `GET /api/v1/conversations`: 대화 목록 조회
- `GET /api/v1/conversations/{id}/messages`: 대화 내역 조회
- `POST /api/v1/conversations/{id}/messages`: 메시지 전송 및 LLM 응답 (SSE Stream 반환)

## 15. Mobile 변경 계획
- `ConversationScreen.tsx`에서 SSE 기반 Fetch 통신을 적용하여, 응답 청크(Chunk)가 도착할 때마다 메시지 텍스트를 실시간으로 업데이트(append)하는 Streaming UI 구현.
- 로딩 상태, 에러 처리(재시도 버튼) 추가 및 Zustand 상태 업데이트.

## 16. Test 계획
- Backend: Pytest 기반 `ConversationService`, `ContextBuilder` 단위 테스트.
- E2E: 안드로이드/에뮬레이터 상에서 새 대화 생성 -> 메시지 전송 -> 실시간 응답 출력 -> 앱 재시작 후 복구 시나리오 E2E 매뉴얼 테스트.

## 17. Security Risk
- **LLM Secret 노출 방지**: OpenAI API Key 등은 절대 Mobile에 포함하지 않고 Backend `.env`로 격리.
- **Data Isolation**: API 호출 시 User 식별자 기반으로 권한(Ownership) 체크 수행 (Sprint 2에서는 임시 `user_id`를 헤더에 부여해 격리).

## 18. Performance Risk
- **TTFT (Time To First Token)**: 모바일 네트워크 지연율과 LLM 초기 응답 대기 시간이 겹쳐 느려보일 수 있습니다. 백엔드에서 소요 시간(Latency) 추적 로그를 남기도록 합니다.

## 19. 예상 변경(생성) 파일 목록
- **Backend**:
  - `backend/app/db/` (models.py, session.py)
  - `backend/alembic/` (Migrations)
  - `backend/app/api/endpoints/conversations.py`
  - `backend/app/services/conversation_service.py`
  - `backend/app/services/context_builder.py`
  - `backend/app/services/llm_provider.py`
- **Mobile**:
  - `mobile/src/screens/ConversationScreen.tsx` (고도화)
  - `mobile/src/services/api.ts` (API 추가 및 SSE 파서)

---

## 20. Sprint 2 구현 순서
1. Sprint 1 결과/저장소 분석 (완료)
2. Database / SQLAlchemy + Alembic 셋업 및 스키마 생성
3. Backend LLM Provider Interface 및 Context Builder 작성
4. Backend Conversation Service (저장/조회 로직) 작성
5. Backend API Routes 및 SSE Streaming 구현
6. Mobile Conversation UI/State 연동 (SSE Fetch)
7. Error / Retry 로직 및 App 재실행 복구 테스트
8. 최종 E2E 검증 및 Sprint Report 작성

> [!IMPORTANT]
> 본 Sprint 2 사전 분석 보고서를 검토해 주십시오. "Conversation Engine이 특정 UI 또는 특정 LLM에 종속되지 않게 한다"는 목표에 완벽히 부합하도록 설계되었습니다.
> 승인해 주시면 즉시 **STEP 3. Conversation Domain 설계 및 DB 마이그레이션(Alembic)**부터 실제 백엔드 개발을 시작해 인프라를 연결하겠습니다.
