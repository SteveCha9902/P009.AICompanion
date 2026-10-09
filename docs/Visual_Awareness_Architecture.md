# Visual Awareness & Companion Perception Architecture (Sprint 48)

본 문서는 Sprint 48에서 구축된 **Visual Awareness & Companion Perception Engine**의 전체 시스템 아키텍처, 4번째 인지 계층(Awareness Layer) 분리 및 데이터 흐름을 정의합니다.

---

## 🏛️ 1. 전체 인지 파이프라인 구조

```text
[Camera Frame / Stub Stream]
             │
             ▼
[Vision Analyzer (OpenAI/Stub)] ── (Zero Raw Storage, In-Memory Only)
             │
             ▼
[Awareness Engine Pipeline]
   ├─ UserAwarenessEngine (Face, Gaze, Attention, 8-Tier Facial Emotion)
   └─ EnvironmentAwarenessEngine (8 Major Object Types, Confidence Thresholding, BBox)
             │
             ▼
[AwarenessContext DTO] (Freshness Validation, FocusTarget Resolution)
             │
             ▼
[AwarenessReactionPlanner] ── (ReactionBudgetManager, Non-Assertive Suggestive Guidance)
             │
             ▼
[ContextBuilder (4th Cognitive Layer)]
   ├─ Level 1: System & Safety Rules
   ├─ Level 2: Character Identity DNA
   ├─ Level 3: Application State (Memory, Emotion, Relationship)
   ├─ Level 4: Observation (Awareness Guidance) ◄── [NEW]
   └─ Level 5: Untrusted Conversation History & Input
             │
             ▼
[CompanionOrchestrator] ➔ [Avatar Behavior Engine] ➔ [Avatar Renderer]
```

---

## 🔒 2. 핵심 아키텍처 원칙 (7대 설계 원칙)

1. **Privacy First (최상위 원칙)**:
   - 기본값: Visual Awareness OFF
   - 사용자 명시적 카메라 토글 시에만 활성화.
   - 디스크/DB에 원본 이미지 영구 저장 절대 금지 (Ephemeral Memory).
2. **Structured DTO Only (No Direct Raw Image to LLM)**:
   - Vision Analyzer가 추출한 정형화된 메타데이터 DTO만 LLM 컨텍스트에 전달.
   - 비용 절감, 속도 향상, 프라이버시 보호 극대화.
3. **8-Tier Facial Emotion Classification**:
   - `SMILING`, `NEUTRAL`, `FOCUSED`, `CONFUSED`, `THINKING`, `FATIGUED`, `SURPRISED`, `UNKNOWN`
4. **Confidence Thresholding (>= 0.70)**:
   - 낮은 신뢰도 객체는 자동 필터링하여 오인식 및 억측 반응 원천 차단.
5. **Awareness Freshness (Age <= 10s)**:
   - 10초 이상 경과된 과거 관측은 대화 주입에서 자동 제외.
6. **Visual Focus Target Binding**:
   - 아바타의 시선(USER_FACE, CUP, LAPTOP, PET 등)과 자연스러운 연동.
7. **Reaction Budget Controller**:
   - 분당 멘션 한도 및 25초 쿨다운을 적용하여 과도한 관찰 피로도 원천 방지.
