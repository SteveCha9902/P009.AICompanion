/**
 * Brow Engine (Sprint 41)
 * Calculates eyebrow elevation and furrow offsets.
 */
export class BrowEngine {
  public static calculateBrowTranslateY(browRaise: number): number {
    // -1.0 (Furrowed / Down 3px) to +1.0 (Raised / Up 4px)
    const clamped = Math.max(-1.0, Math.min(1.0, browRaise));
    return -clamped * 3.5;
  }
}
