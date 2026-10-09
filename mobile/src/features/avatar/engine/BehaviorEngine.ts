import { BehaviorParameters } from '../domain/behavior_parameters';

/**
 * Embodied Behavior Engine (Sprint 43)
 * Manages physical non-verbal embodiment: eye contact, head tilts, nods, attention, and settling.
 */
export class BehaviorEngine {
  /**
   * Evaluates listening nod wave offset based on elapsed time and nod intensity
   */
  public static calculateNodOffset(nodIntensity: number, elapsedSec: number): number {
    if (nodIntensity <= 0.05) return 0.0;
    // Rhythmic gentle agreement nod (1.2 Hz)
    return Math.sin(elapsedSec * 4.5) * 2.0 * nodIntensity;
  }

  /**
   * Applies attention-based jitter suppression factor (higher attention = less chaotic jitter)
   */
  public static getAttentionNoiseScale(attentionLevel: number): number {
    return Math.max(0.1, 1.0 - attentionLevel * 0.75);
  }

  /**
   * Calculates settling interpolation weight (0.0 to 1.0)
   */
  public static getSettlingBlend(progress: number): number {
    // Smooth cubic ease-out
    const clamped = Math.max(0.0, Math.min(1.0, progress));
    return 1.0 - Math.pow(1.0 - clamped, 3);
  }
}
