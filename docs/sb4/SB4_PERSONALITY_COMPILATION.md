# [SB-4 Architecture 3] Personality Compilation & Trait Vector Synthesis

- **작성자**: 🐍 미나리 (Backend Lead) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-4 Character Creation Engine & Personality DNA Factory

---

## 1. 성격 컴파일 파이프라인 (Personality Compilation Pipeline)

사용자가 복잡한 15개 Trait 수치를 직접 입력하지 않아도, `Template + MBTI + Keywords`의 3단계 합성을 통해 정밀한 `PersonalityProfile`을 자동 도출합니다.

```text
1. Template Base Traits (e.g. professional_assistant: conscientiousness=0.85, warmth=0.60)
         +
2. MBTI 16-type Trait Vector (e.g. ENTJ: extraversion=0.75, assertiveness=0.85, intellectuality=0.80)
         +
3. Keyword Modifiers (e.g. "친절한": warmth +0.15, empathy +0.15, agreeableness +0.10)
         +
4. Clamping & Normalization [0.05, 0.98]
         ↓
Final PersonalityProfile
```

---

## 2. 16종 MBTI 지원 및 방향성 검증

- 16종의 표준 MBTI(INTJ, INTP, ENTJ, ENTP, INFJ, INFP, ENFJ, ENFP, ISTJ, ISFJ, ESTJ, ESFJ, ISTP, ISFP, ESTP, ESFP)를 모두 지원하며,
- E/I (Extraversion), N/S (Openness/Curiosity), T/F (Agreeableness/Empathy), J/P (Conscientiousness)의 심리학적 Big-5 차원을 충실히 반영합니다.
