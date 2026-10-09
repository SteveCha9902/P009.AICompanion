// Emotion to Presentation State Mapper
export type EmotionState = 'JOY' | 'SADNESS' | 'ANGER' | 'FEAR' | 'SURPRISE' | 'DISGUST' | 'ANTICIPATION' | 'TRUST' | 'NEUTRAL';
export type PresentationState = 'SMILE' | 'CONCERNED' | 'EXCITED' | 'NEUTRAL' | 'FOCUSED';

export function mapEmotionToPresentation(emotion: EmotionState): PresentationState {
  switch (emotion) {
    case 'JOY':
    case 'TRUST':
      return 'SMILE';
    case 'SADNESS':
    case 'FEAR':
    case 'DISGUST':
      return 'CONCERNED';
    case 'ANTICIPATION':
    case 'SURPRISE':
      return 'EXCITED';
    case 'ANGER':
      return 'FOCUSED';
    case 'NEUTRAL':
    default:
      return 'NEUTRAL';
  }
}

export function getFaceForPresentation(state: PresentationState): string {
  switch (state) {
    case 'SMILE': return '😊';
    case 'CONCERNED': return '😟';
    case 'EXCITED': return '🤩';
    case 'FOCUSED': return '🤔';
    case 'NEUTRAL':
    default: return '🙂';
  }
}
