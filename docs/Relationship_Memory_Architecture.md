# Relationship Memory Architecture (Sprint 50)

본 문서는 Sprint 50에서 구축된 **Relationship Memory & Persistent Companion Engine**의 전체 시스템 아키텍처, 5번째 인지 계층(Relationship Memory Layer) 및 회상 파이프라인 데이터 흐름을 정의합니다.

---

## 🏛️ 1. 전체 아키텍처 구조

```text
[Conversation Utterance] + [Visual Awareness Tags] + [Shared Reality Context]
                            │
                            ▼
              [CandidateExtractor]
                            │
                            ▼
              [PrivacyFilterEngine] (Sensitive Health/Finance/Political Exclusion)
                            │
                            ▼
              [ImportanceScoringEngine] (3-Axis: Importance x Future x Relationship)
                            │
                            ▼
              [RelationshipMemoryStore] (Category TTL + Pin + Review + Forget)
                            │
                            ▼
              [RecallRankingEngine] (4-Factor Product: Relevance x Recency x Imp x Conf)
                            │
                            ▼
              [MemoryVerificationLayer] (Confident vs Tentative Framing vs Block)
                            │
                            ▼
              [RelationshipMemoryContextProvider] ➔ [ContextBuilder] ➔ [LLM]
```

---

## 📦 2. 5번째 인지 계층: 9대 MemoryType & Category TTL

| Memory Type | 설명 | 기본 TTL 수명 | 주요 예시 |
| :--- | :--- | :--- | :--- |
| **PET** | 반려동물 | **영구 (No Expiry)** | "새 강아지를 입양했어", "고양이 이름은 나비야" |
| **PERSON** | 가족, 소중한 친구 | **영구 (No Expiry)** | "우리 언니 결혼식", "친한 친구 민수" |
| **GOAL** | 개인적 결심, 목표 | **365일 (1년)** | "올해 안에 자격증 취득하기", "다이어트 5kg" |
| **PROJECT** | 진행 중인 주요 과제 | **180일 (6개월)** | "AI 컴패니언 개발 및 론칭", "신규 웹앱 제작" |
| **HOBBY** | 지속적 여가, 취미 | **180일 (6개월)** | "기타 레슨 시작", "주말마다 수영하기" |
| **PREFERENCE** | 개인 기호 및 취향 | **180일 (6개월)** | "라떼만 마심", "민트초코 좋아함" |
| **PLACE** | 의미 있는 장소 | **120일 (4개월)** | "제주도 여행", "자주 가는 아지트 카페" |
| **OBJECT** | 의미 있는 사물, 화분 | **60일 (2개월)** | "반려식물 몬스테라", "새로 산 텀블러" |
| **EVENT** | 일회성 특별 이벤트 | **45일 (1.5개월)** | "좋아하는 가수 콘서트", "친구 집들이" |

---

## 🎯 3. 핵심 설계 원칙

1. **3-Axis Importance Scoring Matrix**:
   - `CompositeScore = Importance × FutureRelevance × RelationshipValue`
   - 일회성 회식/점심(0.05)과 같은 노이즈는 저장하지 않고, 중요한 삶의 순간만 선별 기억.
2. **Visual Memory Link (Visual Signature Object Tags)**:
   - 원본 이미지는 저장하지 않고 객체 태그(`PLANT:monstera`, `CUP`, `PET`)만 기억과 연결하여, 카메라에 해당 사물이 등장했을 때 자연스러운 회상 트리거 작동.
3. **Recall Ranking Engine (4-Factor Product)**:
   - `RecallScore = Relevance × Recency × Importance × EffectiveConfidence`
   - 상위 1~3개의 최적 기억만 선별하여 프롬프트 오염 및 기억 과잉 회상 방지.
4. **False Memory Protection (Verification Guard)**:
   - `Confidence < 0.70`은 완곡한 표현("내가 잘 기억하는지 모르겠지만...")을 적용하고, `Confidence < 0.50`은 회상을 원천 차단.
5. **User-Controlled Memory Center**:
   - 사용자가 언제든 기억 목록을 확인(Review), 영구 고정(Pin), 개별 삭제(Delete), 전체 망각(Forget All)할 수 있는 완벽한 통제권 부여.
