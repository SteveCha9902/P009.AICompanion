import { VisemeCode, SpeechParameters, DEFAULT_SPEECH_PARAMETERS } from '../domain/speech_parameters';
import { MouthEngine, MouthState, MouthTier } from './MouthEngine';

export type LipSyncVersion = 'V1_AMPLITUDE' | 'V2_VOICE_FEATURE' | 'V3_PHONEME_VISEME';

/**
 * Common Extensible Interface for Lip Sync Providers (V1 Amplitude -> V2 Voice Feature -> V3 Viseme)
 */
export interface ILipSyncProvider {
  version: LipSyncVersion;
  processFrame(audioTimeSec: number, durationSec: number, amplitudeRms?: number): SpeechParameters;
  reset(): void;
}

/**
 * V1: Amplitude / RMS-based Lip Sync Provider
 * Converts audio waveform energy into mouth opening tiers (Closed, Slight, Medium, Open).
 */
export class V1AmplitudeLipSyncProvider implements ILipSyncProvider {
  public readonly version: LipSyncVersion = 'V1_AMPLITUDE';
  private smoothedMouthOpen = 0.0;
  private readonly EMA_ALPHA = 0.45; // Smooth blend factor to eliminate jitter

  public processFrame(audioTimeSec: number, durationSec: number, amplitudeRms?: number): SpeechParameters {
    if (durationSec <= 0 || audioTimeSec < 0 || audioTimeSec > durationSec) {
      this.reset();
      return { ...DEFAULT_SPEECH_PARAMETERS, isSpeaking: false };
    }

    let rawAmplitude = 0.0;
    if (amplitudeRms !== undefined) {
      rawAmplitude = Math.max(0.0, Math.min(1.0, amplitudeRms));
    } else {
      // Synthesize realistic speech envelope synced with playback clock
      // Syllabic envelope modulation (4Hz fundamental syllabic rhythm + 8Hz micro-formants)
      const syllableWave = Math.sin(audioTimeSec * Math.PI * 8.0);
      const subHarmonic = Math.sin(audioTimeSec * Math.PI * 16.0) * 0.3;
      const envelope = Math.sin((audioTimeSec / durationSec) * Math.PI); // Attack and release
      rawAmplitude = Math.max(0.0, (syllableWave * 0.7 + subHarmonic + 0.3)) * envelope;
    }

    // Apply Exponential Moving Average (EMA) smoothing
    this.smoothedMouthOpen = this.EMA_ALPHA * rawAmplitude + (1.0 - this.EMA_ALPHA) * this.smoothedMouthOpen;
    const mouthOpen = Math.round(this.smoothedMouthOpen * 1000) / 1000;

    // Map to Visemes based on amplitude stages
    let viseme: VisemeCode = 'closed';
    if (mouthOpen >= 0.68) {
      viseme = 'viseme_a'; // Open
    } else if (mouthOpen >= 0.38) {
      viseme = 'viseme_o'; // Medium
    } else if (mouthOpen >= 0.12) {
      viseme = 'viseme_e'; // Slight
    } else {
      viseme = 'closed'; // Closed
    }

    return {
      isSpeaking: true,
      mouthOpen,
      viseme,
      speechIntensity: Math.min(1.0, mouthOpen * 1.2),
      speechProgress: durationSec > 0 ? audioTimeSec / durationSec : 0.0,
    };
  }

  public reset(): void {
    this.smoothedMouthOpen = 0.0;
  }
}

/**
 * V2: Voice Feature Extensible Stub (Prepared for Spectral / Formant features)
 */
export class V2VoiceFeatureLipSyncProvider implements ILipSyncProvider {
  public readonly version: LipSyncVersion = 'V2_VOICE_FEATURE';
  private v1Fallback = new V1AmplitudeLipSyncProvider();

  public processFrame(audioTimeSec: number, durationSec: number, amplitudeRms?: number): SpeechParameters {
    return this.v1Fallback.processFrame(audioTimeSec, durationSec, amplitudeRms);
  }

  public reset(): void {
    this.v1Fallback.reset();
  }
}

/**
 * V3: Phoneme / Viseme Extensible Stub (Prepared for Whisper timestamped phonemes)
 */
export class V3PhonemeVisemeLipSyncProvider implements ILipSyncProvider {
  public readonly version: LipSyncVersion = 'V3_PHONEME_VISEME';
  private v1Fallback = new V1AmplitudeLipSyncProvider();

  public processFrame(audioTimeSec: number, durationSec: number, amplitudeRms?: number): SpeechParameters {
    return this.v1Fallback.processFrame(audioTimeSec, durationSec, amplitudeRms);
  }

  public reset(): void {
    this.v1Fallback.reset();
  }
}

/**
 * Lip Sync Engine (STEP 11 — Audio Driven Lip Sync Master Controller)
 * Connects audio amplitude, mouth opening states (Closed, Slight, Medium, Open),
 * animation clock synchronization, and extensible V1/V2/V3 providers.
 */
export class LipSyncEngine {
  private static activeProvider: ILipSyncProvider = new V1AmplitudeLipSyncProvider();

  public static setProvider(provider: ILipSyncProvider): void {
    this.activeProvider = provider;
  }

  public static getProviderVersion(): LipSyncVersion {
    return this.activeProvider.version;
  }

  /**
   * Evaluates current speech frame synced to audio playback clock
   */
  public static processAudioFrame(audioTimeSec: number, durationSec: number, amplitudeRms?: number): SpeechParameters {
    return this.activeProvider.processFrame(audioTimeSec, durationSec, amplitudeRms);
  }

  private static staticSmoothedMouthOpen = 0.0;
  private static readonly EMA_ALPHA = 0.45;

  /**
   * Applies Exponential Moving Average (EMA) smoothing to prevent mouth jitter
   */
  public static smoothMouthOpen(rawTarget: number): number {
    const clamped = Math.max(0.0, Math.min(1.0, rawTarget));
    this.staticSmoothedMouthOpen = this.EMA_ALPHA * clamped + (1.0 - this.EMA_ALPHA) * this.staticSmoothedMouthOpen;
    return Math.round(this.staticSmoothedMouthOpen * 1000) / 1000;
  }

  /**
   * Resets smoothing state upon speech termination
   */
  public static reset(): void {
    this.staticSmoothedMouthOpen = 0.0;
    this.activeProvider.reset();
  }

  /**
   * Returns mouth opening stage: 'Closed' | 'Slight' | 'Medium' | 'Open'
   */
  public static getMouthState(mouthOpen: number): MouthState {
    return MouthEngine.getMouthState(mouthOpen);
  }

  /**
   * Returns legacy mouth tier: 'closed' | 'small' | 'medium' | 'wide'
   */
  public static getMouthTier(mouthOpen: number): MouthTier {
    return MouthEngine.getMouthTier(mouthOpen);
  }

  /**
   * Returns viseme scale modifiers for realistic articulation
   */
  public static getVisemeScale(viseme: VisemeCode): { scaleX: number; scaleY: number } {
    switch (viseme) {
      case 'viseme_a':
        return { scaleX: 1.0, scaleY: 1.4 }; // Wide vertical open
      case 'viseme_e':
        return { scaleX: 1.1, scaleY: 1.2 }; // Neutral medium open
      case 'viseme_i':
        return { scaleX: 1.3, scaleY: 1.05 }; // Lateral horizontal stretch
      case 'viseme_o':
        return { scaleX: 0.85, scaleY: 1.35 }; // Rounded open
      case 'viseme_u':
        return { scaleX: 0.75, scaleY: 1.15 }; // Small rounded protrusion
      case 'closed':
      default:
        return { scaleX: 1.0, scaleY: 1.0 };
    }
  }

  /**
   * Calculates speaking micro head and brow accent
   */
  public static getSpeakingMicroMotion(intensity: number, elapsedSec: number): { headPitchAccent: number; browAccent: number } {
    const headPitchAccent = Math.sin(elapsedSec * 5.0) * 1.5 * intensity;
    const browAccent = Math.max(0.0, Math.sin(elapsedSec * 2.5) * 0.15 * intensity);
    return { headPitchAccent, browAccent };
  }
}

