/**
 * Latest Camera Frame Cache (P009 Client Engine)
 * - Retains the single most recent camera frame in-memory for instant multimodal binding
 * - Manages frameId, timestamp, image data, and capture status
 * - Graceful fallback to Audio-only mode when camera is unavailable
 */

export type CaptureStatus = "ready" | "capturing" | "stale" | "error" | "unavailable";

export interface CachedFrame {
  frameId: string;
  timestamp: number;
  uri: string;
  base64?: string;
  width?: number;
  height?: number;
  status: CaptureStatus;
}

export class LatestFrameCache {
  private latestFrame: CachedFrame | null = null;
  private status: CaptureStatus = "ready";
  private maxFreshnessMs: number = 10000; // 10 seconds freshness window

  public getStatus(): CaptureStatus {
    return this.status;
  }

  public setStatus(status: CaptureStatus): void {
    this.status = status;
    if (this.latestFrame) {
      this.latestFrame.status = status;
    }
  }

  /**
   * Updates the cache with a newly captured camera frame.
   */
  public updateFrame(photo: any): CachedFrame | null {
    if (!photo || (!photo.uri && !photo.base64)) {
      this.status = "error";
      return null;
    }

    const frameId = `frame_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    const newFrame: CachedFrame = {
      frameId,
      timestamp: Date.now(),
      uri: photo.uri || "",
      base64: photo.base64 || undefined,
      width: photo.width,
      height: photo.height,
      status: "ready",
    };

    this.latestFrame = newFrame;
    this.status = "ready";
    console.log(`[LatestFrameCache] 📸 Updated cache with Frame #${frameId} (${photo.width || "?"}x${photo.height || "?"})`);
    return newFrame;
  }

  /**
   * Returns the latest cached frame if available and fresh.
   * If stale or empty, returns null (triggers Audio-only fallback).
   */
  public getLatestFrame(): CachedFrame | null {
    if (!this.latestFrame) return null;

    const age = Date.now() - this.latestFrame.timestamp;
    if (age > this.maxFreshnessMs) {
      this.latestFrame.status = "stale";
      console.log(`[LatestFrameCache] Cached frame #${this.latestFrame.frameId} is stale (${age}ms old)`);
    }

    return this.latestFrame;
  }

  /**
   * Returns whether a valid camera frame is available for multimodal binding.
   */
  public isAvailable(): boolean {
    return this.latestFrame !== null && this.status !== "error" && this.status !== "unavailable";
  }

  /**
   * Clears the cached frame and resets status.
   */
  public clear(): void {
    this.latestFrame = null;
    this.status = "ready";
    console.log("[LatestFrameCache] Frame cache cleared.");
  }
}

export const latestFrameCache = new LatestFrameCache();
