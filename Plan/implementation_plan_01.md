# SPRINT 1 PRE-IMPLEMENTATION REPORT

> [!NOTE]
> 본 리포트는 P009.AICompanion Sprint 1 (Mobile App Foundation)의 실제 구현을 시작하기 전 수행된 사전 분석 및 실행 계획서입니다. 코드를 수정하기 전, 요구사항과 아키텍처 원칙(Companion Core 분리, 확장성)에 입각하여 작성되었습니다.

---

## 1. Current Repository Structure
- 현재 `P009.AICompanion/` 디렉토리 내부에는 Sprint 0에서 작성된 `docs/` (총 12개의 아키텍처 마크다운 문서)만 존재합니다.
- 실제 소스코드 폴더(`mobile/`, `backend/`, `ai/` 등)는 스캐폴딩되지 않은 100% Zero-base 상태입니다.

## 2. Current Technology Stack
- **존재하는 기술 스택 없음.** (아직 프레임워크나 라이브러리가 하나도 설치되지 않음)

## 3. Existing Mobile Components
- 없음.

## 4. Existing Backend Components
- 없음.

## 5. Sprint 0 Architecture와의 일치 여부
- **일치함.** Sprint 0에서 확인된 바와 같이 레거시 의존성이 전혀 없으므로, Master Specification v2.0이 지시하는 "React Native + Expo" 모바일 우선 구조와 "FastAPI" 백엔드 기초 뼈대를 충돌 없이 즉각 구축할 수 있습니다.

## 6. Missing Components (Sprint 1 대상)
- Mobile App Shell (Expo 프로젝트)
- Cross-platform Navigation (React Navigation)
- Adaptive Layout System (Smartphone/Tablet 분기)
- Application State Management
- Secure Storage Abstraction Layer
- Backend API Client Service
- Backend Health-check API (FastAPI)

---

## 7. Recommended Mobile Architecture
- **Framework**: `React Native` + `Expo` (TypeScript 기반)
- **UI & Layout**: 컴포넌트 기반 아키텍처로 UI와 비즈니스/API 로직 완전 분리. `react-native-safe-area-context`를 이용해 노치/Safe Area를 방어하고, 해상도 분기 로직(Dimensions API)을 통해 Phone/Tablet 레이아웃을 분기합니다.

## 8. Recommended Folder Structure
요구사항에서 권장한 구조를 그대로 따르며, 핵심(Business/API)과 표면(UI)을 명확히 나눕니다.
```text
P009.AICompanion/
├── mobile/
│   ├── app.json (Expo Config)
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── components/  # 재사용 가능한 UI 컴포넌트
│   │   ├── screens/     # Home, Conversation, Memories, Relationship, Settings (Placeholder)
│   │   ├── navigation/  # RootNavigator 및 Tab/Stack 라우팅
│   │   ├── services/    # api.ts, storage.ts (Backend 연동 및 Secure Storage)
│   │   ├── state/       # 전역 상태 관리 (Companion State 대비)
│   │   ├── types/       # TypeScript Interface/Type 정의
│   │   ├── utils/       # 반응형 크기 계산(Responsive), 디바이스 분기 유틸
│   │   └── constants/   # Theme(Colors), Environment URL 등
│   └── assets/
└── backend/
    ├── requirements.txt
    └── app/
        └── main.py      # /health 엔드포인트 단일 제공용
```

## 9. Technology Decisions
1. **React Native / Expo 적용**: 
   - **결정**: 채택 (Managed Workflow로 시작하되 향후 Vision 모듈이 C++ 프레임 프로세서를 요구할 경우 Custom Dev Client로 원활한 Transition이 가능함).
2. **State Management (상태 관리)**: 
   - **결정**: `Zustand`
   - **근거**: 향후 `companion_state`, `user_context`, `emotion` 등 다중 상태 트리가 발생할 텐데, Redux는 보일러플레이트가 과도하고 Context API는 리렌더링 최적화가 어렵습니다. Zustand는 가벼우면서도 Companion Core State를 담기에 충분한 유연성과 성능을 제공합니다.
3. **API 통신 구조**:
   - **결정**: `axios` 또는 `fetch` 기반의 싱글톤 API 클라이언트 (`services/api.ts`). UI 컴포넌트 내부에서의 직접 fetch 호출을 엄격히 금지합니다.
4. **Secure Storage 전략**:
   - **결정**: `expo-secure-store`를 활용하여 `services/storage.ts`에 Interface(get/save/remove)화.

## 10. Architecture Risks
> [!CAUTION]
> 1. **Expo Managed Workflow 제약**: 향후 Sprint 9(Vision) 도입 시 실시간 프레임 분석 라이브러리 연동이 Expo Managed에서 막힐 수 있습니다. 초기부터 네이티브 코드 분리를 고려한 플러그인 설정 기반(EAS Build)을 염두에 두어야 합니다.
> 2. **Tablet 대응 복잡도**: 단순 `width: 100%` 처리 시 태블릿에서 버튼이나 텍스트가 심각하게 늘어납니다. 컴포넌트 설계 시 처음부터 Container 사이즈에 반응형으로 동작하도록 최소한의 Constraint를 정의해야 합니다.

---

## 11. Sprint 1 Implementation Plan
아래 순서로 Sprint 1 코드를 작성합니다.

1. **Backend Foundation**: `backend/` 폴더를 만들고 FastAPI로 단순 `GET /health` API 생성. (Uvicorn으로 로컬 구동 테스트)
2. **Mobile Foundation**: `mobile/` 폴더에 `npx create-expo-app`을 통해 TypeScript 템플릿 프로젝트 생성.
3. **Environment**: `.env` 세팅 및 `expo-constants`로 API_URL 로딩.
4. **Navigation**: `react-navigation`을 설치하고 BottomTabs(스마트폰) / Drawer(태블릿) 혹은 단순 Root 구조 확보 및 5대 Screen 껍데기(Placeholder) 생성.
5. **State & Storage**: `Zustand` 기반 빈 스토어 작성, `expo-secure-store` 모듈로 스토리지 서비스 계층 구축.
6. **API Service**: `services/api.ts` 구축 및 Home 화면에 Backend Health-check 연동 결과 텍스트 출력.
7. **Responsive Check**: 디바이스 크기를 읽어 Smartphone/Tablet 여부를 판단하는 훅 작성.

## 12. 예상 변경(생성) 파일 목록
- **Mobile (`mobile/*`)**:
  - `package.json`, `app.json`, `babel.config.js`
  - `App.tsx` (엔트리 및 Provider 셋업)
  - `src/navigation/RootNavigator.tsx`
  - `src/screens/HomeScreen.tsx`, `ConversationScreen.tsx`, `SettingsScreen.tsx`, `MemoriesScreen.tsx`, `RelationshipScreen.tsx`
  - `src/services/api.ts`, `src/services/storage.ts`
  - `src/state/useAppStore.ts`
  - `src/utils/responsive.ts`
- **Backend (`backend/*`)**:
  - `requirements.txt`
  - `app/main.py` (Health check)

---

> 본 Sprint 1 사전 분석 보고서를 검토해주십시오. 계획에 문제가 없다고 승인하시면 즉시 **STEP 5. Mobile Foundation 구현**부터 실제 코딩을 시작하여 **Definition of Done** 상태까지 도달시키겠습니다.
