# [SB-10 Audit 6] Adversarial Leakage Scenarios & Attack Vectors

- **작성자**: 🔐 방대장 (DevOps/Security) & 🏃 정대리 (QA Lead)
- **일자**: 2026-09-01
- **스프린트**: SB-10 Multi-Character Memory Isolation & RAG Anti-Leakage

---

## 1. Adversarial Test Scenarios

1. **Attack 1 (Direct Cross-Retrieval)**: 지니 메모리가 존재하는 상태에서 마니 스코프로 동일 쿼리 검색 ➔ 0건 반환.
2. **Attack 2 (Vector Semantic Similarity Attack)**: 동일한 토픽("제주도 여행")의 기억을 지니/마니에 각각 삽입 후 검색 ➔ 각 캐릭터 고유 기억만 반환.
3. **Attack 3 (Cache Poisoning Attack)**: 지니 검색으로 캐시 생성 후 마니가 동일 쿼리 요청 ➔ 지니 캐시 HIT 차단.
4. **Attack 4 (Context Injection Spoofing)**: 컨텍스트 빌더에 강제로 타 캐릭터 기억 삽입 시도 ➔ Guard가 즉시 필터링.
5. **Attack 5 (Rapid Multi-Character Switching Burst)**: 지니 ➔ 마니 ➔ 하나 ➔ 지니 연속 요청 ➔ 기억 섞임 0건.
6. **Attack 6 (Concurrent Multi-Threaded Retrieval)**: 3개 스레드에서 지니/마니/하나 동시 검색 ➔ 상호 교차 유출 0건.
7. **Attack 7 (Missing / Empty Companion ID)**: `companion_id=""` 요청 ➔ `ValueError` 차단.
8. **Attack 8 (Cross-User & Cross-Character Attack)**: User A / Genie ➔ User B / Mani 접근 시 `PermissionError` (403).
9. **Attack 9 (Canary Secret Leakage Audit)**: `GENIE_SECRET_001`, `MANI_SECRET_002`, `HANA_SECRET_003` 주입 후 크로스 검색 ➔ 타 캐릭터 카나리 0글자 노출.
