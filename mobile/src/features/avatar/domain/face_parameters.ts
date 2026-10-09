/**
 * Standard FaceParameters DTO for real-time renderer (Sprint 41)
 */
export interface FaceParameters {
  eyeOpenness: number;    // 0.0 ~ 1.0
  blinkWeight: number;    // 0.0 ~ 1.0
  eyeDirectionX: number;  // -1.0 ~ 1.0
  eyeDirectionY: number;  // -1.0 ~ 1.0

  mouthOpen: number;      // 0.0 ~ 1.0
  smileStrength: number;  // 0.0 ~ 1.0

  browRaise: number;      // -1.0 ~ 1.0

  headPitch: number;      // -10.0 ~ 10.0 deg
  headYaw: number;        // -10.0 ~ 10.0 deg
  headRoll: number;       // -10.0 ~ 10.0 deg

  warmth: number;         // 0.0 ~ 1.0
}

export const DEFAULT_FACE_PARAMETERS: FaceParameters = {
  eyeOpenness: 0.9,
  blinkWeight: 0.0,
  eyeDirectionX: 0.0,
  eyeDirectionY: 0.0,
  mouthOpen: 0.0,
  smileStrength: 0.3,
  browRaise: 0.0,
  headPitch: 0.0,
  headYaw: 0.0,
  headRoll: 0.0,
  warmth: 0.5,
};
