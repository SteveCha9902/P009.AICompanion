# [SB-9 Architecture 8] Error Handling, Network Fault & Stale State Recovery

- **작성자**: 🔐 방대장 (DevOps/Security) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-9 Multi-Character Mobile Studio & Real-Time Switching UX

---

## 1. Failure Handling Policies

| 실패 시나리오 | 동작 및 정책 | 사용자 경험 |
| :--- | :--- | :--- |
| **Network Timeout / Failure** | 기존 Active Character 상태를 온전히 보존하고 `isSwitching = false`로 복구 | "네트워크 연결을 확인해주세요" 토스트 표시 |
| **403 Forbidden (소유권 불일치)** | 스위칭 거부 및 목록 강제 리프레시 | "해당 캐릭터에 대한 접근 권한이 없습니다" 경고 |
| **404 Not Found (삭제/보관된 캐릭터)** | 갤러리 목록에서 제외 및 이전 활성 캐릭터 유지 | "존재하지 않는 캐릭터입니다" 알림 후 목록 갱신 |
| **Stale Cache / Offline** | 캐시된 목록을 즉시 렌더링하되 백그라운드에서 최신 상태를 비동기 갱신 | 매끄러운 오프라인 렌더링 + 온라인 복구 |
