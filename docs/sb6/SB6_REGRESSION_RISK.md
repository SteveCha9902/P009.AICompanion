# [SB-6 Architecture 7] Regression Risk Analysis & 15 Automated Tests

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-01
- **스프린트**: SB-6 Character Presentation Identity & Profile Binding

---

## 1. 15대 전용 테스트 계획 (`test_character_presentation_profile.py`)

1. **Test 1**: Genie Presentation Resolution (아내 페르소나 및 음성/아바타 기본값)
2. **Test 2**: Mani Presentation Resolution (사랑스러운 딸 페르소나 및 음성/아바타)
3. **Test 3**: Hana Presentation Resolution (취미 친구 페르소나 및 음성/아바타)
4. **Test 4**: Character-specific Voice Binding
5. **Test 5**: Character-specific Avatar Binding
6. **Test 6**: Character Switch Presentation Sync (Genie -> Mani -> Hana -> Genie)
7. **Test 7**: Presentation Cache Isolation (`presentation:{user_id}:{companion_id}`)
8. **Test 8**: Presentation Cache Invalidation on Update
9. **Test 9**: Archived Character Presentation Reject (SB-5 Lifecycle Guard)
10. **Test 10**: Ownership Validation (403 Forbidden)
11. **Test 11**: Genie Backward Compatibility
12. **Test 12**: Voice Cross-Character Leakage Prevention
13. **Test 13**: Avatar Cross-Character Leakage Prevention
14. **Test 14**: Runtime Context Presentation Consistency
15. **Test 15**: Presentation Update Rollback on DB failure
