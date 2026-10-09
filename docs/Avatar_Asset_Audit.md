# Avatar Asset Audit Report (Avatar_Asset_Audit.md)

**Sprint 40: Avatar Asset Audit & Real-Time Renderer PoC**  
**작성자**: 🐟 코다리 Architect & 🌸 진달래 주임 (Vision/Mobile)  
**일자**: 2026-08-30

---

## 1. 현재 아바타 자산 정밀 조사

| 조사 항목 | 조사 결과 | 상세 내용 |
| :--- | :--- | :--- |
| **캐릭터 명칭** | Genie (지니) | P009.AICompanion 대표 AI 비주얼 페르소나 |
| **자산 원본 유형** | **AI 생성 고해상도 포트레이트 (AI-Generated Image)** | Midjourney/Stable Diffusion 기반 극사실 2.5D 한국인 여성 포트레이트 |
| **실사 영상 여부** | ❌ 실사 인물 아님 | AI로 렌더링된 인공 캐릭터 (초상권 이슈 없음) |
| **현재 보유 포맷** | JPG 포트레이트 5종 + MP4 4종 | `neutral.jpg`, `smile.jpg`, `speaking.jpg`, `thinking.jpg`, `listening.jpg` |
| **원본 해상도** | 1024 x 1024 px (고해상도) | 모바일 Retina 디스플레이(2x/3x) 완벽 지원 |
| **원본 PSD 존재 여부** | ❌ 원본 단일 레이어 이미지 | 단일 비트맵 이미지로 구성되어 있어 파츠 분리 작업 필요 |
| **저작권 / 라이선스** | ✅ 자체 생성 상업용 라이선스 | 프로젝트 독점 소유 라이선스 클리어 |

---

## 2. Layer Extraction Feasibility Test (레이어 분리 타당성 검증)

현재 `neutral.jpg`와 `smile.jpg`를 대상으로 파츠 분리 가능성을 검증한 결과입니다:

### (1) 베이스 신체/얼굴 (Base Body & Face)
- **분리 난이도**: **LOW (매우 용이)**
- **전략**: 눈, 눈썹, 입을 Inpainting(인페인팅)으로 매끄러운 피부톤으로 메운 클린 베이스(Clean Base Portrait) 생성 가능.

### (2) 눈 영역 (Eyes Open, Half, Blink)
- **분리 난이도**: **MEDIUM (용이)**
- **전략**:
  - `eyes_open`: 기본 상태에서 눈 영역만 크롭 및 알파 마스킹.
  - `eyes_closed`: 피부톤 눈꺼풀 텍스처를 오버레이하여 120ms 순식간에 눈을 감는 Blink 구현 완료 (PoC 검증 완료).

### (3) 입 및 립싱크 영역 (Mouth Visemes)
- **분리 난이도**: **MEDIUM (용이)**
- **전략**:
  - `mouth_closed`: 기본 닫힌 입.
  - `mouth_open / visemes`: 입 내부(치아, 혀, 어두운 구강)와 입술을 파라미터 스케일링으로 합성 가능.

### (4) 눈썹 및 표정 (Eyebrows)
- **분리 난이도**: **LOW (매우 용이)**
- **전략**: 투명 알파 배경의 눈썹 파츠를 추출하여 ±3px Y축 이동으로 찡그림/놀람/경청 표현 가능.

---

## 3. 종합 평가
현재 보유한 AI 생성 고해상도 포트레이트는 **실시간 2.5D 레이어드 캐릭터 렌더러로 전환하기에 100% 충분한 해상도와 시각적 품질**을 갖추고 있습니다.
