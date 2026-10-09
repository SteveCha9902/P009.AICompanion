import { API_URL } from '../../../config/env';

export interface CharacterPreviewPayload {
  name: string;
  template_id?: string;
  role_title?: string;
  tagline?: string;
  relationship_type?: string;
  mbti?: string;
  personality_keywords?: string[];
  interests?: string[];
  speaking_style?: string;
  speech_profile?: Record<string, any>;
  voice_id?: string;
  avatar_preset?: string;
  behavior_rules?: string[];
  origin_story?: string;
}

export interface CharacterPreviewData {
  name: string;
  role_title: string;
  tagline?: string;
  mbti: string;
  personality_traits: Record<string, number>;
  values: Record<string, number>;
  relationship_seed: Record<string, any>;
  interests: string[];
  speech_profile: Record<string, any>;
  voice: {
    voice_id: string;
    provider: string;
  };
  avatar: {
    avatar_preset: string;
    visual_style: string;
  };
  behavior_rules: string[];
  origin_story?: string;
}

export interface CharacterCreateResult {
  companion_id: string;
  name: string;
  role_title: string;
  status: string;
  is_active: boolean;
  message: string;
}

export const characterCreationApi = {
  previewCharacter: async (payload: CharacterPreviewPayload, userId: string = 'default_user'): Promise<CharacterPreviewData> => {
    const res = await fetch(`${API_URL}/api/v1/characters/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-user-id': userId
      },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to preview character' }));
      throw new Error(err.detail || 'Failed to preview character');
    }
    return res.json();
  },

  createCharacter: async (payload: CharacterPreviewPayload, userId: string = 'default_user'): Promise<CharacterCreateResult> => {
    const res = await fetch(`${API_URL}/api/v1/characters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-user-id': userId
      },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to create character' }));
      throw new Error(err.detail || 'Failed to create character');
    }
    return res.json();
  }
};
