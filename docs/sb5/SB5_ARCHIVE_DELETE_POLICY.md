# [SB-5 Architecture 4] Archive, Restore, Agency Block & HTTP 409 Policy

- **작성자**: 🔐 방대장 (DevOps & Security) & 🧭 세종이 (PM Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-5 Character Lifecycle Management & Safe Evolution

---

## 1. Archive & Agency / Proactive Action 차단

- **Archive**:
  - 캐릭터의 모든 기억과 프로필은 DB에 온전히 보존됩니다.
  - 대화 런타임 진입 불가, 활성화 불가.
  - **Agency Scheduler 및 Proactive Trigger 차단**: `ARCHIVED` 또는 `DELETED` 상태의 캐릭터는 자율 행동 결정 및 선제적 알림 발송이 전면 차단됩니다.
- **Restore**:
  - `ARCHIVED` ➔ `AVAILABLE` 상태 전이 (복원 후 `Inactive` 기본값).
  - `DELETED` ➔ `RESTORE` 시도는 부적절한 전이이므로 `409 Conflict` 차단.

---

## 2. API Error Code 표준화 매핑

| 상황 | HTTP Status | Detail 메시지 |
| :--- | :--- | :--- |
| **존재하지 않는 Character** | `404 Not Found` | Companion not found |
| **타인 소유 Character** | `403 Forbidden` | User does not have access |
| **Active Character Archive 시도** | `409 Conflict` | Active character cannot be archived. Switch active character first. |
| **Active Character Delete 시도** | `409 Conflict` | Active character cannot be deleted. Switch active character first. |
| **System Character (Genie) Archive/Delete** | `403 Forbidden` | System default character cannot be archived or deleted. |
| **Archived / Deleted Activate 시도** | `409 Conflict` | Cannot activate archived or deleted character. |
| **Deleted Character Restore 시도** | `409 Conflict` | Cannot restore deleted companion. |
