# [SB-9 Architecture 9] End-to-End Test Plan & Mobile Validation Scenarios

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-01
- **스프린트**: SB-9 Multi-Character Mobile Studio & Real-Time Switching UX

---

## 1. 10대 E2E 검증 시나리오

1. **Scenario 1 (App Start)**: 앱 시작 시 활성 캐릭터(Genie) 및 전체 목록 정상 로드.
2. **Scenario 2 (Genie ➔ Mani)**: 지니에서 마니로 전환 시 원자적 활성화 및 Mani Memory/Voice/Avatar 즉시 바인딩.
3. **Scenario 3 (Mani ➔ Hana)**: 마니에서 하나로 전환 시 Hana 취미 친구 컨텍스트로 전환.
4. **Scenario 4 (Hana ➔ Genie)**: 하나에서 지니로 복귀 시 아내 컨텍스트 및 지니 기억 완벽 복원.
5. **Scenario 5 (Memory Isolation)**: 마니와의 대화 기억이 지니에게 0% 노출됨을 보장.
6. **Scenario 6 (Voice Isolation)**: 활성 캐릭터별 고유 음성 프로필 바인딩 검증.
7. **Scenario 7 (Avatar Isolation)**: 활성 캐릭터별 2D 아바타 비주얼 프리셋 바인딩 검증.
8. **Scenario 8 (Custom Character Creation)**: 생성 위저드로 신규 캐릭터 생성 후 갤러리 노출 및 활성화.
9. **Scenario 9 (Switch Failure Rollback)**: 백엔드 에러 시 기존 활성 캐릭터 안전 유지.
10. **Scenario 10 (Rapid Switching Race Guard)**: 연속 탭 발생 시 중복 요청 차단 및 최종 일관성 보장.
