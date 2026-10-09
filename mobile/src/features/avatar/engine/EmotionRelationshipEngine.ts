import { RelationshipParameters } from '../domain/relationship_parameters';

export type RelationshipLevel = 'stranger' | 'familiar' | 'trusted' | 'close_companion';

/**
 * Emotion & Relationship Embodiment Engine (Sprint 44)
 * Modulates visual facial warmth, smile scale, eye contact, and head tilt based on relational bond.
 */
export class EmotionRelationshipEngine {
  /**
   * Classifies numerical parameters into UX relationship level
   */
  public static getRelationshipLevel(rel: RelationshipParameters): RelationshipLevel {
    const score = (rel.familiarity * 0.4 + rel.trust * 0.4 + rel.warmth * 0.2);
    if (score < 0.30) return 'stranger';
    if (score < 0.60) return 'familiar';
    if (score < 0.85) return 'trusted';
    return 'close_companion';
  }

  /**
   * Calculates modulated smile strength with relationship bias
   */
  public static modulateSmile(baseSmile: number, rel: RelationshipParameters): number {
    const familiarityFactor = 0.7 + 0.3 * Math.max(0.0, Math.min(1.0, rel.familiarity));
    const bonus = 0.15 * Math.max(0.0, Math.min(1.0, rel.warmth));
    return Math.min(1.0, Math.max(0.0, baseSmile * familiarityFactor + bonus));
  }

  /**
   * Calculates modulated warmth aura opacity
   */
  public static modulateWarmthAura(baseWarmth: number, rel: RelationshipParameters): number {
    return Math.min(1.0, Math.max(0.2, baseWarmth * 0.6 + rel.warmth * 0.4));
  }
}
