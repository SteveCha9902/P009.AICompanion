# [SB-8 Architecture 9] Test Plan & 18 Dedicated Automated Tests

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-01
- **스프린트**: SB-8 Character Creation Studio & Character Factory

---

## 1. 18대 전용 테스트 계획 (`test_character_factory.py`)

1. **Test 1**: Create Character (기본 생성 및 8개 엔티티 원자적 트랜잭션)
2. **Test 2**: Create Character Transaction (중간 DB 에러 시 완전한 롤백)
3. **Test 3**: Create Character Ownership (`user_id` 영구 바인딩)
4. **Test 4**: Create Personality (Trait Vector 및 MBTI 컴파일)
5. **Test 5**: Create Relationship Seed (딸/친구/파트너 관계 시드)
6. **Test 6**: Create Voice Profile (`shimmer`, `nova` 등 바인딩)
7. **Test 7**: Create Avatar Profile (아바타 비주얼 프리셋 바인딩)
8. **Test 8**: Create Version 1 (INITIAL DNA 스냅샷 자동 생성)
9. **Test 9**: New Character Memory Empty (신규 생성 캐릭터의 메모리 0건)
10. **Test 10**: New Character Cannot Access Genie Memory (지니 기억 접근 차단)
11. **Test 11**: Created Character Resolver (런타임 컨텍스트 정상 해소)
12. **Test 12**: Created Character Registry (목록 조회 및 필터링)
13. **Test 13**: Created Character Activation (활성 캐릭터 전환)
14. **Test 14**: Invalid Character Creation Rollback (유효성 검증 실패 롤백)
15. **Test 15**: Duplicate/Invalid Character Handling (중복 이름 409 에러)
16. **Test 16**: System Character Protection (`is_system_character=False`)
17. **Test 17**: Character Lifecycle Integration (`AVAILABLE` 상태 시작)
18. **Test 18**: Character Runtime E2E (Mani 생성 후 런타임 해소)
