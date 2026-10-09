/**
 * Motion Parameters DTO (Sprint 45)
 */
export interface MotionParameters {
  activeMotionId: string;
  headTilt: number;        // -10.0 ~ 10.0 deg
  headPitch: number;       // -10.0 ~ 10.0 deg
  headYaw: number;         // -10.0 ~ 10.0 deg
  nodIntensity: number;    // 0.0 ~ 1.0
  bodyLean: number;        // -1.0 ~ 1.0
  jitterFactor: number;    // 0.90 ~ 1.10
}

export const DEFAULT_MOTION_PARAMETERS: MotionParameters = {
  activeMotionId: 'DEFAULT_IDLE',
  headTilt: 0.0,
  headPitch: 0.0,
  headYaw: 0.0,
  nodIntensity: 0.0,
  bodyLean: 0.0,
  jitterFactor: 1.0,
};
