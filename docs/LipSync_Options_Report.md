# Lip-Sync Feasibility & Options Report (LipSync_Options_Report.md)

**Sprint 40: Avatar Asset Audit & Real-Time Renderer PoC**  
**작성자**: 🐍 미나리 과장 (Backend) & 🌸 진달래 주임 (Vision/Mobile)  
**일자**: 2026-08-30

---

## 1. 립싱크(Lip-Sync) 3대 구현 방식 비교

| 비교 항목 | 방법 1: Audio Amplitude (진폭 기반) | 방법 2: Phoneme (음소 분석 기반) | 방법 3: Viseme (시각적 입모양 매핑) |
| :--- | :--- | :--- | :--- |
| **원리** | 음성의 RMS 볼륨 크기에 따라 입 벌림(`mouth_open`) 조절 | TTS 오디오 음성 파형을 시간별 음소(ㄱ, ㄴ, ㅏ, ㅗ 등)로 분해 | 한국어 5대 대표 모음(A, E, I, O, U)을 시각적 입모양으로 매핑 |
| **장점** | 구현이 매우 간단하고 실시간 레이턴시가 0ms에 수렴 | 단어 발음과 입술 모양이 100% 정밀하게 일치 | 계산량이 적으면서도 자연스러운 조음(Articulation) 표현 |
| **단점** | '오'나 '우' 같은 입모양 형태 구분이 불가 (상하로만 벌어짐) | 고성능 음소 추출 파서(Forced Aligner) 필요로 지연 가능 | 음소 단위 추출 데이터가 없을 시 주기적 보간 필요 |
| **적합성** | **Phase 1 기본 보조로 채택** | **Phase 3 정밀 고도화용** | **Phase 1~2 메인 엔진으로 채택 (권장)** |

---

## 2. P009 권장 립싱크 하이브리드 파이프라인

1. **현재 (Sprint 40 PoC 구현)**:
   - **Viseme Cycle + Audio Amplitude Hybrid**:
   - 오디오 출력 중 100ms 간격으로 대표 Viseme(A, E, I, O, U)을 부드럽게 순환하면서 볼륨 진폭에 따라 `mouth_open` 스케일을 0.2~0.8로 가변 조절.
   - ➔ 동영상 루프와 달리 **실제 발화 시작과 끝에 정확히 동기화**되어 "실제로 말하고 있다"는 강한 체감을 제공.
2. **후속 고도화 (Sprint 41~42)**:
   - OpenAI TTS / Google TTS의 타임스탬프 메타데이터(Word Timestamp)를 수신하여 음소별 Viseme 직접 매핑.
