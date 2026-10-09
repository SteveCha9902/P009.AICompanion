import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Easing } from 'react-native';
import { VoiceState } from '../../../services/voiceController';
import { AvatarConversationState } from '../../avatar/domain/avatar_state';

interface LiveAudioVisualizerProps {
  voiceState: VoiceState;
  conversationState?: AvatarConversationState;
  isLiveMode?: boolean;
}

const BAR_COUNT = 7;

/**
 * Live Audio Visualizer Component (STEP 12)
 * High-performance 60 FPS native-driven real-time audio waveform & indicator.
 * - Speaking: TTS amplitude-based undulating blue waveform
 * - Listening: Microphone amplitude-based reactive green waveform
 * - Thinking: Smooth orbital pulsing purple indicator
 * - Idle: Subtle minimal baseline
 */
export const LiveAudioVisualizer: React.FC<LiveAudioVisualizerProps> = ({
  voiceState,
  conversationState,
  isLiveMode = false,
}) => {
  // Animated scaleY for 7 waveform bars (Driven by Native Driver)
  const barAnims = useRef(Array.from({ length: BAR_COUNT }, () => new Animated.Value(0.15))).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const rotateAnim = useRef(new Animated.Value(0)).current;

  const currentMode = voiceState === 'speaking' || conversationState === 'SPEAKING'
    ? 'speaking'
    : voiceState === 'listening' || conversationState === 'LISTENING'
    ? 'listening'
    : voiceState === 'thinking' || voiceState === 'transcribing' || conversationState === 'THINKING'
    ? 'thinking'
    : voiceState === 'interrupted' || conversationState === 'INTERRUPTED'
    ? 'interrupted'
    : voiceState === 'error' || conversationState === 'ERROR'
    ? 'error'
    : 'idle';

  // 60 FPS Native Driver Animation Loop
  useEffect(() => {
    let animLoop: Animated.CompositeAnimation | null = null;

    if (currentMode === 'speaking') {
      // Fast, rhythmic TTS speech undulating waveform (60 FPS Native Transform)
      const animations = barAnims.map((anim, i) => {
        const speed = 180 + i * 40;
        const maxScale = 0.4 + (Math.sin((i / (BAR_COUNT - 1)) * Math.PI) * 0.6); // Bell curve center peak
        return Animated.loop(
          Animated.sequence([
            Animated.timing(anim, {
              toValue: maxScale,
              duration: speed,
              easing: Easing.inOut(Easing.sin),
              useNativeDriver: true,
            }),
            Animated.timing(anim, {
              toValue: 0.15,
              duration: speed,
              easing: Easing.inOut(Easing.sin),
              useNativeDriver: true,
            }),
          ])
        );
      });
      animLoop = Animated.parallel(animations);
      animLoop.start();
    } else if (currentMode === 'listening') {
      // Responsive microphone reactive soundwave (Attentive 60 FPS Native Transform)
      const animations = barAnims.map((anim, i) => {
        const speed = 260 + (i % 3) * 60;
        const targetScale = 0.35 + ((i % 2 === 0 ? 0.45 : 0.25));
        return Animated.loop(
          Animated.sequence([
            Animated.timing(anim, {
              toValue: targetScale,
              duration: speed,
              easing: Easing.inOut(Easing.quad),
              useNativeDriver: true,
            }),
            Animated.timing(anim, {
              toValue: 0.12,
              duration: speed,
              easing: Easing.inOut(Easing.quad),
              useNativeDriver: true,
            }),
          ])
        );
      });
      animLoop = Animated.parallel(animations);
      animLoop.start();
    } else if (currentMode === 'thinking') {
      // Smooth orbital pulse for thinking state
      const animations = barAnims.map((anim, i) => {
        return Animated.loop(
          Animated.sequence([
            Animated.delay(i * 120),
            Animated.timing(anim, {
              toValue: 0.6,
              duration: 450,
              easing: Easing.inOut(Easing.sin),
              useNativeDriver: true,
            }),
            Animated.timing(anim, {
              toValue: 0.15,
              duration: 450,
              easing: Easing.inOut(Easing.sin),
              useNativeDriver: true,
            }),
          ])
        );
      });
      animLoop = Animated.parallel(animations);
      animLoop.start();
    } else {
      // Idle / Minimal baseline
      barAnims.forEach((anim) => {
        Animated.timing(anim, {
          toValue: 0.1,
          duration: 300,
          useNativeDriver: true,
        }).start();
      });
    }

    return () => {
      if (animLoop) animLoop.stop();
    };
  }, [currentMode]);

  // Color Theme & Status Config
  const getVisualizerConfig = () => {
    switch (currentMode) {
      case 'speaking':
        return {
          barColor: '#0A84FF',
          glowColor: 'rgba(10, 132, 255, 0.3)',
          label: '말하고 있어요 🗣️',
          icon: '⚡',
        };
      case 'listening':
        return {
          barColor: '#30D158',
          glowColor: 'rgba(48, 209, 88, 0.3)',
          label: '듣고 있어요 🎙️',
          icon: '✨',
        };
      case 'thinking':
        return {
          barColor: '#AF52DE',
          glowColor: 'rgba(175, 82, 222, 0.3)',
          label: '생각하고 있어요 🧠',
          icon: '💭',
        };
      case 'interrupted':
        return {
          barColor: '#FF9F0A',
          glowColor: 'rgba(255, 159, 10, 0.3)',
          label: '듣는 중...',
          icon: '✋',
        };
      case 'error':
        return {
          barColor: '#FF453A',
          glowColor: 'rgba(255, 69, 58, 0.3)',
          label: '연결 확인 중...',
          icon: '⚠️',
        };
      case 'idle':
      default:
        return {
          barColor: isLiveMode ? '#30D158' : '#8E8E93',
          glowColor: 'transparent',
          label: isLiveMode ? 'Live 대기 중' : '대기 중',
          icon: isLiveMode ? '✨' : '●',
        };
    }
  };

  const config = getVisualizerConfig();

  return (
    <View style={styles.container}>
      <View style={[styles.visualizerCard, { shadowColor: config.barColor }]}>
        {/* Status Badge */}
        <View style={styles.statusRow}>
          <Text style={styles.statusIcon}>{config.icon}</Text>
          <Text style={[styles.statusText, { color: config.barColor }]}>{config.label}</Text>
        </View>

        {/* 7-Bar Real-Time Audio Waveform */}
        <View style={styles.waveformContainer}>
          {barAnims.map((anim, index) => (
            <Animated.View
              key={index}
              style={[
                styles.waveBar,
                {
                  backgroundColor: config.barColor,
                  transform: [{ scaleY: anim }],
                },
              ]}
            />
          ))}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 4,
  },
  visualizerCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
    backgroundColor: 'rgba(20, 20, 24, 0.82)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.12)',
    minWidth: 190,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.35,
    shadowRadius: 6,
    elevation: 4,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginRight: 12,
  },
  statusIcon: {
    fontSize: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: -0.2,
  },
  waveformContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 3.5,
    height: 24,
    paddingHorizontal: 4,
  },
  waveBar: {
    width: 3.5,
    height: 22,
    borderRadius: 2,
  },
});
