# P009.AICompanion - Beta Test Environment Matrix

---

| 환경 / 시나리오 | 검증 항목 | 상태 |
| :--- | :--- | :---: |
| **Android Emulator** | API 34 기본 구동 및 루프백 통신 | **PASS** |
| **Android Mid-range Device** | UI 렌더링, 메모리/배터리 점유율 | **PASS** |
| **Android High-end Device** | 고속 스트리밍 및 오디오 재생 | **PASS** |
| **Slow Network (3G 시뮬레이션)** | SSE 버퍼링 및 재연결 배지 | **PASS** |
| **Fast Network (Wi-Fi 6)** | TTFT 1.2초 저지연 스트리밍 | **PASS** |
| **Camera Permission Denied** | 시각 기능 비활성화, 대화 정상 유지 | **PASS** |
| **Mic Permission Denied** | 음성 기능 비활성화, 텍스트 정상 유지 | **PASS** |
| **Notification Permission Denied** | 포그라운드 대화 무영향 | **PASS** |
| **Backend Offline / Restart** | 크래시 없이 RETRYING 배지 복구 | **PASS** |
| **OpenAI API Temporary Error** | 사용자 친화적 에러 메시지 표시 | **PASS** |
