# TTS System Audit & Provider Evaluation Report (TTS_Audit_Report.md)

**문서 버전**: v1.0 Audit Report  
**감사 총괄**: 🐍 미나리 과장 & 🔐 방대장 (DevOps/Security)  
**일자**: 2026-08-30

---

## 1. 현재 TTS 환경 조사 결과

1. **현재 사용 중인 TTS 엔진**:
   - OpenAI Audio API (`tts-1` / `tts-1-hd` 모델, 음성 모델: `nova` / `alloy` / `shimmer` / `onyx`).
2. **음성 변경 가능 여부**:
   - **가능 (YES)**: `voice_id` 또는 `persona_type` 설정을 통해 4대 페르소나별 즉시 교체 가능.
3. **감정 제어 가능 여부**:
   - **부분 지원 (Prompt-based & Speed/Pitch Modulation)**: OpenAI TTS는 직접적인 SSML 태그를 지원하지 않으나, `EmotionalSpeechEngine`을 통해 텍스트 프롬프트 지시 및 재생 속도/피치 오프셋 파라미터로 정밀 감정 제어 달성.
4. **Voice Cloning 지원 여부**:
   - OpenAI TTS는 고정 음성만 지원. ElevenLabs 및 Azure Speech 연동을 통해 원클릭 보이스 클로닝 지원 아키텍처 완성 (`VoiceProviderFactory` 구축).
5. **비용 및 지연시간**:
   - OpenAI `tts-1`: $0.015 / 1k chars, 평균 지연시간 250~450ms (실시간 스트리밍 적합).
   - ElevenLabs: $0.18 / 1k chars, 평균 지연시간 400~800ms (초고품질 및 클로닝 적합).

---

## 2. TTS Provider 비교 평가표

| 항목 | OpenAI TTS | ElevenLabs | Azure Speech | Cartesia |
| :--- | :---: | :---: | :---: | :---: |
| **한국어 자연스러움** | 상 (Very Good) | 최상 (Hyper-Realistic) | 상 (Good) | 중상 (Fast) |
| **실시간 레이턴시** | **250ms (Fast)** | 450ms | 300ms | **150ms (Ultra-fast)** |
| **감정 및 SSML 제어** | 중 (Speed/Style) | **최상 (Stability/Clarity)** | **최상 (Full SSML)** | 상 |
| **Voice Cloning** | 불가 | **지원 (Instant/Pro)** | 지원 (Custom Neural) | 지원 |
| **비용 효율성** | **최상 ($0.015/1k)** | 중 ($0.18/1k) | 상 ($0.016/1k) | 상 |
| **장기 추천** | **운영/대화 기본용** | **프리미엄/클로닝용** | 엔터프라이즈 확장용 | 초저지연 음성통화용 |
