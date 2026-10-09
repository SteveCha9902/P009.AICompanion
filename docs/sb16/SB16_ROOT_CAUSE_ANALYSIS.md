# [SB-16 Doc 12] Technical Root Cause Analysis

- **작성자**: 🐟 코다리 (Lead Architect) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-02
- **스프린트**: SB-16 Real User Pilot & Product Validation

---

## 1. Root Cause Breakdown

1. **ISS-01 (응답 길이 과다)**: System Prompt 내 Max Sentence Constraint 부재 ➔ `Prompt Engineering` & `Response Length Tuner`로 해결.
2. **ISS-02 (조용한 공감 부재)**: 대화 엔진이 항상 Follow-up Question을 던지도록 유도됨 ➔ `Empathy Mode Classifier` 도입 필요.
3. **ISS-03 (TTS 버퍼 지연)**: 오디오 청크 스트리밍 청크 크기 미세 조정 필요 ➔ `Audio Streaming Optimizer`.
4. **ISS-04 (Quiet Hours 부재)**: 사용자 시간대 기반 Proactive 억제 필터 미적용 ➔ `Presence Schedule Filter`.
