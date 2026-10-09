# [SB-5 Architecture 3] Character Update Classification & Impact Rules

- **작성자**: 🐍 미나리 (Backend Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-5 Character Lifecycle Management & Safe Evolution

---

## 1. 4단계 변경 분류 체계 (Change Classification)

| 분류 | 발생 시점 및 항목 | 버전 생성 여부 | 처리 방식 |
| :--- | :--- | :--- | :--- |
| **`INITIAL`** | 신규 캐릭터 최초 생성 시 (`POST /characters`) | **Yes (Version 1)** | 초기 DNA 스냅샷 영속화 |
| **`COSMETIC`** | Avatar Preset, Voice ID, 단순 표시 메타데이터 | **No (버전 불변)** | 프로필 레코드 즉시 갱신 |
| **`MINOR`** | Speaking Style, Personality Keywords 미세 조정 | **Yes (버전 +1)** | 기존 DNA에 모디파이어 재합성 및 스냅샷 기록 |
| **`MAJOR`** | MBTI 변경, Core Values 대폭 수정, Role Title 재정의 | **Yes (버전 +1)** | PersonalityCompiler 완전 재컴파일 및 스냅샷 기록 |

---

## 2. Memory Continuity 보장

- `MAJOR` 변경이라도 기존 대화와 기억을 리셋하지 않으며, "성격이 새롭게 진화한 캐릭터"로서 기존 사용자와의 과거를 기억하며 대화를 이어갑니다.
