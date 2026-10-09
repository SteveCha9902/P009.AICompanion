# P009.AICompanion - Sprint 28 Proactive Intelligence Audit Report
**Proactive Intelligence & Personal Routine Engine Audit**

---

## 1. 개요
Sprint 28에서는 컴패니언이 수동적인 응답자를 넘어, 사용자의 일상 맥락과 루틴을 이해하고 **"지금 먼저 말을 거는 것이 정말 도움이 되는지"** 판단하며, 불필요할 때는 **침묵할 줄 아는(Silence / Should I Act?)** Proactive Intelligence Layer를 완성하기 위해 전수 감사를 수행하였습니다.

---

## 2. 7대 핵심 질문 분석 결과

### Q1. Proactive Trigger가 어디에서 발생하는가?
- **트리거 진입점**: 시간 경과(`LONG_ABSENCE`, `TIME_BASED`), 재방문(`RETURNED_USER`), 사용자 목표/기억 리콜(`GOAL_REMINDER`, `MEMORY_RECALL`), 일상 루틴(`ROUTINE_DETECTED`).

### Q2. 어떤 Context를 사용하는가?
- **평가 컨텍스트**: `PresenceState` (온라인/오프라인/수면), `RelationshipState` (친밀도 레벨), `MemoryItem` (관련 기억 존재 여부), 현재 시각(`now`), 사용자 설정(`ProactiveSettings`).

### Q3. Notification을 누가 결정하는가?
- **결정 주체**: `ProactivePolicyEngine`이 Master Switch, Presence, Quiet Hours, Daily Limit, Cooldown 및 가중치 Score(`>= 0.60`)를 검증하여 `ALLOW` / `DENY`를 단독 판정.

### Q4. 중복 알림은 어떻게 방지하는가?
- **Anti-Spam 2.0**: 최근 발송된 알림 기록(`get_recent_events`)과 쿨다운 시간(기본 4시간), 일일 상한(기본 3회), 동일 주제 반복 억제(Topic Cooldown) 적용.

### Q5. 사용자가 거부(Opt-Out)할 방법이 있는가?
- **사용자 제어권**: 모바일 `ProactiveSettingsScreen`에서 마스터 스위치, 일일 한도, 방해 금지 시간대(Quiet Hours), 루틴 제안 여부를 자유롭게 설정 가능.

### Q6. 앱이 Background일 때 어떤 방식으로 동작하는가?
- **프라이버시 경계**: 백그라운드에서는 카메라/마이크/비전 캡처가 100% OFF 상태를 유지하며, 오직 OS의 로컬 알림(Local Notification)만 안전하게 트리거.

### Q7. Proactive Action이 Memory / Relationship에 어떤 영향을 주는가?
- **상호작용 반영**: 사용자가 알림을 탭하여 복귀(`NOTIFICATION_OPENED` / `RESPOND`) 시 긍정적 신호로 기록되어 유대감 강화에 기여. 무시/거부 시 부정적 신호 학습으로 알림 빈도 자동 감쇠.
