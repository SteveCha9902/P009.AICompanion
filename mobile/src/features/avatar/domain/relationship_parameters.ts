/**
 * Relationship Parameters DTO (Sprint 44)
 */
export interface RelationshipParameters {
  familiarity: number;    // 0.0 ~ 1.0 (Stranger to Close Friend)
  trust: number;          // 0.0 ~ 1.0 (Base Trust to Absolute Trust)
  warmth: number;         // 0.0 ~ 1.0 (Polite distance to Deep warmth)
  engagement: number;     // 0.0 ~ 1.0 (Passive to Active)
}

export const DEFAULT_RELATIONSHIP_PARAMETERS: RelationshipParameters = {
  familiarity: 0.50,
  trust: 0.50,
  warmth: 0.50,
  engagement: 0.60,
};
