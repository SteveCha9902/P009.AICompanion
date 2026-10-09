export interface CharacterIdentityData {
  id: string;
  companion_id: string;
  name: string;
  display_name: string;
  age_appearance: number;
  gender_expression: string;
  origin_story: string;
  self_description: string;
  core_identity: string;
  version: number;
}

export interface PersonalityProfileData {
  mbti_type: string;
  openness: number;
  conscientiousness: number;
  extraversion: number;
  agreeableness: number;
  neuroticism: number;
  humor_level: number;
  curiosity_level: number;
  empathy_level: number;
  assertiveness: number;
  playfulness: number;
  emotional_expressiveness: number;
  communication_directness: number;
  warmth: number;
  intellectuality: number;
}

export interface CharacterValuesData {
  curiosity: number;
  honesty: number;
  loyalty: number;
  independence: number;
  kindness: number;
  growth_orientation: number;
  humor: number;
}

export interface CharacterPreferenceData {
  category: string;
  item: string;
  preference_score: number;
  confidence: number;
  source: string;
}

export interface CharacterBoundaryData {
  topic: string;
  response_policy: string;
  flexibility: number;
}

export interface FullCharacterProfileResponse {
  identity: CharacterIdentityData;
  personality: PersonalityProfileData;
  values: CharacterValuesData;
  preferences: CharacterPreferenceData[];
  boundaries: CharacterBoundaryData[];
}
