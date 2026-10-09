# Avatar Known Issues & Technical Debt Registry (Avatar_Known_Issues.md)

**문서 버전**: v1.0 Release Candidate  
**작성자**: 🐟 코다리 Architect & 📚 묵사관 (Memory Keeper)  
**일자**: 2026-08-30

---

## 1. 기술 부채 및 알려진 이슈 현황 (Technical Debt Registry)

| 분류 (Severity) | 이슈 ID | 내용 | 영향 및 향후 개선 계획 |
| :--- | :--- | :--- | :--- |
| **Critical** | 없음 | - | 프로덕션 출시를 저해하는 Critical 이슈 0건 |
| **Major** | `DEBT-46-1` | 3D Skeletal Mesh 미지원 | 현재 2.5D 레이어드 합성 방식이며, 향후 Live2D/VRM 3D 메시 엔진으로 원활히 마이그레이션 가능하도록 DTO가 정규화되어 있음 |
| **Minor** | `DEBT-46-2` | 저사양 단말 절전 모드 | Android 배터리 절약 모드 시 FPS가 30fps로 강제 제한될 수 있으나, 가속 엔진이 프레임 드랍을 보정함 |
| **Minor** | `DEBT-46-3` | 모음 Viseme의 복합 자음 세분화 | 현재 5대 대표 모음(A, E, I, O, U) 중심이며, 추후 한글 자음(ㄱ, ㄴ, ㄷ, ㅂ) 입술 닫힘을 세부 추가 예정 |
