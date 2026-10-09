/**
 * Eye Engine (Sprint 41)
 * Controls random blinking intervals (2~7s) and real-time gaze direction (X/Y).
 */
export class EyeEngine {
  private static blinkTimer: ReturnType<typeof setTimeout> | null = null;

  public static scheduleNextBlink(onBlinkTrigger: (weight: number) => void): () => void {
    const nextInterval = 2000 + Math.random() * 5000; // 2.0s to 7.0s
    this.blinkTimer = setTimeout(() => {
      onBlinkTrigger(1.0);
      setTimeout(() => {
        onBlinkTrigger(0.0);
        this.scheduleNextBlink(onBlinkTrigger);
      }, 120); // 120ms blink duration
    }, nextInterval);

    return () => {
      if (this.blinkTimer) clearTimeout(this.blinkTimer);
    };
  }

  public static clampOpenness(value: number): number {
    return Math.max(0.0, Math.min(1.0, value));
  }

  public static clampDirection(value: number): number {
    return Math.max(-1.0, Math.min(1.0, value));
  }
}
