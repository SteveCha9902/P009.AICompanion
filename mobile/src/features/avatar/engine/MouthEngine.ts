export type MouthTier = 'closed' | 'small' | 'medium' | 'wide';
export type MouthState = 'Closed' | 'Slight' | 'Medium' | 'Open';

/**
 * Mouth Engine (STEP 11 — Audio Driven Lip Sync)
 * Evaluates mouth opening stages (Closed, Slight, Medium, Open) from Audio Amplitude / RMS.
 */
export class MouthEngine {
  public static getMouthState(mouthOpen: number): MouthState {
    const clamped = Math.max(0.0, Math.min(1.0, mouthOpen));
    if (clamped < 0.12) return 'Closed';
    if (clamped < 0.38) return 'Slight';
    if (clamped < 0.68) return 'Medium';
    return 'Open';
  }

  public static getMouthTier(mouthOpen: number): MouthTier {
    const clamped = Math.max(0.0, Math.min(1.0, mouthOpen));
    if (clamped < 0.12) return 'closed';
    if (clamped < 0.38) return 'small';
    if (clamped < 0.68) return 'medium';
    return 'wide';
  }

  public static getMouthScaleY(mouthOpen: number): number {
    return 1.0 + Math.max(0.0, Math.min(1.0, mouthOpen)) * 0.4;
  }
}

