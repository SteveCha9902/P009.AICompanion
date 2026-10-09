# Mobile Architecture (React Native + Expo)

## 1. Core Principles
P009.AICompanion은 처음부터 스마트폰과 태블릿을 1급(First-class) 플랫폼으로 취급합니다. Desktop/Web 포팅 방식이 아닌 **Mobile-First** 설계입니다.

## 2. Framework Choice: React Native + Expo
Expo 프레임워크를 활용하여 다음과 같은 Native Capability를 안정적으로 다룹니다.
- **Push Notification**: `expo-notifications` (Ambient Mode 지원)
- **Background Task**: `expo-background-fetch` (Event-driven background)
- **Camera/Vision**: `expo-camera`, `react-native-vision-camera` (Edge Vision 가능성)
- **Audio (Mic/Speaker)**: `expo-av`
- **Secure Storage**: `expo-secure-store` (Token 및 민감 정보 보관)

## 3. Adaptive UI (Smartphone vs Tablet)
- **Smartphone**: 세로(Portrait) 모드 최적화, 하단에 Input/Mic, 중앙에 Avatar 배치.
- **Tablet**: 화면 분할(Split) 레이아웃. 좌측에 Companion Avatar/Stats, 우측에 Conversation/Memory 정보를 병렬 배치하여 공간 활용.

## 4. Mode Switching Architecture
동일한 Companion 코어가 두 가지 경험을 제공합니다.
1. **Ambient Mode**: 앱이 백그라운드에 있을 때, 시간/이벤트에 맞춰 Push Notification 송신. (무작위가 아닌 Context 기반 트리거)
2. **Interactive Avatar Mode**: 앱이 포그라운드에 있을 때, Avatar 애니메이션과 카메라 센서를 활용한 실시간 상호작용.
