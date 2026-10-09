# [SB-7 Architecture 8] Regression Risk & 15 Dedicated Automated Tests

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-01
- **스프린트**: SB-7 Character Memory Isolation & Independent Experience System

---

## 1. 15대 전용 테스트 계획 (`test_character_memory_isolation.py`)

1. **Test 1**: Genie Memory Isolation (아내 결혼기념일/가족 여행 기억 정상 검색)
2. **Test 2**: Mani Memory Isolation (딸 미술학원/아이돌/일상 기억 정상 검색)
3. **Test 3**: Hana Memory Isolation (친구 카메라 렌즈/출사 기억 정상 검색)
4. **Test 4**: Cross Character Retrieval Prevention (Mani 질의 시 Genie/Hana 기억 검색 차단)
5. **Test 5**: Cross Character Memory Write Prevention (타 캐릭터 ID로 메모리 침범 저장 차단)
6. **Test 6**: Character Switch Memory Isolation (Genie -> Mani -> Hana -> Genie 순차 전환 시 메모리 완전 격리)
7. **Test 7**: ContextBuilder Character Memory Isolation (ContextBuilder가 Active Character의 기억만 주입)
8. **Test 8**: Memory Extraction Character Binding (추출된 기억에 `companion_id` 필수 바인딩)
9. **Test 9**: Archived Character Memory Access (SB-5 Lifecycle Guard에 의한 런타임 검색 차단)
10. **Test 10**: Ownership Validation (타 사용자 메모리 접근 시 403 Forbidden 차단)
11. **Test 11**: Legacy Genie Memory Compatibility (기존 Genie 대화 및 메모리 100% 하위 호환)
12. **Test 12**: Memory Retrieval Cache Isolation (`memory_cache:user:companion:hash` 격리)
13. **Test 13**: Embedding Search Character Isolation (pgvector 검색 시 `companion_id` 필터링 검증)
14. **Test 14**: Concurrent Character Interaction Isolation (동시 요청 환경에서 메모리 혼선 제로)
15. **Test 15**: No Character ID Failure Safety (`companion_id` 누락 시 방어적 거부/폴백 처리)
