# Privacy Rules & Security Audit (Sprint 48) — Bang Chul-byeok's Standard

본 문서는 시각 인지 및 카메라 기능 활용 시 반드시 준수해야 하는 **프라이버시 최우선 원칙과 보안 감사 기준**을 기술합니다.

---

## 🛡️ 1. Zero Raw Frame Storage Guarantee
1. **휘발성 인메모리 처리 (Ephemeral In-Memory Pipeline)**:
   - 클라이언트에서 전송된 프레임 이미지는 메모리 상에서 시각 분석 직후 즉시 가비지 컬렉션(GC)으로 파기됩니다.
   - 디스크, 파일 시스템, 로컬 스토리지, 데이터베이스 어디에도 원본 프레임이 영구 보존되지 않습니다.
2. **얼굴 생체 정보 저장 금지**:
   - 얼굴 임베딩 벡터나 생체 고유 식별자는 일절 저장하지 않으며, 일시적 표정 카테고리(`FacialEmotionType`)만 DTO로 다룹니다.

---

## 🔒 2. 사용자 명시적 제어 원칙
1. **기본값 OFF (Default Inactive)**:
   - 앱 구동 시 카메라는 항상 꺼진 상태(Inactive)로 시작합니다.
2. **명시적 토글**:
   - 사용자가 화면의 [📷 카메라 (Cam)] 버튼을 직접 눌렀을 때만 권한 요청 및 프레임 샘플링이 개시됩니다.
3. **백그라운드 즉시 차단**:
   - 앱이 백그라운드로 전환되는 즉시 센서 및 타이머가 강제 종료(Privacy Cleanup)됩니다.

---

## 📊 3. Privacy Compliance Checklist
- [x] No raw frame disk saving
- [x] Ephemeral frame processing
- [x] Explicit user toggle required
- [x] Immediate background resource release
- [x] Low confidence (< 0.70) auto-filtering to prevent hallucinations
- [x] Privacy Dashboard notice in Settings screen
