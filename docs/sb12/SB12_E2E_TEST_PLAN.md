# [SB-12 Audit 8] Multi-Character Orchestration E2E Test Plan

- **작성자**: 🏃 정대리 (QA Lead) & 🔐 방대장 (DevOps/Security)
- **일자**: 2026-09-02
- **스프린트**: SB-12 Multi-Character Companion Orchestration & End-to-End Scope Integrity

---

## 1. 15대 E2E 오케스트레이션 테스트 매트릭스

1. **Test 01 (Text Interaction)**: Genie ➔ Text ➔ Pinned SSE Response
2. **Test 02 (Voice Interaction)**: Mani ➔ Audio/STT ➔ Shimmer TTS ➔ Clean Finish
3. **Test 03 (Vision Interaction)**: Hana ➔ Vision Observation ➔ Context ➔ Response
4. **Test 04 (Full Pipeline)**: Memory + Emotion + Relationship + Growth + Agency + LLM + Presentation
5. **Test 05 (Rapid Switching)**: Genie ➔ Mani ➔ Hana ➔ Genie 각 interaction이 정확한 캐릭터에 귀속
6. **Test 06 (Concurrent Characters)**: Genie / Mani / Hana 3중 동시 실행
7. **Test 07 (Stale Response)**: 오래 걸리는 Genie 요청 중 Mani 전환 시 Genie 응답 격리
8. **Test 08 (TTS Stream Race)**: Genie TTS vs Mani TTS 독립 스트림 보장
9. **Test 09 (Avatar Animation Race)**: Genie 아바타 상태 vs Mani 아바타 상태 분리
10. **Test 10 (Agency Proactive Race)**: Genie Proactive Action의 Mani 컨텍스트 침범 방지
11. **Test 11 (Idempotent Retry)**: 동일 interaction_id 재전송 시 중복 처리 차단
12. **Test 12 (Subsystem Failure Recovery)**: LLM 에러 발생 시 안전 종료 및 Scope 유지
13. **Test 13 (Ownership Attack)**: User A가 User B의 캐릭터 지정 시 403 차단
14. **Test 14 (Invalid Character ID)**: 없는 ID 시 Fail Closed 차단
15. **Test 15 (Archived Character ID)**: 보관된 캐릭터 시 403 차단
