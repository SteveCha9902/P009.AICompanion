# P009.AICompanion Master Architecture

## 1. System Overview
P009.AICompanion은 Mobile-First 기반의 AI 애플리케이션으로, 프론트엔드(Mobile Client)와 백엔드(FastAPI + AI Core)로 구성됩니다.

```text
                  [ User / Mobile Client ]
                             │
                (REST / WebSocket / Push)
                             │
                  [ FastAPI Backend ]
                             │
       ┌─────────────────────┴─────────────────────┐
       │                                           │
  [ Ambient Mode Engine ]                  [ AI Core Engines ]
  - Notification Scheduler                 - Memory Engine
  - Event Trigger                          - Emotion Engine
                                           - Relationship Engine
                                           - Persona Engine
                                           - Context Builder
                                           - Behavior Engine
                                           - Vision Pipeline
                                           - LLM Engine
                             │
                  [ PostgreSQL (pgvector) ]
```

## 2. Companion Core (Single Source of Truth)
모바일 앱이 **Ambient Mode** 상태이든 **Avatar Mode** 상태이든 상관없이, 단 하나의 `Companion Core` 상태를 공유합니다. 
UI는 단지 Companion 상태의 Presenter 역할을 할 뿐이며, AI 비즈니스 로직(Memory, Emotion 등)을 프론트엔드에 의존시키지 않습니다.

## 3. Technology Stack
- **Mobile Client**: React Native + Expo
- **Backend API**: Python 3.11+, FastAPI
- **Database**: PostgreSQL + pgvector (Vector DB for Memory)
- **Cache/Queue**: Redis (for Event Engine & Session)
- **AI/LLM Provider**: OpenAI (추상화 모듈 적용)
