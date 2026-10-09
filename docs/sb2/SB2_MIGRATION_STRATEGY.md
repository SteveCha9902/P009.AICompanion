# [SB-2 Architecture 4] Legacy Genie Migration & Lazy Bootstrap Strategy

- **작성자**: 📚 묵사관 (Memory Keeper) & 🔐 방대장 (DevOps & Security)
- **일자**: 2026-09-01
- **스프린트**: SB-2 Multi-Character Persistence & Registry

---

## 1. 레거시 지니(Genie) 무손실 보존 원칙

기존 시스템의 단일 캐릭터인 지니 데이터를 보존하기 위해 다음 규칙을 엄격히 준수합니다:
1. **Companion PK 유지**: 기존 `companions` 테이블에 저장된 지니의 실제 Primary Key를 그대로 조회하여 사용하며, `"default_companion"` 등 임의 문자열로 덮어쓰지 않습니다.
2. **Memory / State 불변**: 기존 `memories`, `emotion_states`, `relationship_states`, `avatar_profiles`의 외래키는 일체 수정하지 않습니다.
3. **무중단 점진 전환**: 수동 마이그레이션 스크립트 실행 없이도, 시스템이 구동되면서 점진적으로 적용되는 **Lazy Bootstrap**을 도입합니다.

---

## 2. Lazy Bootstrap 메커니즘

```text
User Request (user_id)
        │
        ▼
CharacterRegistryService.get_active_companion_id(user_id)
        │
        ├── 1. user_character_preferences 조회
        │      │
        │      ├── [발견됨] ➔ active_companion_id 즉시 반환
        │      │
        │      └── [없음 (Legacy User)]
        │             │
        │             ├── 2. companions 테이블에서 해당 user_id의 기존 Companion 조회
        │             │      (예: name='지니' 또는 최초 등록된 Companion)
        │             │
        │             ├── 3. 기존 Companion의 실제 id로 user_character_preferences 레코드 자동 생성
        │             │
        │             └── 4. 생성된 active_companion_id 반환 (멱등성 보장)
```

---

## 3. 동시성 및 멱등성 (Idempotency & Concurrency Safety)

- `user_id` 컬럼에 적용된 **`UNIQUE(user_id)`** 제약조건과 데이터베이스 트랜잭션을 통해, 여러 요청이 동시에 인입되어도 중복 Preference 레코드가 생성되지 않음을 보장합니다.
