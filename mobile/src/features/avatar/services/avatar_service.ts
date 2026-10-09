import { AvatarState, AvatarConversationState } from '../domain/avatar_state';

class AvatarService {
  private currentState: AvatarState;
  private listeners: ((state: AvatarState) => void)[] = [];
  
  constructor() {
    this.currentState = {
      state_version: 0,
      timestamp: new Date().toISOString(),
      conversation_state: 'IDLE',
      expression: 'neutral',
      animation: 'idle',
      gaze: 'user',
      speaking: false,
      listening: false,
      intensity: 0.5,
      energy: 0.5
    };
  }

  // Called for immediate partial updates
  public updatePartialState(partial: Partial<AvatarState>) {
    this.currentState = {
      ...this.currentState,
      ...partial,
      state_version: this.currentState.state_version + 1,
      timestamp: new Date().toISOString(),
    };
    this.notifyListeners();
  }

  public setConversationState(conversationState: AvatarConversationState) {
    let speaking = false;
    let listening = false;
    let animation = 'idle';

    switch (conversationState) {
      case 'LISTENING':
        listening = true;
        animation = 'listening';
        break;
      case 'THINKING':
        animation = 'thinking';
        break;
      case 'SPEAKING':
        speaking = true;
        animation = 'speaking';
        break;
      case 'INTERRUPTED':
        listening = true;
        animation = 'interrupted';
        break;
      case 'ERROR':
        animation = 'error';
        break;
      case 'IDLE':
      default:
        animation = 'idle';
        break;
    }

    this.updatePartialState({
      conversation_state: conversationState,
      speaking,
      listening,
      animation,
    });
  }

  public setAnimation(animation: string) {
    this.updatePartialState({ animation });
  }

  // Called when polling/SSE receives an update from backend AvatarStateResolver
  public updateSemanticState(newState: AvatarState) {
    if (newState.state_version >= this.currentState.state_version) {
      this.currentState = {
        ...this.currentState,
        ...newState,
        speaking: this.currentState.speaking 
      };
      this.notifyListeners();
    }
  }

  // Called by AudioPlayer.onStart / onComplete
  public setSpeaking(isSpeaking: boolean) {
    if (isSpeaking) {
      this.setConversationState('SPEAKING');
    } else {
      if (this.currentState.conversation_state === 'SPEAKING') {
        this.setConversationState('IDLE');
      }
    }
  }

  public subscribe(listener: (state: AvatarState) => void) {
    this.listeners.push(listener);
    listener(this.currentState); // immediate sync
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notifyListeners() {
    for (const listener of this.listeners) {
      listener(this.currentState);
    }
  }
}

export const avatarService = new AvatarService();

