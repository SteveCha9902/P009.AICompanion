import { create } from 'zustand';

interface AppState {
  isConnected: boolean;
  setConnected: (status: boolean) => void;
  // Companion state placeholder
  companionState: {
    emotion: string;
    relationshipLevel: number;
  };
}

export const useAppStore = create<AppState>((set) => ({
  isConnected: false,
  setConnected: (status: boolean) => set({ isConnected: status }),
  companionState: {
    emotion: 'neutral',
    relationshipLevel: 0
  }
}));
