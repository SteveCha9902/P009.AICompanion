import { MotionParameters } from '../domain/motion_parameters';

/**
 * Mobile Behavioral Variety & Motion Layer V2 Engine (Sprint 45)
 * Synthesizes head rotations, nods, and body leans with stochastic micro-jitter.
 */
export class MotionVarietyEngine {
  /**
   * Applies +-10% stochastic jitter to prevent mechanical movement repetition
   */
  public static applyMicroJitter(value: number): number {
    const jitter = 0.90 + Math.random() * 0.20;
    return Math.round(value * jitter * 100) / 100;
  }

  /**
   * Calculates dynamic head rotation combining face, behavior, and motion parameters
   */
  public static calculateTotalHeadRoll(baseRoll: number, behaviorTilt: number, motionTilt: number): number {
    return baseRoll + behaviorTilt * 0.3 + motionTilt * 0.7;
  }

  /**
   * Calculates total pitch combining expression pitch, nod offset, and motion pitch
   */
  public static calculateTotalHeadPitch(basePitch: number, nodOffset: number, motionPitch: number): number {
    return basePitch + nodOffset + motionPitch;
  }
}
