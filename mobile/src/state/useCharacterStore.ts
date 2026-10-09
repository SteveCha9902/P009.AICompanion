import { create } from 'zustand';
import { characterApi, CharacterSummary } from '../features/character/services/characterApi';

interface CharacterState {
  characterList: CharacterSummary[];
  activeCharacterId: string | null;
  activeCharacter: CharacterSummary | null;
  isLoading: boolean;
  isSwitching: boolean;
  error: string | null;
  lastUpdated: number | null;

  fetchCharacters: (userId?: string) => Promise<void>;
  fetchActiveCharacter: (userId?: string) => Promise<void>;
  switchCharacter: (companionId: string, userId?: string) => Promise<boolean>;
  refreshCharacters: (userId?: string) => Promise<void>;
  clearError: () => void;
}

export const useCharacterStore = create<CharacterState>((set, get) => ({
  characterList: [],
  activeCharacterId: null,
  activeCharacter: null,
  isLoading: false,
  isSwitching: false,
  error: null,
  lastUpdated: null,

  fetchCharacters: async (userId: string = 'default_user') => {
    set({ isLoading: true, error: null });
    try {
      const list = await characterApi.listCharacters(userId);
      const active = list.find((c) => c.is_active) || (list.length > 0 ? list[0] : null);
      set({
        characterList: list,
        activeCharacter: active,
        activeCharacterId: active ? active.companion_id : null,
        isLoading: false,
        lastUpdated: Date.now()
      });
    } catch (err: any) {
      set({
        isLoading: false,
        error: err.message || '캐릭터 목록을 불러오지 못했습니다.'
      });
    }
  },

  fetchActiveCharacter: async (userId: string = 'default_user') => {
    try {
      const active = await characterApi.getActiveCharacter(userId);
      set({
        activeCharacter: active,
        activeCharacterId: active.companion_id
      });
    } catch (err: any) {
      console.warn('[useCharacterStore] fetchActiveCharacter failed:', err);
    }
  },

  switchCharacter: async (companionId: string, userId: string = 'default_user') => {
    const { isSwitching, activeCharacterId } = get();

    // Prevent redundant or race-condition switching
    if (isSwitching) {
      console.warn('[useCharacterStore] Switch already in progress, dropping request.');
      return false;
    }
    if (activeCharacterId === companionId) {
      return true;
    }

    set({ isSwitching: true, error: null });

    try {
      // 1. Server-Confirmed Activation
      const res = await characterApi.activateCharacter(companionId, userId);

      // 2. Update Local State on Server Success
      const currentList = get().characterList;
      const updatedList = currentList.map((c) => ({
        ...c,
        is_active: c.companion_id === res.active_companion_id
      }));

      set({
        characterList: updatedList,
        activeCharacter: res.character,
        activeCharacterId: res.active_companion_id,
        isSwitching: false,
        lastUpdated: Date.now()
      });

      return true;
    } catch (err: any) {
      console.error('[useCharacterStore] switchCharacter failed:', err);
      set({
        isSwitching: false,
        error: err.message || '캐릭터 전환에 실패했습니다.'
      });
      return false;
    }
  },

  refreshCharacters: async (userId: string = 'default_user') => {
    await get().fetchCharacters(userId);
  },

  clearError: () => set({ error: null })
}));
