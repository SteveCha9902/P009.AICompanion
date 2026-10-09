/**
 * Embodied Behavior Parameters DTO (Sprint 43)
 */
export interface BehaviorParameters {
  attentionLevel: number;      // 0.0 ~ 1.0
  eyeContact: number;          // 0.0 ~ 1.0
  headTilt: number;            // -10.0 ~ 10.0 deg
  nodIntensity: number;        // 0.0 ~ 1.0
  bodyLean: number;            // -1.0 ~ 1.0
  curiosityLevel: number;      // 0.0 ~ 1.0
  thinkingIntensity: number;   // 0.0 ~ 1.0
}

export const DEFAULT_BEHAVIOR_PARAMETERS: BehaviorParameters = {
  attentionLevel: 0.80,
  eyeContact: 0.85,
  headTilt: 0.0,
  nodIntensity: 0.0,
  bodyLean: 0.0,
  curiosityLevel: 0.50,
  thinkingIntensity: 0.0,
};
