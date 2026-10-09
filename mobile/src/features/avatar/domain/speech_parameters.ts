/**
 * Speech Parameters DTO (Sprint 42)
 */
export type VisemeCode = 'closed' | 'viseme_a' | 'viseme_e' | 'viseme_i' | 'viseme_o' | 'viseme_u';

export interface SpeechParameters {
  isSpeaking: boolean;
  mouthOpen: number;         // 0.0 ~ 1.0
  viseme: VisemeCode;
  speechIntensity: number;   // 0.0 ~ 1.0
  speechProgress: number;    // 0.0 ~ 1.0
}

export const DEFAULT_SPEECH_PARAMETERS: SpeechParameters = {
  isSpeaking: false,
  mouthOpen: 0.0,
  viseme: 'closed',
  speechIntensity: 0.5,
  speechProgress: 0.0,
};
