import { API_URL } from "../../../config/env";
import { CurrentRelationshipResponse, RelationshipAnchorData, RelationshipTimelineResponse } from "../domain/relationshipProfile";

export async function getCurrentRelationship(userId: string = "default_user", companionId: string = "default_companion"): Promise<CurrentRelationshipResponse> {
  const res = await fetch(`${API_URL}/api/v1/relationships/current?companion_id=${companionId}`, {
    headers: { "x-user-id": userId }
  });
  if (!res.ok) throw new Error(`Failed to fetch relationship: ${res.status}`);
  return await res.json();
}

export async function getRelationshipAnchors(userId: string = "default_user", companionId: string = "default_companion"): Promise<RelationshipAnchorData[]> {
  const res = await fetch(`${API_URL}/api/v1/relationships/anchors?companion_id=${companionId}`, {
    headers: { "x-user-id": userId }
  });
  if (!res.ok) throw new Error(`Failed to fetch anchors: ${res.status}`);
  return await res.json();
}

export async function getRelationshipTimeline(userId: string = "default_user", companionId: string = "default_companion"): Promise<RelationshipTimelineResponse> {
  const res = await fetch(`${API_URL}/api/v1/relationships/timeline?companion_id=${companionId}`, {
    headers: { "x-user-id": userId }
  });
  if (!res.ok) throw new Error(`Failed to fetch timeline: ${res.status}`);
  return await res.json();
}
