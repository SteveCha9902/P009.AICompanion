# [SB-3 Architecture 5] Regression Risk & Verification Plan

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps & Security)
- **일자**: 2026-09-01
- **스프린트**: SB-3 Character Switching & Full Context Isolation

---

## 1. 회귀(Regression) 위험도 점검

| 위험 항목 | 영향도 | 방지 대책 |
| :--- | :--- | :--- |
| **기존 단일 지니 대화 중단 위험** | High | `companion_id=None` 시 Active/Legacy Fallback을 통해 기존 호출 100% 정상 작동 |
| **대화 중 활성 캐릭터 변경 시 충돌** | High | Interaction 시작 시 생성된 `InteractionContext` 스냅샷 불변성으로 격리 |
| **타 캐릭터 메모리/감정 데이터 오염** | Critical | RAG 쿼리 및 DB 조회 시 `companion_id` 외래키 strict filtering 검증 |
| **동시 요청 시 세션 레이스 컨디션** | Medium | 전역 가변 상태 제거 및 함수 스코프 내 불변 객체 전달 |

---

## 2. 11대 전용 자동화 테스트 계획 (`test_character_switching_isolation.py`)

1. **Test 1**: Explicit Character Override
2. **Test 2**: Active Character Resolution
3. **Test 3**: Mid Interaction Switch (Snapshot Isolation)
4. **Test 4**: New Interaction After Switch
5. **Test 5**: Memory Isolation (No cross-character recall)
6. **Test 6**: Emotion Isolation (Independent PAD dynamics)
7. **Test 7**: Relationship Isolation (Independent intimacy/trust)
8. **Test 8**: Voice Isolation (Distinct voice profile binding)
9. **Test 9**: Avatar Isolation (Distinct expression/motion plan)
10. **Test 10**: Agency Isolation (Distinct autonomous actions)
11. **Test 11**: Concurrent Interaction Isolation (Parallel requests)
