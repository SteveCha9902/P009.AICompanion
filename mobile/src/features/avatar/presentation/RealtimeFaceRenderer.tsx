import React, { useEffect, useRef, useState } from 'react';
import { View, Image, StyleSheet, Animated, Dimensions } from 'react-native';
import { FaceParameters, DEFAULT_FACE_PARAMETERS } from '../domain/face_parameters';
import { SpeechParameters, DEFAULT_SPEECH_PARAMETERS, VisemeCode } from '../domain/speech_parameters';
import { BehaviorParameters, DEFAULT_BEHAVIOR_PARAMETERS } from '../domain/behavior_parameters';
import { RelationshipParameters, DEFAULT_RELATIONSHIP_PARAMETERS } from '../domain/relationship_parameters';
import { MotionParameters, DEFAULT_MOTION_PARAMETERS } from '../domain/motion_parameters';
import { EyeEngine } from '../engine/EyeEngine';
import { MouthEngine } from '../engine/MouthEngine';
import { BrowEngine } from '../engine/BrowEngine';
import { SmileEngine } from '../engine/SmileEngine';
import { LipSyncEngine } from '../engine/LipSyncEngine';
import { BehaviorEngine } from '../engine/BehaviorEngine';
import { EmotionRelationshipEngine } from '../engine/EmotionRelationshipEngine';
import { MotionVarietyEngine } from '../engine/MotionVarietyEngine';
import { useCharacterStore } from '../../../state/useCharacterStore';

const GENIE_PORTRAITS = {
  neutral: require('../../../../assets/avatar/neutral.jpg'),
  smile: require('../../../../assets/avatar/smile.jpg'),
  thinking: require('../../../../assets/avatar/thinking.jpg'),
  speaking: require('../../../../assets/avatar/speaking.jpg'),
  listening: require('../../../../assets/avatar/listening.jpg'),
};

const MANI_PORTRAITS = {
  neutral: require('../../../../assets/avatar/mani/neutral.jpg'),
  smile: require('../../../../assets/avatar/mani/smile.jpg'),
  thinking: require('../../../../assets/avatar/mani/thinking.jpg'),
  speaking: require('../../../../assets/avatar/mani/speaking.jpg'),
  listening: require('../../../../assets/avatar/mani/listening.jpg'),
};

export interface RealtimeFaceRendererProps {
  faceParameters?: FaceParameters;
  speechParameters?: SpeechParameters;
  behaviorParameters?: BehaviorParameters;
  relationshipParameters?: RelationshipParameters;
  motionParameters?: MotionParameters;
  stateName?: string;
  isSpeaking?: boolean;
  focusAnchor?: string; // USER_FACE, LOWER_LEFT, LOWER_CENTER, LOWER_RIGHT, etc.
}

/**
 * Real-Time Embodied Avatar & Variety Renderer (Sprint 49)
 * Full Integration of Face, LipSync, Behavior, Motion Variety, and Joint Attention Alignment
 */
export const RealtimeFaceRenderer: React.FC<RealtimeFaceRendererProps> = ({
  faceParameters = DEFAULT_FACE_PARAMETERS,
  speechParameters = DEFAULT_SPEECH_PARAMETERS,
  behaviorParameters = DEFAULT_BEHAVIOR_PARAMETERS,
  relationshipParameters = DEFAULT_RELATIONSHIP_PARAMETERS,
  motionParameters = DEFAULT_MOTION_PARAMETERS,
  stateName = 'idle',
  isSpeaking = false,
  focusAnchor = 'USER_FACE',
}) => {
  const [blinkWeight, setBlinkWeight] = useState(0.0);
  const [currentViseme, setCurrentViseme] = useState<VisemeCode>('closed');

  // Animated Values for 60fps Native Driver Execution
  const headRollAnim = useRef(new Animated.Value(0)).current;
  const headPitchAnim = useRef(new Animated.Value(0)).current;
  const browAnim = useRef(new Animated.Value(0)).current;
  const mouthScaleXAnim = useRef(new Animated.Value(1)).current;
  const mouthScaleYAnim = useRef(new Animated.Value(1)).current;
  const auraGlowAnim = useRef(new Animated.Value(0.35)).current;
  const breathingScale = useRef(new Animated.Value(1)).current;

  const elapsedTimeRef = useRef(0.0);

  // Joint Attention Gaze & Head Tilt Alignment (Sprint 49)
  useEffect(() => {
    let targetPitch = 0.0;
    let targetRoll = 0.0;

    switch (focusAnchor) {
      case 'LOWER_RIGHT':
        targetPitch = 3.5;
        targetRoll = 2.0;
        break;
      case 'LOWER_LEFT':
        targetPitch = 3.5;
        targetRoll = -2.0;
        break;
      case 'LOWER_CENTER':
        targetPitch = 4.0;
        targetRoll = 0.5;
        break;
      case 'UPPER_RIGHT':
        targetPitch = -2.5;
        targetRoll = 1.5;
        break;
      case 'UPPER_LEFT':
        targetPitch = -2.5;
        targetRoll = -1.5;
        break;
      default:
        targetPitch = faceParameters.headPitch;
        targetRoll = faceParameters.headRoll;
    }

    Animated.parallel([
      Animated.timing(headPitchAnim, { toValue: targetPitch, duration: 400, useNativeDriver: true }),
      Animated.timing(headRollAnim, { toValue: targetRoll, duration: 400, useNativeDriver: true }),
    ]).start();
  }, [focusAnchor, faceParameters.headPitch, faceParameters.headRoll]);


  // 1. Organic Breathing Loop
  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(breathingScale, { toValue: 1.018, duration: 2250, useNativeDriver: true }),
        Animated.timing(breathingScale, { toValue: 1.0, duration: 2250, useNativeDriver: true }),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, []);

  // 2. EyeEngine Blink Loop (Modulated by Attention & Trust)
  useEffect(() => {
    const cancelBlink = EyeEngine.scheduleNextBlink((weight) => {
      setBlinkWeight(weight);
    });
    return () => cancelBlink();
  }, [behaviorParameters.attentionLevel, relationshipParameters.trust]);

  // 3. Lip Sync & Speaking Micro Motion Loop
  const activeSpeaking = isSpeaking || speechParameters.isSpeaking;
  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    if (activeSpeaking) {
      const visemesList: VisemeCode[] = ['viseme_a', 'viseme_e', 'viseme_i', 'viseme_o', 'viseme_u'];
      let vIndex = 0;

      intervalId = setInterval(() => {
        elapsedTimeRef.current += 0.08;
        const targetViseme = visemesList[vIndex % visemesList.length];
        vIndex++;
        setCurrentViseme(targetViseme);

        const rawMouthOpen = 0.3 + Math.random() * 0.45 * speechParameters.speechIntensity;
        const smoothedOpen = LipSyncEngine.smoothMouthOpen(rawMouthOpen);
        const visemeScale = LipSyncEngine.getVisemeScale(targetViseme);
        const microMotion = LipSyncEngine.getSpeakingMicroMotion(speechParameters.speechIntensity, elapsedTimeRef.current);

        Animated.parallel([
          Animated.timing(mouthScaleYAnim, {
            toValue: smoothedOpen * visemeScale.scaleY,
            duration: 80,
            useNativeDriver: true,
          }),
          Animated.timing(mouthScaleXAnim, {
            toValue: visemeScale.scaleX,
            duration: 80,
            useNativeDriver: true,
          }),
          Animated.timing(headPitchAnim, {
            toValue: faceParameters.headPitch + microMotion.headPitchAccent + motionParameters.headPitch,
            duration: 80,
            useNativeDriver: true,
          }),
        ]).start();
      }, 80);
    } else {
      LipSyncEngine.reset();
      elapsedTimeRef.current = 0.0;
      setCurrentViseme('closed');
      Animated.parallel([
        Animated.timing(mouthScaleYAnim, { toValue: 1.0, duration: 100, useNativeDriver: true }),
        Animated.timing(mouthScaleXAnim, { toValue: 1.0, duration: 100, useNativeDriver: true }),
      ]).start();
    }

    return () => clearInterval(intervalId);
  }, [activeSpeaking, speechParameters.speechIntensity, motionParameters.headPitch]);

  // 4. Physical Embodiment & Behavioral Variety Layer V2
  useEffect(() => {
    const targetBrowY = BrowEngine.calculateBrowTranslateY(faceParameters.browRaise);
    const nodOffset = BehaviorEngine.calculateNodOffset(behaviorParameters.nodIntensity, elapsedTimeRef.current);

    const totalRoll = MotionVarietyEngine.calculateTotalHeadRoll(
      faceParameters.headRoll,
      behaviorParameters.headTilt,
      motionParameters.headTilt
    );
    const totalPitch = MotionVarietyEngine.calculateTotalHeadPitch(
      faceParameters.headPitch,
      nodOffset,
      motionParameters.headPitch
    );

    // Apply Relationship Warmth Aura
    const modulatedWarmth = EmotionRelationshipEngine.modulateWarmthAura(faceParameters.warmth, relationshipParameters);

    Animated.parallel([
      Animated.timing(headRollAnim, {
        toValue: totalRoll,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(headPitchAnim, {
        toValue: totalPitch,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(browAnim, {
        toValue: targetBrowY,
        duration: 250,
        useNativeDriver: true,
      }),
      Animated.timing(auraGlowAnim, {
        toValue: modulatedWarmth,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  }, [faceParameters, behaviorParameters, relationshipParameters, motionParameters]);

  // Detect Active Character (Genie vs Mani)
  const activeCharacterId = useCharacterStore((s) => s.activeCharacterId) || '';
  const activeCharacter = useCharacterStore((s) => s.activeCharacter);
  const isMani =
    activeCharacterId.toLowerCase().includes('mani') ||
    activeCharacter?.name?.toLowerCase().includes('mani') ||
    activeCharacter?.name === '마니';

  const portraits = isMani ? MANI_PORTRAITS : GENIE_PORTRAITS;

  // Select Portrait based on Relationship Bias & State
  const getActivePortrait = () => {
    if (activeSpeaking) return portraits.speaking;
    const effectiveSmile = EmotionRelationshipEngine.modulateSmile(faceParameters.smileStrength, relationshipParameters);
    if (effectiveSmile >= 0.55) return portraits.smile;
    if (stateName === 'thinking' || behaviorParameters.thinkingIntensity >= 0.5) return portraits.thinking;
    if (stateName === 'listening' || behaviorParameters.attentionLevel >= 0.9) return portraits.listening;
    return portraits.neutral;
  };

  const activePortrait = getActivePortrait();

  const auraColor = activeSpeaking
    ? '#0A84FF'
    : stateName === 'listening'
    ? '#30D158'
    : stateName === 'thinking'
    ? '#BF5AF2'
    : '#FF9F0A';

  const interpolatedRotation = headRollAnim.interpolate({
    inputRange: [-10, 10],
    outputRange: ['-10deg', '10deg'],
  });

  return (
    <View style={styles.container}>
      {/* Main Face & Physical Embodiment Container */}
      <Animated.View
        style={[
          styles.portraitContainer,
          {
            transform: [
              { scale: breathingScale },
              { rotate: interpolatedRotation },
            ],
          },
        ]}
      >
        <Image source={activePortrait} style={styles.portraitImage} resizeMode="cover" />
      </Animated.View>
    </View>
  );
};



const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');
const PORTRAIT_WIDTH = Math.min(SCREEN_WIDTH * 0.96, 420);
const PORTRAIT_HEIGHT = Math.min(SCREEN_HEIGHT * 0.69, 580);

const styles = StyleSheet.create({
  container: {
    justifyContent: 'flex-start',
    alignItems: 'center',
    width: '100%',
    height: '100%',
    paddingTop: 0,
  },
  auraGlow: {
    position: 'absolute',
    top: 0,
    width: PORTRAIT_WIDTH + 14,
    height: PORTRAIT_HEIGHT + 14,
    borderRadius: 28,
    borderWidth: 2.5,
    backgroundColor: 'transparent',
    shadowColor: '#FFA000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.45,
    shadowRadius: 16,
    elevation: 8,
  },
  portraitContainer: {
    width: PORTRAIT_WIDTH,
    height: PORTRAIT_HEIGHT,
    borderRadius: 24,
    overflow: 'hidden',
    backgroundColor: '#1c1c1e',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.65,
    shadowRadius: 14,
    elevation: 10,
  },

  portraitImage: {
    width: '100%',
    height: '100%',
  },
});


