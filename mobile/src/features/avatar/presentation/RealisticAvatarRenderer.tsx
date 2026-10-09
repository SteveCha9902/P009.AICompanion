import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet, Animated, Dimensions } from 'react-native';
import { AvatarState } from '../domain/avatar_state';
import { useCharacterStore } from '../../../state/useCharacterStore';
import { LipSyncEngine } from '../engine/LipSyncEngine';
import { MouthEngine, MouthState } from '../engine/MouthEngine';

// Pre-bundled realistic portrait assets for Genie (Wife)
const GENIE_ASSETS = {
  neutral: require('../../../../assets/avatar/neutral.jpg'),
  smile: require('../../../../assets/avatar/smile.jpg'),
  thinking: require('../../../../assets/avatar/thinking.jpg'),
  speaking: require('../../../../assets/avatar/speaking.jpg'),
  listening: require('../../../../assets/avatar/listening.jpg'),
};

// Pre-bundled realistic portrait assets for Mani (Daughter - 딸.png)
const MANI_ASSETS = {
  neutral: require('../../../../assets/avatar/mani/neutral.jpg'),
  smile: require('../../../../assets/avatar/mani/smile.jpg'),
  thinking: require('../../../../assets/avatar/mani/thinking.jpg'),
  speaking: require('../../../../assets/avatar/mani/speaking.jpg'),
  listening: require('../../../../assets/avatar/mani/listening.jpg'),
};

export interface RealisticAvatarRendererProps {
  state: AvatarState;
}

export const RealisticAvatarComponent: React.FC<RealisticAvatarRendererProps> = ({ state }) => {
  // Animation Values
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const glowOpacity = useRef(new Animated.Value(0.3)).current;
  const mouthScaleY = useRef(new Animated.Value(1)).current;
  const [mouthState, setMouthState] = useState<MouthState>('Closed');

  const convState = state.conversation_state || (state.speaking ? 'SPEAKING' : state.listening ? 'LISTENING' : 'IDLE');

  // Lip Sync Audio Playback Clock Synchronizer (STEP 11)
  useEffect(() => {
    let syncTimer: any = null;
    let elapsedSec = 0;

    if (convState === 'SPEAKING' || state.speaking) {
      syncTimer = setInterval(() => {
        elapsedSec += 0.05;
        // Synchronize audio clock with LipSync engine
        const speechParams = LipSyncEngine.processAudioFrame(elapsedSec, 4.0);
        const currentMouthState = MouthEngine.getMouthState(speechParams.mouthOpen);
        setMouthState(currentMouthState);

        const targetScaleY = MouthEngine.getMouthScaleY(speechParams.mouthOpen);
        Animated.timing(mouthScaleY, {
          toValue: targetScaleY,
          duration: 45,
          useNativeDriver: true,
        }).start();
      }, 50);
    } else {
      LipSyncEngine.reset();
      setMouthState('Closed');
      Animated.timing(mouthScaleY, {
        toValue: 1.0,
        duration: 200,
        useNativeDriver: true,
      }).start();
    }

    return () => {
      if (syncTimer) clearInterval(syncTimer);
    };
  }, [convState, state.speaking]);

  // Dynamic animation based on 6 conversation states
  useEffect(() => {
    let animation: Animated.CompositeAnimation;

    if (convState === 'SPEAKING' || state.speaking) {
      // Fast, rhythmic speech pulse
      animation = Animated.loop(
        Animated.sequence([
          Animated.parallel([
            Animated.timing(pulseAnim, { toValue: 1.04, duration: 350, useNativeDriver: true }),
            Animated.timing(glowOpacity, { toValue: 0.85, duration: 350, useNativeDriver: true }),
          ]),
          Animated.parallel([
            Animated.timing(pulseAnim, { toValue: 1.0, duration: 350, useNativeDriver: true }),
            Animated.timing(glowOpacity, { toValue: 0.35, duration: 350, useNativeDriver: true }),
          ]),
        ])
      );
    } else if (convState === 'THINKING' || state.animation === 'thinking') {
      // Thoughtful, steady breathing pulse
      animation = Animated.loop(
        Animated.sequence([
          Animated.parallel([
            Animated.timing(pulseAnim, { toValue: 1.03, duration: 1100, useNativeDriver: true }),
            Animated.timing(glowOpacity, { toValue: 0.75, duration: 1100, useNativeDriver: true }),
          ]),
          Animated.parallel([
            Animated.timing(pulseAnim, { toValue: 1.0, duration: 1100, useNativeDriver: true }),
            Animated.timing(glowOpacity, { toValue: 0.25, duration: 1100, useNativeDriver: true }),
          ]),
        ])
      );
    } else if (convState === 'LISTENING' || state.listening || state.animation === 'listening') {
      // Attentive, responsive listening pulse
      animation = Animated.loop(
        Animated.sequence([
          Animated.parallel([
            Animated.timing(pulseAnim, { toValue: 1.025, duration: 750, useNativeDriver: true }),
            Animated.timing(glowOpacity, { toValue: 0.7, duration: 750, useNativeDriver: true }),
          ]),
          Animated.parallel([
            Animated.timing(pulseAnim, { toValue: 1.0, duration: 750, useNativeDriver: true }),
            Animated.timing(glowOpacity, { toValue: 0.3, duration: 750, useNativeDriver: true }),
          ]),
        ])
      );
    } else if (convState === 'INTERRUPTED' || state.animation === 'interrupted') {
      // Fast alert pulse on interruption
      animation = Animated.sequence([
        Animated.parallel([
          Animated.timing(pulseAnim, { toValue: 1.035, duration: 250, useNativeDriver: true }),
          Animated.timing(glowOpacity, { toValue: 0.9, duration: 250, useNativeDriver: true }),
        ]),
        Animated.parallel([
          Animated.timing(pulseAnim, { toValue: 1.0, duration: 350, useNativeDriver: true }),
          Animated.timing(glowOpacity, { toValue: 0.4, duration: 350, useNativeDriver: true }),
        ]),
      ]);
    } else if (convState === 'ERROR' || state.animation === 'error') {
      // Soft red warning glow
      animation = Animated.sequence([
        Animated.parallel([
          Animated.timing(pulseAnim, { toValue: 1.02, duration: 300, useNativeDriver: true }),
          Animated.timing(glowOpacity, { toValue: 0.8, duration: 300, useNativeDriver: true }),
        ]),
        Animated.parallel([
          Animated.timing(pulseAnim, { toValue: 1.0, duration: 300, useNativeDriver: true }),
          Animated.timing(glowOpacity, { toValue: 0.3, duration: 300, useNativeDriver: true }),
        ]),
      ]);
    } else {
      // Natural idle calm breathing
      animation = Animated.loop(
        Animated.sequence([
          Animated.parallel([
            Animated.timing(pulseAnim, { toValue: 1.015, duration: 2500, useNativeDriver: true }),
            Animated.timing(glowOpacity, { toValue: 0.45, duration: 2500, useNativeDriver: true }),
          ]),
          Animated.parallel([
            Animated.timing(pulseAnim, { toValue: 1.0, duration: 2500, useNativeDriver: true }),
            Animated.timing(glowOpacity, { toValue: 0.2, duration: 2500, useNativeDriver: true }),
          ]),
        ])
      );
    }

    animation.start();
    return () => animation.stop();
  }, [convState, state.speaking, state.listening, state.animation]);

  // Detect Active Character (Genie vs Mani)
  const activeCharacterId = useCharacterStore((s) => s.activeCharacterId) || '';
  const activeCharacter = useCharacterStore((s) => s.activeCharacter);
  const isMani =
    activeCharacterId.toLowerCase().includes('mani') ||
    activeCharacter?.name?.toLowerCase().includes('mani') ||
    activeCharacter?.name === '마니';

  const assets = isMani ? MANI_ASSETS : GENIE_ASSETS;

  // Determine active image based on Avatar State Priority
  const getActiveSource = () => {
    if (convState === 'SPEAKING' || state.speaking) {
      return assets.speaking;
    }
    if (convState === 'THINKING' || state.animation === 'thinking') {
      return assets.thinking;
    }
    if (convState === 'LISTENING' || convState === 'INTERRUPTED' || state.listening || state.animation === 'listening' || state.animation === 'interrupted') {
      return assets.listening;
    }
    if (state.expression === 'warm_smile' || state.expression === 'smile' || state.expression === 'happy') {
      return assets.smile;
    }
    return assets.neutral;
  };

  // Determine Dynamic Glow Color for 6 Conversation States
  const getGlowColor = () => {
    switch (convState) {
      case 'SPEAKING':
        return '#0A84FF'; // Blue
      case 'THINKING':
        return '#AF52DE'; // Purple
      case 'LISTENING':
        return '#30D158'; // Emerald Green
      case 'INTERRUPTED':
        return '#FF9F0A'; // Amber Orange
      case 'ERROR':
        return '#FF453A'; // Alert Crimson
      case 'IDLE':
      default:
        return '#30D158'; // Calm Green
    }
  };

  const activeSource = getActiveSource();
  const glowColor = getGlowColor();

  return (
    <View style={styles.container}>
      {/* Dynamic Glow Aura */}
      <Animated.View
        style={[
          styles.glowRing,
          {
            transform: [{ scale: pulseAnim }],
            opacity: glowOpacity,
            borderColor: glowColor,
          },
        ]}
      />

      {/* Main Realistic Portrait Frame */}
      <Animated.View style={[styles.avatarFrame, { transform: [{ scale: pulseAnim }, { scaleY: mouthScaleY }] }]}>
        <Image source={activeSource} style={styles.avatarImage} resizeMode="cover" />
      </Animated.View>
    </View>
  );
};

const AVATAR_SIZE = 140;

const styles = StyleSheet.create({
  container: {
    width: AVATAR_SIZE + 24,
    height: AVATAR_SIZE + 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  glowRing: {
    position: 'absolute',
    width: AVATAR_SIZE + 18,
    height: AVATAR_SIZE + 18,
    borderRadius: (AVATAR_SIZE + 18) / 2,
    borderWidth: 3,
    backgroundColor: 'transparent',
  },
  avatarFrame: {
    width: AVATAR_SIZE,
    height: AVATAR_SIZE,
    borderRadius: AVATAR_SIZE / 2,
    overflow: 'hidden',
    backgroundColor: '#2c2c2e',
    borderWidth: 2.5,
    borderColor: '#e5e5ea',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.6,
    shadowRadius: 10,
    elevation: 10,
  },
  avatarImage: {
    width: '100%',
    height: '100%',
  },
});

