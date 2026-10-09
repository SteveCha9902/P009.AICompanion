import { API_URL } from "../../../config/env";
import { TimelineEventData, StoryChapterData, LifeEventData, NarrativeResponse } from "../domain/timeline";

export async function getSharedTimeline(userId: string = "default_user", companionId: string = "default_companion"): Promise<TimelineEventData[]> {
  const res = await fetch(`${API_URL}/api/v1/memory/timeline?companion_id=${companionId}`, {
    headers: { "x-user-id": userId }
  });
  if (!res.ok) throw new Error(`Failed to fetch timeline: ${res.status}`);
  return await res.json();
}

export async function getStoryChapters(userId: string = "default_user", companionId: string = "default_companion"): Promise<StoryChapterData[]> {
  const res = await fetch(`${API_URL}/api/v1/memory/story?companion_id=${companionId}`, {
    headers: { "x-user-id": userId }
  });
  if (!res.ok) throw new Error(`Failed to fetch story chapters: ${res.status}`);
  return await res.json();
}

export async function getLifeEvents(userId: string = "default_user", companionId: string = "default_companion"): Promise<LifeEventData[]> {
  const res = await fetch(`${API_URL}/api/v1/memory/life-events?companion_id=${companionId}`, {
    headers: { "x-user-id": userId }
  });
  if (!res.ok) throw new Error(`Failed to fetch life events: ${res.status}`);
  return await res.json();
}

export async function generateNarrative(topic: string = "our_history", userId: string = "default_user", companionId: string = "default_companion"): Promise<NarrativeResponse> {
  const res = await fetch(`${API_URL}/api/v1/memory/narrative?companion_id=${companionId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-user-id": userId
    },
    body: JSON.stringify({ topic })
  });
  if (!res.ok) throw new Error(`Failed to generate narrative: ${res.status}`);
  return await res.json();
}
