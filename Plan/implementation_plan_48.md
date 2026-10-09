# Implementation Plan — Sprint 48: Visual Awareness & Companion Perception Engine

## 🎯 Sprint Mission
> "캐릭터가 사용자를 보고, 사용자의 상태를 이해하고, 주변 환경을 인식하여 반응한다."
> 사용자와 같은 공간을 인지하는 동반자(Companion) 경험을 구축하되, 철저한 **Privacy First(제로 원본 저장, 명시적 동의 제어)** 원칙을 준수합니다.

---

## 👥 에이전트별 역할 및 작업 분담

- **🧭 세종이 PM**: Sprint 48 목표 관리, Privacy First 원칙(기본값 OFF, 사용자 제어) 및 Exit Criteria 획정
- **🐟 코다리 Architect**: Awareness Architecture 설계, `AwarenessContext` DTO 정의, 4번째 인지 레이어(Awareness Layer) 분리
- **🐍 미나리 과장**: `UserAwarenessEngine`, `EnvironmentAwarenessEngine`, `AwarenessReactionPlanner`, `AwarenessContextProvider` 구현
- **🌸 진달래 주임**: 모바일 `AwarenessBadge` / `VisualAwarenessOverlay`, `PrivacyDashboard` UI, 아바타 시선/관심도 연동
- **✍️ Amy**: `CompanionReactionGuide` (공감/호기심/격려/관찰형 반응 템플릿 및 단정형 금지 가이드라인)
- **🏃 정대리 QA**: Gate VA1 ~ VA6 검증 테스트 스위트 (`test_visual_awareness_perception_engine.py`) 및 전체 회귀 테스트
- **🔐 방대장 DevOps/Sec**: Zero Raw Frame Storage, Ephemeral In-Memory Processing, 데이터 유출 방지 및 Privacy Compliance Audit
- **📚 묵사관 Memory Keeper**: 5대 핵심 문서 작성 (`Visual_Awareness_Architecture.md`, `Awareness_Context_Spec.md`, `Companion_Reaction_Guide.md`, `Privacy_Rules.md`, `Sprint48_Report.md`)

---

## 🏛️ System Architecture

```text
[Camera Frame / Stub]
       │
       ▼
[Vision Analyzer / Provider]
       │
       ▼
[Awareness Engine Pipeline]
 ├─ UserAwarenessEngine (Face, Gaze, Attention, Emotion: smiling/neutral/fatigued/surprised)
 └─ EnvironmentAwarenessEngine (Scene Objects: cup, food, book, laptop, pet, plant, tv, window)
       │
       ▼
[AwarenessContext DTO]
       │
       ▼
[ContextBuilder: Memory + Emotion + Relationship + Awareness]
       │
       ▼
[AwarenessReactionPlanner] ➔ [CompanionOrchestrator] ➔ [Avatar Behavior Engine]
```

---

## 📋 Proposed Changes

### Backend Domain & Services
#### [NEW] [awareness_context.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/domain/awareness/awareness_context.py)
- `AwarenessContext`, `UserAwarenessState`, `EnvironmentAwarenessState`, `FacialEmotionType`, `SceneObjectType` DTO 정의.

#### [NEW] [user_awareness_engine.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/awareness/user_awareness_engine.py)
- 얼굴 감지, 시선(toward_camera/away), 집중도(0.0~1.0), 4대 기본 표정(웃음, 중립, 피곤함, 놀람) 정량 분석.

#### [NEW] [environment_awareness_engine.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/awareness/environment_awareness_engine.py)
- 8대 주요 객체(컵, 음식, 책, 노트북, 반려동물, 식물, TV, 창문) 감지 및 객체 맥락 분석.

#### [NEW] [reaction_planner.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/awareness/reaction_planner.py)
- Amy의 4대 반응 페르소나(공감형, 호기심형, 격려형, 관찰형) 기반 제안형 프롬프트 주입 및 단정형("너는 ~한다") 원천 차단.

#### [NEW] [awareness_provider.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/context/providers/awareness_provider.py)
- `ContextBuilder`에 통합되어 LLM 프롬프트에 시각 인지 컨텍스트를 주입하는 프로바이더.

#### [MODIFY] [orchestrator.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/companion/orchestrator.py)
- ContextBuilder에 AwarenessContextProvider 연결 및 응답 생성 시 시각 정보 활용.

#### [MODIFY] [provider_factory.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/providers/factory.py) & [adapters](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/app/services/vision/adapters/openai.py)
- Awareness 구조화 포맷 출력 지원.

### Mobile Frontend
#### [MODIFY] [CompanionScreen.tsx](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/screens/CompanionScreen.tsx)
- 상단 인지 상태 배지(👁️ Visual Awareness Pill: 사용자 감지 / 객체 감지 실시간 피드백).
- 카메라 On/Off 시 인지 상태 부드러운 전환.

#### [MODIFY] [SettingsScreen.tsx](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/mobile/src/screens/SettingsScreen.tsx)
- Privacy & Awareness 제어 섹션 (Visual Awareness 토글, 얼굴 인식 토글, 환경 분석 토글, Zero Data Storage 보장 안내).

### QA & Documentation
#### [NEW] [test_visual_awareness_perception_engine.py](file:///d:/99.Repos/00.AntiGGG/P009.AICompanion/backend/tests/test_visual_awareness_perception_engine.py)
- Gate VA1: User Detection (Face, Gaze, Attention)
- Gate VA2: Scene Object Detection (8 Object categories)
- Gate VA3: Awareness Accuracy & Context DTO Validation
- Gate VA4: Privacy Compliance (Ephemeral in-memory, Zero Raw Storage)
- Gate VA5: False Claim Prevention (Strict Non-Assertive Suggestive phrasing)
- Gate VA6: Reaction Naturalness & Avatar Behavior Alignment

#### [NEW] 5대 핵심 문서
- `docs/Visual_Awareness_Architecture.md`
- `docs/Awareness_Context_Spec.md`
- `docs/Companion_Reaction_Guide.md`
- `docs/Privacy_Rules.md`
- `docs/Sprint48_Report.md`

---

## 🧪 Verification Plan
1. **Automated Unit & Integration Tests**:
   - `backend/tests/test_visual_awareness_perception_engine.py` (Gate VA1 ~ VA6).
   - `cmd /c run_tests.bat --no-pause` 전체 110+ 테스트 및 모바일 TypeScript 0 Errors 검증.
2. **Privacy Audit**:
   - 프레임 버퍼가 분석 후 즉시 메모리 해제되고 디스크나 DB에 영구 보존되지 않음을 검증.
