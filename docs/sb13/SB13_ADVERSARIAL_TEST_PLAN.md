# [SB-13 Audit 8] Controlled Sharing Adversarial Test Plan

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-02
- **스프린트**: SB-13 Controlled Shared Experience & Character-to-Character Information Sharing

---

## 1. 15대 적대적 및 기능 테스트 매트릭스

| Test ID | 시나리오 | 기대 결과 |
| :--- | :--- | :--- |
| **Test 01** | Private Memory Not Shared | Genie 프라이빗 메모리를 Mani가 직접 조회 시 차단 |
| **Test 02** | Explicit Shared Experience | Genie 제안 ➔ 승인 ➔ Shared Experience ➔ Mani 조회 성공 |
| **Test 03** | Denied Proposal | 거부된 제안은 Mani 조회 결과에 미포함 |
| **Test 04** | Target Restriction | Target이 Mani인 공유 경험을 Hana가 조회 시 차단 |
| **Test 05** | Revocation | 철회된 경험은 즉시 Mani 조회 차단 |
| **Test 06** | Cache Revocation | 캐시 적재 후 철회 시 즉시 캐시 무효화 및 조회 차단 |
| **Test 07** | User Isolation | User A의 공유 경험을 User B가 조회 시 차단 |
| **Test 08** | Character State Isolation | 공유 경험 주입 시 Mani의 Emotion/Relationship/Growth 불변 |
| **Test 09** | Provenance Tracking | 공유 경험의 `source_character_id` 및 출처 메타데이터 보존 |
| **Test 10** | Concurrent Sharing | 30개 동시 제안/승인 시 타겟 간 상태 혼선 0건 |
| **Test 11** | Duplicate Proposal | 동일한 내용의 제안 중복 방어 |
| **Test 12** | Unauthorized Target | 타 사용자의 캐릭터를 Target으로 지정 시 거부 |
| **Test 13** | Prompt Injection Defense | 악의적 시스템 지시문이 주입되어도 데이터 태그로 격리 |
| **Test 14** | Archived Character Target | 보관된 캐릭터로의 공유 조회 차단 |
| **Test 15** | Deleted Source Character | 원 캐릭터 삭제 후에도 공유 경험 데이터 무결성 유지 |
