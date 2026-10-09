export type AvatarConversationState = 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'INTERRUPTED' | 'ERROR';

export interface AvatarState {
  state_version: number;
  timestamp: string;
  conversation_state: AvatarConversationState;
  expression: string;
  animation: string;
  gaze: string;
  speaking: boolean;
  listening: boolean;
  intensity: number;
  energy: number;
}
