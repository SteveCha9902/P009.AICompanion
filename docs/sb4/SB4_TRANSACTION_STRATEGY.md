# [SB-4 Architecture 4] Transactional Persistence & Rollback Strategy

- **작성자**: 🔐 방대장 (DevOps & Security) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-4 Character Creation Engine & Personality DNA Factory

---

## 1. All-or-Nothing 트랜잭션 보장

캐릭터 생성 시 생성되어야 하는 DB 엔티티 목록:
1. `Companion` (ID, UserID, Name)
2. `CharacterProfileModel` (Name, Core Identity, Origin Story)
3. `CharacterPersonalityModel` (Big-5 & Dynamic Traits)
4. `CharacterValueModel` (Core Values)
5. `EmotionState` (초기 중립/차분 감정)
6. `RelationshipState` (초기 관계 단계 및 점수)
7. `AvatarProfile` (아바타 프리셋 및 초기 표현)

---

## 2. 롤백 메커니즘 (Rollback Mechanism)

```python
async with db.begin():
    try:
        # Step 1 ~ Step 7 삽입
        ...
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise DatabaseTransactionError(f"Character creation aborted: {e}")
```

중간에 오류가 발생하면 즉시 전체 롤백되어 어떠한 고아 데이터도 남지 않습니다.
