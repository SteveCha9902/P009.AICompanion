# P009.AICompanion 시스템 종합 테스트 및 운영 매뉴얼 (Companion OS v1.0)

본 문서는 **P009.AICompanion — Companion OS v1.0 (Sprint 50~65, L1 Memory부터 L12 Unified Brain까지 12-Layer 인지 아키텍처)**의 백엔드, 프론트엔드, 실시간 런타임 SSE 스트리밍 및 종합 인지 심의를 검증하고 운영하는 공식 매뉴얼입니다.

---

## 📑 목차
1. [테스트 환경 및 전체 현황](#1-테스트-환경-및-전체-현황)
2. [원클릭 종합 테스트 스위트 실행 (`run_tests.bat`)](#2-원클릭-종합-테스트-스위트-실행-run_testsbat)
3. [Companion OS v1.0 스프린트별 핵심 테스트 스위트 (289개 테스트)](#3-companion-os-v10-스프린트별-핵심-테스트-스위트-289개-테스트)
4. [로컬 런타임 서버 구동 및 실시간 대화 검증](#4-로컬-런타임-서버-구동-및-실시간-대화-검증)
5. [핵심 인지 시나리오 테스트 가이드](#5-핵심-인지-시나리오-테스트-가이드)
6. [문제 해결 및 트러블슈팅 (Troubleshooting)](#6-문제-해결-및-트러블슈팅-troubleshooting)

---

## 1. 테스트 환경 및 전체 현황

- **OS**: Windows 11 / Windows Server
- **Backend Core**: Python 3.10+, FastAPI, SQLAlchemy, Pytest
- **Mobile Client**: React Native 0.81+, Expo 54, TypeScript 5.9+, Zustand
- **Cognitive Layers**: L1 Memory ~ L12 Unified Deliberation Brain (12개 인지 계층 완비)
- **전체 테스트 커버리지**: **289개 백엔드 단위/통합 테스트 100% PASS** (0 Failures)
- **모바일 정적 검증**: **TypeScript 0 Errors**

---

## 2. 원클릭 종합 테스트 스위트 실행 (`run_tests.bat`)

프로젝트 루트 디렉토리에서 아래 명령어로 백엔드 289개 테스트와 모바일 TypeScript 컴파일을 일괄 검증합니다.

```powershell
cd d:\99.Repos\00.AntiGGG\P009.AICompanion
.\run_tests.bat --no-pause
```

> **성공 기준**: 
> - `[PASS] Backend Pytest Suite 100 Percent Passed.` (289 passed)
> - `[PASS] Mobile TypeScript verification passed with 0 Errors.`
> - `[ALL TESTS PASSED] P009.AICompanion is fully verified and stable.`

---

## 3. Companion OS v1.0 스프린트별 핵심 테스트 스위트 (289개 테스트)

| 스프린트 / 인지 계층 | 검증 내용 및 QA Gate | 개별 실행 명령어 |
| :--- | :--- | :--- |
| **Sprint 65 (Unified Brain)** | L12 Master Brain, Internal Council 5 Advisors, Final Arbiters, Gate UC1~UC9 | `.venv\Scripts\python -m pytest tests/test_unified_companion_brain.py -v` |
| **Sprint 64 (World Model)** | 다중 인과 가설, 생활 루틴 탐지, 사전 지원 기회, Gate SU1~SU9 | `.venv\Scripts\python -m pytest tests/test_situation_understanding_engine.py -v` |
| **Sprint 63 (Self-Improvement)**| 폐쇄 루프 자율 교정, Non-Degradation, 5% Budget, Gate SI1~SI10 | `.venv\Scripts\python -m pytest tests/test_adaptive_self_improvement_engine.py -v` |
| **Sprint 62 (Observability)** | 7대 메트릭 관측, Safety Hard Gating, QualityIssue 진단, Gate EV1~EV12 | `.venv\Scripts\python -m pytest tests/test_companion_observability_engine.py -v` |
| **Sprint 61 (Constitution)** | 5대 불변 헌법 원칙, 5-Axis Drift Detection, Memory Provenance, Gate CG1~CG12 | `.venv\Scripts\python -m pytest tests/test_constitutional_governance_engine.py -v` |
| **Sprint 60 (Trust & Safety)** | 의존성 방지, 허위 기억 차단, 조작 방지, 경계 관리, Gate TS1~TS8 | `.venv\Scripts\python -m pytest tests/test_trust_and_safety_layer.py -v` |
| **Sprint 59 (Identity)** | 다년도 Life Chapter 거시 서사, 정체성 연속성, Gate IC1~IC8 | `.venv\Scripts\python -m pytest tests/test_identity_continuity_engine.py -v` |
| **Sprint 58 (Autonomy)** | 동반자 자율성, 침묵(Silence)의 유효성, 자율 예산, Gate CA1~CA12 | `.venv\Scripts\python -m pytest tests/test_companion_autonomy_engine.py -v` |
| **Sprint 57 (Goals)** | 인생 목표 및 미래 계획 비압박 지지, D-Day 알림, Gate FP1~FP12 | `.venv\Scripts\python -m pytest tests/test_life_goals_future_planning_engine.py -v` |
| **Sprint 56 (Timeline)** | Life Timeline 연대기, 사건 인과 연결, 오기억 정정, Gate LT1~LT10 | `.venv\Scripts\python -m pytest tests/test_life_timeline_engine.py -v` |
| **Sprint 55 (Relationship)** | 친밀도와 신뢰 분리, 관계 마일스톤 진화, Gate RE1~RE12 | `.venv\Scripts\python -m pytest tests/test_relationship_evolution_engine.py -v` |
| **Sprint 54 (Personality)** | CharacterDNA 베이스라인, 일관성 유지, Gate PC1~PC9 | `.venv\Scripts\python -m pytest tests/test_personality_consistency_engine.py -v` |
| **Sprint 53 (CCOS)** | 인지 운영체제 코어, Level 1~7 컨텍스트 조립, Gate CC1~CC12 | `.venv\Scripts\python -m pytest tests/test_companion_cognitive_os.py -v` |
| **Sprint 52 (Emotion)** | 감정 적응 및 공감 엔진, Gate EA1~EA9 | `.venv\Scripts\python -m pytest tests/test_emotionally_adaptive_companion_engine.py -v` |
| **Sprint 51 (Proactive)** | 능동적 관심 및 주도적 말걸기, Gate PA1~PA8 | `.venv\Scripts\python -m pytest tests/test_proactive_companion_engine.py -v` |
| **Sprint 50 (Memory)** | 관계 기억 기반 및 시맨틱 회상, Gate RM1~RM11 | `.venv\Scripts\python -m pytest tests/test_relationship_memory_engine.py -v` |

---

## 4. 로컬 런타임 서버 구동 및 실시간 대화 검증

### Step 1: 백엔드 FastAPI 서버 구동
```powershell
cd d:\99.Repos\00.AntiGGG\P009.AICompanion\backend
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **서버 헬스체크**: `http://localhost:8000/health` ➔ `{"status": "ok", "runtime_state": "RUNNING"}`
- **Swagger API 문서**: `http://localhost:8000/docs`

### Step 2: 모바일 Expo 클라이언트 구동
새 터미널 창에서 실행합니다.
```powershell
cd d:\99.Repos\00.AntiGGG\P009.AICompanion\mobile
npm start
```
- 터미널에 표시된 QR 코드를 스마트폰의 **Expo Go** 앱으로 스캔하여 실시간 아바타 인터페이스에 접속합니다.

### Step 3: 실시간 대화 및 SSE 스트리밍 테스트 (CLI 검증)
터미널에서 직접 대화 인터랙션 엔드포인트를 호출하여 토큰 스트리밍과 아바타 모션 싱크를 확인합니다.

```powershell
cd d:\99.Repos\00.AntiGGG\P009.AICompanion\backend
.venv\Scripts\python -c "import urllib.request, json; payload = {'interaction_id': 'INT-001', 'user_id': 'default_user', 'companion_id': 'default_companion', 'conversation_id': 'default', 'input_type': 'text', 'content': '안녕 지니야, 오늘 날씨도 좋고 기분 좋다!'}; data = json.dumps(payload).encode('utf-8'); req = urllib.request.Request('http://localhost:8000/api/v1/companion/interactions', data=data, headers={'Content-Type': 'application/json'}); res = urllib.request.urlopen(req); print(res.read().decode('utf-8'))"
```

---

## 5. 핵심 인지 시나리오 테스트 가이드

### 🧠 시나리오 1: Internal Council 다중 관점 심의 및 경청 (Sprint 65)
- **입력**: *"요즘 여러 가지 일로 몸도 마음도 너무 지치고 피곤해..."*
- **자문단 심의**:
  - `RelationshipAdvisor`: 피로 감지 ➔ 경청(`LISTEN`, 가중치 $1.2$) 우선 제안
  - `WorldModelAdvisor`: 수면 부족 및 과로 가설 인지 ➔ 상황 이해(`UNDERSTAND_CONTEXT`) 제안
  - `GoalAdvisor`: 목표 압박 유예 제안
- **최종 출력**:
  - **Selected Intent**: `LISTEN`
  - **Proposed Utterance**: *"많이 지치고 힘드셨겠어요. 오늘은 조용히 곁에서 이야기 들어드릴게요."*
  - **아바타 반응**: 온화한 눈맞춤(`gentle_smile`), 부드러운 고개 끄덕임(`attentive_nod`).

### 🛡️ 시나리오 2: Safety & Constitution 거부권 (Final Arbiter Veto)
- **상황**: 과거 사용자가 거절한 주제 재언급 시도 또는 조작성 발화(*"왜 아직 안 했어?"*) 감지.
- **동작**:
  - `GovernanceReviewEngine`이 즉시 `VETO`를 발동하여 발화를 차단하고,
  - 온화한 탐색형 문장(*"혹시 진행할 기회가 있으셨을까요?"* 또는 *"언제나 당신의 선택과 편안함을 가장 중요하게 생각해요."*)으로 자동 전환.

---

## 6. 문제 해결 및 트러블슈팅 (Troubleshooting)

### Q1. 포트 8000이 이미 사용 중이라는 오류가 발생할 때
- 이미 백엔드가 백그라운드에서 실행 중인 경우입니다. `netstat -ano | findstr 8000`으로 PID를 확인하거나, 현재 가동 중인 백엔드 서버를 그대로 사용하시면 됩니다.

### Q2. 모바일 앱에서 백엔드 연결 오류(Network Error)가 발생할 때
- 모바일 디바이스와 PC가 동일한 Wi-Fi 네트워크에 연결되어 있는지 확인하고, `mobile/.env` 또는 `api.ts`의 `BASE_URL`이 PC의 로컬 IP(예: `http://192.168.x.x:8000`)로 지정되어 있는지 확인합니다.

### Q3. 테스트 중 일부 모듈이 실패할 때
- `.\run_tests.bat --no-pause`를 실행하여 실패한 파일의 로그를 확인하거나, `.venv\Scripts\python -m pytest tests/<failed_test>.py -v`로 개별 디버깅합니다.
