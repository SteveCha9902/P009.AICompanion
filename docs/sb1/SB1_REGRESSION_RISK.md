# [SB-1 Audit 8] Regression Risk & Validation Strategy

- **작성자**: 🏃 정대리 (QA & Automation Lead) & 🔐 방대장 (DevOps & Security)
- **일자**: 2026-09-01
- **스프린트**: SB-1 Character Runtime Foundation

---

## 1. 회귀(Regression) 위험도 분석

| 위험 항목 | 심각도 | 발생 가능성 | 회귀 방지 메커니즘 |
| :--- | :--- | :--- | :--- |
| **기존 단일 캐릭터(지니) 호출 실패** | High | Low | `companion_id=None` 시 Default Companion(`default_companion`/Genie) 자동 매핑 |
| **Resolver 캐시 오염 (Cross-talk)** | High | Low | `(user_id, companion_id)` 복합 튜플을 캐시 키로 강제하여 격리 보장 |
| **음성/비전/아바타 파이프라인 중단** | Medium | Low | Presentation Layer에 Fallback 메커니즘 유지 및 인터페이스 점진 연동 |
| **DB 마이그레이션 실패 위험** | None | None | SB-1에서는 DB 스키마 수정을 일체 진행하지 않으므로 위험 제로 (0%) |
| **기존 57개 테스트 슈트 실패 위험** | High | Low | 모든 변경이 non-breaking 확장 방식으로 이루어져 기존 테스트 전량 패스 유지 |

---

## 2. SB-1 전용 8대 자동화 검증 계획 (`test_character_runtime_foundation.py`)

1. **Test 1: Default Character Resolution** - `companion_id=None` 시 지니 런타임 컨텍스트 반환 검증
2. **Test 2: Explicit Character Resolution** - `companion_id="sua"` 명시 시 해당 스코프 반환 검증
3. **Test 3: Backward Compatibility** - 기존 오케스트레이터 호출 시 100% 정상 작동 검증
4. **Test 4: Scope Propagation** - `NormalizedInput` -> `Resolver` -> `Tracer`까지 `companion_id` 유지 검증
5. **Test 5: Context Isolation** - 지니와 수아 컨텍스트 비교 시 스코프/성격/음성 완전 독립 검증
6. **Test 6: No Context Leakage** - 연속 대화 호출 시 인격 정보 간섭 없음 검증
7. **Test 7: Resolver Cache Isolation** - 복합키 `(user_id, companion_id)` 캐시 격리 검증
8. **Test 8: Default Resolution Stability** - 다중 캐릭터 존재 환경에서도 디폴트 요청 안정성 검증
