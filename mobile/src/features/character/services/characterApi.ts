import { API_URL } from '../../../config/env';

export interface CharacterSummary {
  companion_id: string;
  name: string;
  role_title: string;
  avatar_preview?: string;
  voice_name?: string;
  is_active: boolean;
}

export interface ActivateCharacterResponse {
  active_companion_id: string;
  character: CharacterSummary;
  message: string;
}

export interface VoiceConfig {
  provider?: string;
  voice_id: string;
  persona_type?: string;
  speaking_rate: number;
  pitch_offset: number;
  warmth: number;
  energy: number;
  empathy: number;
}

export interface CharacterPresentation {
  companion_id: string;
  voice: VoiceConfig;
  avatar?: any;
  expression?: any;
  gesture?: any;
}

export interface CharacterDetail {
  companion_id: string;
  name: string;
  display_name: string;
  role_title: string;
  origin_story: string;
  core_identity: string;
  personality_archetype?: string;
  avatar_preview?: string;
  voice_name?: string;
  is_active: boolean;
  personality?: Record<string, number>;
  dna?: {
    warmth: number;
    humor: number;
    curiosity: number;
    empathy: number;
    playfulness: number;
    formality: number;
    optimism: number;
  };
}

export const characterApi = {
  listCharacters: async (userId: string = 'default_user'): Promise<CharacterSummary[]> => {
    const res = await fetch(`${API_URL}/api/v1/characters`, {
      headers: { 'x-user-id': userId }
    });
    if (!res.ok) {
      throw new Error('Failed to fetch character list');
    }
    const data = await res.json();
    return data.characters || [];
  },

  getActiveCharacter: async (userId: string = 'default_user'): Promise<CharacterSummary> => {
    const res = await fetch(`${API_URL}/api/v1/characters/active`, {
      headers: { 'x-user-id': userId }
    });
    if (!res.ok) {
      throw new Error('Failed to fetch active character');
    }
    return res.json();
  },

  activateCharacter: async (companionId: string, userId: string = 'default_user'): Promise<ActivateCharacterResponse> => {
    const res = await fetch(`${API_URL}/api/v1/characters/${companionId}/activate`, {
      method: 'POST',
      headers: { 'x-user-id': userId }
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to switch character' }));
      throw new Error(err.detail || 'Failed to switch character');
    }
    return res.json();
  },

  getPresentation: async (companionId: string, userId: string = 'default_user'): Promise<CharacterPresentation> => {
    const res = await fetch(`${API_URL}/api/v1/characters/${companionId}/presentation`, {
      headers: { 'x-user-id': userId }
    });
    if (!res.ok) {
      throw new Error('Failed to fetch character presentation');
    }
    return res.json();
  },

  updatePresentation: async (companionId: string, payload: Partial<CharacterPresentation>, userId: string = 'default_user'): Promise<CharacterPresentation> => {
    const res = await fetch(`${API_URL}/api/v1/characters/${companionId}/presentation`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'x-user-id': userId
      },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to update character presentation' }));
      throw new Error(err.detail || 'Failed to update character presentation');
    }
    return res.json();
  },

  getCharacterDetail: async (companionId: string, userId: string = 'default_user'): Promise<CharacterDetail> => {
    const res = await fetch(`${API_URL}/api/v1/characters/${companionId}`, {
      headers: { 'x-user-id': userId }
    });
    if (!res.ok) {
      throw new Error('Failed to fetch character detail');
    }
    return res.json();
  },

  updateCharacter: async (companionId: string, payload: Partial<CharacterDetail>, userId: string = 'default_user'): Promise<CharacterDetail> => {
    const res = await fetch(`${API_URL}/api/v1/characters/${companionId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'x-user-id': userId
      },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to update character' }));
      throw new Error(err.detail || 'Failed to update character');
    }
    return res.json();
  }
};
