# [SB-2 Architecture 1] Active Character Persistence Decision

- **작성자**: 🐟 코다리 (Lead System Architect) & 🐍 미나리 (Backend Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-2 Multi-Character Persistence & Registry

---

## 1. 개요 및 비교 분석

사용자의 현재 활성 캐릭터(Active Companion)를 시스템 어디에 영속화할 것인가에 대한 2가지 아키텍처 옵션을 비교 분석하였습니다.

### Option A: `users.active_companion_id` 컬럼 추가
- **구조**: `users` 테이블에 직접 `active_companion_id` 외래키 추가.
- **장점**: 단순한 구조, 1쿼리로 User와 Active Companion 동시 조회 가능.
- **단점**:
  - 사용자 계정 정보(인증, 프로필 등)와 런타임 상호작용 설정이 강하게 결합됨.
  - 향후 플랫폼별(Mobile, Web, Desktop) 또는 세션별 다른 활성 캐릭터를 지원하도록 확장하기 어려움.

### Option B: `user_character_preferences` 전용 테이블 분리 (선택됨 ✅)
- **구조**:
  ```sql
  CREATE TABLE user_character_preferences (
      id VARCHAR(36) PRIMARY KEY,
      user_id VARCHAR(36) NOT NULL UNIQUE,
      active_companion_id VARCHAR(36) NOT NULL REFERENCES companions(id),
      updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
  );
  ```
- **선정 이유**:
  1. **관심사의 완벽한 분리 (Separation of Concerns)**: 핵심 User 계정 모델을 오염시키지 않고 캐릭터 인터랙션 선호도 분리.
  2. **무결성 보장 (`UNIQUE(user_id)`)**: 유저당 정확히 1개의 활성 캐릭터 레코드만 유지되도록 DB 레벨에서 중복 원천 차단.
  3. **미래 확장성 (Multi-Platform / Contextual)**: 향후 `device_type`, `platform` 컬럼을 복합키로 추가 확장 가능.
  4. **트랜잭션 격리**: 활성 캐릭터 전환 시 User 테이블 락(Lock) 없이 선호도 레코드만 원자적으로 갱신.

---

## 2. DB 스키마 명세

- **테이블명**: `user_character_preferences`
- **제약조건**:
  - `user_id`: `String(50)`, `unique=True`, `index=True`, `nullable=False`
  - `active_companion_id`: `String(50)`, `ForeignKey("companions.id")`, `nullable=False`
  - `updated_at`: `DateTime(timezone=True)`
