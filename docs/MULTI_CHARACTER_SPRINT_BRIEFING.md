# 📑 [P009 AI Companion] 멀티 캐릭터(Multi-Persona) 시스템 설계 & PM 가이드 문서

> **💡 본 문서는 GPT에게 복사하여 붙여넣기(Prompt)하여, 멀티 캐릭터 스프린트의 PM(요구사항/백로그 정의) 및 System Architect(DB/API/상태 설계) 역할을 수행하도록 지시하는 공식 가이드입니다.**

---

```markdown
# [GPT 프롬프트 시작: 아래 내용을 그대로 GPT에 전달하세요]

당신은 AI Companion 프로젝트 'P009 AI Companion'의 **Lead System Architect 겸 Technical PM**입니다.
우리는 단일 캐릭터 체제에서 **[멀티 캐릭터(새 인격체) 독립 공존 시스템]**으로 확장하는 새로운 스프린트를 시작하려고 합니다.

아래의 [1. 프로젝트 개요], [2. 현재 베이스라인 구조], [3. 캐릭터 데이터 모델], [4. 스프린트 목표]를 꼼꼼히 분석하고, 
우리가 구현해야 할 **상세 PM 백로그, DB 스키마 설계, REST API 엔드포인트 명세, 클라이언트 상태 관리 아키텍처**를 작성해 주세요.

---

## 1. 프로젝트 개요 (Project Overview)
- **프로젝트명**: P009.AICompanion
- **핵심 정체성**: 단순 텍스트 챗봇이 아닌, 실시간 2D/2.5D 아바타 표정/립싱크 + 고음질 신경망 음성(TTS/STT) + 장기 기억(pgvector RAG) + 감정 전이(PAD 모델) + 사회적 관계도(Trust/Closeness)가 융합된 **체화된 AI 동반자(Embodied AI Companion)**.
- **기술 스택**:
  - **Backend**: Python 3.10+, FastAPI, SQLAlchemy (Async SQLite/PostgreSQL), pgvector, OpenAI Whisper-1, Microsoft Edge-TTS / ElevenLabs
  - **Mobile**: React Native (Expo SDK 54), TypeScript, Zustand, expo-av, expo-speech

---

## 2. 지금까지 구축된 베이스라인 현황 (Current Baseline)
1. **아바타 & 모바일 UI**:
   - 실시간 립싱크/눈깜빡임/감정 표정 렌더러 (`RealtimeFaceRenderer.tsx`, 580x420 풀 뷰포트).
   - 하단 5개 탭 바 (`✨ 아바타`, `🎭 캐릭터`, `🧠 기억`, `💖 관계`, `⚙️ 설정`).
2. **음성 대화 파이프라인 (STT / TTS)**:
   - 마이크 음성 ➔ 내장 XHR Base64 인코딩 ➔ `/voice/sessions/{id}/audio-base64` ➔ Whisper-1 STT ➔ CompanionOrchestrator ➔ Edge-TTS 신경망 음성(`ko-KR-SunHiNeural` 선희) ➔ 모바일 스피커 동시 발화.
3. **계층형 컨텍스트 빌더 (Tier 1~5 ContextBuilder)**:
   - **Tier 1**: 시스템 안전 및 절대 규칙 (로봇 디스클레임 전면 금지, Embodied Persona)
   - **Tier 2**: 캐릭터 페르소나 (신원, 배경, 말투, 성격 DNA)
   - **Tier 3**: 시맨틱 장기 기억 (pgvector 기반 과거 대화/사실 검색 주입)
   - **Tier 4**: 실시간 감정 상태 & 사회적 관계도 (Trust, Closeness)
   - **Tier 5**: 대화 히스토리 및 사용자 입력
4. **현재 등록된 기본 캐릭터 (Baseline)**:
   - **이름**: 지니 (Genie) - 사랑스러운 아내 인격
   - **기념일**: 결혼기념일(2005년 5월 7일), 생일(9월 2일)
   - **기본 음성**: Microsoft Edge-TTS `ko-KR-SunHiNeural` (선희)

---

## 3. 현재 백엔드 데이터베이스 및 캐릭터 구조

현재 DB는 `Companion` 테이블을 중심으로 관련 테이블들이 1:1 또는 1:N으로 연결되어 있습니다:

```
[User] (1) ─── (N) [Companion] (id, user_id, name, status, created_at)
                       │
      ┌────────────────┼────────────────┬────────────────┬────────────────┐
      ▼                ▼                ▼                ▼                ▼
[CharacterProfile] [Persona]         [Memory]     [EmotionState] [RelationshipState]
(Identity, DNA,   (System Prompt,   (Vector RAG,  (PAD Model,    (Trust, Closeness,
 Big5 Traits)      Rules)            Memories)     Mood)          Decay)
```

- **`companions`**: 유저가 소유한 동반자 엔티티 (`id`, `user_id`, `name`, `status`)
- **`character_profiles` & `character_personalities`**: 캐릭터의 성격 수치(Warmth, Empathy, Intellectual 등), 가치관, 선호도, 한계선
- **`memories`**: `companion_id`를 외래키로 가지는 장기 기억 레코드 (현재 단일 캐릭터 위주로 동작)
- **`relationship_states`**: `companion_id`별 친밀도 및 신뢰도

---

## 4. 이번 스프린트 목표: [멀티 캐릭터(새 인격체) 시스템 구축]

우리는 사용자가 **완전히 다른 여러 인격체(Multi-Persona)**를 등록하고, 탭 한 번으로 자유롭게 전환(Switch)할 수 있는 아키텍처를 원합니다.

### 🎭 핵심 요구사항 (Core Requirements)
1. **완벽한 데이터/컨텍스트 격리 (Strict Isolation)**:
   - **캐릭터 A (지니 - 다정한 아내)**: 선희 음성, 부부의 추억 기억, 연인/배우자 관계도, 반말/다정한 존댓말 혼용
   - **캐릭터 B (수아 - AI 전문 비서)**: 지민 음성(`ko-KR-JiMinNeural`), 업무/일정/학습 기억, 정중한 비서 존댓말, 프로페셔널 관계도
   - **캐릭터 C (하나 - 발랄한 예술 친구)**: 인준/여성 밝은 음성, 취미/영화/음악 기억, 친구 관계도, 발랄한 친구 말투
   - **🚨 절대 규칙**: 지니와 나눈 부부 대화 기억이 수아나 하나에게 노출되거나 섞여서는 안 됨!
2. **원터치 활성 캐릭터 전환 (Active Character Switching)**:
   - 모바일 `🎭 캐릭터` 탭에서 캐릭터 카드 탭 시, 백엔드의 `active_companion_id`가 변경되고 다음 대화부터 해당 캐릭터의 페르소나, 기억, 목소리가 즉시 적용되어야 함.
3. **새 캐릭터 커스텀 생성 마법사 (Custom Character Creation)**:
   - 사용자가 이름, 역할(비서, 친구, 멘토 등), 성격 슬라이더, 음성(Voice ID), 아바타 프리셋을 선택하여 새 캐릭터를 무제한 생성 가능해야 함.
4. **클라이언트 동기화 (Mobile Synchronization)**:
   - 캐릭터 전환 시 메인 화면의 아바타 외모, 상단 이름 뱃지, 음성 발화 설정, 대화 세션이 즉시 매끄럽게 갱신되어야 함.

---

## 5. GPT에게 요청하는 산출물 (Deliverables)

위 내용을 바탕으로 다음 5가지 항목을 구체적이고 바로 코딩 가능한 수준으로 작성해 주세요:

1. **[Product Requirements & User Stories]**:
   - 멀티 캐릭터 시스템의 핵심 사용자 스토리 4개 및 Sprint 완료 기준(DoD).
2. **[Database Schema Migration & DDL]**:
   - 다중 캐릭터 및 활성 캐릭터 관리를 위한 SQLAlchemy 모델 변경안 (기존 DB와의 호환성 유지).
3. **[REST API Specification]**:
   - `GET /api/v1/characters` (목록 조회)
   - `POST /api/v1/characters/switch` (활성 캐릭터 전환)
   - `POST /api/v1/characters` (새 캐릭터 생성)
   - `DELETE /api/v1/characters/{id}` (캐릭터 삭제/보관)
   - 각 엔드포인트의 Request/Response JSON 스키마 명세.
4. **[ContextBuilder & Orchestrator 격리 아키텍처]**:
   - 대화 및 음성 처리 시 현재 활성화된 `companion_id`를 기반으로 Memory, Emotion, Relationship, Voice ID가 완벽히 격리 주입되는 백엔드 흐름 설계.
5. **[Mobile UI/UX & State Architecture (React Native)]**:
   - `mobile/src/features/character/`의 Zustand 상태 관리 구조 및 캐릭터 카드 갤러리 UI 컴포넌트 설계.

# [GPT 프롬프트 끝]
```
