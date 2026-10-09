# P009.AICompanion - Real User Journey Test Report

---

## 1. Scenario A — 첫 만남 (First Impression)
- **흐름**: 앱 실행 ➔ INITIALIZING ➔ ONLINE 배지 표시 ➔ "안녕!" 인사 ➔ 따뜻하고 자연스러운 환영 응답 및 아바타 미소.
- **결과**: 첫 30초 내 단순 챗봇 이상의 온화한 동반자적 느낌 전달 성공.

---

## 2. Scenario B — 일상 대화 및 연속성 (Daily Conversation & Context)
- **Day 1**: "오늘 회사에서 일이 너무 많아서 힘들었어." ➔ 공감 및 위로 응답 (Emotion: Empathy, Avatar: Soft).
- **Day 2**: "어제 이야기했던 그 프로젝트 말인데..." ➔ 이전 세션 기억을 바탕으로 대화 자연스럽게 연결.
- **결과**: 세션 간 맥락 유지 100% 성공.

---

## 3. Scenario C — Multimodal & User Interrupt
- **음성/비전 질문**: "오늘 내 얼굴 표정 어때 보여?" ➔ 카메라 4초 관찰 ➔ `FACE_DETECTED` ➔ "조금 피곤해 보이지만 편안해 보여요."
- **인터럽트**: AI 답변 도중 마이크 터치 ➔ 50ms 내 음성 중단 및 `LISTENING` 전이 ➔ 새 질문 정상 처리.
- **결과**: 음성/시각/아바타 상호작용 지연 없는 부드러운 전이 확인.
