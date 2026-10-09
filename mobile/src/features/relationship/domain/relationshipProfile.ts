export interface RelationshipDimensionsData {
  familiarity: number;
  trust: number;
  affection: number;
  intimacy: number;
  respect: number;
  comfort: number;
  attachment: number;
}

export interface RelationshipAnchorData {
  id: string;
  user_id: string;
  companion_id: string;
  anchor_type: string;
  summary: string;
  importance: number;
  created_at: string;
}

export interface CurrentRelationshipResponse {
  user_id: string;
  companion_id: string;
  stage: string;
  stage_display: string;
  dimensions: RelationshipDimensionsData;
  recent_presence: number;
  total_conversations: number;
  last_interacted_at: string | null;
}

export interface RelationshipTimelineResponse {
  current_stage: string;
  total_conversations: number;
  milestones: RelationshipAnchorData[];
}
