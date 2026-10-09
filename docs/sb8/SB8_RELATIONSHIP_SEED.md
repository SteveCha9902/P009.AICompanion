# [SB-8 Architecture 5] Relationship Archetype Seed Specification

- **작성자**: 🌸 진달래 (Vision/Presentation) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-8 Character Creation Studio & Character Factory

---

## 1. Relationship Seeds by Type

| 관계 유형 (`relationship_type`) | 초기 신뢰도 (`trust_score`) | 친밀도 (`intimacy_score`) | 초기 애착 수준 | 기본 관계 레벨 |
| :--- | :--- | :--- | :--- | :--- |
| **`family` (사랑스러운 딸)** | `0.90` | `0.85` | High Attachment | `CLOSE_BOND` |
| **`friend` (친구/취미 친구)** | `0.70` | `0.65` | Balanced | `FRIEND` |
| **`romantic` (연인/배우자)** | `0.92` | `0.90` | Deep Attachment | `INTIMATE` |
| **`mentor` (조언자/멘토)** | `0.85` | `0.55` | Respectful | `RESPECTED` |
| **`custom` (기본/직접설정)** | `0.50` | `0.50` | Neutral | `ACQUAINTANCE` |
