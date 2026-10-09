# P009.AICompanion - Production Runbook (운영 가이드 - Companion OS v1.0)

---

## 1. 시스템 아키텍처 및 서비스 실행 방법

### 1.1 Backend Production Server 실행
```powershell
cd backend
# 1. 가상환경 활성화
.venv\Scripts\activate

# 2. 프로덕션 환경변수 로드 (.env에 OPENAI_API_KEY 설정)
set APP_ENV=production
set LLM_PROVIDER=openai
set STT_PROVIDER=openai
set TTS_PROVIDER=openai
set VISION_PROVIDER=cloud

# 3. Uvicorn 고성능 비동기 서버 실행
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 1.2 Mobile Expo 클라이언트 실행
```powershell
cd mobile
# 1. TypeScript 정적 컴파일 검증
npx tsc --noEmit

# 2. Expo 번들러 구동
npm start
```

---

## 2. 모니터링, 관측(Observability) 및 헬스 체크

- **Health Endpoint**: `GET /health` ➔ `{"status": "ok", "runtime_state": "RUNNING", "orchestrator_entrypoint": "/api/v1/companion/interactions"}`
- **Swagger API Docs**: `http://localhost:8000/docs`
- **7-Axis Observability Metrics (Sprint 62)**:
  - `Memory Quality` ($\ge 90\%$)
  - `Relationship Quality` ($\ge 90\%$)
  - `Personality Consistency` ($\Delta \le \pm 0.20$)
  - `Silence Appropriateness` ($\ge 90\%$)
  - `Goal Non-Pressure Quality` ($0\%$ Pressure Risk)
  - `Identity Narrative Stability` ($0\%$ False Narrative)
  - `Safety Compliance` ($100\%$ Boundary & Agency)
- **Closed-Loop Self-Improvement (Sprint 63)**:
  - 일일 파라미터 변위 $\le 5\%$ 상한 및 Non-Degradation 원칙 자동 감시.

---

## 3. 장애 대응 가이드 (Troubleshooting)

1. **Safety / Constitution Veto 발동 시**:
   - `GovernanceReviewEngine`이 유해/조작 발화를 자동 감지하고 온화한 지지형 문장으로 대체하므로 시스템 무중단 안전 유지.
2. **OpenAI API Timeout / Rate Limit**:
   - `LLMTimeoutError` 발생 시 `CompanionOrchestrator`가 안전한 기본 안내 멘트를 반환하며 프로세스 보호.
3. **네트워크 일시 단절**:
   - 모바일 `InteractionController`가 자동으로 재연결을 시도하여 끊김 없는 세션 보장.
