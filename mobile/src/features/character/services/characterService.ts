import { API_URL } from "../../../config/env";
import { FullCharacterProfileResponse } from "../domain/characterProfile";

export async function getCharacterProfile(companionId: string = "default_companion"): Promise<FullCharacterProfileResponse> {
  const response = await fetch(`${API_URL}/api/v1/character/profile?companion_id=${companionId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch character profile: ${response.status}`);
  }
  return await response.json();
}
