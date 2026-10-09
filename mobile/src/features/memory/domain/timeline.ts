export interface TimelineEventData {
  id: string;
  user_id: string;
  companion_id: string;
  occurred_at: string;
  title: string;
  summary: string;
  importance: number;
  event_type: string;
}

export interface StoryChapterData {
  id: string;
  user_id: string;
  companion_id: string;
  chapter_number: number;
  title: string;
  theme: string;
  started_at: string;
  ended_at: string | null;
  summary: string;
  importance: number;
}

export interface LifeEventData {
  id: string;
  title: string;
  summary: string;
  category: string;
  occurred_at: string | null;
  importance: number;
}

export interface NarrativeResponse {
  narrative: string;
  chapters_included: number;
  timeline_events_included: number;
}
