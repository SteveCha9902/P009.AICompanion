import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Dimensions, TouchableOpacity, AppState, AppStateStatus } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { avatarService } from '../features/avatar/services/avatar_service';
import { AvatarState } from '../features/avatar/domain/avatar_state';
import { RealtimeFaceRenderer } from '../features/avatar/presentation/RealtimeFaceRenderer';
import { FaceParameters, DEFAULT_FACE_PARAMETERS } from '../features/avatar/domain/face_parameters';
import { SpeechParameters, DEFAULT_SPEECH_PARAMETERS } from '../features/avatar/domain/speech_parameters';
import { BehaviorParameters, DEFAULT_BEHAVIOR_PARAMETERS } from '../features/avatar/domain/behavior_parameters';
import { RelationshipParameters, DEFAULT_RELATIONSHIP_PARAMETERS } from '../features/avatar/domain/relationship_parameters';
import { MotionParameters, DEFAULT_MOTION_PARAMETERS } from '../features/avatar/domain/motion_parameters';
import { ConversationView } from '../features/conversation/presentation/ConversationView';
import { interactionController, InteractionState, NetworkInteractionStatus } from '../services/interactionController';
import { voiceController, VoiceState } from '../services/voiceController';
import { visionController, VisionStatus, VisionObservationData } from '../services/visionController';
import { useCharacterStore } from '../state/useCharacterStore';
import { LiveAudioVisualizer } from '../features/conversation/presentation/LiveAudioVisualizer';

const TEMP_USER_ID = "default_user";
const DEFAULT_COMPANION_ID = "genie_pk";

export function CompanionScreen({ route, navigation }: any) {
  const [currentConversationId, setCurrentConversationId] = useState<string>("default");
  const [isOverlayVisible, setIsOverlayVisible] = useState<boolean>(true);

  // Active Character Store Subscription
  const activeCharacter = useCharacterStore((state) => state.activeCharacter);
  const activeCharacterId = useCharacterStore((state) => state.activeCharacterId) || DEFAULT_COMPANION_ID;
  const fetchActiveCharacter = useCharacterStore((state) => state.fetchActiveCharacter);

  useEffect(() => {
    fetchActiveCharacter(TEMP_USER_ID);
  }, []);

  // Expo Camera Permissions & Ref
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<any>(null);

  // Multimodal & Avatar States
  const [avatarState, setAvatarState] = useState<AvatarState | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [micActive, setMicActive] = useState(false);
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [networkState, setNetworkState] = useState<NetworkInteractionStatus>("idle");
  const [voiceState, setVoiceState] = useState<VoiceState>("idle");
  const [visionStatus, setVisionStatus] = useState<VisionStatus>("inactive");
  const [lastVisionObs, setLastVisionObs] = useState<VisionObservationData | null>(null);

  // Relational Parameters (Dynamic bond level)
  const [relationshipParams, setRelationshipParams] = useState<RelationshipParameters>({
    familiarity: 0.75,
    trust: 0.80,
    warmth: 0.85,
    engagement: 0.80,
  });

  const appState = useRef(AppState.currentState);
  const clearChatRef = useRef<(() => void) | null>(null);
  const focusInputRef = useRef<(() => void) | null>(null);

  // -------------------------------------------------------------------------
  // Subscriptions & Multimodal Controllers
  // -------------------------------------------------------------------------
  useEffect(() => {
    const unsubAvatar = avatarService.subscribe((state) => {
      setAvatarState(state);
    });

    const unsubNet = interactionController.subscribe((iState: InteractionState) => {
      setNetworkState(iState.status);
    });

    const unsubVoice = voiceController.subscribe((vState, live) => {
      setVoiceState(vState);
      setIsLiveMode(live);
      if (vState === 'listening') setMicActive(true);
      else if ((vState === 'idle' || vState === 'error') && !live) setMicActive(false);
    });

    const unsubVision = visionController.subscribe((vStatus, obs) => {
      setVisionStatus(vStatus);
      if (obs) setLastVisionObs(obs);
      if (vStatus === 'active' || vStatus === 'sampling') setCameraActive(true);
      else if (vStatus === 'inactive' || vStatus === 'error') {
        setCameraActive(false);
        setLastVisionObs(null);
      }
    });

    // Privacy Boundary: Resource Cleanup on Background
    const appStateSubscription = AppState.addEventListener('change', (nextAppState: AppStateStatus) => {
      if (appState.current.match(/inactive|background/) && nextAppState === 'active') {
        console.log("[Privacy] App returned to FOREGROUND.");
      } else if (nextAppState.match(/inactive|background/)) {
        setCameraActive(false);
        setMicActive(false);
        interactionController.cancelInteraction();
        voiceController.cleanup();
        visionController.cleanup();
        avatarService.setSpeaking(false);
      }
      appState.current = nextAppState;
    });

    return () => {
      appStateSubscription?.remove();
      unsubAvatar();
      unsubNet();
      unsubVoice();
      unsubVision();
      interactionController.cancelInteraction();
      voiceController.cleanup();
      visionController.cleanup();
    };
  }, []);

  const handleToggleLiveMode = async () => {
    const nextLive = !isLiveMode;
    setIsLiveMode(nextLive);
    if (nextLive) {
      setMicActive(true);
      await voiceController.startLiveMode(TEMP_USER_ID, activeCharacterId, currentConversationId);
    } else {
      await voiceController.stopLiveMode();
      setMicActive(false);
    }
  };

  const handleToggleMic = async () => {
    if (isLiveMode) {
      await voiceController.stopLiveMode();
      setIsLiveMode(false);
      setMicActive(false);
      return;
    }

    const nextState = !micActive;
    if (nextState) {
      setMicActive(true);
      try {
        const ok = await voiceController.startListening(TEMP_USER_ID, activeCharacterId, currentConversationId);
        if (!ok) {
          setMicActive(false);
        }
      } catch (err) {
        console.warn("[CompanionScreen] Mic recording start failed:", err);
        setMicActive(false);
      }
    } else {
      setMicActive(false);
      await voiceController.stopListeningAndSend();
    }
  };

  const handleToggleCamera = async () => {
    if (!permission?.granted) {
      const res = await requestPermission();
      if (!res.granted) {
        alert("시각 인지를 위해 전면 카메라 권한을 허용해 주세요.");
        return;
      }
    }

    const nextState = !cameraActive;
    setCameraActive(nextState);
    if (nextState) {
      const started = await visionController.startVision(activeCharacterId);
      if (!started) setCameraActive(false);
    } else {
      await visionController.stopVision();
    }
  };

  // Derive Current Face, Speech, Behavior, and Motion Parameters
  const resolveCurrentParameters = (): {
    face: FaceParameters;
    speech: SpeechParameters;
    behavior: BehaviorParameters;
    motion: MotionParameters;
  } => {
    const isSpeaking = avatarState?.speaking || voiceState === 'speaking';

    if (voiceState === 'listening') {
      return {
        face: {
          ...DEFAULT_FACE_PARAMETERS,
          eyeOpenness: 1.0,
          browRaise: 0.35,
          headPitch: 2.0,
          headRoll: 2.5,
          warmth: 0.85,
        },
        speech: DEFAULT_SPEECH_PARAMETERS,
        behavior: {
          ...DEFAULT_BEHAVIOR_PARAMETERS,
          attentionLevel: 0.95,
          eyeContact: 1.0,
          headTilt: 2.5,
          nodIntensity: 0.6,
          curiosityLevel: 0.85,
        },
        motion: {
          activeMotionId: 'LISTENING_SIDE_TILT',
          headTilt: 2.0,
          headPitch: 1.5,
          headYaw: 0.0,
          nodIntensity: 0.5,
          bodyLean: 0.2,
          jitterFactor: 1.02,
        },
      };
    }

    const isInteracting = interactionController.getState().isInteracting;
    if (voiceState === 'thinking' || (networkState === 'connecting' && isInteracting)) {
      return {
        face: {
          ...DEFAULT_FACE_PARAMETERS,
          eyeOpenness: 0.8,
          eyeDirectionY: -0.4,
          headPitch: -2.0,
          headRoll: -4.0,
          smileStrength: 0.20,
          warmth: 0.6,
        },
        speech: DEFAULT_SPEECH_PARAMETERS,
        behavior: {
          ...DEFAULT_BEHAVIOR_PARAMETERS,
          attentionLevel: 0.70,
          eyeContact: 0.40,
          headTilt: -4.0,
          thinkingIntensity: 0.85,
        },
        motion: {
          activeMotionId: 'THINKING_DOWN_GAZE',
          headTilt: -3.0,
          headPitch: -2.5,
          headYaw: 1.0,
          nodIntensity: 0.0,
          bodyLean: -0.1,
          jitterFactor: 0.98,
        },
      };
    }

    if (avatarState?.expression === 'smile' || avatarState?.expression === 'warm_smile' || avatarState?.expression === 'happy') {
      return {
        face: {
          ...DEFAULT_FACE_PARAMETERS,
          smileStrength: 0.85,
          eyeOpenness: 0.95,
          browRaise: 0.2,
          warmth: 0.95,
        },
        speech: DEFAULT_SPEECH_PARAMETERS,
        behavior: {
          ...DEFAULT_BEHAVIOR_PARAMETERS,
          attentionLevel: 0.90,
          eyeContact: 0.95,
          headTilt: 1.5,
        },
        motion: {
          activeMotionId: 'SPEAKING_WARM_LEAN',
          headTilt: 1.5,
          headPitch: 1.0,
          headYaw: 0.0,
          nodIntensity: 0.3,
          bodyLean: 0.3,
          jitterFactor: 1.04,
        },
      };
    }

    if (isSpeaking) {
      return {
        face: {
          ...DEFAULT_FACE_PARAMETERS,
          mouthOpen: 0.55,
          smileStrength: 0.65,
          headPitch: 1.0,
          warmth: 0.85,
        },
        speech: {
          isSpeaking: true,
          mouthOpen: 0.55,
          viseme: 'viseme_a',
          speechIntensity: 0.75,
          speechProgress: 0.5,
        },
        behavior: {
          ...DEFAULT_BEHAVIOR_PARAMETERS,
          attentionLevel: 0.90,
          eyeContact: 0.85,
          headTilt: 1.0,
          nodIntensity: 0.3,
        },
        motion: {
          activeMotionId: 'SPEAKING_GENTLE_EMPHASIS',
          headTilt: 1.0,
          headPitch: 1.2,
          headYaw: 0.5,
          nodIntensity: 0.4,
          bodyLean: 0.2,
          jitterFactor: 1.01,
        },
      };
    }

    return {
      face: DEFAULT_FACE_PARAMETERS,
      speech: DEFAULT_SPEECH_PARAMETERS,
      behavior: DEFAULT_BEHAVIOR_PARAMETERS,
      motion: DEFAULT_MOTION_PARAMETERS,
    };
  };

  const { face, speech, behavior, motion } = resolveCurrentParameters();

  // 10-State UX Badge Resolver (including Gemini Live Mode)
  const renderStatusBadge = () => {
    let text = "ONLINE";
    let badgeColor = "#30D158";

    if (isLiveMode) {
      if (voiceState === "speaking") {
        text = "LIVE 발화 중 🔊";
        badgeColor = "#BF5AF2";
      } else if (voiceState === "thinking" || voiceState === "transcribing") {
        text = "LIVE 생각 중 🧠";
        badgeColor = "#FFD60A";
      } else {
        text = "✨ GEMINI LIVE ⚡";
        badgeColor = "#30D158";
      }
    } else if (networkState === "error" || voiceState === "error" || visionStatus === "error") {
      text = "SYSTEM ERROR";
      badgeColor = "#FF453A";
    } else if (networkState === "disconnected") {
      text = "OFFLINE - RETRYING";
      badgeColor = "#FF9F0A";
    } else if (networkState === "retrying" || networkState === "connecting") {
      text = "CONNECTING...";
      badgeColor = "#FF9F0A";
    } else if (voiceState === "listening") {
      text = "LISTENING 🎤";
      badgeColor = "#0A84FF";
    } else if (voiceState === "transcribing" || networkState === "streaming") {
      text = "THINKING 🧠";
      badgeColor = "#BF5AF2";
    } else if (voiceState === "speaking") {
      text = "SPEAKING 🔊";
      badgeColor = "#5E5CE6";
    } else if (visionStatus === "sampling" || visionStatus === "active") {
      text = "VISION ACTIVE 👁️";
      badgeColor = "#64D2FF";
    }

    return (
      <View style={[styles.statusBadge, { borderColor: badgeColor }]}>
        <View style={[styles.statusDot, { backgroundColor: badgeColor }]} />
        <Text style={styles.statusText}>{text}</Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* 1. Real-Time Embodied Avatar & Behavioral Variety Renderer (Sprint 49) */}
      <View style={styles.avatarLayerContainer}>
        <RealtimeFaceRenderer
          faceParameters={face}
          speechParameters={speech}
          behaviorParameters={behavior}
          relationshipParameters={relationshipParams}
          motionParameters={motion}
          stateName={voiceState}
          isSpeaking={speech.isSpeaking}
          focusAnchor={lastVisionObs?.awareness?.focus_target || 'USER_FACE'}
        />
      </View>


      {/* 2. Transparent Foreground Safe Layout */}
      <SafeAreaView style={styles.foregroundSafeView}>
        {/* Top Header Bar */}
        <View style={styles.headerBar}>
          <TouchableOpacity
            style={styles.companionIdentity}
            onPress={() => navigation.navigate('Character')}
          >
            <Text style={styles.companionName}>{activeCharacter ? `${activeCharacter.name} (${activeCharacter.role_title})` : 'Genie'}</Text>
            {renderStatusBadge()}
          </TouchableOpacity>

          {/* Action Icons (Clear, Toggle Visibility, Settings) */}
          <View style={styles.headerActions}>
            <TouchableOpacity
              style={styles.headerActionButton}
              onPress={() => clearChatRef.current?.()}
            >
              <Text style={styles.actionButtonText}>🧹 비우기</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.headerIconButton}
              onPress={() => setIsOverlayVisible(!isOverlayVisible)}
            >
              <Text style={styles.iconButtonText}>{isOverlayVisible ? '👁️' : '💬'}</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.headerIconButton}
              onPress={() => navigation.navigate('Settings')}
            >
              <Text style={styles.iconButtonText}>⚙️</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Real Front Camera PIP Preview (Active when Camera On) */}
        {cameraActive && permission?.granted && (
          <View style={styles.cameraPipContainer}>
            <CameraView
              ref={(ref) => {
                cameraRef.current = ref;
                visionController.setCameraRef(ref);
              }}
              style={styles.cameraPipView}
              facing="front"
              animateShutter={false}
            />
            <View style={styles.cameraPipBadge}>
              <View style={styles.cameraRecDot} />
              <Text style={styles.cameraPipText}>LIVE</Text>
            </View>
          </View>
        )}

        {/* Real-Time Visual Awareness Indicator (Sprint 48) */}
        {cameraActive && (
          <View style={styles.awarenessPillContainer}>
            <Text style={styles.awarenessPillIcon}>👁️</Text>
            <Text style={styles.awarenessPillText}>
              {lastVisionObs?.awareness?.user_presence
                ? `시각 인지: ${lastVisionObs.awareness.facial_emotion || '중립'} ${lastVisionObs.awareness.detected_objects.length > 0 ? `| ${lastVisionObs.awareness.detected_objects[0].type}` : ''}`
                : '시각 인지 활성화됨 (Zero Storage)'}
            </Text>
          </View>
        )}

        {/* Real-Time 60 FPS Audio Visualizer (STEP 12) */}
        <LiveAudioVisualizer
          voiceState={voiceState}
          conversationState={avatarState?.conversation_state}
          isLiveMode={isLiveMode}
        />


        {/* 3. Transparent Floating Conversation Overlay */}
        <View style={styles.conversationOverlayArea}>
          <ConversationView
            userId={TEMP_USER_ID}
            companionId={activeCharacterId}
            visible={isOverlayVisible}
            onConversationLoaded={setCurrentConversationId}
            onClearMessagesRef={(fn) => { clearChatRef.current = fn; }}
            onFocusInputRef={(fn) => { focusInputRef.current = fn; }}
          />
        </View>

        {/* 4. Bottom Controls Bar (Live Mode, Mic & Cam) */}
        <View style={styles.bottomControlsBar}>
          <TouchableOpacity
            style={[
              styles.controlPillButton,
              isLiveMode && styles.liveActivePillButton,
            ]}
            onPress={handleToggleLiveMode}
          >
            <Text style={styles.pillIconText}>✨</Text>
            <Text style={[styles.pillLabelText, isLiveMode && styles.liveActiveText]}>
              {isLiveMode ? 'Live 종료' : 'Live 모드'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlPillButton, micActive && !isLiveMode && styles.activePillButton]}
            onPress={handleToggleMic}
          >
            <Text style={styles.pillIconText}>🎤</Text>
            <Text style={styles.pillLabelText}>{micActive && !isLiveMode ? '음성 중지' : '마이크'}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.controlPillButton, cameraActive && styles.activePillButton]}
            onPress={handleToggleCamera}
          >
            <Text style={styles.pillIconText}>📷</Text>
            <Text style={styles.pillLabelText}>{cameraActive ? '카메라 OFF' : '카메라'}</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0c0c0e' },
  avatarLayerContainer: {
    ...StyleSheet.absoluteFill,
    zIndex: 0,
    justifyContent: 'flex-start',
    alignItems: 'center',
    paddingTop: 46,
  },
  foregroundSafeView: { flex: 1, zIndex: 1, justifyContent: 'space-between' },

  headerBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 6,
    backgroundColor: 'rgba(12, 12, 14, 0.40)',
    borderBottomWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  companionIdentity: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  companionName: { fontSize: 18, fontWeight: 'bold', color: '#ffffff', textShadowColor: '#000', textShadowOffset: { width: 0, height: 1 }, textShadowRadius: 3 },
  statusBadge: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10, borderWidth: 1, backgroundColor: 'rgba(0,0,0,0.6)' },
  statusDot: { width: 6, height: 6, borderRadius: 3, marginRight: 5 },
  statusText: { color: '#ffffff', fontSize: 10, fontWeight: '700' },
  headerActions: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  headerActionButton: { paddingHorizontal: 10, paddingVertical: 5, borderRadius: 14, backgroundColor: 'rgba(28,28,30,0.75)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.2)' },
  actionButtonText: { color: '#ffffff', fontSize: 11, fontWeight: '600' },
  headerIconButton: { padding: 6, borderRadius: 16, backgroundColor: 'rgba(28,28,30,0.75)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)' },
  iconButtonText: { fontSize: 14 },

  awarenessPillContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'center',
    backgroundColor: 'rgba(10, 132, 255, 0.20)',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 4,
    marginTop: 4,
    borderWidth: 1,
    borderColor: 'rgba(10, 132, 255, 0.40)',
    gap: 6,
  },
  awarenessPillIcon: { fontSize: 13 },
  awarenessPillText: { color: '#64D2FF', fontSize: 11.5, fontWeight: '600' },

  conversationOverlayArea: { flex: 1, backgroundColor: 'transparent', justifyContent: 'flex-end' },


  bottomControlsBar: {
    flexDirection: 'row',
    justifyContent: 'center',
    paddingHorizontal: 14,
    paddingTop: 2,
    paddingBottom: 4,
    backgroundColor: 'transparent',
    gap: 10,
    top: 42,
  },
  controlPillButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    backgroundColor: 'rgba(28, 28, 30, 0.85)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.4,
    shadowRadius: 4,
    elevation: 4,
    gap: 6,
  },
  activePillButton: {
    backgroundColor: 'rgba(255, 69, 58, 0.90)',
    borderColor: '#FF453A',
  },
  liveActivePillButton: {
    backgroundColor: 'rgba(48, 209, 88, 0.25)',
    borderColor: '#30D158',
    borderWidth: 1.5,
  },
  liveActiveText: {
    color: '#30D158',
    fontWeight: 'bold',
  },
  pillIconText: { fontSize: 15 },
  pillLabelText: { color: '#ffffff', fontSize: 12.5, fontWeight: 'bold' },

  cameraPipContainer: {
    position: 'absolute',
    top: 56,
    right: 14,
    width: 88,
    height: 118,
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: '#0A84FF',
    backgroundColor: '#000',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 6,
    elevation: 8,
    zIndex: 10,
  },
  cameraPipView: {
    width: '100%',
    height: '100%',
  },
  cameraPipBadge: {
    position: 'absolute',
    top: 4,
    left: 4,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.65)',
    paddingHorizontal: 5,
    paddingVertical: 2,
    borderRadius: 8,
    gap: 4,
  },
  cameraRecDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#FF453A',
  },
  cameraPipText: {
    color: '#fff',
    fontSize: 8.5,
    fontWeight: '800',
  },
});


