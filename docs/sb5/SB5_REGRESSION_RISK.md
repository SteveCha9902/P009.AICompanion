# [SB-5 Architecture 5] Regression Risk & 17 Automated Tests Plan

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps & Security)
- **일자**: 2026-09-01
- **스프린트**: SB-5 Character Lifecycle Management & Safe Evolution

---

## 1. 17대 전용 자동화 테스트 계획 (`test_character_lifecycle.py`)

1. **Test 1**: Cosmetic Update (Avatar/Voice 변경 시 DNA 업데이트, Version 유지)
2. **Test 2**: Personality Update & Version 2 Creation (MINOR/MAJOR 시 Version 2 생성)
3. **Test 3**: Memory Preservation on Evolution (DNA 수정 후 기존 기억 데이터 100% 보존)
4. **Test 4**: Archive Character & Runtime Block (아카이브 후 대화/Resolver 차단)
5. **Test 5**: Active Character Archive Reject (409 Conflict 차단)
6. **Test 6**: Restore Character & State Transition (복원 시 Available 상태 전이)
7. **Test 7**: Soft Delete Character (Soft delete 및 무손실 보존)
8. **Test 8**: Deleted Character Runtime Reject (삭제 캐릭터 런타임 차단)
9. **Test 9**: Deleted Character Activation Reject (409 Conflict 차단)
10. **Test 10**: Character Version History (V1 INITIAL -> V2 MINOR -> V3 MAJOR 이력 조회)
11. **Test 11**: System Character (Genie) Protection (지니 아카이브/삭제 403 차단)
12. **Test 12**: Ownership Validation on Lifecycle Ops (타인 캐릭터 403 차단)
13. **Test 13**: Transaction Rollback on Failure (DB 에러 시 롤백 무결성)
14. **Test 14**: Runtime Context Cache Invalidation (수정 후 캐시 무효화 및 신규 DNA 로딩)
15. **Test 15**: Version Concurrency & Unique Constraint (`UNIQUE(companion_id, version)` 무결성)
16. **Test 16**: Archived Character Agency Block (아카이브 상태 시 Agency/Proactive 차단)
17. **Test 17**: Invalid Lifecycle Transition Reject (DELETED -> RESTORE 시 409 Conflict 차단)
