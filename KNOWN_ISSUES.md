# P009.AICompanion - Known Issues & Non-blocking Backlog

---

## 📌 P2 — Major / Post-Release Improvements
1. **Live2D / 3D Character Renderer**:
   - 현재 2D Baseline Renderer(`StaticImageRenderer`) 및 `IAvatarRenderer` 인터페이스가 연결되어 있으며, 후속 마일스톤에서 Three.js / Expo-GL 기반 3D 또는 Live2D Cubism SDK 교체 가능.
2. **Push Notification Native APNS/FCM Token Linking**:
   - 백엔드 RemotePushAdapter 구조 완료 상태이며, 네이티브 기기별 푸시 토큰 등록 엔드포인트 연동 대기.

---

## 💡 P3 — Minor UI & Polish
1. **Chat Bubble Timestamp Formatting**:
   - 로컬 타임존에 맞춘 밀리초 포맷 축약.
2. **Dark Theme Custom Palette Switcher**:
   - 설정 화면에서 사용자 정의 테마 선택 기능.
