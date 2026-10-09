# [SB-5 Architecture 2] Character DNA Versioning & Evolution History

- **작성자**: 🐟 코다리 (Lead System Architect) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-5 Character Lifecycle Management & Safe Evolution

---

## 1. Character Versioning 원칙

1. **Version 1 (INITIAL) 생성 시점**:
   - 캐릭터가 처음 생성될 때(`SB-4 CharacterCreationService`), `version = 1`, `change_type = "initial"`인 최초의 DNA 스냅샷이 생성됩니다.
2. **Evolution Versioning (MINOR / MAJOR)**:
   - 성격, 가치관, 역할이 수정될 때마다 `version = 2, 3, ...`으로 증가하며 이력이 축적됩니다.
   - 단순 외형/음성(`COSMETIC`) 변경 시에는 Version을 증가시키지 않고 최신 프로필만 갱신합니다.
3. **`dna_snapshot` 경계 한정 (Strict DNA Boundary)**:
   - **포함**: `identity`, `personality`, `values`, `speaking_style`, `voice_id`, `avatar_preset`
   - **제외**: `Memory`, `Emotion State`, `Relationship State`, `Growth State`, `Agency Action Logs` (이들은 연속된 디지털 경험으로 보존됨).

---

## 2. DB 스키마 (`character_versions`)

```sql
CREATE TABLE character_versions (
    id VARCHAR(36) PRIMARY KEY,
    companion_id VARCHAR(50) NOT NULL REFERENCES companions(id),
    version INTEGER NOT NULL,
    dna_snapshot JSON NOT NULL,
    change_type VARCHAR(20) NOT NULL, -- 'initial', 'cosmetic', 'minor', 'major'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_character_version UNIQUE (companion_id, version)
);
```
