import { API_URL } from "../config/env";
import * as FileSystem from "expo-file-system/legacy";
import { CameraProvider, StubCameraProvider, CameraPermissionStatus } from "./camera/CameraProvider";
import { latestFrameCache } from "./camera/LatestFrameCache";

export interface DetectedObjectData {
  type: string;
  confidence: number;
  label?: string;
}

export interface AwarenessData {
  user_presence: boolean;
  face_detected: boolean;
  facial_emotion: string;
  attention_level: number;
  focus_target: string;
  detected_objects: DetectedObjectData[];
  awareness_timestamp_ms: number;
}

export interface VisionObservationData {
  id: string;
  observation_type: string;
  confidence: number;
  data: Record<string, any>;
  awareness?: AwarenessData;
}


export type VisionStatus = "inactive" | "active" | "sampling" | "error";

type VisionStatusListener = (status: VisionStatus, lastObs: VisionObservationData | null) => void;

class VisionController {
  private status: VisionStatus = "inactive";
  private currentSessionId: string | null = null;
  private cameraProvider: CameraProvider;
  private samplingTimer: any = null;
  private lastObservation: VisionObservationData | null = null;
  private listeners: Set<VisionStatusListener> = new Set();

  constructor() {
    this.cameraProvider = new StubCameraProvider();
  }

  public getStatus(): VisionStatus {
    return this.status;
  }

  public getLastObservation(): VisionObservationData | null {
    return this.lastObservation;
  }

  public subscribe(listener: VisionStatusListener): () => void {
    this.listeners.add(listener);
    listener(this.status, this.lastObservation);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify() {
    this.listeners.forEach(l => l(this.status, this.lastObservation));
  }

  public async startVision(companionId: string = "default_companion"): Promise<boolean> {
    const initialized = await this.cameraProvider.initialize();
    if (!initialized || this.cameraProvider.getPermissionStatus() === "DENIED") {
      this.status = "error";
      latestFrameCache.setStatus("unavailable");
      this.notify();
      return false;
    }

    try {
      this.cameraProvider.startCapture();
      latestFrameCache.setStatus("ready");
      
      // Start vision session
      const res = await fetch(`${API_URL}/api/v1/vision/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ companion_id: companionId }),
      });

      if (res.ok) {
        const data = await res.json();
        this.currentSessionId = data.session_id;
        this.status = "active";
        this.notify();

        // Start throttled frame sampling (every 4 seconds)
        this.startSampling();
        return true;
      }
    } catch (e) {
      console.warn("[VisionController] startVision failed (Failure Isolation):", e);
      this.status = "error";
      latestFrameCache.setStatus("error");
      this.notify();
    }
    return false;
  }

  private startSampling() {
    if (this.samplingTimer) clearInterval(this.samplingTimer);

    // Initial immediate sample
    this.sampleNow();

    // Periodic 4-second throttle sampling
    this.samplingTimer = setInterval(() => {
      this.sampleNow();
    }, 4000);
  }

  public setCameraRef(ref: any) {
    if (this.cameraProvider && typeof this.cameraProvider.setCameraRef === 'function') {
      this.cameraProvider.setCameraRef(ref);
    }
  }

  public async sampleNow(): Promise<VisionObservationData | null> {
    if (!this.currentSessionId || this.status === "inactive") return null;

    try {
      const frameResult = await this.cameraProvider.captureFrame();
      if (!frameResult || !frameResult.uri) {
        return null;
      }

      // Always update in-memory Latest Frame Cache (1 frame retention)
      latestFrameCache.updateFrame(frameResult);

      console.log(`[VisionController] Uploading camera frame (${frameResult.uri})...`);
      let rawBody: string | null = null;
      let statusCode = 0;

      try {
        const uploadResult = await FileSystem.uploadAsync(
          `${API_URL}/api/v1/vision/sessions/${this.currentSessionId}/observations`,
          frameResult.uri,
          {
            httpMethod: "POST",
            uploadType: FileSystem.FileSystemUploadType.MULTIPART,
            fieldName: "file",
            mimeType: "image/jpeg",
          }
        );
        statusCode = uploadResult.status;
        rawBody = uploadResult.body;
      } catch (fsErr) {
        // Fallback: standard FormData fetch for React Native 0.86+ engine
        const formData = new FormData();
        formData.append("file", {
          uri: frameResult.uri,
          name: "frame.jpg",
          type: "image/jpeg",
        } as any);

        const res = await fetch(
          `${API_URL}/api/v1/vision/sessions/${this.currentSessionId}/observations`,
          {
            method: "POST",
            body: formData,
          }
        );
        statusCode = res.status;
        rawBody = await res.text();
      }

      if (rawBody && statusCode >= 200 && statusCode < 300) {
        const obs: VisionObservationData = JSON.parse(rawBody);
        this.lastObservation = obs;
        this.notify();
        return obs;
      }
    } catch (err) {
      console.warn("[VisionController] sampleNow failed (Isolated):", err);
    }
    return null;
  }


  public async stopVision(): Promise<void> {
    if (this.samplingTimer) {
      clearInterval(this.samplingTimer);
      this.samplingTimer = null;
    }

    this.cameraProvider.stopCapture();

    if (this.currentSessionId) {
      try {
        await fetch(`${API_URL}/api/v1/vision/sessions/${this.currentSessionId}/end`, {
          method: "POST",
        });
      } catch (e) {
        // ignore close error
      }
      this.currentSessionId = null;
    }

    this.status = "inactive";
    this.notify();
  }

  public cleanup(): void {
    if (this.samplingTimer) {
      clearInterval(this.samplingTimer);
      this.samplingTimer = null;
    }
    this.cameraProvider.stopCapture();
    this.status = "inactive";
    this.notify();
    console.log("[VisionController] Privacy Cleanup: Camera capture & sampling stopped.");
  }
}

export const visionController = new VisionController();
