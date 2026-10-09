# [SB-8 Architecture 3] Personality & Character Compiler Specification

- **작성자**: 🐍 미나리 (Backend Lead) & 🐟 코다리 (Lead Architect)
- **일자**: 2026-09-01
- **스프린트**: SB-8 Character Creation Studio & Character Factory

---

## 1. Compiler Responsibility

- **역할**: 사용자의 자연어 키워드, MBTI, 선택된 아키타입 템플릿을 정규화된 Big-5 Trait Vector (0.0~1.0) 및 Character Values로 컴파일.
- **원칙**: Compiler는 Character Runtime이 아니며, 오직 사전 컴파일/정규화(Normalization) 역할만 수행.
