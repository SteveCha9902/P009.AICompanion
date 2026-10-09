# Avatar v1.0 Release Guide & Production Operations (Avatar_Release_Guide.md)

**문서 버전**: v1.0 (Release Candidate 1)  
**작성자**: 🔐 방대장 (DevOps/Security) & 📚 묵사관 (Memory Keeper)  
**일자**: 2026-08-30

---

## 1. 릴리즈 개요 및 배포 기준

- **릴리즈 대상**: P009.AICompanion Embodied Avatar System v1.0 RC1
- **지원 플랫폼**: Android (v10+), iOS (v14+), Expo / React Native Runtime
- **배포 기준 (Go/No-Go)**:
  - Final Release Gates P1~P10 100% 통과
  - 백엔드 105개 단위/통합 테스트 100% PASS
  - 모바일 TypeScript 컴파일 오류 0건
  - 1시간 연속 세션 메모리 누수 제로

---

## 2. 프로덕션 모니터링 체계 (Production Monitoring Setup)

| 모니터링 항목 | 측정 도구/지표 | 허용 임계치 (Threshold) | 이상 징후 시 조치 |
| :--- | :--- | :--- | :--- |
| **렌더링 FPS** | React Native Performance Monitor | 평균 58.5 ~ 60.0 FPS 유지 | Jitter/Animation Frame Throttling 자동 발동 |
| **CPU 점유율** | Backend cAdvisor / Mobile Profiler | CPU < 4.5% (백그라운드 < 0.1%) | SSE 전송 주기 100ms ➔ 200ms 자동 백오프 |
| **메모리 누수** | LeakCanary / Instruments | 1시간 사용 후 증가량 < 15MB | 렌더러 애니메이션 리소스 강제 가비지 컬렉션 |
| **Crash-Free율** | Sentry / Firebase Crashlytics | **99.9% 이상** 무결점 유지 | P0 긴급 패치 및 이전 빌드 롤백 |

---

## 3. 릴리즈 롤백 계획 (Release Rollback Plan)

프로덕션 배포 후 치명적 오류(FPS < 45fps 급락, 메모리 누수 폭증, 앱 강제 종료) 발생 시 즉시 아래 절차를 수행합니다:

1. **Phase 1: Feature Flag 비상 차단 (`AVATAR_REALTIME_RENDERER=false`)**:
   - 앱 재배포 없이 서버 구성 변경을 통해 정적 포트레이트 모드로 1초 내 즉시 전환.
2. **Phase 2: Mobile Fallback Image Layer 유지**:
   - `AVATAR_PORTRAITS.neutral` 정적 캐시 이미지로 안전하게 안착.
3. **Phase 3: Hotfix 배포 및 원인 분석**:
   - 묵사관 및 코다리 주관 하에 Decision Log 분석 후 패치 빌드 생성.
